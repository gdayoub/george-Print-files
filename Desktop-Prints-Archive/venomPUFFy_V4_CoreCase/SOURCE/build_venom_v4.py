"""Editable parametric mesh CAD for the muscular Symbiote Core.
Run using Python 3.13 with numpy, trimesh, scipy and manifold3d.
V4 uses the complete supplied Core_Case.3mf base and lid, retained exactly.
Original 3MF remains byte-identical. Original meshes remain separate exact components.
Front is -Y; Z is up; units are mm. Parts export in shared assembly coordinates.
"""
from pathlib import Path
import sys,json,math,hashlib,shutil,zipfile,struct
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
for parent in [ROOT,Path(r'C:\Users\george\Documents\ChatGPT\Proxy-CaseScrewOn')]+list(ROOT.parents):
 if (parent/'.deps').is_dir():sys.path.insert(0,str(parent/'.deps'));break
import numpy as np
import trimesh
from scipy.interpolate import PchipInterpolator, CubicSpline
from manifold3d import Manifold as M, CrossSection as CS, Mesh64
P=json.loads((ROOT/'parameters.json').read_text())
OUT=ROOT/'outputs';PARTS=OUT/'aligned_color_parts';TEST=OUT/'TEST_PRINT_FIRST'
for p in [OUT,PARTS,TEST]:p.mkdir(exist_ok=True,parents=True)
N=120
def sphere(c,s,n=80):return M.sphere(1,n).scale(s).translate(c).set_tolerance(.0001)
def cyl(r,z0,z1):return M.cylinder(z1-z0,r,circular_segments=N).translate((0,0,z0))
def box(lo,hi):return M.cube(tuple(np.array(hi)-lo)).translate(lo)
def union(bits):return M.batch_boolean(bits,__import__('manifold3d').OpType.Add)
def mesh(m):
 a=m.to_mesh64();return trimesh.Trimesh(np.array(a.vert_properties)[:,:3],np.array(a.tri_verts),process=True)
def sector(r0,r1,a0,a1,z0,z1):
 a=np.radians(np.linspace(a0,a1,max(3,int(abs(a1-a0)*2)+1)))
 xy=[(r1*math.cos(t),r1*math.sin(t)) for t in a]+[(r0*math.cos(t),r0*math.sin(t)) for t in a[::-1]]
 return M.extrude(CS([xy]),z1-z0).translate((0,0,z0))
def tube(points,r,n=40):
 bits=[sphere(p,(r,r,r),n) for p in points]
 for a,b in zip(points[:-1],points[1:]):
  d=np.array(b)-a;length=np.linalg.norm(d)
  if length<1e-7:continue
  v=d/length;up=np.array([0,0,1.]) if abs(v[2])<.95 else np.array([0,1.,0])
  u=np.cross(up,v);u/=np.linalg.norm(u);w=np.cross(v,u)
  bits.append(M.cylinder(length,r,circular_segments=n).transform(np.column_stack([u,w,v,np.array(a)])))
 return union(bits)
def curve(points,r,steps=22):
 a=np.array(points);t=np.r_[0,np.cumsum(np.linalg.norm(np.diff(a,axis=0),axis=1))]
 return tube(CubicSpline(t,a,axis=0)(np.linspace(0,t[-1],steps)),r)
def shape_xz(points):
 # Project 2D silhouette along Y, preserving real modeled surface curvature.
 area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))
 if area<0:points=list(reversed(points))
 return M.extrude(CS([points]),90).transform([[1,0,0,0],[0,0,1,-90],[0,1,0,0]])
