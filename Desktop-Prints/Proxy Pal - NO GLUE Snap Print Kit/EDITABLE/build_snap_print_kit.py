"""Proxy Pal: independently printable colors, hollow body, glue-free split snaps.
All CAD units mm. Source sleeve is never changed. Run using requirements.txt.
"""
from pathlib import Path
import json,sys,math,shutil,struct,zipfile
import xml.etree.ElementTree as E
R=Path(__file__).parent;sys.path.insert(0,str(R/'.deps'))
import numpy as np,trimesh
from manifold3d import Manifold as M,Mesh as MM,CrossSection as CS
P=json.loads((R/'snap_parameters.json').read_text());O=R/'outputs'/('snap_speed_baseline' if '--solid-body' in sys.argv else 'snap_print_kit');A=O/'ASSEMBLY';S=O/'PRINT_STLS';T=O/'FIT_TEST_FIRST'
for p in [O,A,S,T,O/'REFERENCE']:p.mkdir(parents=True,exist_ok=True)
old=R/P['asset_directory'];shift=np.array(P['source_translation_mm'])
def frommesh(m):return M(MM(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
def mesh(m):
 t=m.to_mesh();out=trimesh.Trimesh(np.array(t.vert_properties)[:,:3],np.array(t.tri_verts),process=True)
 if not out.is_watertight:
  # Remove numerical zero-area seams in NEW Boolean solids only. Never used on
  # the unchanged source sleeve. Maximum coordinate rounding 0.0000005 mm.
  out.vertices=np.round(out.vertices,6);out.merge_vertices(digits_vertex=6)
  f=out.faces;out.update_faces((f[:,0]!=f[:,1])&(f[:,1]!=f[:,2])&(f[:,2]!=f[:,0]));out.update_faces(out.unique_faces());out.remove_unreferenced_vertices()
 return out
def load(n):
 m=trimesh.load_mesh(old/(n+'.stl'));m.apply_translation(shift);return frommesh(m)
def box(lo,hi):return M.cube(tuple(np.array(hi)-lo)).translate(lo)
def cyl(r,z0,z1,n=160):return M.cylinder(z1-z0,r,circular_segments=n).translate((0,0,z0))
def sphere(p,s):return M.sphere(1,64).scale(s).translate(p)
def rev(points):return M.revolve(CS([points]),160)
def union(ms):
 a=ms[0]
 for b in ms[1:]:a=a+b
 return a
def frame(p,n,u=None):
 n=np.array(n,dtype=float);n/=np.linalg.norm(n)
 if u is None:
  ref=np.array([0,0,1.]) if abs(n[2])<.9 else np.array([0,1.,0])
  u=np.cross(ref,n)
 u=np.array(u,dtype=float);u/=np.linalg.norm(u);v=np.cross(n,u)
 return np.column_stack([u,v,n,np.array(p)])
def xf(s,F):return s.transform(F)
def snap(cfg):
 w,t,L,slot,barb=[cfg[k] for k in ['width','thickness','length','slot','barb_per_side']]
 # Beveled retention on both sides: removable without glue or hidden fasteners.
 prof=[(-w/2,.9),(w/2,.9),(w/2,-L+2.0),(w/2+barb,-L+1.4),(w/2+barb,-L+.95),(w/2-.2,-L),(-w/2+.2,-L),(-w/2-barb,-L+.95),(-w/2-barb,-L+1.4),(-w/2,-L+2.0)]
 # 2D (x,z) polygon extruded along y.
 peg=M.extrude(CS([prof[::-1]]),t).rotate((90,0,0)).translate((0,t/2,0))
 peg=peg-box((-slot/2,-t,-L-.2),(slot/2,t,-1.5))
 return peg
def socket(cfg,top=.5,bottom=None,clearance=None):
 w,t,L=[cfg[k] for k in ['width','thickness','length']];c=cfg['clearance_per_side'] if clearance is None else clearance
 bottom=-L+2.4 if bottom is None else bottom
 return box((-w/2-c,-t/2-c,bottom-.05),(w/2+c,t/2+c,top))
def boss(cfg,top=-.5,bottom=None):
 L=cfg['length'];bottom=-L+2.4 if bottom is None else bottom
 return box((-cfg['width']/2-1.8,-cfg['thickness']/2-1.8,bottom),(cfg['width']/2+1.8,cfg['thickness']/2+1.8,top))
body=load('01_red_exterior_added_to_core');head=load('03_red_head_shell');base=load('05_black_feet_storage_base');tongue=load('02_pink_tongue')
original_body_volume=body.volume()
# Open annular weight-relief cavities, retaining cup carrier, storage walls and
# the full storage/cup separator. Four 2.4mm webs connect inner and outer shells.
seam=75.92204647064209;headz=seam+.6;hc=headz+2.2
head=head-sphere((0,0,hc),(53.6,53.6,54.6))
void=rev([(35.9,4.75),(39.0,4.75),(41.6,8),(46.2,18),(51.4,37),(52.25,61),(52.6,seam+.2),(24.8,seam+.2),(24.8,47.3),(31.4,40.7),(31.4,18.5),(35.9,14)])
rib=union([box((-70,-1.2,0),(70,1.2,80)),box((-1.2,-70,0),(1.2,70,80))])
if P.get('hollow_body',False) and '--solid-body' not in sys.argv:body=body-(void-rib)
print('Initial body/head/base',body.status(),head.status(),base.status(),body.volume(),flush=True)
details=[];interfaces=[]
black=trimesh.load_mesh(old/'04_black_head_details.stl');black.apply_translation(shift)
components=black.split(only_watertight=False,repair=False)
def surface(x,z):
 y=-56*math.sqrt(max(.0001,1-(x/56)**2-((z-hc)/57)**2));p=np.array([x,y,z]);n=np.array([x/56**2,y/56**2,(z-hc)/57**2]);n/=np.linalg.norm(n);return p,n
def add_detail(name,solid,anchors,host='head'):
 global head,body
 cfg=P['detail_clip'];hostsolid=head if host=='head' else body;original_detail=solid
 common_n=np.mean([n for p,n in anchors],axis=0);common_n/=np.linalg.norm(common_n)
 anchors=[(p,common_n) for p,n in anchors]
 mats=[]
 for p,n in anchors:
  F=frame(p,n);mats.append(F)
  solid=solid+xf(snap(cfg),F)
  # Receiver boss is entirely within the decorative structure, not the sleeve.
  receiver=boss(cfg)
  if name=='BLACK_crest':receiver=box((-6.3,-4.2,-cfg['length']+2.4),(6.3,4.2,-.5))
  hostsolid=(hostsolid+xf(receiver,F))-xf(socket(cfg,top=3),F)
  # Clear the projecting retention bead behind the receiver, including any
  # pre-existing thick solid material in the fixed body (tongue).
  relief=box((-cfg['width']/2-.6,-cfg['thickness']/2-.5,-cfg['length']-.7),(cfg['width']/2+.6,cfg['thickness']/2+.5,-cfg['length']+2.4))
  hostsolid=hostsolid-xf(relief,F)
  interfaces.append({'part':name,'host':host,'frame':F.tolist(),'clip':'detail','deflection_per_prong_mm':.2,'free_length_mm':cfg['length']-3.5})
 dc=mesh(original_detail).bounds.mean(axis=0);expanded=original_detail.scale((1.015,1.015,1.015)).translate(dc*(1-1.015))
 hostsolid=hostsolid-(original_detail+expanded)
 if host=='head':head=hostsolid
 else:body=hostsolid
 print('Detail',name,'solid',solid.status(),'host',hostsolid.status(),flush=True)
 details.append((name,solid,mats[0],'pink' if host=='body' else 'black'))
for m in components:
 c=m.center_mass;s=frommesh(m)
 if c[1]>-10:
  name='BLACK_crest';anchors=[]
  for ang in [5,55]:
   a=math.radians(ang);p=np.array([0,56*math.sin(a),hc+57*math.cos(a)]);n=np.array([0,math.sin(a),math.cos(a)]);anchors.append((p,n))
 elif c[2]>hc+35:
  sign=1 if c[0]>0 else -1;name='BLACK_brow_'+('right' if sign>0 else 'left');anchors=[surface(sign*26,hc+43.8)]
 elif c[2]<hc+12:
  name='BLACK_smile';anchors=[]
  for x in [-20,0,20]:anchors.append(surface(x,headz+3.4+7*(x/28)**2))
 else:
  sign=1 if c[0]>0 else -1;name='BLACK_eye_'+('right' if sign>0 else 'left');p,n=surface(sign*28,hc+25);F=frame(p,n);anchors=[(p+F[:,1]*off,n) for off in [-6,6]]
 add_detail(name,s,anchors)
add_detail('PINK_tongue',tongue,[(np.array([0,-54.8,seam-3.7]),np.array([0,-1,0]))],'body')
# Keyed snap-on head: body pins point up into bosses inside the complete head.
# Unequal angular spacing permits only one face orientation.
cfg=P['closure_clip'];closure_parts=[]
for angle in [0,130,230]:
 a=math.radians(angle);rad=np.array([math.cos(a),math.sin(a),0]);tangent=np.array([-math.sin(a),math.cos(a),0])
 p=rad*49.5+np.array([0,0,seam]);F=frame(p,[0,0,-1],tangent)
 support=box((-4,-4,-.15),(4,5.8,2.4))
 # local v points inward for n=-Z and the chosen tangent; extend both sides.
 bearing=box((-3,4.3,-.6),(3,5.5,.1))
 body=body+xf(support,F)+xf(bearing,F)+xf(snap(cfg),F)
 receiver=box((-3.8,-5.0,-cfg['length']+2.4),(3.8,5.0,-.7))
 head=(head+xf(receiver,F))-xf(socket(cfg,top=2),F)
 relief=box((-3,-2.2,-14),(3,2.2,-10.6));head=head-xf(relief,F)
 interfaces.append({'part':'RED_body','host':'RED_head','frame':F.tolist(),'clip':'closure','angle_degrees':angle,'deflection_per_prong_mm':.2,'free_length_mm':9.5})
print('After head clips',body.status(),head.status(),flush=True)
# Base pins point up into the added red housing. This leaves the source untouched.
for angle in [45,170,285]:
 a=math.radians(angle);rad=np.array([math.cos(a),math.sin(a),0]);tangent=np.array([-math.sin(a),math.cos(a),0]);p=rad*38+np.array([0,0,4.5]);F=frame(p,[0,0,-1],tangent)
 bearing=box((-2.5,2.0,-.4),(2.5,3.5,.1))
 base=base+xf(snap(cfg),F)+xf(bearing,F)
 body=(body+xf(boss(cfg,top=-.45),F))-xf(socket(cfg,top=2),F)
 body=body-xf(box((-3,-2.2,-14),(3,2.2,-10.6)),F)
 interfaces.append({'part':'BLACK_feet_base','host':'RED_body','frame':F.tolist(),'clip':'closure','angle_degrees':angle,'deflection_per_prong_mm':.2,'free_length_mm':9.5})
print('After base clips',body.status(),base.status(),flush=True)
head=head^(M.sphere(1,128).scale((56,56,57)).translate((0,0,hc))^box((-100,-100,headz),(100,100,160)))
parts={'RED_body':body,'RED_head':head,'BLACK_feet_base':base}
for n,s,F,c in details:parts[n]=s
print('Checking exported solids and seated snap interfaces...',flush=True)
report={'source_original_file_unchanged':True,'closure_type':'removable keyed snap-on head and base; no screw threads','before_body_solid_volume_mm3':original_body_volume,'after_body_solid_volume_mm3':body.volume(),'body_CAD_volume_reduction_percent':100*(1-body.volume()/original_body_volume),'parts':{},'interfaces':interfaces,'seated_collisions':{},'physical_testing':'Required: clip coupons first, then cup/jar fit and repeated opening.'}
report['body_strategy']=P['body_strategy']
meshes={};manifest=[];plate_meshes={}
for n,s in parts.items():
 m=mesh(s);m.export(A/(n+'.stl'));check=trimesh.load_mesh(A/(n+'.stl'))
 report['parts'][n]={'watertight':bool(check.is_watertight),'components':len(s.decompose()),'volume_mm3':float(m.volume),'triangles':len(m.faces)}
 meshes[n]=m
 color='red' if n.startswith('RED') else ('pink' if n.startswith('PINK') else 'black')
 manifest.append({'name':n,'path':'ASSEMBLY/'+n+'.stl','color':color,'group':'head' if n=='RED_head' or n.startswith(('BLACK_eye','BLACK_brow','BLACK_smile','BLACK_crest')) else ('bottom' if n=='BLACK_feet_base' else 'body')})
 if n in ['RED_body','RED_head','BLACK_feet_base']:
  pm=m.copy()
 else:
  F=next(f for name,_,f,_ in details if name==n);rot=F[:,:3];pm=m.copy();pm.vertices=(pm.vertices-F[:,3])@rot
  # Horizontal snap stems: long axis follows X on the bed, bending along Y.
  # Preserve curved approved details; small tree supports are allowed underneath.
  pm.vertices=pm.vertices[:,[2,1,0]]*[-1,1,1] if n=='BLACK_crest' else pm.vertices[:,[2,0,1]]*[-1,1,1]
 pm.apply_translation(-pm.bounds[0]);pm.export(S/(n+'.stl'));plate_meshes[n]=pm
for n,s,_,_ in details:
 host=head if n.startswith('BLACK') else body
 report['seated_collisions'][n]=float((s^host).volume())
report['seated_collisions']['head_body']=float((head^body).volume())
report['seated_collisions']['base_body']=float((base^body).volume())
report['cup_guard_overlap_mm3']=float((body^cyl(22.39,40.8,93.923)).volume())
report['all_new_parts_watertight']=all(x['watertight'] for x in report['parts'].values())
report['all_new_parts_single_solid']=all(x['components']==1 for x in report['parts'].values())
(O/'geometry_checks.json').write_text(json.dumps(report,indent=2))
(O/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['parts','interfaces']},indent=2),flush=True)
# Exact sleeve raw triangle copy; translated only as an assembly component.
source=Path(P['source_stl']);source=source if source.is_absolute() else R/source
shutil.copyfile(source,O/'REFERENCE'/'ORIGINAL_sleeve_UNCHANGED.stl')
raw=source.read_bytes();count=struct.unpack_from('<I',raw,80)[0];dt=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]);vs=np.frombuffer(raw,dt,count,84)['v'].reshape(-1,3).astype(float)+shift
# 3MF requires shared vertex indices for connected triangles. Weld EXACT duplicate
# coordinates only: retain every original triangle and move no source vertex.
unique_vs,indices=np.unique(vs,axis=0,return_inverse=True)
core=trimesh.Trimesh(unique_vs,indices.reshape(-1,3),process=False);core.export(A/'ORIGINAL_core_aligned.stl')
# Color-independent fit coupons for both the small detail and main closure snap.
for size in ['detail','closure']:
 cfg=P[size+'_clip'];L=cfg['length'];test=snap(cfg)+box((-5,-4,.2),(5,4,2.6))
 # Upright male coupon replicates the structural clip layer orientation.
 tm=mesh(test.rotate((180,0,0)));tm.apply_translation(-tm.bounds[0]);tm.export(T/(size+'_pin.stl'))
 for i,clear in enumerate([.15,.20,.25]):
  rec=boss(cfg,top=-1.0)-socket(cfg,top=2,clearance=clear)
  for dot in range(i+1):rec=rec-sphere(((dot-i/2)*1.25,-cfg['thickness']/2-1.05,-L+2.35),(.45,.45,.45))
  # Flat-footed open-ended receiver, print upright like closure receivers.
  rm=mesh(rec.rotate((180,0,0)));rm.apply_translation(-rm.bounds[0]);rm.export(T/(size+'_socket_'+str(i+1)+'.stl'))
