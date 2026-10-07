"""Check new shelf assembly travel without changing any geometry."""
from pathlib import Path
import json,sys,numpy as np,manifold3d as mf
ROOT=Path(__file__).resolve().parent
for product in sys.argv[1:] or ['king_shark','venom']:
 src=ROOT/product;parts={}
 for p in (src/'final_parts').glob('*.npz'):
  a=np.load(p);s=mf.Manifold(mf.Mesh64(np.ascontiguousarray(a['vertices'],dtype=np.float64),np.ascontiguousarray(a['faces'],dtype=np.uint64)))
  assert s.status()==mf.Error.NoError and len(s.decompose())==1
  parts[p.stem]=s
 checks=[]
 for name in parts:
  if name=='Body':continue
  direction=(0,0,1) if name=='Tray' else (0,-1,0)
  for travel in ([0,.05,.2,.5,1,2,3,4,8,16] if name=='Tray' else [0,.05,.2,.5,1,2,3,4,8,16,40,80]):
   moved=parts[name].translate(tuple(travel*q for q in direction))
   for other in parts:
    if name==other:continue
    volume=max(0.,(moved^parts[other]).volume())
    checks.append(dict(part=name,other=other,travel_mm=travel,direction=direction,overlap_mm3=volume))
    assert volume<.05,(product,checks[-1])
  if name=='Tray':
   for travel in [0,.2,.5,1,2,3,4,8,16,40,80]:
    volume=max(0.,(parts[name].translate((0,-travel,16))^parts['Body']).volume())
    checks.append(dict(part=name,other='Body',travel_mm=travel,lift_mm=16,direction=(0,-1,0),overlap_mm3=volume))
    assert volume<.05,(product,checks[-1])
 report=dict(assembly_paths_pass=True,numerical_overlap_tolerance_mm3=.05,max_overlap_mm3=max(c['overlap_mm3'] for c in checks),notes='Tray path: lift 16mm, then slide forward away from the wall. Reverse to install. Lifting straight through the sculpt is not an assembly path. Submicron serialization cleanup can produce tiny numerical intersections along nominal contact planes. This checks rigid CAD travel, not a physical assembly.',samples=checks)
 (src/'validation').mkdir(exist_ok=True)
 (src/'validation/assembly_insertion.json').write_text(json.dumps(report,indent=2))
 print(product,report['max_overlap_mm3'],len(checks))
