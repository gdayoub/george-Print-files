"""GengarPuffco Girth V5. One continuous source-bowl character split across the middle.
All coordinates millimetres. Front -Y, up Z. Run with numpy/trimesh/manifold3d.
The upper Gengar half turns with the original lid over the stationary lower half.
"""
from pathlib import Path
import json, math, hashlib
import numpy as np
import trimesh
from scipy.interpolate import PchipInterpolator
from manifold3d import Manifold as M, Mesh64, CrossSection as CS, OpType

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'CAD'/'outputs'; OUT.mkdir(exist_ok=True)
REF=ROOT/'Foundations'
N=144
def cyl(r,lo,hi): return M.cylinder(hi-lo,r,circular_segments=N).translate((0,0,lo))
def box(lo,hi): return M.cube(tuple(np.array(hi)-lo)).translate(lo)
def sphere(c,s): return M.sphere(1,96).scale(s).translate(c)
def union(parts): return M.batch_boolean(parts,OpType.Add)
def mesh(m):
 a=m.to_mesh64();return trimesh.Trimesh(np.asarray(a.vert_properties)[:,:3],np.asarray(a.tri_verts),process=False)
def solid(m):
 t=trimesh.Trimesh(m.vertices,m.faces,process=True)
 r=M(Mesh64(np.asarray(t.vertices),np.asarray(t.faces,dtype=np.uint64)))
 assert str(r.status())=='Error.NoError',str(r.status())
 return union([c for c in r.decompose() if c.volume()>1e-6])
def cleaned(m):return union([c for c in m.decompose() if c.volume()>.0001])
def load_exact(name):
 d=np.load(REF/(name+'_exact.npz'));return trimesh.Trimesh(d['vertices'],d['faces'],process=False)

base=load_exact('base'); lid=load_exact('lid')
base_shift=14.-base.bounds[0,2]
base_T=trimesh.transformations.translation_matrix([0,0,base_shift]);base.apply_transform(base_T)
seat=base_shift+18.75
lid_T=trimesh.transformations.rotation_matrix(math.radians(20),[0,0,1])@trimesh.transformations.rotation_matrix(math.pi,[1,0,0])
lid_T[2,3]=seat+lid.bounds[1,2];lid.apply_transform(lid_T)
BS=solid(base); LS=solid(lid)
# Exact void guards: within each source convex envelope, new material can only
# occupy pre-existing solid. This is stronger than a nominal bore-radius check.
base_hull=solid(base.convex_hull);lid_hull=solid(lid.convex_hull)
base_void=base_hull-BS;lid_void=lid_hull-LS
print('Loading and simplifying bowl EXTERIOR only',flush=True)
d=np.load(REF/'gengar_source.npz');gv=d['vertices'].copy();gf=d['faces']
# Reshape the entire source character around the original case, not just its head.
XY=.90
source_z=np.array([-45.9650002,-35.,-30.,12.,32.,45.9650002])
case_z=np.array([0.,22.,45.,83.,111.,118.])
zmap=PchipInterpolator(source_z,case_z)
def xmap(x,z=0.):
 x=np.asarray(x)*XY
 fullness=5+6*np.sin(np.pi*zmap(np.asarray(z))/118.)
 return x+fullness*np.sin(np.pi*x/(72.8470001*XY))
gv[:,0]=xmap(gv[:,0],gv[:,2]);gv[:,1]*=XY;gv[:,2]=zmap(gv[:,2])
gengar=solid(trimesh.Trimesh(gv,gf,process=False)).simplify(.012)
np.savez_compressed(OUT/'bowl_transformed.npz',vertices=gv,faces=gf)
print('Closing bowl crown and splitting continuous character',flush=True)
# Close the bowl opening below its ears. The source forehead and crown spikes
# remain visible above this shallow curved roof.
crown=sphere((0,0,108),(51.,46.,9.))
whole=gengar+cyl(31.2,0,110)+crown
head_bottom=59.3;body_top=58.7
head_whole=whole^box((-100,-100,head_bottom),(100,100,140))
head_whole=head_whole-cyl(29.55,head_bottom-.1,seat+8.)
head_whole=head_whole-cyl(28.42,seat+7.99,lid.bounds[1,2]-.25)
head_whole=cleaned(head_whole)-lid_void
carrier=whole^box((-100,-100,0),(100,100,body_top))
carrier=carrier-cyl(28.42,14,body_top+.1)-base_void

