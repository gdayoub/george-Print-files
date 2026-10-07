"""Physical, integrated shark eyes at the actual source's lateral eye positions.

Writes eye_parts/Eye_sockets.npz, Eyeballs.npz and eye_parameters.json.
The sockets are subtracted first, then eyeballs unioned into the closed head.
Optional --head-source validates connectivity and renders an actual clay crop.
"""
from pathlib import Path
import argparse
import json
import sys
import numpy as np
import manifold3d as mf
import trimesh

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'blender_runtime'))
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def solid(v, f):
    return mf.Manifold(mf.Mesh64(np.ascontiguousarray(v, dtype=np.float64),
                               np.ascontiguousarray(f, dtype=np.uint64)))


def load(path):
    data = np.load(path)
    m = solid(data['vertices'], data['faces'])
    if m.status() != mf.Error.NoError:
        raise ValueError(f'{path}: {m.status()}')
    return m


def save(m, path):
    mesh = m.to_mesh64()
    np.savez_compressed(path, vertices=np.asarray(mesh.vert_properties)[:, :3], faces=np.asarray(mesh.tri_verts))


def ellipsoid(center, radii, R=np.eye(3)):
    m = trimesh.creation.icosphere(subdivisions=4, radius=1)
    v = (m.vertices * radii) @ R.T + center
    return solid(v, m.faces)


def eye_frame(normal):
    n = np.asarray(normal, dtype=float)
    n /= np.linalg.norm(n)
    up = np.array([0., 0, 1])
    up -= n * (up @ n)
    up /= np.linalg.norm(up)
    across = np.cross(up, n)
    return np.column_stack([across, up, n])


def fit_surface(tree, side, y0, z0):
    # Texture iris dark spot sits in a malformed depression. Fit the surrounding
    # 4..7mm annulus to anchor the natural eye plane, not the depression bottom.
    points = []
    for y in np.arange(y0 - 8, y0 + 8.01, .5):
        for z in np.arange(z0 - 8, z0 + 8.01, .5):
            if 4 < np.hypot(y - y0, z - z0) < 7:
                hit, normal, index, distance = tree.ray_cast(Vector((side * 200, y, z)), Vector((-side, 0, 0)))
                if hit is not None:
                    points.append(list(hit))
    pts = np.asarray(points)
    A = np.column_stack([np.ones(len(pts)), pts[:, 1] - y0, pts[:, 2] - z0])
    b = np.linalg.lstsq(A, pts[:, 0], rcond=None)[0]
    n = side * np.array([1, -b[1], -b[2]])
    n /= np.linalg.norm(n)
    return np.array([b[0], y0, z0]), n


