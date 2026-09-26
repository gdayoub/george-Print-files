from pathlib import Path
import bpy,json,bmesh,math,struct
from mathutils import Vector
R=Path(__file__).parent;O=R/'outputs'/'snap_print_kit';PRE=O/'REFERENCE';PRE.mkdir(exist_ok=True)
items=json.loads((O/'manifest.json').read_text());checks=json.loads((O/'geometry_checks.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1200;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.world.color=(.4,.4,.4);scene.view_settings.view_transform='AgX'
def mat(name,col):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
 n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*col,1);n.inputs['Roughness'].default_value=.36;return m
mats={'red':mat('Soyelin red',(.69,.0116,.022)),'black':mat('Creality black',(.012,.013,.017)),'pink':mat('Pink accent',(.98,.26,.36))}
gray=mat('Unchanged core (section highlight)',(.25,.37,.44));stage_mat=mat('Backdrop',(.73,.75,.77))
obs={}
for e in items:
 bpy.ops.wm.stl_import(filepath=str(O/e['path']));ob=bpy.context.object;ob.name=e['name'];ob.data.materials.append(mats[e['color']]);ob['assembly']=e['group']
 for f in ob.data.polygons:f.use_smooth=True
 if e['name']=='RED_head':
  # Analytic normals on the unchanged outer dome avoid Boolean-triangulation
  # shading marks. Geometry and printable exports are untouched by this step.
  normals=[tuple(n.vector) for n in ob.data.corner_normals];center_z=78.72204647064208
  for face in ob.data.polygons:
   points=[ob.data.vertices[v].co for v in face.vertices]
   rho=[(v.x/56)**2+(v.y/56)**2+((v.z-center_z)/57)**2 for v in points]
   c=face.center;out=Vector((c.x/56**2,c.y/56**2,(c.z-center_z)/57**2)).normalized()
   if min(rho)>.997 and max(rho)<1.003 and face.normal.dot(out)>.85:
    for li in face.loop_indices:
     v=ob.data.vertices[ob.data.loops[li].vertex_index].co;normals[li]=tuple(Vector((v.x/56**2,v.y/56**2,(v.z-center_z)/57**2)).normalized())
  ob.data.normals_split_custom_set(normals)
 obs[e['name']]=ob
# Core vertices are loaded directly, retaining the source triangle ordering.
raw=(O/'REFERENCE'/'ORIGINAL_sleeve_UNCHANGED.stl').read_bytes();count=struct.unpack_from('<I',raw,80)[0];verts=[]
for i in range(count):verts.extend(struct.unpack_from('<3f',raw,84+i*50+12+j*12) for j in range(3))
me=bpy.data.meshes.new('Exact source triangles');me.from_pydata(verts,[],[(3*i,3*i+1,3*i+2) for i in range(count)]);me.update()
core=bpy.data.objects.new('ORIGINAL sleeve — unchanged',me);scene.collection.objects.link(core);core.location=json.loads((R/'snap_parameters.json').read_text())['source_translation_mm'];core.data.materials.append(mats['red'])
def light(name,loc,power,size):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,70))-o.location).to_track_quat('-Z','Y').to_euler()
light('Key',(-150,-180,260),850000,190);light('Fill',(180,-50,140),500000,160);light('Rim',(60,160,230),1000000,130)
bpy.ops.mesh.primitive_plane_add(size=20000,location=(0,0,-.2));stage=bpy.context.object;stage.name='Studio only';stage.data.materials.append(stage_mat)
d=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',d);scene.collection.objects.link(cam);scene.camera=cam;d.type='ORTHO';d.clip_end=100000
def camera(loc,target,scale):cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale
def render(name):scene.render.filepath=str(PRE/(name+'.png'));bpy.ops.render.render(write_still=True)
camera((205,-345,210),(0,0,73),195)
for name in ['build_snap_print_kit.py','snap_parameters.json']:
 t=bpy.data.texts.new(name);t.write((R/name).read_text())
scene['assembly']='Separate color snap fit parts. No glue. Head and feet base snap on/off.'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Proxy_Pal_SNAP_EDITABLE.blend'))
render('01_ASSEMBLED')
for name,ob in obs.items():
 if ob['assembly']=='head':ob.location.z+=48
 if name.startswith(('BLACK_eye','BLACK_brow','BLACK_smile','BLACK_crest','PINK')):
  it=next(i for i in checks['interfaces'] if i['part']==name);n=Vector([row[2] for row in it['frame']]);ob.location+=n*20
 if ob['assembly']=='bottom':ob.location.z=-35
stage.location.z=-35.2;camera((245,-400,255),(0,-4,79),270);render('02_EXPLODED_NO_GLUE')
for ob in obs.values():ob.location=(0,0,0)
stage.location.z=-.2
core.data.materials.clear();core.data.materials.append(gray)
for ob in list(obs.values())+[core]:
 ob.data=ob.data.copy();bm=bmesh.new();bm.from_mesh(ob.data)
 px=-ob.location.x
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(px,0,0),plane_no=(1,0,0),dist=.00001,clear_outer=True,clear_inner=False)
 if ob!=core:
  edges=[e for e in bm.edges if e.is_boundary and all(abs(v.co.x-px)<.001 for v in e.verts)]
  if edges:bmesh.ops.holes_fill(bm,edges=edges,sides=0)
 bm.to_mesh(ob.data);bm.free()
 for face in ob.data.polygons:
  if all(abs(ob.data.vertices[v].co.x-px)<.001 for v in face.vertices):face.use_smooth=False
camera((300,-190,150),(0,0,72),190);render('03_SECTION')
print('Rendered actual snap geometry; editable model saved before exploded/section views.')