# Analytic right-hand single-start helix, trapezoidal flanks, 2 degree sampling.
# The female cutter extends beyond both ends; this creates an open thread lead-in.
pitch=P['thread_pitch_mm'];depth=P['thread_depth_mm'];rc=P['thread_radial_clearance_mm'];ac=P['thread_axial_clearance_mm']
def helix(root,zc0,zc1,phase_z,female=False):
    a0=360*(zc0-phase_z)/pitch;a1=360*(zc1-phase_z)/pitch
    angles=np.linspace(a0,a1,int(round((a1-a0)/2))+1)
    rw=P['thread_root_width_mm']/2;cw=P['thread_crest_width_mm']/2
    add=ac if female else 0.;out=rc if female else 0.
    verts=[]
    for a in angles:
        z=phase_z+pitch*a/360
        # Taper ends of male ridge over 90 degrees for easier entry.
        taper=1. if female else min(1.,max(.015,(a-a0)/90),max(.015,(a1-a)/90))
        rmax=root+depth*taper+out
        profile=[(root-.35,z-rw-add),(rmax,z-cw-add),(rmax,z+cw+add),(root-.35,z+rw+add)]
        for r,zz in profile:verts.append((r*math.cos(math.radians(a)),r*math.sin(math.radians(a)),zz))
    faces=[]
    for i in range(len(angles)-1):
        for j in range(4):
            a=i*4+j;b=i*4+(j+1)%4;c=(i+1)*4+(j+1)%4;d=(i+1)*4+j
            faces.extend([(a,b,c),(a,c,d)])
    faces.extend([(0,2,1),(0,3,2)])
    e=(len(angles)-1)*4;faces.extend([(e,e+1,e+2),(e,e+2,e+3)])
    t=trimesh.Trimesh(verts,faces,process=True);t.fix_normals()
    assert t.is_watertight
    solid=M(Mesh64(np.asarray(t.vertices,dtype=np.float64),np.asarray(t.faces,dtype=np.uint64)))
    assert str(solid.status())=='Error.NoError',solid.status()
    return solid


REF=ROOT/'reference'
if not REF.exists():REF=ROOT.parent/'REFERENCE'
source=REF/'Core_Case_ORIGINAL.3mf';digest=hashlib.sha256(source.read_bytes()).hexdigest()
source_parts={}
for name in ['base','lid']:
 a=np.load(REF/(name+'_exact.npz'))
 source_parts[name]=trimesh.Trimesh(a['vertices'],a['faces'],process=False)
base_top=10.;floor_bottom=base_top+P['storage_clear_height_mm'];floor_top=floor_bottom+P['separator_thickness_mm']
base_shift=floor_top+.3-source_parts['base'].bounds[0,2]
seat=base_shift+18.75
seam=seat+.7;hc=seam+9
original_base=source_parts['base'].copy();original_base.apply_translation((0,0,base_shift))
lid_rotation=trimesh.transformations.rotation_matrix(math.radians(20),[0,0,1]) @ trimesh.transformations.rotation_matrix(math.pi,[1,0,0])
lid_transform=lid_rotation.copy();lid_transform[2,3]=seat+source_parts['lid'].bounds[1,2]
original_lid=source_parts['lid'].copy();original_lid.apply_transform(lid_transform)
def solid_from_original(m):
 t=trimesh.Trimesh(m.vertices,m.faces,process=True)
 solid=M(Mesh64(np.asarray(t.vertices),np.asarray(t.faces,dtype=np.uint64)))
 assert str(solid.status())=='Error.NoError'
 # Union overlapping source shells only in the analysis copy. Exact export arrays stay untouched.
 return union([c for c in solid.decompose() if c.volume()>1e-8])
original_base_solid=solid_from_original(original_base)
original_lid_solid=solid_from_original(original_lid)
# Muscle positions move with the sleeve/storage height while the base stays planted.
dz=seam-100.;Z=lambda z:z+dz
print('Building muscular exterior around untouched sleeve envelope...',flush=True)
zs=np.array([10.5,17,36,Z(59),Z(80),seam-2.0]);rs=np.array([32,33,34,39,39,28])
sample=np.linspace(zs[0],zs[-1],85);profile=[(0,zs[0])]+list(zip(PchipInterpolator(zs,rs)(sample),sample))+[(0,zs[-1])]
core=M.revolve(CS([profile]),N).scale((1,0.88,1))
muscles=[core,cyl(34.5,base_top+.5,23),cyl(27,seam-12,seam-1.0)]
for s in [-1,1]:
 muscles += [sphere((s*20,-29,Z(77)),(23,15,17)), # broad pectoral
  sphere((s*44,-1,Z(79)),(20,22,18)),           # deltoid
  sphere((s*54,-4,Z(60)),(16.5,17,21)),        # biceps
  sphere((s*61,-9,Z(43)),(16,18,19)),          # forearm
  sphere((s*19,25,Z(75)),(23,12,19)),          # upper back
  sphere((s*20,21,Z(52)),(16,12,20)),          # lats
  sphere((s*25,-1,25),(16,23,19))]            # thick compact thighs
 for z,x,w,h in [(57,10,12,9),(44,9,11,8),(33,8,10,8)]:
  muscles.append(sphere((s*x,-29 if z>40 else -26,Z(z)),(w,8,h)))
