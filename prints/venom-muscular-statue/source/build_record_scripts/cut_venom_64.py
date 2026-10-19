from pathlib import Path
import numpy as np,manifold3d as mf,json
A=np.load('work/venom/source_480.npz');S=mf.Manifold(mf.Mesh64(np.asarray(A['vertices'],dtype=np.float64),np.asarray(A['faces'],dtype=np.uint64)))
parts={};joints=[]
def split(s,n,offset):
 n=np.array(n,dtype=float);ln=np.linalg.norm(n);return s.split_by_plane(n/ln,offset/ln)
for sign,label in [(-1,'R'),(1,'L')]:
 # Clip cutter below the feet-safe shoulder region; no source triangles moved.
 box=mf.Manifold.cube((1200,1200,800)).translate((-600,-600,200));cutter=box.trim_by_plane(np.array([sign,0,.15])/np.linalg.norm([sign,0,.15]),164.0/np.linalg.norm([sign,0,.15]));arm,S=S.split(cutter)
 upper,lower=split(arm,[0,0,1],330); lower_main=max(lower.decompose(),key=lambda x:x.volume()); upper=upper+(lower-lower_main); lower=lower_main; forearm,hand=split(lower,[0,0,1],275)
 parts[f'{label}_upper_arm']=upper;parts[f'{label}_forearm']=forearm;parts[f'{label}_hand']=hand
 joints.extend([dict(a='Torso',b=f'{label}_upper_arm',normal=[sign,0,.15],offset=164.0),dict(a=f'{label}_forearm',b=f'{label}_upper_arm',normal=[0,0,1],offset=330),dict(a=f'{label}_hand',b=f'{label}_forearm',normal=[0,0,1],offset=275)])
upper,lower=split(S,[0,0,1],270);pelvis,legs=split(lower,[0,0,1],200);L,R=split(legs,[1,0,0],0);parts.update(Torso=upper,Pelvis=pelvis,L_leg=L,R_leg=R);joints.append(dict(a='Pelvis',b='Torso',normal=[0,0,1],offset=270));joints.extend([dict(a=k,b='Pelvis',normal=[0,0,1],offset=200) for k in ['L_leg','R_leg']])
root=Path('work/venom/cuts');root.mkdir(exist_ok=True)
for name,s in parts.items():
 m=s.to_mesh64();v=np.array(m.vert_properties[:,:3]);f=np.array(m.tri_verts);np.savez_compressed(root/(name+'.npz'),vertices=v,faces=f);print(name,'components',[(round(c.volume(),2),np.round(c.bounding_box(),1).tolist()) for c in s.decompose()],'size',np.ptp(v,axis=0).round(1).tolist(),flush=True)
(root/'joints.json').write_text(json.dumps(joints,indent=2))


