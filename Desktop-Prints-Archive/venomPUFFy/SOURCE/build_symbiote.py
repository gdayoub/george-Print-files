"""Editable parametric mesh CAD for the muscular Symbiote Core.
Run using Python 3.13 with numpy, trimesh, scipy and manifold3d.
User requested plain full screw-on printed closures with no separate seals or hardware.
STL source remains byte-for-byte unchanged. No geometric repair is applied to it.
Front is -Y; Z is up; units are mm. Parts export in shared assembly coordinates.
"""
from pathlib import Path
import sys,json,math,hashlib,shutil,zipfile,struct
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
for parent in [ROOT]+list(ROOT.parents):
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

source=Path(P['source_sleeve'])
if not source.exists():source=ROOT.parent/'REFERENCE'/'ORIGINAL_sleeve_UNCHANGED.stl'
raw=source.read_bytes();digest=hashlib.sha256(raw).hexdigest()
shutil.copyfile(source,OUT/'original_sleeve_UNCHANGED.stl')
original=trimesh.load_mesh(source);sleeve=original.copy()
assert digest=='b4eef4a572c2d5ad06dac0f7b08190e719f11ef21ee1fecb9e061a9505f9e225'
# Decode raw binary STL facets without processing: source triangles stay exact.
source_face_count=struct.unpack_from('<I',raw,80)[0]
source_dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')])
source_tri=np.frombuffer(raw,dtype=source_dtype,count=source_face_count,offset=84)['vertices'].astype(np.float64)
center=(sleeve.bounds[0,:2]+sleeve.bounds[1,:2])/2
base_top=10.;floor_bottom=base_top+P['storage_clear_height_mm'];floor_top=floor_bottom+P['separator_thickness_mm']
shift=np.r_[-center,floor_top+P['sleeve_floor_clearance_mm']-sleeve.bounds[0,2]]
sleeve.apply_translation(shift);rim=float(sleeve.bounds[1,2]);seam=rim+.5;hc=seam+9
original_exact=trimesh.Trimesh((source_tri+shift).reshape(-1,3),np.arange(source_face_count*3).reshape(-1,3),process=False)
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
body=body-cyl(P['sleeve_carrier_bore_radius_mm'],floor_top,250)-cyl(P['storage_clear_diameter_mm']/2,-5,floor_bottom)
# Additive bonding band overlaps the original OUTSIDE wall; its inner edge is
# beyond all measured internal-fit vertices in this band. Source is not repaired.
bond_lo=shift[2]+8;bond_hi=shift[2]+35
body=body+(cyl(23.7,bond_lo,bond_hi)-cyl(22.4,bond_lo-.1,bond_hi+.1))
# Oversized fists are part of the stationary body. Knuckles and thumb are fused.
fists=[]
for s in [-1,1]:
 fist=sphere((s*63,-17,Z(30)),(17,17,17))
 for dx in [-9,-3,3,9]:fist=fist+sphere((s*63+dx,-29,Z(32)),(4.4,6.5,7),48)
 fist=fist+sphere((s*51,-29,Z(26)),(7,7,9),48)
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
body_whole=body+fists
# Preserve the fixed decorative envelope separately from the new joint.
body_decoration=body_whole
# HEAD: full screw-on connection above untouched sleeve. 4 mm lead, >2 turns.
hr=P['head_thread_root_radius_mm'];br=P['base_thread_root_radius_mm']
head_phase=seam+2.0
head_male=(cyl(hr,seam-4,seam+12.4)-cyl(23.4,seam-4.1,seam+12.5))
head_male=head_male+(cyl(36.5,seam-3,seam)-cyl(23.4,seam-3.1,seam+.1))
head_ridge=helix(hr,seam+2,seam+10.8,head_phase)
head_male=head_male+head_ridge
# An outer alignment stop engages only in the final 45 degrees of travel.
# Thread backlash therefore cannot clock the face beyond the nominal front.
head_stop=sector(35.0,36.2,82,90,seam-.05,seam+.5)
head_male=head_male+head_stop
body_whole=body_whole+head_male
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
# Continuous sealing face outside the thread, with no bayonet entry openings.
head_web=(outer^cyl(60,seam,seam+3.2))-cyl(hr+rc,seam-.1,seam+3.3)
head_socket=(cyl(36.5,seam,seam+14)-cyl(hr+rc,seam-.1,seam+14.1))+head_web
head_socket=head_socket-helix(hr,seam-8,seam+24,head_phase,True)
head_socket=head_socket-sector(34.9,36.3,20,90,seam-.1,seam+.7)
head=head+head_socket
pink_cutter=union(pinkbits);black_cutter=union(blackbits)
# Keep the hidden connection red; avoid extra color boundaries in the socket.
black_cutter=black_cutter-cyl(37,seam-.1,seam+15)
pink_cutter=pink_cutter-cyl(37,seam-.1,seam+15)
head_pink=head^pink_cutter
head_black=(head-pink_cutter)^black_cutter
head_red=head-pink_cutter-black_cutter
for label,solid in [('head',head),('skin',skin),('pink',head_pink),('black',head_black),('red',head_red),('base',base),('base_red',base_red)]:
 print(label,str(solid.status()),solid.num_tri(),solid.volume(),flush=True)
