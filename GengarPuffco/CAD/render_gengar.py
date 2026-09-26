from pathlib import Path
import json,math,sys
import numpy as np
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parent.parent;O=R/'CAD/outputs';P=R/'Previews';P.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
def material(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True
 rgb=tuple((int(color.lstrip('#')[i:i+2],16)/255)**2.2 for i in (0,2,4))
 m.diffuse_color=(*rgb,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=.45;return m
manifest=json.loads((O/'manifest.json').read_text());objects=[]
for e in manifest:
 a=np.load(O/e['file']);me=bpy.data.meshes.new(e['name']);me.from_pydata(a['vertices'].tolist(),[],a['faces'].tolist());me.update()
 ob=bpy.data.objects.new(e['name'],me);bpy.context.collection.objects.link(ob);ob.data.materials.append(material(e['name'],e['color']));ob['assembly']=e['group'];objects.append(ob)
 for p in me.polygons:p.use_smooth=not e['name'].startswith('ORIGINAL') and abs(p.normal.z)<.98
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=1100;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.18,.22,1)
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.12));plane=bpy.context.object;plane.name='STUDIO_NOT_FOR_PRINT';plane.data.materials.append(material('backdrop','#C4CBD7'))
for pos,power,size in [((-150,-180,250),400000,170),((160,-50,160),200000,130),((0,160,210),500000,120)]:
 bpy.ops.object.light_add(type='AREA',location=pos);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;aim(l,(0,0,65))
bpy.ops.object.camera_add(location=(170,-280,155));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=175;aim(cam,(0,0,65));s.camera=cam
s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'CAD/Gengar_Compact_EDITABLE.blend'))
def render(name,location,target,scale):
 if '--comparison-only' in sys.argv and name!='06_size_comparison.png':return
 if '--only' in sys.argv and name!=sys.argv[sys.argv.index('--only')+1]:return
 cam.location=location;aim(cam,target);cam.data.ortho_scale=scale;s.render.filepath=str(P/name);bpy.ops.render.render(write_still=True)
render('01_assembled.png',(145,-280,145),(0,0,61),160)
render('02_front.png',(0,-300,62),(0,0,61),150)
for ob in objects:
 if ob['assembly']=='head':ob.location.x=75;ob.location.z=40
render('03_head_removed.png',(170,-320,180),(30,0,70),220)
for ob in objects:
 if ob['assembly']=='head':ob.location=(0,0,0)
 if ob['assembly']=='bottom':ob.location.z=-30
plane.location.z=-30.2
render('04_bottom_open.png',(155,-280,70),(0,0,46),190)

# Both designs at the same real-world scale, standing on the same plane.
plane.location.z=-.12;plane.hide_render=True
for ob in objects:ob.location=(44,0,0)
for name in ['ORIGINAL_CASE_BASE_EXACT','ORIGINAL_CASE_LID_EXACT']:
 source=bpy.data.objects[name];ob=source.copy();ob.data=source.data.copy();bpy.context.collection.objects.link(ob)
 ob.name='COMPARISON_'+name;ob.location=(-44,0,-14);ob.data.materials.clear();ob.data.materials.append(material('Foundation reference','#8B9CAB'))
def label(text,x):
 cu=bpy.data.curves.new('Dimension label','FONT');cu.body=text;cu.align_x='CENTER';cu.size=3.7;cu.space_line=1.3
 ob=bpy.data.objects.new('Dimension label',cu);bpy.context.collection.objects.link(ob);ob.location=(x,-37,-8);ob.rotation_euler=(math.pi/2,0,0);cu.materials.append(material('Label ink','#14202E'))
label('ORIGINAL CASE\n57.4 x 57.4 x 96 mm',-44)
dimensions=json.loads((R/'Reports/geometry_validation.json').read_text())['assembled_size_mm']
label('GENGAR BOWL V4\n'+' x '.join(f'{x:.1f}' for x in dimensions)+' mm',44)
s.render.resolution_x=1550;s.render.resolution_y=1050
render('06_size_comparison.png',(0,-320,70),(0,0,55),225)
