"""Original shelf prototypes. Millimetres. Run with Python 3.11+ from source/.
pip install -r requirements.txt
Local dependencies are supported in ./python_libs.
"""
import sys, json, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'python_libs'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'python_libs'))
import numpy as np
import trimesh
from shapely.geometry import Polygon, LineString, box

ROOT = Path(__file__).parent
PROJECT = ROOT.parent
OUT = PROJECT / 'files' / 'stl'
IMAGES = PROJECT / 'images'
REPORTS = PROJECT / 'validation'
for folder in (OUT, IMAGES, REPORTS): folder.mkdir(parents=True, exist_ok=True)
WIDTH, DEPTH, BACK, SHELF_Z, DECK, WEB = 120., 64., 3.2, 60., 4.8, 3.2
models, records, scad_parts = {}, [], []

def extrusion(poly, thickness, plane='xy', offset=0):
    if hasattr(poly,'geoms'):
        return trimesh.util.concatenate([extrusion(p,thickness,plane,offset) for p in poly.geoms if p.area>0])
    mesh = trimesh.creation.extrude_polygon(poly, thickness, engine='earcut')
    v = mesh.vertices.copy()
    if plane == 'yz':
        mesh.vertices = np.column_stack([v[:,2]+offset, v[:,0], v[:,1]])
    elif plane == 'xz':
        mesh.vertices = np.column_stack([v[:,0], v[:,2]+offset, v[:,1]])
        mesh.invert()
    return mesh

def combine(items):
    result = trimesh.boolean.union(items, engine='manifold')
    result.merge_vertices(digits_vertex=5)
    result.update_faces(result.nondegenerate_faces())
    result.update_faces(result.unique_faces())
    result.remove_unreferenced_vertices()
    return result

def scad_poly(poly):
    if hasattr(poly,'geoms'):
        return 'union() {' + ''.join(scad_poly(p) for p in poly.geoms if p.area>0) + '}'
    rings = [list(poly.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in poly.interiors]
    pts, paths = [], []
    for r in rings:
        paths.append(list(range(len(pts),len(pts)+len(r))))
        pts += [[round(x,4),round(y,4)] for x,y in r]
    return f'polygon(points={json.dumps(pts)}, paths={json.dumps(paths)});'

def export(name, mesh, transform, description, scad):
    models[name] = mesh.copy()
    printable = mesh.copy()
    printable.apply_transform(transform)
    printable.apply_translation(-printable.bounds[0])
    path = OUT / f'{name}.stl'
    printable.export(path)
    check = trimesh.load_mesh(path)
    components = len(check.split())
    assert check.is_watertight and check.is_volume and components == 1, name
    assert max(check.extents) < 245, name
    records.append(dict(file=path.name, bounds_mm=check.extents.round(2).tolist(),
        watertight=bool(check.is_watertight), connected_components=components,
        volume_cm3=round(check.volume/1000,2),
        solid_PLA_mass_g_at_1_24=round(check.volume/1000*1.24,1), note=description))
    if name.endswith('_FLAT'):
        scad = 'mirror([0,1,0]) {' + scad + '}'
    scad_parts.append(f'// {description}\nmodule part_{name}() {{ {scad} }}')

# Assembly axes: X width, Y away from wall, Z vertical.
# Bed axes for the structural extrusion: Y, Z, X; layers run across shelf width.
SIDE = np.array([[0,1,0,0],[0,0,1,0],[1,0,0,0],[0,0,0,1]],float)
FLAT = np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]],float)

def core(height, roof=False):
    # Triangular shell under the deck is continuous across the width.
    # This avoids unsupported isolated gussets in the side-on print orientation.
    outer = Polygon([(0,0),(0,height),(BACK,height),(BACK,SHELF_Z+DECK),
                     (DEPTH,SHELF_Z+DECK),(DEPTH,SHELF_Z),(BACK,0)])
    slope = SHELF_Z/(DEPTH-BACK)
    intercept = WEB*math.sqrt(1+slope*slope)
    inner = Polygon([(BACK,intercept),(BACK,SHELF_Z),(DEPTH-intercept/slope,SHELF_Z)])
    profile = outer.difference(inner)
    # Small front retaining lip, fused to deck.
    profile = profile.union(box(DEPTH-2.4,SHELF_Z+DECK-.1,DEPTH,SHELF_Z+DECK+2.4))
    if roof:
        profile = profile.union(box(0,height-DECK,DEPTH,height))
    return profile

