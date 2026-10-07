from pathlib import Path
import numpy as np,manifold3d as mf,trimesh,io,json,hashlib
ROOT=Path(__file__).resolve().parent/'venom'
R=np.array([[1,0,0],[0,0,1],[0,-1,0]],float)
path=ROOT/'final_parts/Body.npz';a=np.load(path);v=a['vertices'];f=a['faces'];oldhash=hashlib.sha256(path.read_bytes()).hexdigest()
qv=v@R.T;low=qv.min(0);qv-=low
solid=mf.Manifold(mf.Mesh(qv.astype(np.float32),f.astype(np.uint32)))
assert solid.status()==mf.Error.NoError and len(solid.decompose())==1
m=solid.to_mesh64();local=m.vert_properties[:,:3];faces=m.tri_verts
data=trimesh.Trimesh(local,faces,process=False).export(file_type='stl')
reloaded=trimesh.load_mesh(io.BytesIO(data),file_type='stl',process=True)
assert reloaded.is_watertight and reloaded.is_winding_consistent
rechecked=mf.Manifold(mf.Mesh64(np.ascontiguousarray(reloaded.vertices),np.ascontiguousarray(reloaded.faces,dtype=np.uint64)))
assert rechecked.status()==mf.Error.NoError
np.savez_compressed(path,vertices=(local+low)@R,faces=faces)
report=dict(method='Canonicalized the closed mesh in its float32 print-coordinate representation using Manifold, then restored assembly coordinates. No voxel remeshing or redesigned connectors.',prior_npz_sha256=oldhash,final_npz_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),prior_triangles=len(f),final_triangles=len(faces),maximum_original_vertex_rounding_mm=float(np.abs(qv.astype(np.float32).astype(float)-qv).max()),stl_roundtrip_watertight=True,stl_roundtrip_manifold_status=str(rechecked.status()))
(ROOT/'serialization_repair.json').write_text(json.dumps(report,indent=2))
manifest=json.loads((ROOT/'final_parts/manifest.json').read_text());manifest[0].update(triangles=len(faces),volume_mm3=solid.volume())
(ROOT/'final_parts/manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(report),flush=True)
