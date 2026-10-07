"""Measure garment seams on actual generated geometry using its UV color texture.

Only garment_boundaries.json is written. This is analysis, not a geometry edit.
Angles are radians about +Z: 0=+X, pi/2=back, 3pi/2=front (-Y).
"""
from pathlib import Path
import json
import sys
import numpy as np
import trimesh
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'blender_runtime'))
import bpy  # Registers Blender's bundled mathutils modules.
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def fourier(theta, order=5):
    return np.column_stack([np.ones(len(theta))] +
                           [func(k * theta) for k in range(1, order + 1) for func in (np.cos, np.sin)])


def poly(xy, degree=3):
    # Normalized coordinates keep polynomial coefficients numerically stable.
    x, y = xy[:, 0] / 100, xy[:, 1] / 100
    powers = [(i, total - i) for total in range(degree + 1) for i in range(total + 1)]
    return np.column_stack([x**i * y**j for i, j in powers]), powers


class Sampler:
    def __init__(self):
        data = np.load(ROOT / 'normalized_objects/object_00.npz')
        self.vertices = data['vertices']
        self.faces = data['faces']
        self.uv = data['uv_corners']
        self.triangles = self.vertices[self.faces]
        self.centroids = self.triangles.mean(axis=1)
        scene = trimesh.load(ROOT / 'King_Shark_realistic_v2_raw.glb', force='scene')
        material = next(iter(scene.geometry.values())).visual.material
        self.texture = np.asarray(material.baseColorTexture)
        self.trees = {}
        for name, selector in [
            ('waist', (np.abs(self.centroids[:, 0]) < 99) & (self.centroids[:, 2] > 175) & (self.centroids[:, 2] < 265)),
            ('hem_negative_x', (self.centroids[:, 0] < -5) & (self.centroids[:, 0] > -105) & (self.centroids[:, 2] > 85) & (self.centroids[:, 2] < 170)),
            ('hem_positive_x', (self.centroids[:, 0] > 5) & (self.centroids[:, 0] < 105) & (self.centroids[:, 2] > 85) & (self.centroids[:, 2] < 170)),
            ('panels', (np.abs(self.centroids[:, 0]) < 102) & (self.centroids[:, 2] > 105) & (self.centroids[:, 2] < 235))
        ]:
            indices = np.flatnonzero(selector)
            self.trees[name] = (BVHTree.FromPolygons(self.vertices.tolist(), self.faces[indices].tolist(), all_triangles=True), indices)

    def sample(self, tree_name, center_xy, theta, z):
        direction = np.array([np.cos(theta), np.sin(theta), 0.])
        center = np.r_[center_xy, z]
        origin = center + direction * 145
        tree, mapping = self.trees[tree_name]
        location, normal, index, distance = tree.ray_cast(Vector(origin), Vector(-direction), 290)
        if location is None:
            return None
        xyz = np.asarray(location)
        original_index = mapping[index]
        tri = self.triangles[original_index]
        barycentric = trimesh.triangles.points_to_barycentric(tri[None], xyz[None])[0]
        uv = barycentric @ self.uv[original_index]
        tx = np.clip(int(round(uv[0] * (self.texture.shape[1] - 1))), 0, self.texture.shape[1] - 1)
        ty = np.clip(int(round((1 - uv[1]) * (self.texture.shape[0] - 1))), 0, self.texture.shape[0] - 1)
        rgb = self.texture[ty, tx, :3].astype(float)
        red = rgb[0] > max(rgb[1], rgb[2]) * 1.35 and rgb[0] > 23
        black = rgb.max() < 23
        skin = rgb.max() > 28 and rgb[0] < max(rgb[1], rgb[2]) * 1.26
        label = 1 if red or black else (0 if skin else -1)
        return dict(xyz=xyz, rgb=rgb, label=label, red=red, black=black, skin=skin,
                    source_triangle=int(original_index))


def measure_ring(sampler, name, center, heights, mode, prior):
    angles = np.deg2rad(np.arange(0, 360, 5))
    raw = []
    candidates = np.arange(heights[0] + 7, heights[-1] - 6, .25)
    for angle in angles:
        samples = [sampler.sample(name, center, angle, z) for z in heights]
        labels = np.array([s['label'] if s else -1 for s in samples])
        valid = labels >= 0
        candidates_here = candidates[np.abs(candidates - prior(angle)) < 15]
        scores = []
        for h in candidates_here:
            expected = heights < h if mode == 'waist' else heights >= h
            # A broad transition prior prevents distant knee shadows/cloth folds
            # from winning the classifier; the measured material edge is primary.
            score = np.count_nonzero((labels != expected) & valid) + .025 * (h - prior(angle))**2
            scores.append(score)
        height = candidates_here[int(np.argmin(scores))]
        nearby = np.abs(heights - height) < 5
        expected = heights < height if mode == 'waist' else heights >= height
        confidence = float(np.mean(labels[valid & nearby] == expected[valid & nearby]))
        point = sampler.sample(name, center, angle, height)
        raw.append(dict(angle_degrees=float(np.rad2deg(angle)), height_mm=float(height),
                        xyz_mm=point['xyz'].tolist() if point else None,
                        color_at_cut=point['rgb'].tolist() if point else None,
                        local_label_agreement=confidence))
    h = np.array([r['height_mm'] for r in raw])
    design = fourier(angles)
    initial = np.linalg.lstsq(design, h, rcond=None)[0]
    coefficient = least_squares(lambda b: design @ b - h, initial, loss='soft_l1', f_scale=.7).x
    smooth_h = design @ coefficient
    points = []
    for angle, height in zip(angles, smooth_h):
        sample = sampler.sample(name, center, angle, height)
        if sample:
            points.append(sample['xyz'].tolist())
    points = np.asarray(points)
    fitted = {}
    for degree in [2, 3, 4]:
        A, powers = poly(points[:, :2], degree)
        coef = np.linalg.lstsq(A, points[:, 2], rcond=None)[0]
        error = A @ coef - points[:, 2]
        fitted[str(degree)] = dict(powers_xy=powers, coefficients_mm=coef.tolist(),
                                   rms_boundary_error_mm=float(np.sqrt(np.mean(error**2))),
                                   maximum_boundary_error_mm=float(abs(error).max()))
    return dict(center_xy_mm=center, raw_samples=raw,
                smooth_boundary_xyz_mm=points.tolist(),
                periodic_height=dict(formula='c0 + sum(c_cos_k*cos(k*theta)+c_sin_k*sin(k*theta)), k=1..5',
                                     theta='atan2(y-center_y,x-center_x), radians',
                                     coefficients_mm=coefficient.tolist(),
                                     rms_raw_residual_mm=float(np.sqrt(np.mean((smooth_h - h)**2)))),
                height_field=dict(formula='z = sum(coeff[k]*(x/100)^powers[k][0]*(y/100)^powers[k][1])',
                                  fits=fitted),
                z_range_mm=[float(smooth_h.min()), float(smooth_h.max())],
                confidence_note='UV transitions identify material borders, not guaranteed geometric crease centers. Inspect cut intersections on the repaired exterior before final boolean splits.')