parts={'body_red':body_red,'body_black':body_black,'head_red':head_red,'head_black':head_black,'head_pink':head_pink,'base_black':base_black,'base_red':base_red}
def clean(s):
 s=s.set_tolerance(.005)
 return union([c for c in s.decompose() if c.volume()>0.0001]).simplify(.005)
parts={n:clean(s) for n,s in parts.items()}
groups={n:('head' if n.startswith('head') else 'bottom' if n.startswith('base') else 'body') for n in parts}
colors={n:('#F482A0' if 'pink' in n else '#18191D' if 'black' in n else '#CD1225') for n in parts}
meshes={};manifest=[]
report={'status':P['status'],'units':'mm','source_sha256':digest,'original_source_bounds_mm':original.bounds.tolist(),'source_scale':1,'source_rigid_translation_mm':shift.tolist(),'source_watertight':bool(original.is_watertight),'source_boundary_edges':int(np.count_nonzero(np.bincount(original.edges_unique_inverse)==1)),'parts':{},'checks':{},'dimensions':{'floor_bottom_z':floor_bottom,'floor_top_z':floor_top,'sleeve_rim_z':rim,'head_seam_z':seam,'storage_clear_ID_mm':ri*2,'storage_clear_height_mm':P['storage_clear_height_mm'],'head_shell_nominal_mm':3.2}}
print('Exporting aligned color meshes...',flush=True)
for n,s in parts.items():
 m=mesh(s);(PARTS/(n+'.stl')).write_text(trimesh.exchange.stl.export_stl_ascii(m));meshes[n]=m;back=trimesh.load_mesh(PARTS/(n+'.stl'))
 report['parts'][n]={'triangles':len(back.faces),'watertight':bool(back.is_watertight),'winding_consistent':bool(back.is_winding_consistent),'positive_volume':bool(back.volume>0),'components':len(s.decompose()),'bounds':back.bounds.tolist(),'volume_mm3':float(back.volume)}
 manifest.append({'name':n,'path':'aligned_color_parts/'+n+'.stl','group':groups[n],'color':colors[n]})
