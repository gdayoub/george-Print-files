from pathlib import Path
import json,sys,numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'blender_runtime'))
import bpy
from mathutils import Vector,Matrix
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version=0
s=bpy.context.scene;s.name='Original King Shark statue fin';s.unit_settings.system='METRIC';s.unit_settings.scale_length=.001;s.unit_settings.length_unit='MILLIMETERS'
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.show_shadows=True;s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('World');s.world.color=(.07,.08,.10)
s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
mat=bpy.data.materials.new('Gray charcoal PLA');mat.diffuse_color=(.42,.45,.47,1)
a=np.load(ROOT.parent/'king_shark_v2/final_parts/Dorsal_fin.npz');v=a['vertices'];f=a['faces'];me=bpy.data.meshes.new('Dorsal_fin original 47cm');me.from_pydata(v.tolist(),[],f.tolist());me.materials.append(mat);me.update();o=bpy.data.objects.new('Dorsal_fin',me);s.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.shade_smooth_by_angle(angle=.65)
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.clip_end=2000
target=Vector(tuple(v.mean(0)))
def render(name,loc,scale):
 cam.location=loc;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(ROOT/name);bpy.ops.render.render(write_still=True)
render('fin_preview.png',(130,-135,520),110)
render('fin_socket_view.png',(40,-70,320),110)
layout=json.loads((ROOT/'layout.json').read_text());inst=layout['plates'][0]['instances'][0];R=np.array(inst['rotation']);pv=v@R.T;T=np.eye(4);T[:3,:3]=R;T[:3,3]=np.r_[inst['xy_mm'],0]-pv.min(0)
plate=s.copy();plate.name='P1S_P2S_Fin_Plate';plate.use_fake_user=True
for old in list(plate.objects):plate.collection.objects.unlink(old)
ob=o.copy();plate.collection.objects.link(ob);ob.matrix_world=Matrix(T.tolist())
pc=cam.copy();pc.data=cam.data.copy();plate.collection.objects.link(pc);plate.camera=pc
mebed=bpy.data.meshes.new('256mm bed');mebed.from_pydata([(0,0,-.1),(256,0,-.1),(256,256,-.1),(0,256,-.1)],[],[(0,1,2,3)]);bd=bpy.data.objects.new('Build_plate_256mm',mebed);plate.collection.objects.link(bd)
bpy.context.window.scene=plate;pc.location=(370,-350,440);pc.rotation_euler=(Vector((128,128,0))-pc.location).to_track_quat('-Z','Y').to_euler();pc.data.ortho_scale=380;plate.render.filepath=str(ROOT/'fin_plate.png');bpy.ops.render.render(write_still=True)
bpy.context.window.scene=s
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'King_Shark_Original_Dorsal_Fin.blend'))
(ROOT/'render_validation.json').write_text(json.dumps(dict(actual_source_geometry=True,source_part='Dorsal_fin.npz',images=['fin_preview.png','fin_socket_view.png','fin_plate.png'],scenes=[scene.name for scene in bpy.data.scenes]),indent=2))
