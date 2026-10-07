"""Turn generated double-surface shell into one solid printable exterior.

Reconstruction is local to a 0.45 mm grid. It does not alter musculature or
deliberately close externally accessible cavities such as the mouth/finger gaps.
The original GLB and inspection mesh remain unchanged.
"""
from pathlib import Path
import argparse
import gc
import json
import sys
import time

import numpy as np
import scipy.ndimage as ndi
import trimesh
import manifold3d as mf
from skimage.measure import marching_cubes

ROOT = Path(__file__).resolve().parent


def log(stage, **kwargs):
    print(stage, kwargs, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pitch', type=float, default=.45)
    parser.add_argument('--chunk', type=int, default=2500)
    parser.add_argument('--reuse-voxel-cache', action='store_true')
    args = parser.parse_args()
    started = time.time()
    data = np.load(ROOT / 'normalized_mesh.npz')
    vertices, faces = data['vertices'], data['faces']
    original_bounds = np.array([vertices.min(0), vertices.max(0)])
    pitch = args.pitch
    origin_idx = np.floor(original_bounds[0] / pitch).astype(np.int64) - 4
    shape = np.ceil(original_bounds[1] / pitch).astype(np.int64) - origin_idx + 5
    cache_file = ROOT / 'repair_surface_voxel_cache.npz'
    if args.reuse_voxel_cache and cache_file.exists():
        cache = np.load(cache_file)
        if float(cache['pitch']) != pitch or not np.array_equal(cache['origin_idx'], origin_idx):
            raise RuntimeError('Voxel cache does not match requested pitch/origin')
        surface = cache['surface']
    else:
        surface = np.zeros(shape, dtype=bool)
    log('voxelize_surface', shape=shape.tolist(), pitch_mm=pitch, grid_mb=surface.nbytes / 1e6)
    # Bound subdivision memory: independent triangle chunks rasterize into the same
    # global voxel grid. Maximum edge < pitch preserves six-connected occupancy.
    for start in range(0 if not args.reuse_voxel_cache else len(faces), len(faces), args.chunk):
        chunk = faces[start:start + args.chunk]
        used, inverse = np.unique(chunk, return_inverse=True)
        refined, _ = trimesh.remesh.subdivide_to_size(
            vertices[used], inverse.reshape(-1, 3), max_edge=pitch / 1.5,
            max_iter=10, return_index=False)
        points = np.rint(refined / pitch).astype(np.int64) - origin_idx
        surface[points[:, 0], points[:, 1], points[:, 2]] = True
        if start % (args.chunk * 20) == 0:
            log('rasterized', faces=min(start + args.chunk, len(faces)), total=len(faces))
    if not args.reuse_voxel_cache:
        del refined, points
    gc.collect()
    raw_occupied = int(surface.sum())
    if not args.reuse_voxel_cache:
        np.savez_compressed(cache_file, surface=surface, origin_idx=origin_idx, pitch=pitch)
    # Closing is one voxel and only repairs small shell cracks. It is not repeated
    # until the entire geometry changes, and never bridges large open features.
    closed = ndi.binary_closing(surface, structure=ndi.generate_binary_structure(3, 1), iterations=1)
    del surface
    gc.collect()
    log('fill_enclosed_cavities', rasterized_voxels=raw_occupied, closed_voxels=int(closed.sum()))
    # The generated artificial interior connects to outside through small clothing
    # seams. Horizontal cross-section fill closes its interior even where global
    # flood-fill sees a route out through a different slice. Anatomical openings
    # that are open within each section, such as the mouth and gaps between limbs,
    # remain exterior. No silhouette hull or muscle morphing is used.
    for z in range(closed.shape[2]):
        closed[:, :, z] = ndi.binary_fill_holes(closed[:, :, z])
    solid = ndi.binary_fill_holes(closed)
    del closed
    gc.collect()
    filled_voxels = int(solid.sum())
    log('extract_surface', filled_voxels=filled_voxels, filled_volume_mm3=filled_voxels * pitch ** 3)
    if filled_voxels * pitch ** 3 < 1500000:
        raise RuntimeError('Repair still contains a large artificial internal cavity; not a body solid')
    # Grid already has a four-cell zero border.
    v, f, _, _ = marching_cubes(solid, level=.5, spacing=(pitch, pitch, pitch),
                                gradient_direction='ascent', allow_degenerate=False)
    del solid
    gc.collect()
    v += origin_idx * pitch
    mesh = trimesh.Trimesh(v, f, process=True)
    del v, f
    components = mesh.split(only_watertight=False)
    components.sort(key=lambda c: len(c.faces), reverse=True)
    discarded = [{'triangles': len(c.faces), 'volume_mm3': float(abs(c.volume)), 'bounds_mm': c.bounds.tolist()}
                 for c in components[1:]]
    mesh = components[0]
    del components
    if mesh.volume < 0:
        mesh.invert()
    log('smooth', triangles=len(mesh.faces), components_discarded=len(discarded))
    trimesh.smoothing.filter_taubin(mesh, lamb=.30, nu=.31, iterations=4)
    # Preserve target total height and ground plane, with a tiny uniform adjustment.
    bounds_before_height = mesh.bounds.copy()
    height_scale = 470.0 / mesh.extents[2]
    mesh.vertices *= height_scale
    mesh.vertices[:, 2] -= mesh.bounds[0, 2]
    candidate = mf.Manifold(mf.Mesh64(np.ascontiguousarray(mesh.vertices, dtype=np.float64),
                                     np.ascontiguousarray(mesh.faces, dtype=np.uint64)))
    log('manifold_before_simplify', status=str(candidate.status()), volume_mm3=candidate.volume())
    if candidate.status() != mf.Error.NoError:
        raise RuntimeError(f'Reconstructed mesh is not a valid solid: {candidate.status()}')
    candidate = candidate.simplify(.03)
    if candidate.status() != mf.Error.NoError:
        raise RuntimeError(f'Simplification failed: {candidate.status()}')
    result = candidate.to_mesh64()
    rv = np.asarray(result.vert_properties[:, :3], dtype=np.float64)
    rf = np.asarray(result.tri_verts, dtype=np.int64)
    repaired = trimesh.Trimesh(rv, rf, process=False)
    if not repaired.is_watertight or not repaired.is_winding_consistent or len(candidate.decompose()) != 1:
        raise RuntimeError('Repair did not produce one watertight consistent component')
    np.savez_compressed(ROOT / 'repaired_solid_pending.npz', vertices=rv, faces=rf)
    log('measure_deviation', triangles=len(rf))
    sys.path.insert(0, str(ROOT.parent / 'blender_runtime'))
    import bpy
    from mathutils.bvhtree import BVHTree
    tree = BVHTree.FromPolygons(vertices.tolist(), faces.tolist(), all_triangles=True)
    indices = np.linspace(0, len(rv) - 1, min(25000, len(rv)), dtype=int)
    distances = np.array([tree.find_nearest(point)[3] for point in rv[indices]])
    report = {
        'status': 'Reconstructed one closed exterior solid; cuts, joints and print validation remain pending',
        'source': 'normalized_mesh.npz', 'output': 'repaired_solid.npz',
        'method': 'Triangle surface voxelization, one six-neighbor closing, horizontal section enclosed-loop fill, 3D enclosed cavity flood fill, marching cubes, minimal Taubin smoothing, Manifold simplification',
        'voxel_pitch_mm': pitch, 'grid_shape': shape.tolist(),
        'closing_iterations': 1, 'closing_neighborhood': 6,
        'taubin': {'iterations': 4, 'lambda': .30, 'nu': .31},
        'simplification_tolerance_mm': .03,
        'source_surface_occupied_voxels': raw_occupied,
        'filled_voxels': filled_voxels,
        'uniform_height_scale': float(height_scale),
        'bounds_before_height_normalization': bounds_before_height.tolist(),
        'original_bounds_mm': original_bounds.tolist(), 'repaired_bounds_mm': repaired.bounds.tolist(),
        'bounds_difference_mm': (repaired.bounds - original_bounds).tolist(),
        'dimensions_mm': repaired.extents.tolist(),
        'vertices': len(rv), 'triangles': len(rf),
        'volume_mm3': float(candidate.volume()),
        'manifold_status': str(candidate.status()),
        'watertight': bool(repaired.is_watertight),
        'winding_consistent': bool(repaired.is_winding_consistent),
        'components': len(candidate.decompose()),
        'discarded_isolated_components': discarded,
        'surface_deviation': {'method': 'Sampled repaired vertices to closest original source triangle, exact BVH triangle distance',
                              'samples': len(distances), 'median_mm': float(np.median(distances)),
                              'p95_mm': float(np.percentile(distances, 95)),
                              'p99_mm': float(np.percentile(distances, 99)),
                              'maximum_mm': float(distances.max())},
        'duration_seconds': time.time() - started,
        'cautions': ['Input inner shell intentionally removed; lightweight interior will be controlled by slicer walls and infill.',
                     'A watertight solid is not yet a printable assembly or proof of physical print success.']}
    (ROOT / 'repair_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    (ROOT / 'repaired_solid_pending.npz').replace(ROOT / 'repaired_solid.npz')
    log('complete', volume_mm3=report['volume_mm3'], triangles=len(rf), deviation=report['surface_deviation'])


if __name__ == '__main__':
    main()
