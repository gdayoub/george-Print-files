"""Cut the repaired actual sculpt, preserving its exterior and proven glue keys."""
from pathlib import Path
import argparse, json
import numpy as np
import trimesh
import manifold3d as mf
from shapely.geometry import Polygon
from shapely.ops import polylabel

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'final_parts'; OUT.mkdir(exist_ok=True)

def log(*args): print(*args,flush=True)
def load(path):
    a=np.load(path);return mf.Manifold(mf.Mesh64(np.ascontiguousarray(a['vertices'],dtype=np.float64),np.ascontiguousarray(a['faces'],dtype=np.uint64)))
def mesh(s):
    a=s.to_mesh64();return trimesh.Trimesh(a.vert_properties[:,:3],a.tri_verts,process=False)
def save(s,path):
    assert s.status()==mf.Error.NoError,(path,s.status())
    a=s.to_mesh64();np.savez_compressed(path,vertices=a.vert_properties[:,:3],faces=a.tri_verts)
def union(ss):return mf.Manifold.batch_boolean(ss,mf.OpType.Add).as_original()
def main(s,minvol=1):
    cs=s.decompose();keep=[c for c in cs if c.volume()>minvol]
    return union(keep) if keep else mf.Manifold()
def largest(s):return max(s.decompose(),key=lambda c:c.volume())
def frame(n):
    n=np.array(n,float);n/=np.linalg.norm(n)
    u=np.array([1.,0,0]) if abs(n[0])<.8 else np.array([0.,1,0]);u-=n*(u@n);u/=np.linalg.norm(u)
    return np.column_stack((u,np.cross(n,u),n))
def plane(s,n,off):return s.trim_by_plane(tuple(n),float(off))

garment=json.loads((ROOT/'garment_boundaries.json').read_text())
def seam_function(key,offset=0):
    row=garment[key];fit=row['height_field']['fits']['3'];center=np.array(row['center_xy_mm'])
    ring=np.array(row['smooth_boundary_xyz_mm']);radii=np.max(abs(ring[:,:2]-center),axis=0)
    def polynomial(x,y):return sum(c*(x/100)**p*(y/100)**q for c,(p,q) in zip(fit['coefficients_mm'],fit['powers_xy']))
    inner=float(polynomial(*center))+offset
    def height(x,y):
        # Exterior seam follows the measured curved boundary. A concealed flat
        # center provides a broad glue face and an exact plane for the peg root.
        rho=np.sqrt(((x-center[0])/radii[0])**2+((y-center[1])/radii[1])**2)
        blend=np.clip((rho-.50)/.35,0,1);blend=blend*blend*(3-2*blend)
        z=np.clip(polynomial(x,y)+offset,min(row['z_range_mm'])-12,max(row['z_range_mm'])+5)
        return inner*(1-blend)+z*blend
    return height,center,inner

def heightfield_below(fn):
    xs=np.linspace(-180,180,181);ys=np.linspace(-150,150,151)
    X,Y=np.meshgrid(xs,ys,indexing='ij');Z=fn(X,Y)
    v=np.c_[X.ravel(),Y.ravel(),Z.ravel()];nx,ny=X.shape;faces=[]
    for i in range(nx-1):
        for j in range(ny-1):
            a=i*ny+j;b=(i+1)*ny+j;c=b+1;d=a+1;faces.extend([(a,b,c),(a,c,d)])
    boundary=list(range(0,(nx-1)*ny+1,ny))+list(range((nx-1)*ny+1,nx*ny))+list(range((nx-2)*ny+ny-1,ny-2,-ny))+list(range(ny-2,0,-1))
    m=len(v);bottom=v[boundary].copy();bottom[:,2]=-50;v=np.vstack([v,bottom,[[0,0,-50]]]);ctr=len(v)-1
    for k,a in enumerate(boundary):
        j=(k+1)%len(boundary);b=boundary[j];faces.extend([(a,m+j,b),(a,m+k,m+j),(ctr,m+j,m+k)])
    s=mf.Manifold(mf.Mesh64(np.ascontiguousarray(v),np.array(faces,dtype=np.uint64)))
    assert s.status()==mf.Error.NoError,s.status();return s

