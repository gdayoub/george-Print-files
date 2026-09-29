"""Run in Higgsfield 3D Jutsu's Blender worker. All dimensions are metres.
Editable visual-development models; mounting and print engineering are unresolved.
"""
import bpy, math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

# This script owns this new standalone scene only.
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj,do_unlink=True)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
scene.unit_settings.scale_length=1.0

def material(name,rgb,rough=.36,metal=0):
    mat=bpy.data.materials.new(name);mat.diffuse_color=(*rgb,1);mat.use_nodes=True
    node=mat.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value=(*rgb,1)
    node.inputs['Roughness'].default_value=rough
    node.inputs['Metallic'].default_value=metal
    return mat
red=material('PLA / Ember Red',(.52,.022,.04),.33)
riftred=material('PLA / Garnet Red',(.40,.015,.031),.31)
wallmat=material('Studio / Warm Graphite',(.065,.062,.070),.8)
ivory=material('Studio / Warm White',(.75,.70,.65),.7)
muted=material('Studio / Muted Type',(.32,.29,.31),.8)

def collection(name):
    c=bpy.data.collections.new(name);scene.collection.children.link(c);return c
ember=collection('01 / EMBERWING / visual development')
rift=collection('02 / RIFT / visual development')
stage=collection('00 / STUDIO / do not print')

def put(obj,col,mat,part=None):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    col.objects.link(obj)
    obj.data.materials.append(mat)
    if part: obj['part_id']=part;obj['status']='VISUAL PROTOTYPE — mount and print unverified'
    return obj
def bevel(obj,width=.0012,segments=3):
    mod=obj.modifiers.new('Soft manufactured edges','BEVEL');mod.width=width;mod.segments=segments
    mod.affect='EDGES'
    mod2=obj.modifiers.new('Weighted planar normals','WEIGHTED_NORMAL')
    return obj
def mesh(name,verts,faces,col,mat,part=None,edge=.0007):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);col.objects.link(obj);data.materials.append(mat)
    if part:obj['part_id']=part;obj['status']='VISUAL PROTOTYPE — mount and print unverified'
    if edge:bevel(obj,edge)
    return obj