(OUT/'ORIGINAL_CORE_body_component.stl').write_text(trimesh.exchange.stl.export_stl_ascii(original_exact))
manifest.append({'name':'ORIGINAL_CORE_PRINTS_WITH_BODY','path':'ORIGINAL_CORE_body_component.stl','group':'body','color':'#CD1225'})
meshes['ORIGINAL_CORE_PRINTS_WITH_BODY']=original_exact
groups['ORIGINAL_CORE_PRINTS_WITH_BODY']='body'
colors['ORIGINAL_CORE_PRINTS_WITH_BODY']='#CD1225'
jar=cyl(P['preview_jar_diameter_mm']/2,base_top,base_top+P['preview_jar_height_mm'])
mesh(jar).export(OUT/'jar_PROVISIONAL_REFERENCE_ONLY.stl')
manifest.append({'name':'jar_PROVISIONAL_46x30','path':'jar_PROVISIONAL_REFERENCE_ONLY.stl','group':'jar','color':'#696F78'})
(OUT/'geometry_manifest.json').write_text(json.dumps(manifest,indent=2))
print('Checking meshes, protected sleeve region and closure sweeps...',flush=True)
body_all=body_whole;base_all=base;head_all=head
check=report['checks'];check['source_file_unchanged']=digest==hashlib.sha256(source.read_bytes()).hexdigest()
check['protected_cup_interior_envelope_overlap_mm3']=(body_all^cyl(22.39,floor_top+.0001,rim)).volume()
check['original_core_included_as_printable_body_component']=True
check['original_triangles_preserved']=source_face_count
check['bonding_band_source_z_mm']=[8,35]
check['bonding_band_inside_radius_mm']=22.4
fc=original.triangles_center;xy=fc[:,:2]-center
inside=(np.sum(original.face_normals[:,:2]*xy,axis=1)<-5)&(fc[:,2]>8)&(fc[:,2]<35)
inner_max=float(np.linalg.norm(original.triangles[inside,:,:2]-center,axis=2).max())
check['measured_max_original_inner_radius_in_bonding_band_mm']=inner_max
check['new_material_margin_outside_original_inner_wall_mm']=22.4-inner_max
assert check['new_material_margin_outside_original_inner_wall_mm']>.5
check['source_original_fit_geometry']='Raw original triangles retained exactly with rigid translation only; no repair/remesh/scale. New material overlaps exterior only within bonding band.'
check['head_min_z_mm']=float(mesh(head_all).bounds[0,2]);check['body_max_z_mm']=float(mesh(body_all).bounds[1,2])
check['decorative_head_to_body_clearance_by_disjoint_Z_mm']=float(mesh(head_decoration).bounds[0,2]-mesh(body_decoration).bounds[1,2])
check['decorative_head_full_360_against_new_collar_bound_mm3']=(head_decoration^cyl(36.51,seam-.01,seam+14.01)).volume()
check['head_overlap_rotational_sleeve_keepout_mm3']=(head_all^cyl(23.4,floor_top,rim)).volume()
check['head_connection']='New full single-start right-hand 4 mm pitch thread. 2.2 revolutions of modeled male ridge with tapered ends. Not copied from missing original cap.'
check['face_clocking']='Head and joined feet aligned at modeled seats and terminal stop walls at zero degrees. Physical fit and printed stop strength unverified.'
print('Checking full helical removal paths for head and feet...',flush=True)
head_hits=[];base_hits=[]
# Full model, including arms/tendrils/feet. Opening head is +theta, base is -theta.
# 2 degrees per sample through four turns, to complete axial disengagement.
for angle in np.arange(0,1440.001,2):
    z=float(angle)*pitch/360
    v=(head_all.rotate((0,0,float(angle))).translate((0,0,z))^body_all).volume()
    if v>1e-4:head_hits.append({'angle_deg':float(angle),'lift_mm':z,'volume_mm3':v})
    v=(base_all.rotate((0,0,-float(angle))).translate((0,0,-z))^body_all).volume()
    if v>1e-4:base_hits.append({'angle_deg':-float(angle),'drop_mm':z,'volume_mm3':v})
