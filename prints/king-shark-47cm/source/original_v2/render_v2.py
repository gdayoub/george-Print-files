"""Render only real mesh geometry; never substitute the approved concept image."""
from pathlib import Path
import argparse, json, sys
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'blender_runtime'))
import bpy
from mathutils import Vector,Matrix

ap=argparse.ArgumentParser();ap.add_argument('--source',default='final_parts');ap.add_argument('--out',default='renders');ap.add_argument('--save',action='store_true');args=ap.parse_args()
src=ROOT/args.source;out=ROOT/args.out;out.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
rows=json.loads((src/'manifest.json').read_text()) if (src/'manifest.json').exists() else [dict(name=p.stem,color='Red' if p.stem=='Shorts' else 'Black') for p in src.glob('*.npz')]
colors={'Black':(.18,.20,.22,1),'Red':(.58,.025,.035,1),'White':(.92,.88,.79,1)};mats={}
for name,c in colors.items():
    m=bpy.data.materials.new(name);m.diffuse_color=c;mats[name]=m
s=bpy.context.scene;s.name='King_Shark_realistic_470mm_assembly';s.unit_settings.system='METRIC';s.unit_settings.scale_length=.001;s.unit_settings.length_unit='MILLIMETERS'
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_cavity=True;s.display.shading.cavity_type='WORLD';s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('World');s.world.color=(.045,.055,.07);s.view_settings.view_transform='Standard';s.render.resolution_x=1300;s.render.resolution_y=1300;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.clip_end=10000
objects={}
for row in rows:
    a=np.load(src/(row['name']+'.npz'));v=a['vertices'];f=a['faces'];m=bpy.data.meshes.new(row['name'])
    m.vertices.add(len(v));m.vertices.foreach_set('co',v.astype(np.float32).ravel());m.loops.add(len(f)*3);m.loops.foreach_set('vertex_index',f.astype(np.int32).ravel());m.polygons.add(len(f));m.polygons.foreach_set('loop_start',np.arange(len(f),dtype=np.int32)*3);m.polygons.foreach_set('loop_total',np.full(len(f),3,dtype=np.int32));m.polygons.foreach_set('use_smooth',np.ones(len(f),dtype=bool));m.materials.append(mats[row['color']]);m.update()
    obj=bpy.data.objects.new(row['name'],m);s.collection.objects.link(obj);objects[row['name']]=obj
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.shade_smooth_by_angle(angle=.65)

def render(loc,target,scale,name,scene=s,camera=cam):
    bpy.context.window.scene=scene;camera.location=loc;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale;scene.render.filepath=str(out/name);bpy.ops.render.render(write_still=True)
render((620,-1400,520),(0,0,237),545,'three_quarter.png')
render((0,-1500,280),(0,0,237),520,'front.png')
render((750,1300,470),(0,0,237),550,'back.png')
render((1400,0,370),(0,0,237),540,'side.png')
render((530,-1200,620),(0,-35,373),177,'head_detail.png')

lp=ROOT/'layout.json'
if args.save and lp.exists():
    layout=json.loads(lp.read_text());bedmat=bpy.data.materials.new('Textured PEI plate');bedmat.diffuse_color=(.20,.23,.27,1)
    for pi,p in enumerate(layout['plates'],1):
        scene=s.copy();scene.name=f'Plate_{pi:02}_{p["label"]}';scene.use_fake_user=True
        for o in list(scene.objects):scene.collection.objects.unlink(o)
        pc=cam.copy();pc.data=cam.data.copy();scene.collection.objects.link(pc);scene.camera=pc
        m=bpy.data.meshes.new('256mm bed');m.from_pydata([(0,0,-.4),(256,0,-.4),(256,256,-.4),(0,256,-.4)],[],[(0,1,2,3)]);m.materials.append(bedmat);bo=bpy.data.objects.new('256mm bed',m);scene.collection.objects.link(bo)
        for inst in p['instances']:
            ob=objects[inst['name']].copy();scene.collection.objects.link(ob)
            if 'transform' in inst:T=np.array(inst['transform'])
            else:
                R=np.array(inst['rotation']);v=np.array([v.co[:] for v in ob.data.vertices])@R.T;low=v.min(0);T=np.eye(4);T[:3,:3]=R;T[:3,3]=np.r_[inst['xy_mm'],0]-low
            ob.matrix_world=Matrix(T.tolist())
        render((430,-460,530),(128,128,85),440,f'plate_{pi}.png',scene,pc)
    ex=s.copy();ex.name='Exploded_glue_assembly';ex.use_fake_user=True;offsets={'Torso':(0,0,65),'L_arm':(70,0,35),'R_arm':(-70,0,35),'Dorsal_fin':(0,45,105),'Shorts':(0,0,0),'L_leg':(10,0,-45),'R_leg':(-10,0,-45),'Upper_teeth':(0,-90,70),'Lower_teeth':(0,-90,50),'Shorts_panel_L':(55,0,0),'Shorts_panel_R':(-55,0,0)}
    for old in list(ex.objects):
        if old.type=='MESH':
            ob=old.copy();ex.collection.objects.link(ob);ex.collection.objects.unlink(old);ob.location=Vector(offsets.get(old.name,(0,0,0)))
    ec=cam.copy();ec.data=cam.data.copy();ex.collection.objects.link(ec);ex.camera=ec
    render((650,-1450,680),(0,0,270),780,'exploded_assembly.png',ex,ec)
if args.save:
    bpy.context.window.scene=s
    bpy.data.texts.new('MODEL_NOTES').write('Realistic King Shark fan statue. Generated from the user-approved image using Microsoft TRELLIS.2, then repaired and engineered for printing. Units mm. This file contains actual printable solids, not the source image or texture. Body black/charcoal, shorts red with black inlays, white connected shark teeth; no AMS. Whole arms/hands and whole lower legs. Proven Venom tapered asymmetric glue key, nominal .18mm radial root clearance. Dental clearance .20mm; insert lower dental arch before upper. Use P1S/P2S 3MF for lightweight wall/infill settings and optimized orientations. Fine painted skin coloration from the concept is not geometry. Digital checks do not constitute a physical print test. Raw source GLB and validation reports accompany the project.')
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'King_Shark_realistic_47cm.blend'))
