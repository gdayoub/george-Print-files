from pathlib import Path
import sys,json,numpy as np
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT.parents[1]/'blender_runtime'))
import bpy
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.name='King_Shark_Catchall_Bowl';s.unit_settings.system='METRIC';s.unit_settings.scale_length=.001;s.unit_settings.length_unit='MILLIMETERS';s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.curvature_ridge_factor=1.4;s.display.shading.curvature_valley_factor=1.1;s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('World');s.world.color=(.035,.045,.055);s.view_settings.view_transform='Standard';s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.display.shading.show_shadows=True
m=bpy.data.materials.new('Single gray filament');m.diffuse_color=(.42,.45,.47,1)
d=np.load(ROOT/'King_Shark_Catchall_Bowl.npz');v=d['vertices'];f=d['faces'];me=bpy.data.meshes.new('Printable one-solid bowl');me.from_pydata(v.tolist(),[],f.tolist());me.materials.append(m);me.update();o=bpy.data.objects.new('King_Shark_Catchall_Bowl',me);s.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.shade_smooth_by_angle(angle=.65)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.clip_end=2000
for name,loc,target,scale in [('three_quarter',(205,-320,240),(0,-12,29),204),('front',(0,-400,135),(0,-17,28),186),('inside',(0,-210,350),(0,-10,23),195),('side',(320,-10,160),(0,-10,27),190)]:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(ROOT/(name+'.png'));bpy.ops.render.render(write_still=True)
cam.location=(205,-320,240);cam.rotation_euler=(Vector((0,-12,29))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=204
bpy.data.texts.new('Design_notes').write('Single-colour King Shark catchall bowl, actual sculpted face taken from successful 47cm printed torso; planar stable bottom; smooth elliptical inside; 2.6mm liner normal wall and 2.8mm floor. Intended for keys/accessories. Not sliced or physically tested yet. Source and engineering report accompany this Blender file. Units mm.')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'King_Shark_Catchall_Bowl.blend'))