def prism(name,poly,front,back,col,mat,part=None,dx=0,dz=0,edge=.0007):
    # Input CCW XZ polygon. Face orientation fixed explicitly.
    p=[Vector((x,0,z)) for x,z in poly]
    tri=tessellate_polygon([p]);lookup={tuple(v):i for i,v in enumerate(p)}
    n=len(p);verts=[(x+dx,y,z+dz) for y in [front,back] for x,z in poly]
    faces=[]
    for t in tri:
        ids=[v if isinstance(v,int) else lookup[tuple(v)] for v in t];faces+=[tuple(ids),tuple(i+n for i in reversed(ids))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    obj=mesh(name,verts,faces,col,mat,part,edge)
    # Recalculate outside normals for mirrored polygons as well.
    import bmesh
    bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(obj.data);bm.free()
    return obj
def cube(name,loc,scale,col,mat,part=None,edge=.001):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.name=name;o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    put(o,col,mat,part)
    if edge:bevel(o,edge)
    return o
def ribbon(name,points,radius,col,mat,part):
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=16
    curve.bevel_depth=radius;curve.bevel_resolution=3;curve.use_fill_caps=True
    s=curve.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    obj=bpy.data.objects.new(name,curve);col.objects.link(obj);curve.materials.append(mat)
    obj['part_id']=part;obj['status']='VISUAL PROTOTYPE — mount and print unverified'
    return obj
def clip_z(poly,z,above):
    out=[]
    for i,a in enumerate(poly):
        b=poly[(i+1)%len(poly)];ina=a[1]>=z if above else a[1]<=z;inb=b[1]>=z if above else b[1]<=z
        if ina:out.append(a)
        if ina!=inb:
            t=(z-a[1])/(b[1]-a[1]);out.append((a[0]+t*(b[0]-a[0]),z))
    return out

EX,EZ=-.36,.12
# Broad membranes with deliberate scallops; four panels keep the visual split explicit.
wing=[(.055,.105),(.104,.076),(.127,.008),(.146,.063),(.171,.071),(.202,.036),
      (.207,.120),(.226,.147),(.266,.103),(.258,.202),(.246,.254),(.215,.299),
      (.178,.327),(.137,.355),(.128,.349),(.135,.333),(.151,.305),(.145,.262),
      (.124,.223),(.094,.203),(.055,.203)]
for sign,side in [(-1,'L'),(1,'R')]:
    for above,label in [(False,'LOWER'),(True,'UPPER')]:
        poly=clip_z(wing,.186,above)
        poly=[(sign*x,z+(.0006 if above else 0)) for x,z in poly]
        part=f'EW_WING_{side}_{label}'
        prism(part+'__membrane',poly,-.008,-.004,ember,red,part,EX,EZ)
    # Ribs follow the main fingers of the membrane. They are decorative assembly pieces.
    for j,end in enumerate([(.127,.008),(.202,.036),(.266,.103)]):
        # Split the rib at the panel seam with a linear interpolation at z=.186.
        start=(.140,.333);t=(.186-start[1])/(end[1]-start[1]);cross=(start[0]+t*(end[0]-start[0]),.186)
        for label,ends in [('UPPER',[start,cross]),('LOWER',[cross,end])]:
            pts=[(EX+sign*x,-.009,EZ+z) for x,z in ends]
            ribbon(f'EW_WING_{side}_{label}__rib{j}',pts,.0025,ember,red,f'EW_WING_{side}_{label}')

# Five independent structural-looking shelf modules. Final mounts/joinery are not specified.
def shelf_module(tag,cx,z,width,depth):
    backpoly=[(-width/2,0),(width/2,0),(width/2,.097),(width/2-.008,.11),(-width/2+.008,.11),(-width/2,.097)]
    prism(tag+'__back',backpoly,-.004,0,ember,red,tag,cx,z-.032)
    cube(tag+'__deck',(cx,-depth/2,z),(width,depth,.006),ember,red,tag,.0018)
    cube(tag+'__lip',(cx,-depth+.002,z+.004),(width,.004,.007),ember,red,tag,.0012)
    # Two cheeks make the end view a clean 45-degree bracket, not a deep filled wedge.
    for x in [-width/2+.005,width/2-.005]:
        # Build a YZ triangular brace extruded along X.
        yz=[(-.004,z-.031),(-depth+.004,z-.003),(-.004,z-.003)]
        verts=[(cx+x+xx,y,zz) for xx in [-.003,.003] for y,zz in yz]
        mesh(tag+('__braceL' if x<0 else '__braceR'),verts,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],ember,red,tag,.0008)
for name,xx,zz,w,d in [('BOTTOM_L',-.1005,.045,.199,.090),('BOTTOM_R',.1005,.045,.199,.090),
                        ('MIDDLE_L',-.0805,.151,.159,.080),('MIDDLE_R',.0805,.151,.159,.080),
                        ('TOP',0,.257,.205,.073)]:
    shelf_module('EW_'+name,EX+xx,EZ+zz,w,d)

# Shield and simplified relief motif: bold planes, no tiny engraving.
shield=[(-.032,.022),(0,-.002),(.032,.022),(.034,.063),(0,.079),(-.034,.063)]
prism('EW_CREST__shield',shield,-.095,-.090,ember,red,'EW_CREST',EX,EZ-.014,edge=.0013)
flame=[(-.006,.021),(.008,.030),(.003,.039),(.014,.043),(.002,.061),(-.014,.050),(-.006,.044),(-.017,.034)]
prism('EW_CREST__flame',flame,-.098,-.094,ember,red,'EW_CREST',EX,EZ-.014,edge=.0006)