for name, height, roof in [('01_ledge_core_SIDE_PRINT',140,False),('02_pixel_cubby_core_SIDE_PRINT',180,True)]:
    p = core(height,roof)
    m = extrusion(p,WIDTH,'yz',-WIDTH/2)
    export(name,m,SIDE,'Print as supplied, on its side. No supports intended; inspect sliced preview.',
           f'linear_extrude(height={WIDTH}) {scad_poly(p)}')

# Wings attach ONLY to the front of the core backplate. Wall-contact face stays clear.
wing_points = [(44,42),(58,72),(80,48),(76,93),(104,66),(94,118),
               (118,95),(110,144),(90,172),(66,186),(63,178),(68,160),
               (64,144),(57,133),(44,128)]
wing = Polygon(wing_points)
for label, sign in [('R',1),('L',-1)]:
    p = Polygon([(sign*x,z) for x,z in wing_points])
    base = extrusion(p,2.4,'xz',BACK)
    ribs = []
    for end in [(58,72),(80,48),(104,66),(118,95)]:
        rib = LineString([(sign*67,176),(sign*end[0],end[1])]).buffer(1.1,cap_style=2).intersection(p.buffer(-0.5))
        if not rib.is_empty:
            ribs.append(extrusion(rib,1.0,'xz',BACK+2.3))
    m = combine([base]+ribs)
    # Reverse flat orientation to put plain rear face on the bed.
    rot = np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]],float)
    sc = f'linear_extrude(height=2.4) {scad_poly(p)}'
    for end in [(58,72),(80,48),(104,66),(118,95)]:
        rib=LineString([(sign*67,176),(sign*end[0],end[1])]).buffer(1.1,cap_style=2).intersection(p.buffer(-0.5))
        sc += f'translate([0,0,2.3]) linear_extrude(height=1) {scad_poly(rib)}'
    export(f'03_dragon_wing_{label}_FLAT',m,rot,'Decorative only. Glue overlap to front of backplate; ribs face room.',sc)

shield = Polygon([(-17,126),(0,133),(17,126),(15,103),(0,91),(-15,103)])
crest = extrusion(shield,2.4,'xz',BACK)
mark = Polygon([(-6,122),(4,126),(11,120),(4,117),(8,111),(0,102),(-2,113),(-8,116),(-2,118)])
crest = combine([crest,extrusion(mark,1.2,'xz',BACK+2.3)])
export('04_dragon_crest_FLAT',crest,rot,'Optional decorative crest; glue to front centre of backplate.',
       f'linear_extrude(height=2.4) {scad_poly(shield)} translate([0,0,2.3]) linear_extrude(height=1.2) {scad_poly(mark)}')

# Pixel front frame bonds to deck lip and upper deck front, not to the wall.
pixel_outer = Polygon([(-72,55),(72,55),(72,79),(66,79),(66,169),(78,169),
                       (78,187),(60,187),(60,199),(36,199),(36,187),(-36,187),
                       (-36,199),(-60,199),(-60,187),(-78,187),(-78,169),(-66,169),(-66,79),(-72,79)])
pixel = pixel_outer.difference(box(-54,68,54,174))
pm = extrusion(pixel,2.4,'xz',DEPTH)
export('05_pixel_frame_FLAT',pm,rot,'Decorative front frame. Align bottom at Z=55 and glue to lip/top front edges.',
       f'linear_extrude(height=2.4) {scad_poly(pixel)}')

# Coupon has same vertical print texture as structural wall-facing surface.
coupon = trimesh.creation.box(extents=[30,3.2,110]); coupon.apply_translation([0,1.6,55])
export('00_adhesive_surface_coupon_SIDE_PRINT',coupon,SIDE,
       'Print first to check strip fit and finish. A bond trial does not validate a shelf load.',
       'cube([3.2,110,30]);')

(REPORTS/'mesh_validation.json').write_text(json.dumps(records,indent=2))
(ROOT/'shelves_editable.scad').write_text('// Original prototype geometry. Units: mm. Modules output print orientation.\n'
    '// Set part to an index below, render F6, then export STL. No structural rating.\n'
    +'part=0;\n'+ '\n'.join(scad_parts)+'\n'+ '\n'.join(f'if(part=={i}) part_{rec["file"][:-4]}();' for i,rec in enumerate(records)))

