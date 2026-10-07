"""Show the original fin seated on the unchanged torso; color is a guide."""
from pathlib import Path
import sys,numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'blender_runtime'))
import bpy
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.name='Fin location on original torso';s.unit_settings.system='METRIC';s.unit_settings.scale_length=.001;s.unit_settings.length_unit='MILLIMETERS';s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.show_shadows=True;s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('World');s.world.color=(.06,.07,.08)
s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
for name,color in [('Torso',(.43,.46,.48,1)),('Dorsal_fin',(1,.18,.05,1))]:
 a=np.load(ROOT.parent/'king_shark_v2/final_parts'/(name+'.npz'));me=bpy.data.meshes.new(name);me.from_pydata(a['vertices'].tolist(),[],a['faces'].tolist());me.update();mat=bpy.data.materials.new(name+' material');mat.diffuse_color=color;me.materials.append(mat);o=bpy.data.objects.new(name,me);s.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.shade_smooth_by_angle(angle=.65);o.select_set(False)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.clip_end=2000
target=Vector((0,50,380))
for name,loc,scale in [('fin_on_upper_back.png',(180,580,500),290),('fin_from_side.png',(500,200,460),290)]:
 cam.location=loc;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(ROOT/name);bpy.ops.render.render(write_still=True)
