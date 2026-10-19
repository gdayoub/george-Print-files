from pathlib import Path
import numpy as np,manifold3d as mf,trimesh,json,shutil
old=Path('work/venom/final_parts');out=Path('work/venom_muscular/final_parts');out.mkdir(exist_ok=True)
def load(p):
 a=np.load(p);return mf.Manifold(mf.Mesh64(np.asarray(a['vertices'],dtype=np.float64),np.asarray(a['faces'],dtype=np.uint64)))
mask=load(out.parent/'muscle_envelope.npz');assert mask.status()==mf.Error.NoError
records=json.loads((old/'manifest.json').read_text());joints=json.loads((old/'joints.json').read_text());changes=[]
for r in records:
 if r['color']!='Black' and r['name']!='Chest_R_upper_arm_01':
  lo=np.array(r['bounds_mm'][0])-1.5;hi=np.array(r['bounds_mm'][1])+1.5;mask=mask+mf.Manifold.cube(hi-lo).translate(lo)
mask=mask.as_original()
for r in records:
 name=r['name'];s=load(old/(name+'.npz'));cut=s-mask
 if cut.volume()<.001:
  shutil.copy2(old/(name+'.npz'),out/(name+'.npz'));changes.append(dict(name=name,removed_volume_mm3=0,unchanged=True));continue
 edited=s^mask
 # Preserve the established mechanical mating geometry around every connector.
 restored=0
 for j in joints:
  if name not in [j['male'],j['female']]:continue
  center=np.array(j['center_mm'])+np.array(j['normal'])*j['length_mm']*.4
  zone=mf.Manifold.sphere(max(22,j['half_width_mm']+8),48).translate(center)
  keep=s^zone;extra=(keep-edited).volume();restored+=extra
  if extra>.001:edited=edited+keep
 cs=edited.decompose();edited=max(cs,key=lambda x:x.volume()).as_original().simplify(.01)
 m=edited.to_mesh64();v=np.asarray(m.vert_properties[:,:3]);f=np.asarray(m.tri_verts);tm=trimesh.Trimesh(v,f,process=True)
 
 if not tm.is_watertight:
  cs=tm.split(only_watertight=False);primary=max(cs,key=lambda c:abs(c.volume))
  assert primary.is_watertight and all(abs(c.volume)<.001 for c in cs if c is not primary),name
  tm=primary;v=np.asarray(tm.vertices,dtype=np.float64);f=np.asarray(tm.faces,dtype=np.uint64);edited=mf.Manifold(mf.Mesh64(v,f))
 assert edited.status()==mf.Error.NoError and tm.is_watertight,name
 np.savez_compressed(out/(name+'.npz'),vertices=v,faces=f)
 r.update(triangles=len(f),volume_mm3=edited.volume(),bounds_mm=[v.min(0).tolist(),v.max(0).tolist()],dimensions_mm=np.ptp(v,axis=0).tolist(),components=1,indexed_watertight=True,welded_watertight=True,winding_consistent=bool(tm.is_winding_consistent))
 changes.append(dict(name=name,removed_volume_mm3=s.volume()-edited.volume(),joint_protection_restored_mm3=restored,unchanged=False));print(changes[-1],flush=True)
(out/'manifest.json').write_text(json.dumps(records,indent=2));(out/'revision_changes.json').write_text(json.dumps(changes,indent=2))
for n in ['joints.json','inserts.json']:shutil.copy2(old/n,out/n)
solids={r['name']:load(out/(r['name']+'.npz')) for r in records};checks=[]
for i,a in enumerate(solids):
 for b in list(solids)[i+1:]:
  ab=solids[a].bounding_box();bb=solids[b].bounding_box()
  if any(ab[k]>=bb[k+3] or bb[k]>=ab[k+3] for k in range(3)):continue
  v=abs((solids[a]^solids[b]).volume());assert v<.01,(a,b,v);checks.append(dict(a=a,b=b,intersection_mm3=v))
(out/'assembly_intersections.json').write_text(json.dumps(checks,indent=2));bounds=np.array([r['bounds_mm'] for r in records]);print('DONE',len(records),'max overlap',max(r['intersection_mm3'] for r in checks),'height',bounds[:,1,2].max(),flush=True)