check['head_motion_collisions']=head_hits;check['base_motion_collisions']=base_hits
check['motion_sampling']='Full model helical motion sampled every 2 degrees over 1440 degrees (16 mm axial travel). Not exhaustive continuous swept-volume proof.'
check['head_closed_overlap_mm3']=(head_all^body_all).volume()
check['base_closed_overlap_mm3']=(base_all^body_all).volume()
check['head_clocking_stop_overlap_at_2deg_overturn_mm3']=(head_all.rotate((0,0,-2))^head_stop).volume()
check['base_clocking_stop_overlap_at_2deg_overturn_mm3']=(base_stop.rotate((0,0,2))^body_all).volume()
check['thread_pitch_mm']=pitch;check['male_ridge_turns']=2.2
check['thread_radial_clearance_mm']=rc;check['thread_axial_clearance_each_flank_mm']=ac
check['odor_seal_verified']=False
check['separate_hardware_required']=False
# Confirm the former gasket recesses are solid, restoring continuous flat seats.
neck_seat_band=cyl(34.35,seam-1.5,seam)-cyl(31.65,seam-1.6,seam+.1)
base_seat_band=cyl(33.35,bottom_seat-1.5,bottom_seat)-cyl(30.65,bottom_seat-1.6,bottom_seat+.1)
check['head_flat_seat_missing_material_mm3']=(neck_seat_band-head_male).volume()
check['base_flat_seat_missing_material_mm3']=(base_seat_band-base_all).volume()
assert abs(check['head_flat_seat_missing_material_mm3'])<1e-5
assert abs(check['base_flat_seat_missing_material_mm3'])<1e-5
check['color_overlap_mm3']={}
for g in ['body','head','bottom']:
 ns=[n for n in parts if groups[n]==g]
 check['color_overlap_mm3'][g]=sum(max(0,(parts[a]^parts[b]).volume()) for i,a in enumerate(ns) for b in ns[i+1:])
check['assembly_solid_component_counts_before_color_partition']={g:len(s.decompose()) for g,s in [('body',body_all),('head',head_all),('bottom',base_all)]}
check['color_export_tolerance_mm']=.005
check['color_export_note']='Negligible Boolean slivers under 0.0001 cubic mm removed from generated decoration only. Original sleeve untouched.'
check['provisional_jar_overlap_mm3']=(jar^(body_all+base_all)).volume()
check['provisional_jar_straight_exit_overlap_mm3']=max((jar.translate((0,0,float(z)))^body_all).volume() for z in np.linspace(-50,0,26))
check['jar_roof_gap_mm']=P['storage_clear_height_mm']-P['preview_jar_height_mm']
check['jar_exposed_height_above_base_collar_mm']=base_top+P['preview_jar_height_mm']-(bottom_seat+12.4)
check['separator_minimum_mm']=P['separator_thickness_mm']
check['tendril_minimum_diameter_mm']=8.4
check['wall_thickness']='By construction: 3.2 mm ellipsoid shell offsets, 3.6 mm separator, 2.5 mm minimum base thread-root collar; no exhaustive mesh thickness proof. Check valleys and color interfaces in slicer.'
allm=trimesh.util.concatenate(list(meshes.values()));report['assembled_size_mm']=allm.extents.tolist();report['assembled_bounds_mm']=allm.bounds.tolist()
check['static_mesh_volume_centroid_xy_mm']=allm.center_mass[:2].tolist()
check['stable_base']='Flat joined feet; centroid projection checked against circular base radius 32 mm. Physical stability with actual cup/jar remains untested.'
check['centroid_within_base_disk']=bool(np.linalg.norm(allm.center_mass[:2])<32)
# Small screw-fit test pots: actual interfaces plus 1.6 mm fixture closure floors.
# Closed fixtures reproduce the plain screw-on seats with no separate seals.
female=(body_all^cyl(34.5,bottom_seat,bottom_seat+14.6))+cyl(34.5,bottom_seat+13,bottom_seat+14.6)
male=(base_all^cyl(34.5,8,bottom_seat+13))+cyl(ri,8,9.6)
head_female_test=(head_socket^cyl(36.5,seam,seam+15.6))+cyl(36.5,seam+14,seam+15.6)
head_male_test=head_male+cyl(23.6,seam-4,seam-2.4)
head_female_test=head_female_test-box((-.6,-37,seam+14.5),(.6,-34,seam+15.7))
head_male_test=head_male_test-box((-.6,-37,seam-2.8),(.6,-35,seam-1.8))
for name,solid,zoff,purpose in [
 ('BASE_01_BODY_RING',female,-bottom_seat,'Bottom female thread and sealing face; closed fixture roof'),
 ('BASE_02_FEET_RING',male,-8,'Bottom male thread and continuous flat seat; closed fixture floor'),
 ('HEAD_01_BODY_RING',head_male_test,-seam+4,'Head male thread and continuous flat seat; closed fixture floor'),
 ('HEAD_02_CAP_RING',head_female_test,-seam,'Head female thread and sealing face; closed fixture roof')]:
 t=mesh(clean(solid).translate((0,0,zoff)))
 # Print the fixture closure disk on the bed, avoiding a 50+ mm unsupported roof.
 if name in ['BASE_01_BODY_RING','HEAD_02_CAP_RING']:
  t.apply_transform(trimesh.transformations.rotation_matrix(math.pi,[1,0,0]))
  t.apply_translation([0,0,-t.bounds[0,2]])
 (TEST/(name+'.stl')).write_text(trimesh.exchange.stl.export_stl_ascii(t))
 report.setdefault('test_prints',{})[name]={'watertight':bool(t.is_watertight),'winding_consistent':bool(t.is_winding_consistent),'size_mm':t.extents.tolist(),'purpose':purpose}
 assert t.is_watertight and t.is_winding_consistent and t.volume>0