# Coarse independent bottom thread; fully separate from the foundation thread.
pitch=2.5; root=17.5; depth=.9;radial=.3;axial=.18;phase=7.0
def helix(z0,z1,female=False):
 a0=360*(z0-phase)/pitch;a1=360*(z1-phase)/pitch
 angles=np.linspace(a0,a1,int((a1-a0)/3)+1);v=[];f=[]
 for a in angles:
  z=phase+a*pitch/360;t=1 if female else min(1,max(.02,(a-a0)/100),max(.02,(a1-a)/100))
  ac=axial if female else 0;rc=radial if female else 0
  for r,h in [(root-.3,z-.8-ac),(root+depth*t+rc,z-.27-ac),(root+depth*t+rc,z+.27+ac),(root-.3,z+.8+ac)]:v.append((r*math.cos(math.radians(a)),r*math.sin(math.radians(a)),h))
 for i in range(len(angles)-1):
  for j in range(4):
   a=i*4+j;b=i*4+(j+1)%4;c=(i+1)*4+(j+1)%4;d=(i+1)*4+j;f.extend([(a,b,c),(a,c,d)])
 f.extend([(0,2,1),(0,3,2)]);e=(len(angles)-1)*4;f.extend([(e,e+1,e+2),(e,e+2,e+3)])
 t=trimesh.Trimesh(v,f,process=True);t.fix_normals();return solid(t)
# Small underside cup, tucked inside the original bowl's base silhouette.
cap=cyl(18.5,0,2)+(cyl(18.5,1.8,6)-cyl(16,2,6.1))+(cyl(root,5.8,12)-cyl(16,5.7,12.1))+helix(7,10.7)
for a in np.arange(0,360,30):
 cap=cap-cyl(1.2,.5,4.5).translate((19.*math.cos(math.radians(a)),19.*math.sin(math.radians(a)),0))
carrier=carrier-cyl(18.85,-.1,6.35)-cyl(root+radial,6.34,12.35)-helix(5.5,14,True)
carrier=cleaned(carrier)-base_void

# Face colors follow the actual source face and retain the original relief.
# Coordinates below are in the source bowl's X/Z plane, then transformed.
def face_prism(points):
 pts=[(float(xmap(x,z)),float(zmap(z))) for x,z in points]
 area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(pts,pts[1:]+pts[:1]))
 if area<0:pts=pts[::-1]
 return M.extrude(CS([pts]),36).transform([[1,0,0,0],[0,0,1,-67],[0,1,0,0]])
eyes=[]
for s in [-1,1]:
 eyes.append(face_prism([(s*26,10),(s*27,2),(s*25,-5),(s*19,-9),(s*13,-8),(s*7,-4)]))
eye_mask=union(eyes)
# Preserve dark pupils in the source relief, rather than invent tiny loose parts.
for s in [-1,1]:
 z=float(zmap(-.5))
 eye_mask=eye_mask-sphere((float(xmap(s*16,-.5)),-54,z),(1.9,10,3.2))
grin_mask=face_prism([(-29,-8),(-22,-12),(-10,-15),(0,-16),(10,-15),(22,-12),(29,-8),(25,-20),(17,-26),(0,-29),(-17,-26),(-25,-20)])
# Keep black tooth divisions as broad grooves, matching the bowl's grin rhythm.
for x in [-22,-11,0,11,22]:grin_mask=grin_mask-box((float(xmap(x,-20))-.5,-68,20),(float(xmap(x,-20))+.5,-31,78))
parts={}
for prefix,shape in [('head',head_whole),('body',carrier)]:
 parts[prefix+'_black']=cleaned(shape-eye_mask-grin_mask)
 for name,mask in [('eyes_red',eye_mask),('grin_pink',grin_mask)]:
  region=cleaned(shape^mask)
  if region.volume()>.001:parts[prefix+'_'+name]=region