def measure_panel_front(sampler, side):
    # Only the visible front boundaries are stable in the reconstructed texture.
    # The inferred rear texture is asymmetric and cannot justify symmetric inserts.
    rows = []
    for z in np.arange(122, 213, 5):
        angles = np.deg2rad(np.arange(180 if side < 0 else 270, 271 if side < 0 else 361, 1))
        samples = [sampler.sample('panels', [0, 5], theta, z) for theta in angles]
        # Moving outer-side toward center-front on -X, center-front toward side on +X.
        good = [i for i, s in enumerate(samples) if s and s['red'] and abs(s['xyz'][0]) < 100]
        if not good:
            continue
        i = min(good) if side < 0 else max(good)
        # Require a red region rather than one noisy texture pixel.
        candidates = []
        for k in good:
            window = range(k, min(k + 5, len(samples))) if side < 0 else range(max(0, k - 4), k + 1)
            if sum(samples[j] is not None and samples[j]['red'] for j in window) >= 4:
                candidates.append(k)
        if candidates:
            i = min(candidates) if side < 0 else max(candidates)
            sample = samples[i]
            rows.append(dict(z_mm=float(z), xyz_mm=sample['xyz'].tolist(), angle_degrees=float(np.rad2deg(angles[i]))))
    return rows


def main():
    sampler = Sampler()
    waist = measure_ring(sampler, 'waist', [0, 5], np.arange(190, 256, .5), 'waist',
                         lambda t: 226.5 + 15.5 * np.sin(t) + 4 * np.cos(t)**2)
    negative = measure_ring(sampler, 'hem_negative_x', [-57, 10], np.arange(96, 146, .5), 'hem',
                            lambda t: 119 + 7 * np.sin(t) - 5 * np.cos(t))
    positive = measure_ring(sampler, 'hem_positive_x', [57, 10], np.arange(96, 146, .5), 'hem',
                            lambda t: 118 + 7 * np.sin(t) + 5 * np.cos(t))
    result = dict(status='Measured actual UV/geometry garment seam candidates; not yet cut or validated',
                  units='millimeters', coordinates='front -Y, up +Z, normalized height 470mm',
                  method='BVH radial ray casting of the normalized source shell. First hit samples interpolated triangle UV against original GLB albedo. This excludes interior shell layers and avoids face-centroid UV-seam artifacts.',
                  waist_skin_seam=waist, hem_negative_x=negative, hem_positive_x=positive,
                  front_side_panel_boundary_negative_x=measure_panel_front(sampler, -1),
                  front_side_panel_boundary_positive_x=measure_panel_front(sampler, 1),
                  implementation_notes=[
                      'Use measured 3D rings with RBFInterpolator or a triangulated height-field knife. Rings describe a split through original cloth/skin transitions, not replacement pants geometry.',
                      'The waist ring slopes strongly from low front to high back. Never substitute a horizontal plane.',
                      'For a low-degree compact knife, evaluate the provided normalized polynomial coefficients; use boundary error to decide if approximation is acceptable. High-degree polynomials can overshoot inside/outside ring; RBF plus sensible interior constraints is preferable.',
                      'Cut legs slightly inside the cloth hem undercut to hide glue seams, but inspect the actual repaired outer mesh first. Ring sample confidence is texture agreement only.',
                      'Waistband lower edge and rear side-panel borders are not fully recoverable from color alone: much inferred rear cloth is black. Preserve original waistband relief and use actual crease tracing for the black belt split.',
                      'Front side-panel curves identify red-to-black border candidates only; they do not define thick, removable inserts. Root must construct matching shallow cavities and verify insertion paths.',
                      'Separate eye/teeth geometry, print orientations, joint strength, model closure and supports are not addressed here.'
                  ])
    (ROOT / 'garment_boundaries.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    for name, ring in [('waist', waist), ('hem_negative_x', negative), ('hem_positive_x', positive)]:
        print(name, ring['z_range_mm'], 'Fourier residual', ring['periodic_height']['rms_raw_residual_mm'],
              'polynomial fits', {k: (round(v['rms_boundary_error_mm'], 3), round(v['maximum_boundary_error_mm'], 3)) for k, v in ring['height_field']['fits'].items()}, flush=True)
    print('front panels', len(result['front_side_panel_boundary_negative_x']), len(result['front_side_panel_boundary_positive_x']), flush=True)


if __name__ == '__main__':
    main()
