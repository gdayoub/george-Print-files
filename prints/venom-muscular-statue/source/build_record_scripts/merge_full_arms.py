from pathlib import Path
import json, shutil, numpy as np, trimesh, manifold3d as mf
src=Path('work/venom_muscular/final_parts'); dst=Path('work/venom_fullarms/final_parts');dst.mkdir(parents=True,exist_ok=True)
def load(p):
 a=np.load(p);return mf.Manifold(mf.Mesh64(np.ascontiguousarray(a['vertices'],dtype=np.float64),np.ascontiguousarray(a['faces'],dtype=np.uint64)))
old=json.loads((src/'manifest.json').read_text());rows=[]
for r in old:
 if any(r['name']==side+'_'+part for side in ['L','R'] for part in ['upper_arm','forearm','hand']):continue
 shutil.copy2(src/(r['name']+'.npz'),dst/(r['name']+'.npz'));rows.append(r)
for side in ['L','R']:
 raw=load(Path('work/venom/cuts')/(side+'_upper_arm.npz'))+load(Path('work/venom/cuts')/(side+'_forearm.npz'))+load(Path('work/venom/cuts')/(side+'_hand.npz'))
 # Recover the clipped fingertip from the raw pelvis, as in the original engineering.
 for c in load(Path('work/venom/cuts/Pelvis.npz')).decompose():
  if .01<c.volume()<1000 and (np.asarray(c.to_mesh64().vert_properties)[:,0].mean()>0)==(side=='L'):raw=raw+c
 # Original continuous skin below the elbow socket; final sculpt and shoulder socket above.
 lower=raw.split_by_plane([0,0,1],344)[1].as_original()
 arm=(lower+load(src/(side+'_upper_arm.npz'))).as_original()
 arm=max(arm.decompose(),key=lambda c:c.volume()).as_original()
 m=arm.to_mesh64();v=np.asarray(m.vert_properties)[:,:3];f=np.asarray(m.tri_verts);tm=trimesh.Trimesh(v,f,process=True)
 if not tm.is_watertight:
  cs=tm.split(only_watertight=False);primary=max(cs,key=lambda c:abs(c.volume))
  print('Weld components',[(len(c.faces),c.volume,c.is_watertight) for c in cs],flush=True)
  assert primary.is_watertight and all(abs(c.volume)<.001 for c in cs if c is not primary)
  tm=primary;v=np.asarray(tm.vertices);f=np.asarray(tm.faces,dtype=np.uint64)
  arm=mf.Manifold(mf.Mesh64(np.ascontiguousarray(v,dtype=np.float64),np.ascontiguousarray(f,dtype=np.uint64)))
 assert tm.is_watertight and tm.is_winding_consistent,(side,arm.status())
 np.savez_compressed(dst/(side+'_arm.npz'),vertices=v,faces=f)
 rows.append(dict(name=side+'_arm',color='Black',triangles=len(f),volume_mm3=arm.volume(),bounds_mm=tm.bounds.tolist(),dimensions_mm=tm.extents.tolist(),components=1,manifold_status=str(arm.status()),indexed_watertight=True,welded_watertight=True,winding_consistent=True))
 print(side,'continuous arm',tm.extents,arm.volume(),flush=True)
rows=sorted(rows,key=lambda r:(['Black','White','Red'].index(r['color']),r['name']))
for i,r in enumerate(rows,1):r['id']=i
(dst/'manifest.json').write_text(json.dumps(rows,indent=2))
joints=[j for j in json.loads((src/'joints.json').read_text()) if not any(p in j['male']+j['female'] for p in ['forearm','hand'])]
for j in joints:
 for key in ['male','female']:j[key]=j[key].replace('_upper_arm','_arm')
(dst/'joints.json').write_text(json.dumps(joints,indent=2))
inserts=json.loads((src/'inserts.json').read_text())
for r in inserts:r['host']=r['host'].replace('_upper_arm','_arm')
(dst/'inserts.json').write_text(json.dumps(inserts,indent=2))
solids={r['name']:load(dst/(r['name']+'.npz')) for r in rows};overlaps=[]
for i,r in enumerate(rows):
 for s in rows[i+1:]:
  vol=(solids[r['name']]^solids[s['name']]).volume()
  if vol>.001:overlaps.append([r['name'],s['name'],vol])
assert not overlaps,overlaps
(dst/'assembly_intersections.json').write_text(json.dumps({'overlaps_above_0.001_mm3':overlaps,'parts':len(rows)},indent=2))
print('Validated',len(rows),'closed parts and',len(joints),'retained joints',flush=True)