dragon=[models[n] for n in ['01_ledge_core_SIDE_PRINT','03_dragon_wing_R_FLAT','03_dragon_wing_L_FLAT','04_dragon_crest_FLAT']]
arcade=[models[n] for n in ['02_pixel_cubby_core_SIDE_PRINT','05_pixel_frame_FLAT']]

# Deterministic depth-buffer render; avoids painter-order artefacts in hollow CAD.
from PIL import Image, ImageDraw, ImageFont
def render_meshes(items, size=(1000,850)):
    w,h=size
    eye=np.array([.85,2.7,1.15]); eye/=np.linalg.norm(eye)
    right=np.cross([0,0,1],eye); right/=np.linalg.norm(right)
    up=np.cross(eye,right)
    basis=np.array([right,up,eye])
    allv=np.vstack([m.vertices for m in items])@basis.T
    low,high=allv.min(0),allv.max(0)
    scale=min((w-90)/(high[0]-low[0]),(h-90)/(high[1]-low[1]))
    mid=(low+high)/2
    canvas=np.empty((h,w,3),dtype=np.uint8); canvas[:]=[18,17,23]
    depth=np.full((h,w),-np.inf)
    light=np.array([-.5,1,2]);light/=np.linalg.norm(light)
    for mesh in items:
        coords=mesh.vertices@basis.T
        coords[:,0]=(coords[:,0]-mid[0])*scale+w/2
        coords[:,1]=h/2-(coords[:,1]-mid[1])*scale
        for face,normal in zip(mesh.faces,mesh.face_normals):
            t=coords[face]
            xmin=max(0,int(np.floor(t[:,0].min()))); xmax=min(w-1,int(np.ceil(t[:,0].max())))
            ymin=max(0,int(np.floor(t[:,1].min()))); ymax=min(h-1,int(np.ceil(t[:,1].max())))
            if xmax<xmin or ymax<ymin: continue
            x,y=np.meshgrid(np.arange(xmin,xmax+1)+.5,np.arange(ymin,ymax+1)+.5)
            a,b,c=t
            den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(den)<1e-9: continue
            u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
            v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den
            q=1-u-v; z=u*a[2]+v*b[2]+q*c[2]
            d=depth[ymin:ymax+1,xmin:xmax+1]
            mask=(u>=-1e-7)&(v>=-1e-7)&(q>=-1e-7)&(z>d)
            shade=.58+.42*max(0,float(normal@light))
            colour=(np.array([231,62,77])*shade).astype(np.uint8)
            canvas[ymin:ymax+1,xmin:xmax+1][mask]=colour;d[mask]=z[mask]
    return Image.fromarray(canvas)

def font(size,bold=False):
    candidates = [('C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf'), ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]
    for candidate in candidates:
        if Path(candidate).exists(): return ImageFont.truetype(candidate,size)
    return ImageFont.load_default(size=size)
sheet=Image.new('RGB',(2200,1250),(18,17,23)); draw=ImageDraw.Draw(sheet)
draw.text((85,45),'DRAGON + PIXEL / DISPLAY SHELVES',font=font(51,True),fill='#faf6f5')
draw.text((85,130),'GEORGE PRINTS     /     COLLECTION 005     /     CAD PROTOTYPES',font=font(28),fill='#bcaeb5')
for x,items,title,dim in [(70,dragon,'DRAGON / wing ledge','236 W x 64 D x 186 H mm'),(1150,arcade,'PIXEL / display pod','156 W x 66.4 D x 199 H mm')]:
    draw.text((x+35,225),title,font=font(35,True),fill='#faf6f5')
    draw.text((x+35,277),dim,font=font(26),fill='#bcaeb5')
    sheet.paste(render_meshes(items,(980,760)),(x,325))
draw.text((85,1115),'Actual CAD geometry. Flat decorations attach to the core; each shelf mounts independently.',font=font(28),fill='#faf6f5')
draw.text((85,1170),'UNTETSTED PROTOTYPES — no load rating. Confirm wall, strip product and item size before use.'.replace('UNTETSTED','UNTESTED'),font=font(27),fill='#ff8290')
sheet.save(IMAGES/'design_preview.png')
print(json.dumps(records,indent=2))