# RIFT: five shallow chamfered hexagon pods. Independent modules, no LEGO studs.
RX,RZ=.36,.18
def hexagon(radius):return [(radius*math.cos(i*math.pi/3),radius*math.sin(i*math.pi/3)) for i in range(6)]
for i,(xx,zz) in enumerate([(-.172,0),(0,0),(.172,0),(-.086,.153),(.086,.153)]):
    part=f'RIFT_POD_{i+1:02d}';cx=RX+xx;cz=RZ+zz;r=.084
    prism(part+'__back',hexagon(r),-.004,0,rift,riftred,part,cx,cz,edge=.001)
    # Four ring loops create a broad front chamfer and substantial sculptural rim.
    radii=[r,r,r-.004,r-.012,r-.008,r-.005]
    ys=[-.003,-.083,-.091,-.091,-.083,-.003]
    verts=[(cx+rr*math.cos(j*math.pi/3),y,cz+rr*math.sin(j*math.pi/3)) for rr,y in zip(radii,ys) for j in range(6)]
    faces=[]
    for k in range(6):
        for j in range(6):faces.append((k*6+j,k*6+(j+1)%6,((k+1)%6)*6+(j+1)%6,((k+1)%6)*6+j))
    obj=mesh(part+'__chamfered_frame',verts,faces,rift,riftred,part,.0008)
    import bmesh
    bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(obj.data);bm.free()

# A neutral presentation wall and floor. They are excluded from printable-part manifests.
cube('STUDIO__wall',(0,.034,.36),(1.7,.06,.94),stage,wallmat,None,.01)
cube('STUDIO__floor',(0,-.22,.015),(1.9,.8,.025),stage,wallmat,None,.005)
def label(name,text,loc,size,mat=ivory):
    data=bpy.data.curves.new(name,'FONT');data.body=text;data.align_x='CENTER';data.size=size;data.extrude=0
    obj=bpy.data.objects.new(name,data);stage.objects.link(obj);obj.location=loc;obj.rotation_euler=(math.pi/2,0,0);data.materials.append(mat)
label('STUDIO__brand','GEORGE / PRINTS',(0,-.003,.62),.035)
label('STUDIO__subtitle','BOLD FORMS.  SINGLE COLOUR.  BIG PRESENCE.',(0,-.003,.58),.013,muted)
label('STUDIO__ember','01   EMBERWING',(EX,-.14,.07),.020)
label('STUDIO__rift','02   RIFT',(RX,-.14,.07),.020)
label('STUDIO__status','VISUAL DEVELOPMENT   /   UNTESTED MOUNTING',(0,-.01,.041),.010,muted)

world=bpy.data.worlds.new('Studio ambient') if not scene.world else scene.world
scene.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.22,.26,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.35
def light(name,kind,loc,power,color,size=.15):
    d=bpy.data.lights.new(name,kind);o=bpy.data.objects.new(name,d);stage.objects.link(o);o.location=loc;d.energy=power;d.color=color
    if kind=='POINT':d.shadow_soft_size=size
    if kind=='SUN':d.angle=.12;o.rotation_euler=(.55,-.45,-.4)
    return o
light('Key / upper left','POINT',(-.55,-.85,1.05),90,(1,.88,.82),.32)
light('Fill / camera right','POINT',(.85,-.5,.65),38,(.78,.85,1),.4)
light('Rim / overhead','POINT',(0,-.05,1.0),28,(1,.2,.25),.12)
light('Ambient / soft sun','SUN',(0,0,1),.6,(1,1,1))
camdata=bpy.data.cameras.new('Delivery camera');cam=bpy.data.objects.new('Delivery camera',camdata);stage.objects.link(cam)
cam.location=(.25,-2.3,.83);target=Vector((0,-.02,.35));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
camdata.type='ORTHO';camdata.ortho_scale=1.42;camdata.lens=50;scene.camera=cam
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1400;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.media_type='IMAGE';scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.eevee.taa_render_samples=24
scene.view_settings.view_transform='Khronos PBR Neutral'
scene['design_status']='Prototype geometry. Mesh exports checked separately; physical printing and mounting untested.'
scene['printer_target']='Bambu P1S / PLA / 0.4 mm nozzle; printable engineering not complete.'
targetfile=artifacts.file(name='emberwing-rift-hero.png',media_type='image/png')
scene.render.filepath=targetfile.path;bpy.ops.render.render(write_still=True);targetfile.publish()
result={'designs':['Emberwing','Rift'],'part_ids':sorted({o.get('part_id') for o in bpy.data.objects if o.get('part_id')}),
        'objects':len(bpy.data.objects),'units':'metres','status':'visual concepts; not print or mounting validated'}
