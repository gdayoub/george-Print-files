from pathlib import Path
import sys,json,hashlib
R=Path(__file__).parent;sys.path.insert(0,str(R/'.deps'))
import numpy as np,trimesh
from manifold3d import Manifold as M,Mesh as MM
O=R/'outputs'/'snap_print_kit';P=json.loads((R/'snap_parameters.json').read_text());report=json.loads((O/'geometry_checks.json').read_text())
def load(n):
 m=trimesh.load_mesh(O/'ASSEMBLY'/(n+'.stl'));return M(MM(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
def box(lo,hi):return M.cube(tuple(np.array(hi)-lo)).translate(lo)
solids={n:load(n) for n in report['parts']}
compressed=dict(solids)
for i in report['interfaces']:
 cfg=P[i['clip']+'_clip'];w=cfg['width'];t=cfg['thickness'];L=cfg['length'];limit=w/2+cfg['clearance_per_side']-.01
 cutters=box((limit,-t,-L-.1),(w+2,t,-L+2.01))+box((-w-2,-t,-L-.1),(-limit,t,-L+2.01))
 compressed[i['part']]=compressed[i['part']]-cutters.transform(np.asarray(i['frame']))
results={}
for name in [n for n in solids if n not in ['RED_body','RED_head','BLACK_feet_base']]:
 entries=[i for i in report['interfaces'] if i['part']==name];direction=np.asarray(entries[0]['frame'])[:,2]
 assert all(np.max(np.abs(np.asarray(i['frame'])[:,2]-direction))<1e-8 for i in entries)
 host=solids['RED_head'] if name.startswith('BLACK') else solids['RED_body']
 hits=[]
 for distance in np.arange(0,13.01,.5):
  vol=(compressed[name].translate(direction*distance)^host).volume()
  if vol>1e-4:hits.append({'offset_mm':float(distance),'overlap_mm3':float(vol)})
 results[name]=hits
head_group=solids['RED_head']
for name,s in solids.items():
 if name.startswith('BLACK') and name!='BLACK_feet_base':head_group=head_group+s
for label,moving,stationary,direction in [('head_opening',head_group,compressed['RED_body']+solids['PINK_tongue'],np.array([0,0,1.])),('base_opening',compressed['BLACK_feet_base'],solids['RED_body'],np.array([0,0,-1.]))]:
 hits=[]
 for distance in np.arange(0,16.01,.5):
  vol=(moving.translate(direction*distance)^stationary).volume()
  if vol>1e-4:hits.append({'offset_mm':float(distance),'overlap_mm3':float(vol)})
 results[label]=hits
report['insertion_clearance_check']={'method':'0.5 mm samples along straight insertion/removal direction. Barbs geometrically clipped to a compressed envelope; NOT a force, elasticity or fatigue simulation.','collisions':results,'passed':not any(results.values())}
src=Path(P['source_stl']);src=src if src.is_absolute() else R/src;copy=O/'REFERENCE'/'ORIGINAL_sleeve_UNCHANGED.stl'
report['source_sha256']=hashlib.sha256(src.read_bytes()).hexdigest();report['source_copy_identical']=src.read_bytes()==copy.read_bytes()
assert report['source_copy_identical'] and report['all_new_parts_watertight'] and report['all_new_parts_single_solid']
assert all(abs(v)<1e-4 for v in report['seated_collisions'].values())
(O/'geometry_checks.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report['insertion_clearance_check'],indent=2),flush=True)
