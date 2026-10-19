from pathlib import Path
import numpy as np,manifold3d as mf,trimesh
from scipy import ndimage as ndi
from skimage.measure import marching_cubes
out=Path('work/venom_muscular');a=np.load('work/venom/source_480.npz');s=mf.Manifold(mf.Mesh64(a['vertices'],a['faces']));d=np.load(out/'envelope_voxels.npz');allowed=d['allowed'];origin=d['origin'];pitch=float(d['pitch']);allowed=np.pad(allowed,4,constant_values=False);origin=origin-4*pitch
v,f,_,_=marching_cubes(allowed.astype(np.float32),.5,spacing=(pitch,pitch,pitch),allow_degenerate=False);v+=origin;tm=trimesh.Trimesh(v,f,process=True);trimesh.repair.fix_normals(tm,multibody=True);print('CLOSED',tm.is_watertight,tm.is_volume,tm.volume,flush=True);assert tm.is_volume
tm=trimesh.smoothing.filter_laplacian(tm,lamb=.35,iterations=50,volume_constraint=False);mask=mf.Manifold(mf.Mesh64(np.asarray(tm.vertices,dtype=np.float64),np.asarray(tm.faces,dtype=np.uint64)));print('MASK',mask.status(),flush=True)
lower=mf.Manifold.cube((1000,1000,600)).translate((-500,-500,-270));mask=mask+lower
mm=mask.to_mesh64();np.savez_compressed(out/'muscle_envelope.npz',vertices=mm.vert_properties[:,:3],faces=mm.tri_verts)
clean=s^mask;clean=max(clean.decompose(),key=lambda c:c.volume()).as_original().simplify(.015);m=clean.to_mesh64();np.savez_compressed(out/'source_muscular.npz',vertices=m.vert_properties[:,:3],faces=m.tri_verts)
removed=s-clean;rm=removed.to_mesh64();np.savez_compressed(out/'removed.npz',vertices=rm.vert_properties[:,:3],faces=rm.tri_verts)
print('RESULT',clean.status(),clean.num_tri(),clean.bounding_box(),'removed volume',removed.volume(),flush=True)





