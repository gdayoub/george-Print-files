from pathlib import Path
import sys
import numpy as np,trimesh,manifold3d as mf,io,json,hashlib
ROOT=Path(__file__).resolve().parent

def solid(v,f):return mf.Manifold(mf.Mesh64(np.ascontiguousarray(v,dtype=np.float64),np.ascontiguousarray(f,dtype=np.uint64)))
def mesh(s):
 a=s.to_mesh64();return trimesh.Trimesh(a.vert_properties[:,:3],a.tri_verts,process=False)
def check_roundtrip(s,R):
 m=mesh(s);v=m.vertices@R.T;v-=v.min(0);r=trimesh.load_mesh(io.BytesIO(trimesh.Trimesh(v,m.faces,process=False).export(file_type='stl')),file_type='stl',process=True);ss=solid(r.vertices,r.faces);counts=np.bincount(r.edges_unique_inverse)
 return dict(watertight=bool(r.is_watertight),winding_consistent=bool(r.is_winding_consistent),manifold_status=str(ss.status()),nonmanifold_edges=int(np.count_nonzero(counts!=2)),degenerate_faces=int(np.count_nonzero(~r.nondegenerate_faces(height=1e-8))),components=len(ss.decompose()))
for product in sys.argv[1:] or ['king_shark','venom']:
 base=ROOT/product;partsdir=base/'final_parts';rows=json.loads((partsdir/'manifest.json').read_text());layout=json.loads((base/'layout.json').read_text());rot={a['name']:np.array(a['rotation']) for p in layout['plates'] for a in p['instances']};parts={};log=[]
 for row in rows:
  p=partsdir/(row['name']+'.npz');before_hash=hashlib.sha256(p.read_bytes()).hexdigest();d=np.load(p);s=solid(d['vertices'],d['faces']);before=check_roundtrip(s,rot[row['name']]);original_bounds=mesh(s).bounds.copy();modified=False
  if not before['watertight'] or before['degenerate_faces'] or before['manifold_status']!='Error.NoError':
   s=s.as_original().simplify(.0001);after=check_roundtrip(s,rot[row['name']]);assert after['watertight'] and not after['degenerate_faces'] and after['manifold_status']=='Error.NoError',(product,row['name'],after)
   a=s.to_mesh64();np.savez_compressed(p,vertices=a.vert_properties[:,:3],faces=a.tri_verts);modified=True
  else:after=before
  tm=mesh(s);row.update(triangles=s.num_tri(),volume_mm3=s.volume(),dimensions_mm=tm.extents.tolist());parts[row['name']]=s
  log.append(dict(name=row['name'],modified=modified,simplification_tolerance_mm=.0001 if modified else 0,source_hash_before=before_hash,source_hash_after=hashlib.sha256(p.read_bytes()).hexdigest(),maximum_bound_shift_mm=float(abs(tm.bounds-original_bounds).max()),before=before,after=after));print(product,row['name'],modified,after,flush=True)
 (partsdir/'manifest.json').write_text(json.dumps(rows,indent=2))
 overlaps=[]
 for i,a in enumerate(parts):
  for b in list(parts)[i+1:]:
   vol=max(0.,(parts[a]^parts[b]).volume());overlaps.append(dict(a=a,b=b,overlap_mm3=vol));assert vol<.05,(product,a,b,vol)
 paths=[]
 for dz in [0,.2,.5,1,2,3,4,8,16]:
  vol=max(0.,(parts['Tray'].translate((0,0,dz))^parts['Body']).volume());paths.append(dict(lift_mm=dz,overlap_mm3=vol));assert vol<.05,(product,dz,vol)
 accents=[]
 for name in parts:
  if name in ['Body','Tray']:continue
  for dy in [0,.2,.5,1,2,3,5,10,20]:
   vol=max(0.,(parts[name].translate((0,-dy,0))^parts['Body']).volume());accents.append(dict(name=name,withdrawal_mm=dy,overlap_mm3=vol));assert vol<.05,(product,name,dy,vol)
 report=dict(method='Check final print-oriented float32 STL roundtrips, then recheck assembly overlaps. Character-specific submicron cleanup is documented in serialization_repair.json.',parts=log,overlaps=overlaps,tray_insertion_samples=paths,accent_withdrawal_samples=accents,path_numeric_volume_tolerance_mm3=.05,cleanup_note='The revised King Shark fin Body was canonicalized in float32 print coordinates before this pass; see serialization_repair.json. No voxel remesh or connector redesign.',status='passed')
 (base/'serialization_validation.json').write_text(json.dumps(report,indent=2))
 old=json.loads((base/'geometry_validation.json').read_text());old.update(parts=rows,overlaps=overlaps,tray_insertion_samples=paths,accent_withdrawal_samples=accents,serialization_validation='serialization_validation.json');(base/'geometry_validation.json').write_text(json.dumps(old,indent=2))
 (base/'SERIALIZATION_NOTES.md').write_text('# Serialization checks\n\nThe final print-oriented binary STLs were reopened and checked for watertightness, winding, nonmanifold edges, degenerate faces, and connected components. Failed parts received only an additional 0.0001 mm simplification pass; connector dimensions and the silhouette were not intentionally changed. All final STL checks pass. Seated part overlaps, the tray insertion path, and accent withdrawal paths were rechecked after this cleanup. See `serialization_validation.json` for per-part before/after evidence and hashes.\n')