body=union(muscles)
body=body^box((-120,-120,base_top+1.5),(120,120,250))
body=body-cyl(28.71,floor_top,250)-cyl(P['storage_clear_diameter_mm']/2,-5,floor_bottom)
# Additive bonding band overlaps the original OUTSIDE wall; its inner edge is
# beyond all measured internal-fit vertices in this band. Source is not repaired.
bond_lo=floor_top+4.;bond_hi=seat-1.0
body=body+(cyl(29.3,bond_lo,bond_hi)-cyl(28.0,bond_lo-.1,bond_hi+.1))
# Bond under the source's existing solid floor, ending 0.5 mm into it.
body=body+cyl(28.1,floor_top-.1,floor_top+.8)
# Oversized fists are part of the stationary body. Knuckles and thumb are fused.
fists=[]
for s in [-1,1]:
 fist=sphere((s*63,-17,30.5220464706421),(17,17,17))
 for dx in [-9,-3,3,9]:fist=fist+sphere((s*63+dx,-29,32.5220464706421),(4.4,6.5,7),48)
 fist=fist+sphere((s*51,-29,26.5220464706421),(7,7,9),48)
 fists.append(fist)
fists=union(fists)
# Thick embedded organic contours, deliberately irregular rather than painted textures.
markings=[]
for s in [-1,1]:
 for points,r in [
  ([(s*9,-38,89),(s*23,-41,85),(s*34,-36,75),(s*29,-37,70)],2.6),
  ([(s*4,-34,69),(s*17,-38,64),(s*26,-31,57),(s*22,-31,49)],2.8),
  ([(s*39,-15,92),(s*49,-20,87),(s*47,-22,78),(s*55,-15,72)],3.2),
  ([(s*64,-17,65),(s*68,-23,53),(s*61,-27,48),(s*63,-26,40)],3),
  ([(s*12,31,90),(s*17,36,80),(s*29,31,73),(s*22,32,60),(s*13,29,48)],3.4),
  ([(s*34,10,39),(s*32,-11,33),(s*27,-22,23)],3.0)]:
  markings.append(curve([(x,y,Z(z)) for x,y,z in points],r))
# Curves are embedded in the muscle solid, so tiny floating surface pieces cannot occur.
body_cutter=union(markings)+fists
# Round the otherwise pinched red/black wrist junction before color partitioning.
for s in [-1,1]:body_cutter=body_cutter+sphere((s*47.25,-11.48,Z(33.1)),(1.5,1.5,1.5),48)
# Round two generated color-boundary pinches at wrists; original case untouched.
body_cutter=body_cutter+sphere((-71.5858,-5.3174,21.6739),(1.2,1.2,1.2),48)+sphere((48.726,-11.058,23.48),(1.2,1.2,1.2),48)
body_whole=body+fists
# Preserve the fixed decorative envelope separately from the new joint.
body_decoration=body_whole
br=P["base_thread_root_radius_mm"]
# BOTTOM: both feet spin together on a separate full thread, independent of head.
ri=P['storage_clear_diameter_mm']/2;bottom_seat=11.5;base_phase=bottom_seat+2
base=cyl(32,0,base_top)+(cyl(34.5,8,bottom_seat)-cyl(ri,base_top,bottom_seat+.1))
base=base+(cyl(br,base_top-.4,bottom_seat+12.4)-cyl(ri,base_top,bottom_seat+12.5))
base_ridge=helix(br,bottom_seat+2,bottom_seat+10.8,base_phase)
base=base+base_ridge
keep_profile=[(0,10.35),(32.5,10.35)]+[(float(r)+.6,float(z)) for r,z in profile[1:-1]]+[(0,seam)]
keepout=M.revolve(CS([keep_profile]),N)+cyl(46,base_top+.35,13.0)+cyl(90,13,30)
feet=[]
for direction in [-1,1]:
 f=sphere((direction*23,-12,8),(24,28,13))
 for dx in [-12,-4,4,12]:f=f+sphere((direction*23+dx,-31,6.5),(6.5,10,9),48)
 feet.append(f-keepout)
