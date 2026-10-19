from pathlib import Path
import numpy as np,trimesh,manifold3d as mf,json,time
from shapely.geometry import Polygon,Point
from shapely.ops import polylabel,unary_union
root=Path('work/venom');out=root/'final_parts';out.mkdir(exist_ok=True)
def load(p):
 a=np.load(p);return mf.Manifold(mf.Mesh64(np.asarray(a['vertices'],dtype=np.float64),np.asarray(a['faces'],dtype=np.uint64)))
def save(s,p):
 me=s.to_mesh64();np.savez_compressed(p,vertices=np.array(me.vert_properties[:,:3]),faces=np.array(me.tri_verts))
def mesh(s):
 a=s.to_mesh64();return trimesh.Trimesh(np.array(a.vert_properties[:,:3]),np.array(a.tri_verts),process=False)
def clean(s,threshold=1.0):
 cs=[c for c in s.decompose() if c.volume()>threshold]
 return mf.Manifold.batch_boolean(cs,mf.OpType.Add).as_original()
S=load(root/'source_480.npz');parts={p.stem:load(p) for p in (root/'cuts').glob('*.npz')}
# Return fingers clipped by the shoulder half-space to their corresponding hands.
for name in ['Torso','Pelvis']:
 cs=parts[name].decompose();parts[name]=max(cs,key=lambda c:c.volume())
 for c in cs:
  if c.volume()<.01 or c.volume()>1000:continue
  x=(c.bounding_box()[0]+c.bounding_box()[3])/2;target='L_hand' if x>0 else 'R_hand';parts[target]=parts[target]+c
print('CLEAN BODY',[(n,round(s.volume(),1),len(s.decompose())) for n,s in parts.items()],flush=True)
# Tongue cut follows the tilted lower gum line, rather than cutting through the teeth.
box=mf.Manifold.cube((1200,522,800)).translate((-600,-600,0));n=np.array([-.5,0,-1.]);cutter=box.trim_by_plane(n/np.linalg.norm(n),-393/np.linalg.norm(n));tongue,torso=parts['Torso'].split(cutter);parts['Torso']=clean(torso);parts['Tongue']=clean(tongue)
print('TONGUE',parts['Tongue'].volume(),parts['Tongue'].bounding_box(),flush=True)
materials={n:('Red' if n=='Tongue' else 'Black') for n in parts};original_parts=parts.copy();insertlog=[]
for path in sorted((root/'color_clean').glob('*.npz')):
 W=clean(load(path).simplify(.035),3)
 print('COLOR',path.stem,W.num_tri(),len(W.decompose()),flush=True)
 for name,raw in original_parts.items():
  if name=='Tongue':continue
  b=raw.bounding_box();w=W.bounding_box()
  if any(b[i]>w[i+3] or w[i]>b[i+3] for i in range(3)):continue
  fit=clean(W ^ raw,2)
  if fit.is_empty():continue
  for j,c in enumerate(sorted(fit.decompose(),key=lambda x:-x.volume())):
   if c.volume()<80:continue
   partname=f'{path.stem}_{name}_{j+1:02}'
   # Offset the closed insert by its outward normals to give its socket a nominal 0.20mm glue allowance.
   tm=mesh(c);expanded=mf.Manifold(mf.Mesh64(np.asarray(tm.vertices+tm.vertex_normals*.20,dtype=np.float64),np.asarray(tm.faces,dtype=np.uint64)))
   if expanded.status()!=mf.Error.NoError:raise RuntimeError('Bad insert cutter '+partname)
   parts[name]=clean(parts[name]-expanded)
   parts[partname]=c;materials[partname]='White';insertlog.append(dict(name=partname,host=name,volume_mm3=c.volume(),clearance_mm=.2,triangles=c.num_tri()))
   print('INSERT',partname,round(c.volume(),1),flush=True)
# Keyed, tapered male tabs. The opposite part receives a larger blind socket.
joints=json.loads((root/'cuts/joints.json').read_text());joints.append(dict(a='Torso',b='Tongue',normal=[-.5,0,-1],offset=-393,small=True))
keylog=[]
def frame(n,off):
 n=np.array(n,dtype=float);ln=np.linalg.norm(n);n/=ln;o=n*(off/ln);u=np.array([1.,0,0]) if abs(n[2])>.8 else np.array([0.,1,0]);u-=n*(u@n);u/=np.linalg.norm(u);v=np.cross(n,u);R=np.stack([u,v,n],axis=1);T=np.c_[R.T,-R.T@o];return n,o,R,T