# Core-spec 3MF with colored components; it is not a sliced printer project.
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',NS)
def element(p,t,a={}):return ET.SubElement(p,'{'+NS+'}'+t,a)
r=ET.Element('{'+NS+'}model',{'unit':'millimeter'});element(r,'metadata',{'name':'Title'}).text='Symbiote Core PLAIN SCREW V3 - no extra hardware - fit unverified'
res=element(r,'resources');mat=element(res,'basematerials',{'id':'1'})
for name,c in [('red','#CD1225FF'),('black','#18191DFF'),('pink','#F482A0FF')]:element(mat,'base',{'name':name,'displaycolor':c})
ids={}
for i,(name,m) in enumerate(meshes.items(),2):
 ids[name]=i;ci=2 if 'pink' in name else 1 if 'black' in name else 0
 ob=element(res,'object',{'id':str(i),'name':name,'type':'model','pid':'1','pindex':str(ci)});me=element(ob,'mesh');vs=element(me,'vertices');ts=element(me,'triangles')
 for v in m.vertices:element(vs,'vertex',{k:repr(float(a)) for k,a in zip('xyz',v)})
 for f in m.faces:element(ts,'triangle',{k:str(int(a)) for k,a in zip(['v1','v2','v3'],f)})
build=element(r,'build')
for i,g in enumerate(['body','head','bottom'],30):
 ob=element(res,'object',{'id':str(i),'name':g.upper()+'_ASSEMBLY','type':'model'});cs=element(ob,'components')
 for n in ids:
  if groups[n]==g:element(cs,'component',{'objectid':str(ids[n])})
 element(build,'item',{'objectid':str(i)})
with zipfile.ZipFile(OUT/'multicolor_new.zip','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
 z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
 z.writestr('3D/3dmodel.model',ET.tostring(r,encoding='utf-8',xml_declaration=True))
(OUT/'multicolor_new.zip').replace(OUT/'Symbiote_Core_PLAIN_SCREW_V3.3mf')
# Exact source identity is checked inside the delivered 3MF as well as on disk.
with zipfile.ZipFile(OUT/'Symbiote_Core_PLAIN_SCREW_V3.3mf') as z:
 xml=ET.fromstring(z.read('3D/3dmodel.model'))
 obj=next(o for o in xml.find('{'+NS+'}resources').findall('{'+NS+'}object') if o.get('name')=='ORIGINAL_CORE_PRINTS_WITH_BODY')
 vv=np.array([[float(v.get(k)) for k in 'xyz'] for v in obj.find('{'+NS+'}mesh').find('{'+NS+'}vertices')])
 check['embedded_original_vertex_error_mm']=float(np.abs(vv-original_exact.vertices).max())
 assert check['embedded_original_vertex_error_mm']==0
(OUT/'validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'size_mm':report['assembled_size_mm'],'checks':check},indent=2),flush=True)