def key(parts,j,i):
    a,b=j['a'],j['b'];n=np.array(j['n'],float);n/=np.linalg.norm(n);R=frame(n)
    o=n*j['off'];T=np.c_[R.T,-R.T@o]
    aa=parts[a].transform(T);bb=parts[b].transform(T)
    if 'center' in j:
        p=R.T@(np.array(j['center'])-o);cx,cy=p[:2];r=j['r']
    else:
        cr=aa.slice(-.35)^bb.slice(.35)
        ps=[Polygon(p).buffer(0) for p in cr.to_polygons() if len(p)>=3];ps=[p for p in ps if p.area>1]
        poly=max(ps,key=lambda p:p.area);p=polylabel(poly,.04);cx,cy=p.x,p.y;r=min(j['r'],p.distance(poly.boundary)*.5)
    L=j['L'];success=False
    for k in range(20):
        t=np.linspace(0,2*np.pi,64,endpoint=False)
        cs=mf.CrossSection([np.c_[r*(1+.09*np.cos(3*t))*np.cos(t),.76*r*(1+.06*np.sin(2*t))*np.sin(t)]])
        root=mf.Manifold.extrude(cs,2.5).translate((cx,cy,-2.5))
        peg=mf.Manifold.extrude(cs,L,scale_top=(.84,.84)).translate((cx,cy,0))
        sock=mf.Manifold.extrude(cs.offset(.18),L+.5,scale_top=(.87,.87)).translate((cx,cy,-.12))
        er=(root-aa).volume();ef=(sock.trim_by_plane((0,0,1),.35)-bb).volume()
        if er<.02 and ef<.02:success=True;break
        r*=.9
        if k>7:L*=.92
    assert success and r>2,(a,b,r,L,er,ef)
    W=np.c_[R,o];parts[a]=main(parts[a]+(root+peg).transform(W));parts[b]=main(parts[b]-sock.transform(W))
    intr=(peg.transform(W)^parts[b]).volume();assert intr<.001
    rec=dict(id=f'J{i+1:02}',male=a,female=b,center_mm=(o+R@np.array([cx,cy,0])).tolist(),normal=n.tolist(),half_width_mm=r,half_depth_mm=.76*r,length_mm=L,root_depth_mm=2.5,minimum_nominal_radial_clearance_mm=.18,blind_depth_extra_mm=.38,key_shape='64-sided asymmetric rounded taper; tip scale 0.84',key_vs_socket_interference_mm3=intr,root_exposure_mm3=er,socket_exposure_mm3=ef)
    log('KEY',a,b,'radius',r,'length',L);return rec