def render_head(head, path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.studiolight_rotate_z = .35
    scene.display.shading.color_type = 'MATERIAL'
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = 'WORLD'
    scene.display.shading.cavity_ridge_factor = 1.2
    scene.display.shading.cavity_valley_factor = 1.4
    scene.display.shading.background_type = 'WORLD'
    scene.world = bpy.data.worlds.new('Eye_detail_world')
    scene.world.color = (.055, .065, .08)
    scene.view_settings.view_transform = 'Standard'
    m = head.to_mesh64()
    data = bpy.data.meshes.new('Actual_edited_head')
    data.from_pydata(np.asarray(m.vert_properties)[:, :3].tolist(), [], np.asarray(m.tri_verts).tolist())
    data.update()
    obj = bpy.data.objects.new('Actual_edited_head', data)
    scene.collection.objects.link(obj)
    material = bpy.data.materials.new('Neutral_clay_no_texture')
    material.diffuse_color = (.40, .43, .47, 1)
    obj.data.materials.append(material)
    for polygon in data.polygons:
        polygon.use_smooth = True
    cam = bpy.data.objects.new('Detail_camera', bpy.data.cameras.new('Detail_camera'))
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 120
    cam.data.clip_end = 6000
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    for label, location in [('positive', (1000, -650, 440)), ('negative', (-1000, -650, 440)), ('front', (0, -1500, 412))]:
        cam.location = location
        cam.rotation_euler = (Vector((6, -60, 400)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = str(path / f'eyes_geometry_{label}.png')
        bpy.ops.render.render(write_still=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--head-source', type=Path)
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args()
    source = np.load(ROOT / 'normalized_objects/object_00.npz')
    tree = BVHTree.FromPolygons(source['vertices'].tolist(), source['faces'].tolist(), all_triangles=True)
    sockets, balls, rows = [], [], []
    # Centers located by calibrated lateral textured renders of the actual mesh.
    # Asymmetry is retained because the source head has a slight lateral turn.
    for side, y0, z0, raw_center in [
        (-1, -80.57, 402.38, [-19.2489, -80.5730, 402.375]),
        (1, -78.42, 403.125, [35.6123, -78.4171, 403.125])
    ]:
        center, normal = fit_surface(tree, side, y0, z0)
        R = eye_frame(normal)
        # Oval recess preserves the brow; a mostly embedded sphere merges into
        # the head at the cavity floor instead of becoming a separate insert.
        socket = ellipsoid(center + normal * .5, np.array([4.15, 2.45, 2.7]), R)
        ball_center = center - normal * 1.7
        ball = ellipsoid(ball_center, np.array([2.8, 2.8, 2.8]))
        # 2mm-wide, .35mm-deep pupil dimple adds readable physical shadow in gray
        # filament without a paint texture, floating detail or AMS color change.
        pupil_center = ball_center + normal * (2.8 + .65)
        pupil = ellipsoid(pupil_center, np.array([1., 1., 1.]))
        ball = ball - pupil
        if ball.status() != mf.Error.NoError or socket.status() != mf.Error.NoError:
            raise ValueError('Eye detail manifold operation failed')
        sockets.append(socket)
        balls.append(ball)
        rows.append(dict(side='negative_X' if side < 0 else 'positive_X',
                         source_iris_surface_mm=raw_center, surface_anchor_mm=center.tolist(),
                         normal_outward=normal.tolist(), local_basis_columns=R.tolist(),
                         socket_center_mm=(center + normal * .5).tolist(),
                         socket_radii_mm=[4.15, 2.45, 2.7],
                         eyeball_center_mm=ball_center.tolist(), eyeball_radius_mm=2.8,
                         pupil_radius_mm=1.0, pupil_depth_mm=.35,
                         maximum_eyeball_projection_from_anchor_mm=1.1))
    all_sockets = mf.Manifold.batch_boolean(sockets, mf.OpType.Add)
    all_balls = mf.Manifold.batch_boolean(balls, mf.OpType.Add)
    normalization = dict(scale=1., translation_mm=[0., 0., 0.])
    repair_report = ROOT / 'repair_report.json'
    if repair_report.exists():
        report = json.loads(repair_report.read_text())
        scale = report['uniform_height_scale']
        offset_z = -report['bounds_before_height_normalization'][0][2] * scale
        offset = np.array([0., 0., offset_z])
        all_sockets = all_sockets.scale((scale, scale, scale)).translate(offset)
        all_balls = all_balls.scale((scale, scale, scale)).translate(offset)
        normalization = dict(scale=scale, translation_mm=offset.tolist())
        for row in rows:
            for key in ['surface_anchor_mm', 'socket_center_mm', 'eyeball_center_mm']:
                row[key] = (np.array(row[key]) * scale + offset).tolist()
            row['socket_radii_mm'] = (np.array(row['socket_radii_mm']) * scale).tolist()
            for key in ['eyeball_radius_mm', 'pupil_radius_mm', 'pupil_depth_mm', 'maximum_eyeball_projection_from_anchor_mm']:
                row[key] *= scale
    out = ROOT / 'eye_parts'
    out.mkdir(exist_ok=True)
    save(all_sockets, out / 'Eye_sockets.npz')
    save(all_balls, out / 'Eyeballs.npz')
    validation = dict(source_head_checked=False, intended_sequence='(closed_head - Eye_sockets) + Eyeballs',
                      eye_radius_mm=2.8, socket_status=str(all_sockets.status()), eyeball_status=str(all_balls.status()),
                      socket_components=len(all_sockets.decompose()), eyeball_components=len(all_balls.decompose()))
    if args.head_source:
        head = load(args.head_source)
        source_components = len(head.decompose())
        # Check connectivity after actual Boolean union, not a visual overlap.
        edited = (head - all_sockets) + all_balls
        validation.update(source_head_checked=True, source_head=str(args.head_source.resolve()),
                          edited_status=str(edited.status()), components_before=source_components,
                          components_after=len(edited.decompose()),
                          socket_removed_mm3=float((head ^ all_sockets).volume()),
                          eyeball_overlap_remaining_head_mm3=float(((head - all_sockets) ^ all_balls).volume()))
        validation['connected_to_head'] = len(edited.decompose()) == source_components
        if not validation['connected_to_head'] or edited.status() != mf.Error.NoError:
            raise ValueError(json.dumps(validation))
        if args.render:
            crop = mf.Manifold.cube([500, 500, 200]).translate([-250, -250, 335])
            render_head(edited ^ crop, out)
    result = dict(status='Small physical socket and integrated eyeball geometry; final head verification recorded below',
                  units='millimeters', coordinate_system='Final repaired/polished coordinates; front -Y, up +Z, height470',
                  raw_normalized_to_repaired_transform_applied=normalization,
                  source_likelihood='Positions located from actual textured lateral renders and source BVH ray hits, then adjusted to the surrounding anatomy plane; not chosen from a broad dark-pixel threshold.',
                  operation='Subtract Eye_sockets.npz from repaired head, then union Eyeballs.npz. Do not add balls as separate print objects.',
                  notes=['Eyes are 5.6mm diameter and mostly embedded, preserving small lateral shark eyes.',
                         'Original upper brow and eyelid region remain; an oval recess and shallow pupil depression provide real printed shadows.',
                         'Gray/charcoal head prints eyes in the same filament; no new pieces or AMS changes.',
                         'If whole-model coordinates change during repair normalization, apply the same rigid/scale transform to these NPZs before Boolean operations.'],
                  eyes=rows, validation=validation)
    (ROOT / 'eye_parameters.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(validation, indent=2), flush=True)


if __name__ == '__main__':
    main()
