from pathlib import Path
import sys,json,numpy as np,argparse
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT.parent/'blender_runtime'))
import bpy
from mathutils import Vector,Matrix
ap=argparse.ArgumentParser();ap.add_argument('product',choices=['king_shark','venom']);args=ap.parse_args();base=ROOT/args.product;src=base/'final_parts';rows=json.loads((src/'manifest.json').read_text());layout=json.loads((base/'layout.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
s=bpy.context.scene;s.name=args.product.title()+'_Shelf_Assembly';s.unit_settings.system='METRIC';s.unit_settings.scale_length=.001;s.unit_settings.length_unit='MILLIMETERS';s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.curvature_ridge_factor=1.15;s.display.shading.curvature_valley_factor=1.05;s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('World');s.world.color=(.045,.055,.065);s.view_settings.view_transform='Standard';s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.display.shading.show_shadows=True
colors={'Black':(.42,.45,.47,1) if args.product=='king_shark' else (.07,.08,.10,1),'White':(.90,.89,.83,1),'Red':(.65,.028,.045,1)};mats={}
for name,col in colors.items():
 m=bpy.data.materials.new(name);m.diffuse_color=col;mats[name]=m
objects={}
for row in rows:
 d=np.load(src/(row['name']+'.npz'));v=d['vertices'];f=d['faces'];me=bpy.data.meshes.new(row['name']);me.from_pydata(v.tolist(),[],f.tolist());me.materials.append(mats[row['color']]);me.update();o=bpy.data.objects.new(row['name'],me);s.collection.objects.link(o);bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.shade_smooth_by_angle(angle=.65);objects[row['name']]=o
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.clip_end=2000

def render(scene,cam,name,loc,target,scale):
 bpy.context.window.scene=scene;cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;scene.render.filepath=str(base/(name+'.png'));bpy.ops.render.render(write_still=True)
render(s,cam,'preview',(230,-420,250),(0,-17,77),205)
render(s,cam,'front',(0,-500,150),(0,-15,78),187)
render(s,cam,'back',(0,400,122),(0,0,78),184)
render(s,cam,'side',(400,-10,150),(0,-24,78),183)
# Separate editable exploded scene with independent object transforms.
ex=s.copy();ex.name='Exploded_Assembly';ex.use_fake_user=True
for old in list(ex.objects):
 ex.collection.objects.unlink(old)
 if old.type=='MESH':
  ob=old.copy();ex.collection.objects.link(ob)
  if ob.name.startswith('Tray'):ob.location=(0,-27,24)
  elif old.name.startswith('Eye'):ob.location=(0,-26,6)
  elif old.name=='Chest_Emblem':ob.location=(0,-32,0)
ec=cam.copy();ec.data=cam.data.copy();ex.collection.objects.link(ec);ex.camera=ec
render(ex,ec,'exploded',(230,-450,275),(0,-29,80),220)
# Bed scenes use exactly the supplied rigid layout orientations and locations.
matbed=bpy.data.materials.new('256mm build plate');matbed.diffuse_color=(.20,.22,.25,1)
for pi,p in enumerate(layout['plates'],1):
 sc=s.copy();sc.name=f'Plate_{pi:02}';sc.use_fake_user=True
 for old in list(sc.objects):sc.collection.objects.unlink(old)
 pc=cam.copy();pc.data=cam.data.copy();sc.collection.objects.link(pc);sc.camera=pc
 me=bpy.data.meshes.new('256mm bed');me.from_pydata([(0,0,-.25),(256,0,-.25),(256,256,-.25),(0,256,-.25)],[],[(0,1,2,3)]);me.materials.append(matbed);bd=bpy.data.objects.new('Build_plate_256mm',me);sc.collection.objects.link(bd)
 for inst in p['instances']:
  ob=objects[inst['name']].copy();sc.collection.objects.link(ob);R=np.array(inst['rotation']);v=np.array([v.co[:] for v in ob.data.vertices]);low=(v@R.T).min(0);T=np.eye(4);T[:3,:3]=R;T[:3,3]=np.r_[inst['xy_mm'],0]-low;ob.matrix_world=Matrix(T.tolist())
 render(sc,pc,f'plate_{pi}',(450,-450,530),(128,128,20),395)
bpy.context.window.scene=s;cam.location=(230,-420,250);cam.rotation_euler=(Vector((0,-17,77))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=205
bpy.data.texts.new('Design_notes').write('Actual printable character shelf prototype. All solids use millimetres. Separate tray and colour inserts assemble in the shown coordinates. Back is planar at Y=0, facing front toward -Y. Shelf mounting is not load-rated; see engineering and mounting notes with the model. Geometry from the current source NPZ manifests; this Blender file is a preview/editable geometry copy, not evidence of physical tests. Plate scenes follow the current provided layouts.')
bpy.ops.wm.save_as_mainfile(filepath=str(base/(args.product.title()+'_Shelf.blend')))
(base/'render_validation.json').write_text(json.dumps(dict(product=args.product,source_manifest=str(src/'manifest.json'),actual_geometry_render=True,scenes=[sc.name for sc in bpy.data.scenes],part_names=list(objects),renders=['preview.png','front.png','back.png','side.png','exploded.png']+[f'plate_{i}.png' for i in range(1,len(layout['plates'])+1)]),indent=2))
