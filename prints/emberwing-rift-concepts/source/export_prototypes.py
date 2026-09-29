"""Extract, unite and check prototype parts from the committed Higgsfield GLB.

Run with Python 3.11+, trimesh 5.1, manifold3d 3.5, numpy, scipy and networkx.
No studio objects are exported. Output is millimetres, rear face on the bed.
These checks establish mesh integrity and bounding-box fit, not print or load tests.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'models/emberwing-rift.glb'
scene = trimesh.load(INPUT, force='scene')
groups = {}
for node in sorted(scene.graph.nodes_geometry):
    if not node.startswith(('EW_', 'RIFT_POD_')):
        continue
    transform, geometry = scene.graph[node]
    mesh = scene.geometry[geometry].copy()
    mesh.apply_transform(transform)
    # glTF splits vertices at normal/UV seams. Weld coincident positions first.
    mesh.merge_vertices(merge_tex=True, merge_norm=True)
    mesh.process(validate=True)
    mesh.apply_scale(1000)
    assert mesh.is_volume, f'Invalid source solid: {node}'
    groups.setdefault(node.split('__')[0], []).append(mesh)

assert len(groups) == 15, f'Unexpected part set: {list(groups)}'
entries = []
assemblies = {'emberwing': trimesh.Scene(), 'rift': trimesh.Scene()}
for name, pieces in sorted(groups.items()):
    unified = trimesh.boolean.union(pieces, engine='manifold', check_volume=True)
    assert unified.is_volume, f'Invalid union: {name}'
    assert len(unified.split()) == 1, f'Disconnected union: {name}'
    design = 'emberwing' if name.startswith('EW_') else 'rift'
    # GLB is Y-up: x=wall width, y=wall height, z=distance from wall.
    # These axes directly give the proposed rear-face-down print orientation.
    assemblies[design].add_geometry(unified.copy(), node_name=name)
    mesh = unified.copy()
    world_minimum = mesh.bounds[0].copy()
    mesh.apply_translation(-world_minimum)
    # Stabilise sub-micron union edges for STL's float32 coordinates.
    mesh.merge_vertices(digits_vertex=4)
    mesh.update_faces(mesh.unique_faces())
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    mesh.fix_normals(multibody=True)
    assert mesh.is_volume and len(mesh.split()) == 1, name
    assert np.all(mesh.extents < 246), f'Insufficient bed margin: {name}'
    dest = ROOT / 'files/stl' / design / f'{name}.stl'
    dest.parent.mkdir(parents=True, exist_ok=True)
    # All five Rift pods are checked, but distribute one repeatable print file.
    distributed = not name.startswith('RIFT_POD_') or name == 'RIFT_POD_01'
    if distributed:
        mesh.export(dest)
        reloaded = trimesh.load(dest, force='mesh')
        assert reloaded.is_volume and len(reloaded.split()) == 1, name
        assert np.allclose(reloaded.extents, mesh.extents, atol=.001)
    entries.append({
        'part': name, 'file': str(dest.relative_to(ROOT)).replace('\\', '/') if distributed else None,
        'quantity': 5 if name == 'RIFT_POD_01' else 1,
        'dimensions_xyz_mm': np.round(mesh.extents, 3).tolist(),
        'assembled_min_xyz_mm_gltf_axes': np.round(world_minimum, 3).tolist(),
        'watertight': bool(mesh.is_watertight), 'positive_volume': bool(mesh.volume > 0),
        'connected_components': len(mesh.split()), 'triangles': len(mesh.faces),
        'fits_246mm_margin_box': bool(np.all(mesh.extents < 246)),
        'solid_volume_cm3': round(float(mesh.volume / 1000), 3),
        'solid_equivalent_pla_mass_g_at_1_24': round(float(mesh.volume / 1000 * 1.24), 1),
        'sha256': hashlib.sha256(dest.read_bytes()).hexdigest() if distributed else None,
    })

for design, assembly in assemblies.items():
    # Keep portable model-only assemblies in metres, matching standard GLB units.
    assembly.apply_scale(.001)
    assembly.export(ROOT / 'models' / f'{design}-model-only.glb')

report = {
    'source': 'Higgsfield 3D Jutsu revision 3',
    'source_glb_sha256': hashlib.sha256(INPUT.read_bytes()).hexdigest(),
    'stl_units': 'mm', 'glb_units': 'm',
    'orientation': 'Rear face down. Review supports and first layers in the slicer.',
    'status': 'Mesh checked. Unsliced. Physical print, assembly and mounting untested.',
    'mass_note': 'Solid-equivalent mass is not slicer filament use. Infill and supports change consumption.',
    'parts': entries,
}
(ROOT / 'validation/mesh_validation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps({'checked_parts': len(entries), 'distributed_stls': sum(e['file'] is not None for e in entries),
                  'all_single_connected_solids': True, 'max_dimension_mm': max(max(e['dimensions_xyz_mm']) for e in entries)}, indent=2))
