from pathlib import Path
import json,shutil,numpy as np,trimesh,manifold3d as mf
from scipy.spatial import cKDTree
src=Path('work/venom_fullarms/final_parts');dst=Path('work/venom_lightweight/final_parts');dst.mkdir(parents=True,exist_ok=True)
rows=json.loads((src/'manifest.json').read_text());joints=json.loads((src/'joints.json').read_text());colorpts=[]
for r in rows:
 if r['color']!='Black':colorpts.append(np.load(src/(r['name']+'.npz'))['vertices'])
tree=cKDTree(np.concatenate(colorpts));report=[]
for r in rows:
 a=np.load(src/(r['name']+'.npz'));m=trimesh.Trimesh(a['vertices'],a['faces'],process=True)
 if not m.is_watertight:
  cs=m.split(only_watertight=False);primary=max(cs,key=lambda x:abs(x.volume));assert primary.is_watertight and all(abs(c.volume)<.001 for c in cs if c is not primary);m=primary
 original=np.array(m.vertices);locked=np.ones(len(original),bool)
 if r['color']=='Black':
  locked=tree.query(original,workers=-1)[0]<1.5
  # Lock sharp muscle/vein ridges, cut edges, glue interfaces, and their surroundings.
  edges=m.face_adjacency_edges[m.face_adjacency_angles>np.deg2rad(28)];locked[np.unique(edges)]=True
  for j in joints:
   if r['name'] not in [j['male'],j['female']]:continue
   n=np.array(j['normal']);n/=np.linalg.norm(n);d=original-np.array(j['center_mm']);ax=d@n;radial=np.linalg.norm(d-ax[:,None]*n,axis=1)
   locked|=(radial<j['half_width_mm']+7)&(ax>-7)&(ax<j['length_mm']+7)
  # Prevent relocation of planar contact rims and bed contact.
  for z in ([200] if r['name'].endswith('leg') else [200,270] if r['name']=='Pelvis' else [270] if r['name']=='Torso' else []):locked|=abs(original[:,2]-z)<1
  if r['name'].endswith('arm'):
   n=np.array([1 if r['name'].startswith('L') else -1,0,.15]);locked|=abs(original@n-164)<1
  locked|=original[:,2]<original[:,2].min()+.5
  smooth=m.copy();trimesh.smoothing.filter_taubin(smooth,lamb=.3,nu=.31,iterations=4)
  delta=np.array(smooth.vertices)-original;length=np.linalg.norm(delta,axis=1);delta*=np.minimum(1,.06/np.maximum(length,1e-12))[:,None];delta[locked]=0;m.vertices=original+delta
 else:delta=np.zeros_like(original)
 assert m.is_watertight and m.is_winding_consistent
 s=mf.Manifold(mf.Mesh64(np.ascontiguousarray(m.vertices,dtype=np.float64),np.ascontiguousarray(m.faces,dtype=np.uint64)));assert s.status()==mf.Error.NoError
 np.savez_compressed(dst/(r['name']+'.npz'),vertices=np.array(m.vertices),faces=np.array(m.faces,dtype=np.uint64))
 r.update(triangles=len(m.faces),volume_mm3=float(m.volume),bounds_mm=m.bounds.tolist(),dimensions_mm=m.extents.tolist())
 report.append(dict(name=r['name'],maximum_surface_movement_mm=float(np.linalg.norm(delta,axis=1).max()),protected_vertices=int(locked.sum()),closed=True))
 print(r['name'],'max surface movement',report[-1]['maximum_surface_movement_mm'],flush=True)
(dst/'manifest.json').write_text(json.dumps(rows,indent=2));(dst/'smoothing_report.json').write_text(json.dumps(report,indent=2))
for f in ['joints.json','inserts.json']:shutil.copy2(src/f,dst/f)
def load(n):
 a=np.load(dst/(n+'.npz'));return mf.Manifold(mf.Mesh64(np.ascontiguousarray(a['vertices'],dtype=np.float64),np.ascontiguousarray(a['faces'],dtype=np.uint64)))
solids={r['name']:load(r['name']) for r in rows};overlaps=[]
for i,r in enumerate(rows):
 for q in rows[i+1:]:
  vol=(solids[r['name']]^solids[q['name']]).volume()
  if vol>.001:overlaps.append([r['name'],q['name'],vol])
assert not overlaps,overlaps
(dst/'assembly_intersections.json').write_text(json.dumps({'parts':12,'overlaps_above_0.001_mm3':overlaps},indent=2))