def run():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['cuts','full'],default='full');args=ap.parse_args()
    source=ROOT/'repaired_polished_filled.npz'
    whole=load(source);assert whole.volume()>1500000,'Source repair is still shell'
    parts={};joints=[];inserts=[]
    # Each arm and hand remains one piece. Vertical shoulder seams stay clear
    # of the inward-curled thumbs further down the arm.
    upper=whole
    for sign,name in [(1,'L_arm'),(-1,'R_arm')]:
        n=np.array([float(sign),0,0]);off=85.0
        # The same infinite plane crosses the widely planted feet. Retain only
        # its arm component so unrelated foot/cloth slivers stay on the body.
        parts[name]=largest(plane(upper,n,off));upper=upper-parts[name]
        joints.append(dict(a='Torso',b=name,n=n,off=off,r=13,L=12))
    # Keep the black waistband with the upper body. Seam runs at its lower edge.
    waist,cw,zw=seam_function('waist_skin_seam',-6.5);wc=heightfield_below(waist)
    lower=main(upper^wc);torso=main(upper-wc)
    for sign,side,keyname in [(1,'L','hem_positive_x'),(-1,'R','hem_negative_x')]:
        fn,cc,zz=seam_function(keyname,.7);knife=plane(heightfield_below(fn),(sign,0,0),0)
        parts[side+'_leg']=main(plane(lower^knife,(0,0,1),.5));lower=main(lower-knife)
        joints.append(dict(a=side+'_leg',b='Shorts',n=[0,0,1],off=zz,center=[cc[0],cc[1],zz],r=13,L=16))
    parts['Shorts']=lower
    n=np.array([0,.5,1.]);n/=np.linalg.norm(n);off=460/np.sqrt(1.25)
    parts['Dorsal_fin']=main(plane(torso,n,off));parts['Torso']=main(plane(torso,-n,-off))
    joints.append(dict(a='Torso',b='Dorsal_fin',n=n,off=off,r=6,L=9))
    joints.append(dict(a='Shorts',b='Torso',n=[0,0,1],off=zw,center=[cw[0],cw[1],zw],r=19,L=16))
    colors={name:('Red' if name=='Shorts' else 'Black') for name in parts}
    if args.stage=='cuts':
        dst=ROOT/'cut_preview';dst.mkdir(exist_ok=True)
        for name,s in parts.items():
            save(s,dst/(name+'.npz'));log('CUT',name,s.volume(),len(s.decompose()),mesh(s).bounds.tolist())
        (dst/'joint_plan.json').write_text(json.dumps(joints,indent=2,default=lambda a:a.tolist()))
        return
    # Small anatomically placed eyes, reconstructed as actual surface relief.
    eyes=ROOT/'eye_parts'
    if not eyes.exists():raise RuntimeError('Eye geometry is not ready')
    parts['Torso']=main(parts['Torso']-load(eyes/'Eye_sockets.npz')+load(eyes/'Eyeballs.npz'))
    dp=ROOT/'dental_parts'
    parts['Torso']=largest(parts['Torso']-load(dp/'Old_teeth_removal.npz'))
    mouth={r['name']:r for r in json.loads((ROOT/'mouth_parameters.json').read_text())['parts']}
    for name in ['Lower_teeth','Upper_teeth']:
        arch=load(dp/(name+'.npz'));contact=(arch^parts['Torso']).volume()
        parts['Torso']=largest(parts['Torso']-load(dp/(name+'_socket.npz'))-load(dp/(name+'_insertion_sweep.npz')))
        parts[name]=arch;colors[name]='White'
        inserts.append(dict(name=name,host='Torso',nominal_clearance_mm=.20,engaged_volume_mm3=contact,withdrawal_path_offsets_mm=mouth[name]['withdrawal_path_offsets_mm'],assembly_order='Lower teeth first, then upper teeth'))
    # Flat-backed black side panels preserve the actual outer cloth while giving
    # each panel broad bed contact. Slicer walls/infill keep the interior light.
    pants=parts['Shorts']
    for sign,side in [(1,'L'),(-1,'R')]:
        shell=plane(plane(plane(pants,(sign,0,0),75),(0,1,0),-23),(0,-1,0),-43)
        # Cloth concavities can create isolated relief patches; leave those on
        # the red host rather than exporting loose, unregistered black chips.
        inset=largest(shell);assert inset.volume()>100
        # An exact directional shell slides outward from a matching receiver.
        # The relief around its border is the proven small glue clearance.
        tm=mesh(inset);expanded=mf.Manifold(mf.Mesh64(np.ascontiguousarray(tm.vertices+tm.vertex_normals*.18),np.ascontiguousarray(tm.faces,dtype=np.uint64)))
        assert expanded.status()==mf.Error.NoError
        kernel=mf.Manifold.cube((65,.04,.04)).translate((0 if sign>0 else -65,-.02,-.02))
        sweep=inset.minkowski_sum(kernel)
        parts['Shorts']=main(parts['Shorts']-expanded-inset-sweep)
        name='Shorts_panel_'+side;parts[name]=inset;colors[name]='Black'
        inserts.append(dict(name=name,host='Shorts',nominal_clearance_mm=.18,direction=[sign,0,0],construction='Flat-backed original-surface panel with open directional receiver; lightweight slicer infill'))
    keylog=[key(parts,j,i) for i,j in enumerate(joints)]
    manifest=[]
    for name,s in parts.items():
        # Shared curved seam triangles must not be independently simplified:
        # even tiny approximation changes can create seated interference.
        s=main(s.as_original());parts[name]=s;tm=mesh(s)
        if name in ['Torso','Shorts']:
            # Remove numerical micro-edges which otherwise collapse when STL
            # vertices round to float32. This 0.00005mm tolerance is far below
            # printer resolution; larger simplification alters shared seams.
            s=s.simplify(.00005);parts[name]=s;tm=mesh(s)
        assert tm.is_watertight and tm.is_winding_consistent and s.status()==mf.Error.NoError,name
        assert len(s.decompose())==1,(name,'disconnected components',len(s.decompose()))
        save(s,OUT/(name+'.npz'))
        settings={'sparse_infill_pattern':'gyroid','sparse_infill_density':'2%'} if name.endswith('_leg') else {}
        rec=dict(name=name,color=colors[name],settings=settings,triangles=s.num_tri(),volume_mm3=s.volume(),bounds_mm=tm.bounds.tolist(),dimensions_mm=tm.extents.tolist(),components=len(s.decompose()),manifold_status=str(s.status()),watertight=True,winding_consistent=True)
        manifest.append(rec);log('PART',name,rec['components'],np.round(tm.extents,2))
    for name,data in [('manifest',manifest),('joints',keylog),('inserts',inserts)]:
        (OUT/(name+'.json')).write_text(json.dumps(data,indent=2))
    collisions=[];names=list(parts)
    for i,a in enumerate(names):
        for b in names[i+1:]:
            vol=(parts[a]^parts[b]).volume()
            if vol>.01:collisions.append(dict(a=a,b=b,volume_mm3=vol))
    (OUT/'assembly_intersections.json').write_text(json.dumps(collisions,indent=2));log('COLLISIONS',collisions)
    assert not collisions
    log('Geometry saved; run validate_assembly_v2.py for full insertion-path verification')

if __name__=='__main__':run()