parts['bottom_cap_red']=cleaned(cap)
meshes={n:mesh(s) for n,s in parts.items()}
meshes['ORIGINAL_CASE_BASE_EXACT']=base;meshes['ORIGINAL_CASE_LID_EXACT']=lid
groups={n:('body' if n.startswith('body_') or n=='ORIGINAL_CASE_BASE_EXACT' else 'bottom' if n=='bottom_cap_red' else 'head') for n in meshes}
manifest=[]
for n,m in meshes.items():
 np.savez_compressed(OUT/(n+'.npz'),vertices=m.vertices,faces=m.faces)
 m.export(OUT/(n+'.ply'))
 manifest.append({'name':n,'group':groups[n],'file':n+'.npz','color':'#CE1834' if 'red' in n else '#F481B3' if 'pink' in n else '#1C1B26'})
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
body_complete=BS+carrier;head_complete=LS+head_whole
checks={
 'foundation_sha256':hashlib.sha256((REF/'Core_Case.3mf').read_bytes()).hexdigest(),
 'foundation_scale':[1,1,1], 'base_transform':base_T.tolist(),'lid_transform':lid_T.tolist(),
 'foundation_base_triangles':len(base.faces),'foundation_lid_triangles':len(lid.faces),
 'new_material_in_original_base_void_mm3':(carrier^base_void).volume(),
 'new_material_in_original_lid_void_mm3':(head_whole^lid_void).volume(),
 'head_addition_in_original_base_envelope_mm3':(head_whole^base_hull).volume(),
 'head_bond_mm3':(head_whole^LS).volume(),'body_bond_mm3':(carrier^BS).volume(),
 'revision':'Girth V5: broad Gengar silhouette, unchanged height and original internal fit',
 'shell_base_radial_air_gap_mm':.85,'head_seam_min_axial_gap_mm':.6,
 'storage_clear_diameter_mm':32,'storage_clear_height_mm':10,
 'bottom_thread_pitch_mm':pitch,'bottom_thread_radial_clearance_mm':radial,
 'assembled_size_mm':trimesh.util.concatenate(list(meshes.values())).extents.tolist(),
 'new_meshes':{n:{'watertight':bool(m.is_watertight),'winding':bool(m.is_winding_consistent),'positive_volume':bool(m.volume>0),'triangles':len(m.faces)} for n,m in meshes.items() if not n.startswith('ORIGINAL')},
 'combined_components':{n:len([x for x in s.decompose() if x.volume()>.001]) for n,s in [('head',head_complete),('body',body_complete),('bottom',cap)]},
 'physical_fit_verified':False,'physical_seating_angle_verified':False,
 'validation_scope':'Digital sampled motion and source-geometry checks only; no physical fit claim.',
 'head_collisions':[],'bottom_collisions':[]}
fixed_lower=body_complete+cap
fixed_upper=body_complete+head_complete
print('Checking motion (5-degree samples, four turns)',flush=True)
for a in range(0,1441,5):
 h=head_complete.rotate((0,0,a)).translate((0,0,a*2.5/360))
 v=(h^fixed_lower).volume()
 if v>.001:checks['head_collisions'].append([a,v])
 b=cap.rotate((0,0,-a)).translate((0,0,-a*pitch/360))
 v=(b^fixed_upper).volume()
 if v>.001:checks['bottom_collisions'].append([a,v])
 if a%180==0:print('Motion',a,flush=True)
checks['head_straight_lift_overlap_mm3']=max((head_complete.translate((0,0,float(z)))^fixed_lower).volume() for z in range(10,141,5))
storage_probe=cyl(15.5,2.2,11.8)
checks['storage_exit_overlap_mm3']=max((storage_probe.translate((0,0,float(z)))^fixed_upper).volume() for z in range(-50,1,2))
(ROOT/'Reports'/'geometry_validation.json').write_text(json.dumps(checks,indent=2))
print(json.dumps({k:v for k,v in checks.items() if k not in ['base_transform','lid_transform','new_meshes']},indent=2),flush=True)
assert all(x['watertight'] and x['winding'] and x['positive_volume'] for x in checks['new_meshes'].values())
assert checks['head_bond_mm3']>10 and checks['body_bond_mm3']>10
assert all(v==1 for v in checks['combined_components'].values())
assert checks['assembled_size_mm'][0]<=133 and checks['assembled_size_mm'][1]<=112 and checks['assembled_size_mm'][2]<=119
assert not checks['head_collisions'] and not checks['bottom_collisions']
assert all(abs(checks[k])<.001 for k in ['new_material_in_original_base_void_mm3','new_material_in_original_lid_void_mm3','head_addition_in_original_base_envelope_mm3','head_straight_lift_overlap_mm3','storage_exit_overlap_mm3'])
print('GEOMETRY CHECKS PASSED',flush=True)