# Generic 3MF exporter; Bambu CLI will configure and slice these input projects.
def write3mf(path,objects):
 ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';E.register_namespace('',ns)
 def el(p,t,a={}):return E.SubElement(p,'{'+ns+'}'+t,a)
 root=E.Element('{'+ns+'}model',{'unit':'millimeter'});res=el(root,'resources');build=el(root,'build')
 nextid=1
 for name,submeshes in objects:
  children=[]
  for subname,m in submeshes:
   oid=nextid;nextid+=1;children.append(oid);obj=el(res,'object',{'id':str(oid),'name':subname,'type':'model'});me=el(obj,'mesh');ve=el(me,'vertices');fa=el(me,'triangles')
   for v in m.vertices:el(ve,'vertex',{k:repr(float(x)) for k,x in zip('xyz',v)})
   for f in m.faces:el(fa,'triangle',{k:str(x) for k,x in zip(['v1','v2','v3'],f)})
  groupid=nextid;nextid+=1;ob=el(res,'object',{'id':str(groupid),'name':name,'type':'model'});co=el(ob,'components')
  for oid in children:el(co,'component',{'objectid':str(oid)})
  el(build,'item',{'objectid':str(groupid)})
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
  z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
  z.writestr('3D/3dmodel.model',E.tostring(root,encoding='utf-8',xml_declaration=True))
bodyprint=meshes['RED_body'].copy();coreprint=core.copy();delta=-bodyprint.bounds[0];bodyprint.apply_translation(delta);coreprint.apply_translation(delta)
write3mf(S/'RED_body_with_original_core.3mf',[('Body with preserved original sleeve',[('red exterior',bodyprint),('original sleeve',coreprint)])])
write3mf(O/'REFERENCE'/'assembly_review.3mf',[(n,[(n,m)]) for n,m in meshes.items()]+[('Original sleeve',[('source core',core)])])
print('Snap geometry and fit-test coupons exported.',flush=True)
