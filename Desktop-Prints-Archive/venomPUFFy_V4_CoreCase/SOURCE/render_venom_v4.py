"""Render the exported CAD meshes, never an image-generated concept."""
from pathlib import Path
import bpy,json,math,bmesh,sys
from mathutils import Vector
ROOT=Path(__file__).parent;OUT=ROOT/'outputs';PRE=OUT/'previews';PRE.mkdir(exist_ok=True)
manifest=json.loads((OUT/'geometry_manifest.json').read_text())
ONLY=set(sys.argv[sys.argv.index('--')+1:]) if '--' in sys.argv else set()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.name='Venom V4 - Original Core Case'
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=900;scene.render.resolution_y=1050;scene.render.resolution_percentage=100
scene.world.color=(.35,.35,.35);scene.view_settings.view_transform='AgX'
def material(name,h):
 c=[int(h[i:i+2],16)/255 for i in (1,3,5)];c=[v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in c]
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=.32
 return m
mats={h:material(h,h) for h in set(e['color'] for e in manifest)};models=[]
for e in manifest:
 bpy.ops.wm.stl_import(filepath=str(OUT/e['path']));o=bpy.context.object;o.name=e['name'];o.data.materials.append(mats[e['color']]);o['assembly']=e['group']
 o['status']='Original complete Core Case base and lid retained at scale 1. Physical fit unverified.'
 for p in o.data.polygons:p.use_smooth=True
 o.data.set_sharp_from_angle(angle=math.radians(35))
 models.append(o)
 if e['group']=='jar':o.hide_render=True;o.hide_set(True)
def area(name,loc,power,size):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc
 o.rotation_euler=(Vector((0,0,85))-o.location).to_track_quat('-Z','Y').to_euler()
area('Key',(-150,-220,280),2300000,180);area('Fill',(190,-140,200),1600000,150);area('Rim',(40,130,250),2400000,140)
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.2));ground=bpy.context.object;ground.name='STUDIO not printable';ground.data.materials.append(material('Backdrop','#D3D7DF'))
d=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',d);scene.collection.objects.link(cam);scene.camera=cam;d.type='ORTHO'
def camera(loc,target=(0,0,88),scale=208):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale
def render(name):
 if ONLY and name not in ONLY:return
 scene.render.filepath=str(PRE/(name+'.png'));bpy.ops.render.render(write_still=True)
for f in ['build_venom_v4.py','parameters.json']:
 t=bpy.data.texts.new(f);t.write((ROOT/f).read_text())
camera((220,-400,205));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Venom_Core_Case_V4_EDITABLE.blend'))
render('00_assembled_perspective')
camera((0,-400,88));render('01_front')
camera((400,0,88));render('02_side')
camera((0,400,88));render('03_back')
for o in models:
 if o['assembly']=='head':o.location.z=60
camera((230,-400,245),(0,0,115),270);render('04_head_removed')
for o in models:
 if o['assembly']=='head':o.location.z=0
 if o['assembly'] in ['bottom','jar']:o.location.z=-52
 if o['assembly']=='jar':o.hide_render=False;o.hide_set(False)
ground.location.z=-52.2
camera((210,-400,195),(0,0,63),265);render('05_bottom_open')
for o in models:
 o.location.z=0;o.hide_render=o['assembly']!='head'
ground.hide_render=True
area('Socket fill',(0,-140,35),650000,100)
camera((140,-250,35),(0,0,120),165);render('07_head_underside')
bpy.data.objects['Socket fill'].hide_render=True
for o in models:o.hide_render=False
ground.hide_render=False
# Cut exported meshes exactly at X=0, preserving their actual modeled cavities.
for o in models:
 o.location.z=0;o.data=o.data.copy();bm=bmesh.new();bm.from_mesh(o.data)
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=(0,0,0),plane_no=(1,0,0),clear_outer=True,clear_inner=False)
 if not o.name.startswith('ORIGINAL_CASE'):
  edges=[e for e in bm.edges if e.is_boundary and all(abs(v.co.x)<.001 for v in e.verts)]
  if edges:bmesh.ops.holes_fill(bm,edges=edges,sides=0)
 bm.to_mesh(o.data);bm.free()
 for p in o.data.polygons:
  if all(abs(o.data.vertices[i].co.x)<.001 for i in p.vertices):p.use_smooth=False
ground.location.z=-.2
camera((400,-90,130),(0,0,86),210);render('06_section')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Venom_V4_SECTION_REFERENCE.blend'))

