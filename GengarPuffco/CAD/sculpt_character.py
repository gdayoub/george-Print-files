"""Clean, smoothly blended Gengar-inspired exterior. Coordinates in millimetres.

The original Puffco meshes are not processed here. They are fitted and protected
by build_gengar.py after this decorative sculpt is generated.
"""
from pathlib import Path
import hashlib
import numpy as np
from scipy.interpolate import PchipInterpolator
from skimage.measure import marching_cubes
import trimesh
from manifold3d import Manifold, Mesh64


def sculpt(out):
    key=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    cache=out/'clean_sculpt.npz';stamp=out/'clean_sculpt.sha256'
    if cache.exists() and stamp.exists() and stamp.read_text()==key:
        d=np.load(cache)
        return Manifold(Mesh64(d['vertices'],d['faces'].astype(np.uint64)))
    step=.42
    origin=np.array([-78.,-61.,-4.])
    x=np.arange(-78,78.1,step,dtype=np.float32)[:,None,None]
    y=np.arange(-61,66.1,step,dtype=np.float32)[None,:,None]
    z=np.arange(-4,131.1,step,dtype=np.float32)[None,None,:]
    # One continuous rounded body; enough shoulder width to enclose the full lid.
    heights=[0,8,18,35,55,75,90,102,108,110,112,114]
    radii=[24,38,48,55,57,56,52,45,38,35,29,0]
    r=PchipInterpolator(heights,radii)(np.clip(z,0,114)).astype(np.float32)
    rho=np.sqrt(x*x+(y/.84)**2)
    field=rho-r
    field=np.where(z>=110,z-114+4*(rho/35)**4,field)
    field=np.maximum(field,np.maximum(-z,z-114))

    def blend(other,k=3.):
        nonlocal field
        h=np.maximum(k-np.abs(field-other),0)/k
        field=np.minimum(field,other)-h*h*k*.25

    def ellipsoid(c,s,k=3.):
        v=(np.sqrt(((x-c[0])/s[0])**2+((y-c[1])/s[1])**2+((z-c[2])/s[2])**2)-1)*min(s)
        blend(v,k)

    def spike(a,b,r0,r1,depth=1.,k=3.):
        a=np.array(a,dtype=np.float32);b=np.array(b,dtype=np.float32)
        a[1]/=depth;b[1]/=depth;v=b-a
        px=x-a[0];py=y/depth-a[1];pz=z-a[2]
        t=np.clip((px*v[0]+py*v[1]+pz*v[2])/np.dot(v,v),0,1)
        d=np.sqrt((px-t*v[0])**2+(py-t*v[1])**2+(pz-t*v[2])**2)
        blend(d-(r0+(r1-r0)*t),k)

    for side in [-1,1]:
        # Swept ears, short arms, and broad low feet blend into the same surface.
        spike((side*34,-3,96),(side*57,-2,125),14,1.,.72,4.)
        spike((side*47,0,65),(side*67,-8,44),12,4.,.85,4.)
        ellipsoid((side*29,-12,7),(18,24,10),4.)
        # Small rear crown spikes flank the central point.
        spike((side*15,14,108),(side*21,15,120),7,.8,.55,4.)
    spike((0,15,108),(0,17,124),8,1.,.55,4.)
    # Back ridge: controlled triangular peaks rather than overlapping shells.
    for center,tip,radius in [((0,38,91),(0,54,100),9),((0,43,73),(0,60,79),10),((0,43,54),(0,59,56),10)]:
        spike(center,tip,radius,1.,1.,3.)

    vertices,faces,_,_=marching_cubes(field,level=0,spacing=(step,step,step),allow_degenerate=False)
    vertices+=origin
    t=trimesh.Trimesh(vertices,faces,process=True)
    trimesh.smoothing.filter_taubin(t,lamb=.5,nu=.53,iterations=12)
    t.fix_normals()
    result=Manifold(Mesh64(np.asarray(t.vertices),np.asarray(t.faces,dtype=np.uint64)))
    assert str(result.status())=='Error.NoError'
    result=result.simplify(.025)
    m=result.to_mesh64()
    np.savez_compressed(cache,vertices=np.asarray(m.vert_properties)[:,:3],faces=np.asarray(m.tri_verts))
    stamp.write_text(key)
    return result