base=(base+union(feet))^box((-100,-100,0),(100,100,30))
base=base-cyl(ri,base_top,bottom_seat+21)
# Male stop rotates up into a female sector only for the final 45 degrees.
base_stop=sector(33.65,34.35,82,90,bottom_seat-.05,bottom_seat+.5)
base=base+base_stop
body_whole=body_whole-cyl(br+rc,bottom_seat-.1,bottom_seat+12.75)
body_whole=body_whole-helix(br,bottom_seat-8,bottom_seat+24,base_phase,True)
body_whole=body_whole-sector(33.55,34.45,20,90,bottom_seat-.1,bottom_seat+.7)
body_black=body_whole^body_cutter
body_red=body_whole-body_cutter
# Foot markings embedded in black feet, red with black toe grooves.
redfeet=[]
for s in [-1,1]:
 redfeet.append(curve([(s*17,-11,10),(s*21,-23,10),(s*28,-28,10),(s*27,-36,7)],3.5))
foot_cutter=union(redfeet)
base_red=base^foot_cutter;base_black=base-foot_cutter
# Whole head with integrated female screw socket and sealing face.
outer=sphere((0,0,hc),(55,43,58),128)
inner=sphere((0,0,hc),(51.8,39.8,54.8),128)
clip=box((-100,-100,seam),(100,100,250));head=(outer-inner)^clip
skin=head
blackbits=[];pinkbits=[]
def hp(x,z,back=False):
 y=43*math.sqrt(max(.0001,1-(x/55)**2-((z-hc)/58)**2))
 return (x,y if back else -y,z)
for s in [-1,1]:
 eye=[(s*5,hc+13),(s*17,hc+27),(s*37,hc+40),(s*41,hc+29),(s*37,hc+18),(s*25,hc+13),(s*12,hc+12)]
 border=[(s*1,hc+8),(s*15,hc+28),(s*40,hc+46),(s*47,hc+29),(s*43,hc+9),(s*25,hc+3),(s*9,hc+4)]
 if s<0:eye=eye[::-1];border=border[::-1]
 pinkbits.append(shape_xz(eye));blackbits.append(shape_xz(border))
 # Forehead symbiote fork and hooked cheek markings follow the head surface.
 for pts,r in [([(s*7,hc+53),(s*13,hc+41),(s*7,hc+31),(s*5,hc+23)],3.4),
               ([(s*28,hc+47),(s*24,hc+51),(s*18,hc+49)],3.1)]:
  blackbits.append(curve([hp(x,z) for x,z in pts],r))
 # Rear flowing streaks visible in back preview.
 for pts,r in [([(s*6,hc+53),(s*14,hc+43),(s*10,hc+32),(s*20,hc+20),(s*17,hc+8)],4.0),
               ([(s*35,hc+38),(s*40,hc+24),(s*32,hc+14),(s*37,hc+3)],3.5)]:
  blackbits.append(curve([hp(x,z,True) for x,z in pts],r))
# Wide black grin with large pink, individually modeled rounded teeth.
mouthtop=[(float(x),hc+3+13*(x/43)**2) for x in np.linspace(-43,43,49)]
mouthbottom=[(float(x),seam+1.3+7*(x/43)**2) for x in np.linspace(43,-43,49)]
blackbits.append(shape_xz(mouthtop+mouthbottom))
for x in np.linspace(-38,38,13):
 z=hc-2.6+9.5*(x/40)**2
 # Intersect elongated teeth with the curved facial shell to keep them anchored.
 pinkbits.append(sphere(hp(x,z),(3.25,6,5.5),64))
