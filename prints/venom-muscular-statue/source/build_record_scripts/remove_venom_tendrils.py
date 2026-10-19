from pathlib import Path
import numpy as np,manifold3d as mf,json
from PIL import Image,ImageDraw
from scipy import ndimage as ndi
from skimage.measure import marching_cubes
import trimesh
out=Path('work/venom_muscular');out.mkdir(exist_ok=True)
a=np.load('work/venom/source_480.npz');s=mf.Manifold(mf.Mesh64(a['vertices'],a['faces']))
pitch=.65;origin=np.array([-215.,-125.,300.]);shape=np.ceil((np.array([215.,125.,490.])-origin)/pitch).astype(int)+1;vol=np.zeros(tuple(shape),dtype=bool)
for k in range(shape[2]):
 polys=s.slice(origin[2]+k*pitch).to_polygons();im=Image.new('1',(int(shape[0]),int(shape[1])));draw=ImageDraw.Draw(im)
 for poly in sorted(polys,key=lambda p:-abs(np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1)))):
  area=np.sum(poly[:,0]*np.roll(poly[:,1],-1)-poly[:,1]*np.roll(poly[:,0],-1));p=(poly-origin[:2])/pitch;draw.polygon([tuple(x) for x in p],fill=int(area>0))
 vol[:,:,k]=np.asarray(im).T
print('VOXEL',shape,vol.sum(),flush=True)
# A rolling 12 mm interior radius distinguishes broad muscle masses from the thin external tendrils.
inside=ndi.distance_transform_edt(vol,sampling=pitch);core=inside>=18;del inside
distance=ndi.distance_transform_edt(~core,sampling=pitch);del core
x=origin[0]+np.arange(shape[0])*pitch;y=origin[1]+np.arange(shape[1])*pitch;z=origin[2]+np.arange(shape[2])*pitch
# Preserve the lower body, and the original face/tongue at the front of the head.
allowance=18.2+np.clip((350-z)/20,0,1)*45
allowed=distance<allowance[None,None,:];del distance
allowed|=(z[None,None,:]<330)
head=((x[:,None]+20)/58)**2+((y[None,:]+90)/55)**2<1
allowed|=head[:,:,None] & (z[None,None,:]>378)
allowed[:,:,0]=False;allowed[:,:,-1]=False;allowed[0,:,:]=False;allowed[-1,:,:]=False;allowed[:,0,:]=False;allowed[:,-1,:]=False
np.savez_compressed(out/'envelope_voxels.npz',allowed=allowed,origin=origin,pitch=pitch)
v,f,_,_=marching_cubes(allowed.astype(np.float32),.5,spacing=(pitch,pitch,pitch));v+=origin;tm=trimesh.Trimesh(v,f,process=True);trimesh.repair.fix_normals(tm)
tm=trimesh.smoothing.filter_laplacian(tm,lamb=.35,iterations=3,volume_constraint=False);mask=mf.Manifold(mf.Mesh64(np.asarray(tm.vertices,dtype=np.float64),np.asarray(tm.faces,dtype=np.uint64)));print('MASK',mask.status(),flush=True)
lower=mf.Manifold.cube((1000,1000,600)).translate((-500,-500,-270));mask=mask+lower
mm=mask.to_mesh64();np.savez_compressed(out/'muscle_envelope.npz',vertices=mm.vert_properties[:,:3],faces=mm.tri_verts)
clean=s^mask;clean=max(clean.decompose(),key=lambda c:c.volume()).as_original().simplify(.015);m=clean.to_mesh64();np.savez_compressed(out/'source_muscular.npz',vertices=m.vert_properties[:,:3],faces=m.tri_verts)
removed=s-clean;rm=removed.to_mesh64();np.savez_compressed(out/'removed.npz',vertices=rm.vert_properties[:,:3],faces=rm.tri_verts)
print('RESULT',clean.status(),clean.num_tri(),clean.bounding_box(),'removed volume',removed.volume(),flush=True)