for i,j in enumerate(joints):
 a,b=j['a'],j['b'];n,o,R,T=frame(j['normal'],j['offset']);aa=parts[a].transform(T);bb=parts[b].transform(T);cross=aa.slice(-.35)^bb.slice(.35)
 polys=cross.to_polygons();valid=[Polygon(p) for p in polys if len(p)>=3];valid=[p.buffer(0) for p in valid if p.area>1];poly=max(valid,key=lambda p:p.area);pt=polylabel(poly,tolerance=.05);cx,cy=pt.x,pt.y;radius=pt.distance(poly.boundary)
 small=j.get('small',False);maxR=3.5 if small else (20 if a=='Pelvis' else 13);r=min(maxR,radius*.50);length=4.0 if small else (16 if a=='Pelvis' or 'leg' in a else 12)
 success=False
 for attempt in range(12):
  theta=np.linspace(0,2*np.pi,64,endpoint=False);profile=np.c_[r*(1+.09*np.cos(3*theta))*np.cos(theta),.76*r*(1+.06*np.sin(2*theta))*np.sin(theta)];cs=mf.CrossSection([profile]);rootkey=mf.Manifold.extrude(cs,2.5).translate((cx,cy,-2.5));peg=mf.Manifold.extrude(cs,length,scale_top=(.84,.84)).translate((cx,cy,0));sock=mf.Manifold.extrude(cs.offset(.18),length+.5,scale_top=(.87,.87)).translate((cx,cy,-.12));inside_sock=sock.trim_by_plane((0,0,1),.35)
  exposed=(inside_sock-bb).volume();root_out=(rootkey-aa).volume()
  if exposed<.02 and root_out<.02:success=True;break
  r*=.88
  if attempt>5:length*=.9
 if not success or r<1.0:raise RuntimeError(f'Cannot place safe key {a} {b} r={r} exposed={exposed} rootout={root_out}')
 world=np.c_[R,o];parts[a]=clean(parts[a]+(rootkey+peg).transform(world));parts[b]=clean(parts[b]-sock.transform(world))
 intrusion=(peg.transform(world)^parts[b]).volume()
 keylog.append(dict(id=f'J{i+1:02}',male=a,female=b,center_mm=(o+R@np.array([cx,cy,0])).tolist(),normal=n.tolist(),half_width_mm=r,half_depth_mm=.76*r,length_mm=length,root_depth_mm=2.5,minimum_nominal_radial_clearance_mm=.18,blind_depth_extra_mm=.38,key_shape='64-sided asymmetric rounded taper, tip scale 0.84',key_vs_socket_interference_mm3=intrusion,remaining_host_validation_mm3=exposed))
 print('KEY',a,b,'r',round(r,2),'length',round(length,2),'intrusion',intrusion,flush=True)
(out/'joints.json').write_text(json.dumps(keylog,indent=2)); (out/'inserts.json').write_text(json.dumps(insertlog,indent=2)); manifest=[]
for i,(name,s) in enumerate(parts.items()):
 s=clean(s.as_original().simplify(.01));parts[name]=s;tm=mesh(s);mrg=trimesh.Trimesh(tm.vertices,tm.faces,process=True);vol=s.volume();rec=dict(id=i+1,name=name,color=materials[name],triangles=s.num_tri(),volume_mm3=vol,bounds_mm=np.array([tm.vertices.min(0),tm.vertices.max(0)]).tolist(),dimensions_mm=tm.extents.tolist(),components=len(s.decompose()),manifold_status=str(s.status()),indexed_watertight=bool(tm.is_watertight),welded_watertight=bool(mrg.is_watertight),winding_consistent=bool(tm.is_winding_consistent));manifest.append(rec);save(s,out/(name+'.npz'));print('FINAL',name,rec['components'],rec['indexed_watertight'],rec['welded_watertight'],np.round(tm.extents,1).tolist(),flush=True)
(out/'manifest.json').write_text(json.dumps(manifest,indent=2));(out/'joints.json').write_text(json.dumps(keylog,indent=2));(out/'inserts.json').write_text(json.dumps(insertlog,indent=2));print('DONE',len(parts),flush=True)