# Short round tendrils with 8.4 mm minimum diameter, wholly above rotational seam.
for s in [-1,1]:
 side=curve([(s*49,0,hc+11),(s*63,0,hc+8),(s*69,0,hc+17),(s*64,0,hc+23),(s*59,0,hc+19)],4.2)
 top=curve([(s*31,3,hc+46),(s*42,3,hc+56),(s*40,3,hc+66),(s*33,3,hc+65),(s*32,3,hc+59)],4.2)
 head=head+side+top
 blackbits.append(box((s*60-18,-8,hc+3),(s*60+18,8,hc+15)))
 blackbits.append(box((s*35-13,-6,hc+43),(s*35+13,12,hc+56)))
crest=curve([(0,8,hc+54),(-5,8,hc+62),(-3,8,hc+69),(3,8,hc+66)],4.2)
head=head+crest;blackbits.append(box((-12,0,hc+54),(10,17,hc+78)))
blackbits.append(cyl(56,seam,seam+2.2))
head_decoration=head
# Original lid is the actual closure. Attach only outside its wall.
# Keep all generated head material outside radius 28 mm through original lid height.
head=head-cyl(28.0,seam-.1,float(original_lid.bounds[1,2])+.1)
head_web=(outer^cyl(60,seam+2,seam+5.2))-cyl(28.,seam+1.9,seam+5.3)
head_socket=(cyl(36.5,seam+1,seam+14)-cyl(28.,seam+.9,seam+14.1))+head_web
head=head+head_socket
pink_cutter=union(pinkbits);black_cutter=union(blackbits)
# Keep the hidden connection red; avoid extra color boundaries in the socket.
black_cutter=black_cutter-cyl(37,seam-.1,seam+15)
pink_cutter=pink_cutter-cyl(37,seam-.1,seam+15)
head_pink=head^pink_cutter
head_black=(head-pink_cutter)^black_cutter
head_red=head-pink_cutter-black_cutter

parts={'body_red':body_red,'body_black':body_black,'head_red':head_red,'head_black':head_black,'head_pink':head_pink,'base_black':base_black,'base_red':base_red}
def clean(s):
 return union([c for c in s.set_tolerance(.005).decompose() if c.volume()>.0001]).simplify(.005)
parts={n:clean(v) for n,v in parts.items()}
meshes={n:mesh(v) for n,v in parts.items()}
meshes['ORIGINAL_CASE_BASE_EXACT']=original_base
meshes['ORIGINAL_CASE_LID_EXACT']=original_lid
groups={n:('head' if n.startswith('head') or n=='ORIGINAL_CASE_LID_EXACT' else 'bottom' if n.startswith('base') else 'body') for n in meshes}
colors={n:('#F482A0' if 'pink' in n else '#18191D' if 'black' in n else '#CD1225') for n in meshes}
manifest=[]
for n,m in meshes.items():
 # ASCII STL avoids single-precision loss; delivery 3MF also uses float64 values.
 (PARTS/(n+'.stl')).write_text(trimesh.exchange.stl.export_stl_ascii(m))
 manifest.append({'name':n,'path':'aligned_color_parts/'+n+'.stl','group':groups[n],'color':colors[n]})
