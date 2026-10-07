"""Fill generated interior slit artifacts without remeshing the polished skin."""
from pathlib import Path
import gc
import json
import numpy as np
import scipy.ndimage as ndi
from skimage.measure import marching_cubes
import trimesh
import manifold3d as mf

ROOT = Path(__file__).resolve().parent
cache = np.load(ROOT / 'repair_surface_voxel_cache.npz')
pitch = float(cache['pitch'])
origin_idx = cache['origin_idx']
volume = ndi.binary_closing(cache['surface'], structure=ndi.generate_binary_structure(3, 1), iterations=1)
x = (origin_idx[0] + np.arange(volume.shape[0])) * pitch
y = (origin_idx[1] + np.arange(volume.shape[1])) * pitch
z = (origin_idx[2] + np.arange(volume.shape[2])) * pitch
for zi in range(volume.shape[2]):
    volume[:, :, zi] = ndi.binary_fill_holes(volume[:, :, zi])
volume = ndi.binary_fill_holes(volume)
print('base_volume', volume.sum() * pitch**3, flush=True)
# Protect external negative spaces: hands outside |X|95 below waist, and the
# externally open mouth at forward Y<-55 above Z345.
def protected_mask(xvalue, yvalues, zvalues):
    body = (zvalues < 345) & (abs(xvalue) < np.where(zvalues < 210, 95, 110))
    head = (zvalues >= 345) & (zvalues < 437) & (abs(xvalue) < 75) & (yvalues > -55)
    return body | head

for xi, xv in enumerate(x):
    allowed = protected_mask(xv, y[:, None], z[None, :])
    if allowed.any():
        filled = ndi.binary_fill_holes(volume[xi])
        volume[xi] |= filled & allowed
print('after_YZ_fill', volume.sum() * pitch**3, flush=True)
for yi, yv in enumerate(y):
    allowed = protected_mask(x[:, None], yv, z[None, :])
    filled = ndi.binary_fill_holes(volume[:, yi, :])
    volume[:, yi, :] |= filled & allowed
volume = ndi.binary_fill_holes(volume)
print('after_XZ_fill', volume.sum() * pitch**3, flush=True)
# The core ends 1.8 mm inside the voxel envelope, so its union fills hidden slots
# without replacing the already polished anatomical exterior.
core = ndi.binary_erosion(volume, structure=ndi.generate_binary_structure(3, 1), iterations=4)
del volume
gc.collect()
for xi, xv in enumerate(x):
    core[xi] &= protected_mask(xv, y[:, None], z[None, :])
print('core_volume', core.sum()*pitch**3, flush=True)
v, f, _, _ = marching_cubes(core, .5, spacing=(pitch,)*3, gradient_direction='ascent', allow_degenerate=False)
del core
gc.collect()
v += origin_idx * pitch
scale = .9994207364391529
v *= scale
v[:,2] += .2376000968697206
cm = trimesh.Trimesh(v, f, process=True)
if cm.volume < 0: cm.invert()
core_solid = mf.Manifold(mf.Mesh64(np.ascontiguousarray(cm.vertices), np.ascontiguousarray(cm.faces,dtype=np.uint64)))
assert core_solid.status() == mf.Error.NoError, core_solid.status()
core_solid = core_solid.simplify(.15)
a = np.load(ROOT/'repaired_polished.npz')
skin = mf.Manifold(mf.Mesh64(np.ascontiguousarray(a['vertices']), np.ascontiguousarray(a['faces'],dtype=np.uint64)))
result = (skin + core_solid).as_original().simplify(.008)
print('union_status', str(result.status()), flush=True)
assert result.status()==mf.Error.NoError, result.status()
components = sorted(result.decompose(), key=lambda c: c.volume(), reverse=True)
discarded = [{'volume_mm3':c.volume(),'bounds_mm':list(c.bounding_box())} for c in components[1:]]
print('union_components', len(components), [c.volume() for c in components], flush=True)
result = components[0]
assert result.volume() > skin.volume()
r=result.to_mesh64();rv=np.asarray(r.vert_properties[:,:3]);rf=np.asarray(r.tri_verts)
check=trimesh.Trimesh(rv,rf,process=False)
assert check.is_watertight and check.is_winding_consistent
ray_rows=[]
for xx, yy in [(57,10),(-57,10),(0,10),(50,0),(-50,0)]:
    hits=result.ray_cast((xx,yy,50),(xx,yy,440))
    row={'xy_mm':[xx,yy], 'z_hits_mm':[float(h.position[2]) for h in hits]}
    ray_rows.append(row)
    print('ray',row,flush=True)
np.savez_compressed(ROOT/'repaired_polished_filled_pending.npz',vertices=rv,faces=rf)
report={'status':'Internal slit cavities filled with protected solid core',
        'source':'repaired_polished.npz','output':'repaired_polished_filled.npz',
        'method':'Orthogonal enclosed-loop fill, protected body/head region, 1.8mm eroded core union into polished exterior',
        'voxel_pitch_mm':pitch,'core_erosion_mm':4*pitch,
        'additional_coordinate_transform':False,
        'protected_mouth_region':'Above Z345, Y<=-55 excluded',
        'protected_hand_region':'Below Z210, |X|>=95 excluded',
        'volume_before_mm3':skin.volume(),'volume_after_mm3':result.volume(),
        'material_added_mm3':(result-skin).volume(),'bounds_before_mm':list(skin.bounding_box()),
        'bounds_after_mm':check.bounds.tolist(),'triangles':len(rf),
        'watertight':True,'winding_consistent':True,'manifold_status':str(result.status()),'components':1,
        'discarded_unattached_core_islands':discarded,
        'ray_verification':ray_rows}
(ROOT/'internal_core_report.json').write_text(json.dumps(report,indent=2))
(ROOT/'repaired_polished_filled_pending.npz').replace(ROOT/'repaired_polished_filled.npz')
print('complete',report,flush=True)