jar=cyl(P['preview_jar_diameter_mm']/2,base_top,base_top+P['preview_jar_height_mm'])
mesh(jar).export(OUT/'jar_PROVISIONAL_REFERENCE_ONLY.stl')
manifest.append({'name':'jar_PROVISIONAL_46x30','path':'jar_PROVISIONAL_REFERENCE_ONLY.stl','group':'jar','color':'#696F78'})
(OUT/'geometry_manifest.json').write_text(json.dumps(manifest,indent=2))
body_complete=body_whole+original_base_solid;head_complete=head+original_lid_solid
print('Validating source-based V4 assembly...',flush=True)
checks={
 'original_case_sha256':digest,
 'original_base_triangles':len(original_base.faces),'original_lid_triangles':len(original_lid.faces),
 'original_base_exact_vertex_error_mm':float(np.abs((original_base.vertices-[0,0,base_shift])-source_parts['base'].vertices).max()),
 'original_lid_exact_vertex_error_mm':float(np.abs(trimesh.transform_points(original_lid.vertices,np.linalg.inv(lid_transform))-source_parts['lid'].vertices).max()),
 'original_base_source_watertight':bool(source_parts['base'].is_watertight),'original_lid_source_watertight':bool(source_parts['lid'].is_watertight),
 'source_base_transform':trimesh.transformations.translation_matrix([0,0,base_shift]).tolist(),'source_lid_transform':lid_transform.tolist(),
 'original_thread_pitch_mm':2.5,'bottom_thread_pitch_mm':pitch,
 'source_base_addition_bond_mm3':(body_whole^original_base_solid).volume(),
 'source_lid_addition_bond_mm3':(head^original_lid_solid).volume(),
 'new_material_inside_base_cavity_envelope_mm3':(body_whole^cyl(27.99,floor_top+.81,seat+7.51)).volume(),
 'bottom_bond_original_void_overlap_mm3':(cyl(24.9,floor_top+.301,floor_top+.8)-original_base_solid).volume(),
 'new_material_inside_lid_cavity_envelope_mm3':(head^cyl(27.99,seat-.01,float(original_lid.bounds[1,2])+.05)).volume(),
 'closed_head_body_overlap_mm3':(head_complete^body_complete).volume(),
 'closed_bottom_body_overlap_mm3':(base^body_complete).volume(),
 'original_thread_clearance_retained':True,'physical_fit_verified':False,'odor_seal_verified':False,
 'head_clocking':'Original thread retained with no added stop. Preview uses a collision-free phase; final printed seating angle is unverified.',
 'new_meshes':{n:{'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'positive_volume':bool(m.volume>0),'triangles':len(m.faces)} for n,m in meshes.items() if not n.startswith('ORIGINAL')},
 'assembled_size_mm':trimesh.util.concatenate(list(meshes.values())).extents.tolist(),
 'storage_clear_size_mm':[50,33], 'jar_placeholder_size_mm':[46,30],
 'motion_sampling':'Every 5 degrees over four full turns; original head pitch 2.5 mm, storage base 4 mm. Sampled check, not a continuous proof.'
}
for name,solid in [('body',body_complete),('head',head_complete),('bottom',base)]:
 checks.setdefault('combined_solid_components',{})[name]=len([c for c in solid.decompose() if c.volume()>1e-5])
checks['head_motion_collisions']=[];checks['bottom_motion_collisions']=[]
for angle in np.arange(0,1440.01,5):
 a=float(angle)
 vh=(head_complete.rotate((0,0,a)).translate((0,0,a*2.5/360))^body_complete).volume()
 vb=(base.rotate((0,0,-a)).translate((0,0,-a*pitch/360))^body_complete).volume()
 if vh>1e-4:checks['head_motion_collisions'].append([a,vh])
 if vb>1e-4:checks['bottom_motion_collisions'].append([a,vb])
 if angle%180==0:print('Motion checked',angle,flush=True)
checks['jar_exit_overlap_mm3']=max((jar.translate((0,0,float(z)))^body_complete).volume() for z in np.linspace(-50,0,26))
# Additional head straight lift after threads disengage.
checks['head_after_thread_disengagement_overlap_mm3']=max((head_complete.translate((0,0,float(z)))^body_complete).volume() for z in np.arange(10,91,5))
(OUT/'validation.json').write_text(json.dumps(checks,indent=2))
assert checks['source_base_addition_bond_mm3']>100
assert checks['source_lid_addition_bond_mm3']>100
assert all(m['watertight'] and m['winding_consistent'] and m['positive_volume'] for m in checks['new_meshes'].values())
assert abs(checks['new_material_inside_base_cavity_envelope_mm3'])<1e-4
assert abs(checks['new_material_inside_lid_cavity_envelope_mm3'])<1e-4
assert abs(checks['bottom_bond_original_void_overlap_mm3'])<1e-4
assert not checks['head_motion_collisions'],checks['head_motion_collisions'][:5]
assert not checks['bottom_motion_collisions'],checks['bottom_motion_collisions'][:5]
assert abs(checks['closed_head_body_overlap_mm3'])<1e-4
assert abs(checks['closed_bottom_body_overlap_mm3'])<1e-4
assert checks['jar_exit_overlap_mm3']<1e-4
print('VALIDATION PASSED',checks['assembled_size_mm'],flush=True)
