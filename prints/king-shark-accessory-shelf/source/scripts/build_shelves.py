"""Compact character shelf prototypes, built from the user's existing sculptures.

Usage coordinates: X right, -Y projects away from wall, Z up. Flat backs print
on the bed. Separate flat trays sit on two gussets and register with glue keys.
The mounting is an unrated prototype, not a Command-certified shelf.
"""
from pathlib import Path
import json, sys, hashlib
import numpy as np
import trimesh
import manifold3d as mf
from scipy.ndimage import gaussian_filter, binary_closing, binary_fill_holes, label, distance_transform_edt
from shapely.geometry import box, Polygon, MultiPoint
from shapely.geometry.polygon import orient
from skimage.measure import find_contours

ROOT=Path(__file__).resolve().parent
WORK=ROOT.parent
sys.path.insert(0,str(WORK/'blender_runtime'))
import bpy
from mathutils.bvhtree import BVHTree
from mathutils import Vector

W,H,BASE=148.,156.,3.2
STEP=.25
TRAY_Z=32.

def load_mesh(path):
    a=np.load(path);return trimesh.Trimesh(a['vertices'],a['faces'],process=False)
def solid(mesh):
    s=mf.Manifold(mf.Mesh64(np.ascontiguousarray(mesh.vertices,dtype=np.float64),np.ascontiguousarray(mesh.faces,dtype=np.uint64)))
    assert s.status()==mf.Error.NoError,s.status();return s
def tm(s):
    a=s.to_mesh64();return trimesh.Trimesh(a.vert_properties[:,:3],a.tri_verts,process=False)
def union(items):return mf.Manifold.batch_boolean(items,mf.OpType.Add).as_original()
def save(s,path):
    s=s.as_original().simplify(.00005)
    cs=[p for p in s.decompose() if p.volume()>.001]
    s=union(cs)
    m=tm(s)
    assert len(s.decompose())==1 and m.is_watertight and m.is_winding_consistent,(path,len(s.decompose()))
    a=s.to_mesh64();np.savez_compressed(path,vertices=a.vert_properties[:,:3],faces=a.tri_verts)
    return s
def cs(poly):return mf.CrossSection([np.array(orient(poly,sign=1).exterior.coords)[:-1]])
def rounded(width,height,r):return box(-width/2+r,-height/2+r,width/2-r,height/2-r).buffer(r,quad_segs=16)
def xz_extrude(poly,depth,back_y=0):
    return mf.Manifold.extrude(cs(poly),depth).transform(np.array([[1,0,0,0],[0,0,-1,back_y],[0,1,0,0]],float))
def cube(size,origin):return mf.Manifold.cube(size).translate(origin)

def heightfield(xs,zs,heights,back=0):
    X,Z=np.meshgrid(xs,zs,indexing='ij');nx,nz=X.shape
    v=np.c_[X.ravel(),-heights.ravel(),Z.ravel()];f=[]
    for i in range(nx-1):
        for j in range(nz-1):
            a=i*nz+j;b=a+nz;c=b+1;d=a+1;f.extend([(a,b,c),(a,c,d)])
    boundary=list(range(0,(nx-1)*nz+1,nz))+list(range((nx-1)*nz+1,nx*nz))+list(range((nx-2)*nz+nz-1,nz-2,-nz))+list(range(nz-2,0,-1))
    n=len(v);bottom=v[boundary].copy();bottom[:,1]=-back
    v=np.vstack([v,bottom,[[np.mean(xs),-back,np.mean(zs)]]]);ctr=len(v)-1
    for k,a in enumerate(boundary):
        j=(k+1)%len(boundary);b=boundary[j]
        f.extend([(a,n+j,b),(a,n+k,n+j),(ctr,n+j,n+k)])
    return solid(trimesh.Trimesh(v,np.array(f),process=False))

def bvh(mesh):return BVHTree.FromPolygons(mesh.vertices.tolist(),mesh.faces.tolist(),all_triangles=True)
def raster(mesh,xs,zs):
    tree=bvh(mesh);result=np.full((len(xs),len(zs)),np.nan)
    direction=Vector((0,1,0))
    for i,x in enumerate(xs):
        for j,z in enumerate(zs):
            hit=tree.ray_cast(Vector((float(x),-500,float(z))),direction,1000)
            if hit[0] is not None:result[i,j]=hit[0].y
    return result

def transformed(mesh,scale,zshift,ycompress=.095):
    m=mesh.copy();m.vertices[:,0]*=scale
    m.vertices[:,2]=m.vertices[:,2]*scale+zshift
    m.vertices[:,1]=-BASE-(75-m.vertices[:,1])*ycompress
    # The sculpt becomes shallow relief; preserve its frontal proportions.
    m.vertices[:,1]=np.minimum(m.vertices[:,1],-BASE-1)
    return m

def hand_mesh(character,side):
    if character=='king_shark':
        s=solid(load_mesh(WORK/'king_shark_v2/final_parts'/f'{side}_arm.npz'))
        s=s.trim_by_plane((0,0,-1),-205)
        s=max(s.decompose(),key=lambda q:q.volume());m=tm(s);scale=.30
    else:
        m=load_mesh(WORK/'venom_muscular/final_parts'/f'{side}_hand.npz');scale=.25
    v=np.asarray(m.vertices);v=(v-v.mean(0))*scale
    # Point the existing fingers forward under the tray, with flattened depth.
    R=np.array([[1,0,0],[0,0,1],[0,-1,0]],float)
    v=v@R.T;v[:,2]*=.6
    v[:,2]-=v[:,2].max();v+=np.array([54 if side=='L' else -54,-43,31.7])
    m.vertices=v;return m

def pegs_and_tray():
    # All new products share the same two wide, non-locking registration keys.
    gussets=[];pegs=[];sockets=[]
    for x in [-54,54]:
        poly=Polygon([[-3.2,2],[-3.2,32],[-54,32]]) # Y,Z triangle
        g=mf.Manifold.extrude(cs(poly),6).transform(np.array([[0,0,1,x-3],[1,0,0,0],[0,1,0,0]],float))
        gussets.append(g)
        # Ramped front/rear edges print without unsupported horizontal pins.
        profile=Polygon([[-45,32],[-35,32],[-38,35],[-42,35]])
        peg=mf.Manifold.extrude(cs(profile),6).transform(np.array([[0,0,1,x-3],[1,0,0,0],[0,1,0,0]],float))
        pegs.append(peg)
        pocket=profile.buffer(.22,join_style='mitre')
        sockets.append(mf.Manifold.extrude(cs(pocket),6.44).transform(np.array([[0,0,1,x-3.22],[1,0,0,0],[0,1,0,0]],float)))
    outer=rounded(150,55,8)
    base=mf.Manifold.extrude(cs(outer),4.2).translate((0,-30.7,TRAY_Z))
    inner=rounded(145.2,50.2,5.6)
    rim=mf.Manifold.extrude(cs(outer)-cs(inner),4.8).translate((0,-30.7,TRAY_Z+4.2))
    tray=union([base,rim])-union(sockets)
    return union(gussets+pegs),tray,pegs

def keyholes(body):
    # Optional visible screw slots. Picture-hanging strips are not shelf-rated.
    cutters=[]
    from shapely.geometry import Point
    for x in [-54,54]:
        entry=Point(x,132).buffer(4.6,quad_segs=24)
        neck=box(x-2.35,132,x+2.35,141).union(Point(x,141).buffer(2.35,quad_segs=16))
        through=entry.union(neck)
        headpath=box(x-4.6,132,x+4.6,141).union(entry).union(Point(x,141).buffer(4.6,quad_segs=24))
        cutters.append(xz_extrude(through,6,.1))
        cutters.append(xz_extrude(headpath,1.55,.1))
    return body-union(cutters)

def build(character):
    dst=ROOT/character;partsdir=dst/'final_parts';partsdir.mkdir(parents=True,exist_ok=True)
    king=character=='king_shark'
    grid_height=182 if king else H
    xs=np.linspace(-W/2,W/2,round(W/STEP)+1);zs=np.linspace(0,grid_height,round(grid_height/STEP)+1)
    source_paths=[]
    fin_back=None
    if king:
        base=WORK/'king_shark_v2/final_parts'
        names=['Torso','L_arm','R_arm','Dorsal_fin','Upper_teeth','Lower_teeth']
        scale=.43;shift=58-250*scale
        meshes=[]
        for name in names:
            path=base/(name+'.npz');source_paths.append(path)
            s=solid(load_mesh(path)).trim_by_plane((0,0,1),250)
            if name=='Torso':
                s=s.trim_by_plane((1,0,0),-85).trim_by_plane((-1,0,0),-85)
            if not s.is_empty():
                sculpt=transformed(tm(s),scale,shift)
                if name=='Dorsal_fin':
                    # Make the actual dorsal sculpt legible above the plaque.
                    # Its projection gets its own flat backing so it still
                    # prints on the bed with the rest of the relief.
                    fin_root=float(sculpt.bounds[0,2])
                    sculpt.vertices[:,0]*=1.9
                    sculpt.vertices[:,2]=fin_root+(sculpt.vertices[:,2]-fin_root)*1.9
                    sculpt.vertices[:,1]=-BASE-(-sculpt.vertices[:,1]-BASE)*1.35
                    fin_back=MultiPoint(sculpt.vertices[:,[0,2]]).convex_hull.buffer(1.8,quad_segs=16)
                meshes.append(sculpt)
        accents={}
    else:
        path=WORK/'venom_muscular/source_muscular.npz';source_paths.append(path)
        scale=.35;shift=62-250*scale
        s=solid(load_mesh(path)).trim_by_plane((0,0,1),250)
        meshes=[transformed(tm(s),scale,shift)]
        accents={}
        for name,source in [('Eye_L','Eye_L_Torso_01'),('Eye_R','Eye_R_Torso_01'),('Chest_Emblem','Chest_Torso_01')]:
            p=WORK/'venom_muscular/final_parts'/(source+'.npz');source_paths.append(p)
            accents[name]=transformed(load_mesh(p),scale,shift)
    # Original hands are supported relief on the front of the structural arms.
    meshes += [hand_mesh(character,side) for side in ['L','R']]
    combined=trimesh.util.concatenate(meshes)
    yy=raster(combined,xs,zs)
    h=np.where(np.isfinite(yy),np.maximum(BASE+1,-yy),BASE)
    # Keep facial relief crisp while rounding the projected silhouette over
    # about 1 mm. A coarse pixel edge becomes conspicuous in an oblique view.
    inside=distance_transform_edt(np.isfinite(yy))*STEP
    fine=gaussian_filter(h,.18/STEP)
    edge=gaussian_filter(h,.60/STEP)
    blend=np.clip(inside/1.5,0,1)
    h=np.maximum(edge*(1-blend)+fine*blend,BASE)
    # Keep the full tray installation corridor clear of hand-relief blur.
    h[:,(zs>=31.75)&(zs<=57)]=BASE
    np.savez_compressed(dst/'relief_cache.npz',xs=xs,zs=zs,height=h)
    outline=rounded(W,H,15)
    from shapely.affinity import translate
    outline=translate(outline,yoff=H/2)
    back_outline=outline.union(fin_back) if fin_back is not None else outline
    relief_outline=outline.buffer(-2).union(fin_back.buffer(-.2)) if fin_back is not None else outline.buffer(-2)
    relief=heightfield(xs,zs,h).simplify(.02)^xz_extrude(relief_outline,80)
    body=union([xz_extrude(back_outline,BASE),relief]).simplify(.005)
    # Analytic corridor prevents decimation tolerance protruding into the tray.
    body=body-cube((W+2,80,25.75),(-W/2-1,-BASE-80,31.75))
    accent_solids={}
    for name,mesh in accents.items():
        ay=raster(mesh,xs,zs)
        mask=np.isfinite(ay)&np.isfinite(yy)&(ay<=yy+.9)&(zs[None,:]>55)
        mask=binary_fill_holes(binary_closing(mask,iterations=1))
        labels,n=label(mask)
        if n==0:continue
        sizes=np.bincount(labels.ravel());sizes[0]=0;mask=labels==sizes.argmax()
        contours=find_contours(np.pad(mask,1).astype(float),.5)
        contour=max(contours,key=len)-1
        poly=Polygon(np.c_[xs[0]+contour[:,0]*STEP,zs[0]+contour[:,1]*STEP]).buffer(0).buffer(.4).buffer(-.4).simplify(.10)
        if poly.area<4:continue
        back=max(BASE+.65,float(h[mask].min())-1.0)
        px0,pz0,px1,pz1=poly.bounds
        ix=np.where((xs>=px0-STEP*2)&(xs<=px1+STEP*2))[0]
        iz=np.where((zs>=pz0-STEP*2)&(zs<=pz1+STEP*2))[0]
        field=heightfield(xs[ix],zs[iz],np.maximum(h[np.ix_(ix,iz)]+.08,back+.01),back=back).simplify(.01)
        insert=field^xz_extrude(poly,80)
        # A narrow border clearance and extra pocket depth provide glue room.
        pocket=xz_extrude(poly.buffer(.18),80,back_y=-back+.15)
        body=body-pocket
        accent_solids[name]=insert
    gussets,tray,pegs=pegs_and_tray()
    body=keyholes(union([body,gussets]))
    parts={'Body':body,'Tray':tray,**accent_solids}
    rows=[]
    for name,s in parts.items():
        s=save(s,partsdir/(name+'.npz'));parts[name]=s;m=tm(s)
        color='White' if name in accent_solids else ('Red' if name=='Tray' and character=='king_shark' else 'Black')
        rows.append(dict(name=name,color=color,triangles=s.num_tri(),volume_mm3=s.volume(),
            dimensions_mm=m.extents.tolist(),settings={'enable_support':'0','brim_width':'2'}))
    (partsdir/'manifest.json').write_text(json.dumps(rows,indent=2))
    overlaps=[]
    for i,a in enumerate(parts):
        for b in list(parts)[i+1:]:
            v=max(0.,(parts[a]^parts[b]).volume())
            overlaps.append(dict(a=a,b=b,overlap_mm3=v));assert v<.02,(a,b,v)
    # Shelf lays on both gussets; keys only locate, while glue joins broad seats.
    paths=[]
    for dz in [0,.2,.5,1,2,3,4,8,16]:
        v=max(0.,(parts['Tray'].translate((0,0,dz))^parts['Body']).volume())
        paths.append(dict(lift_mm=dz,overlap_mm3=v));assert v<.02,paths[-1]
    # Print body with the flat back on bed; the tray is printed flat independently.
    R=[[1,0,0],[0,0,1],[0,-1,0]]
    body_inst={'name':'Body','rotation':R,'xy_mm':[54,10]}
    tray_inst={'name':'Tray','rotation':np.eye(3).tolist(),'xy_mm':[53,182]}
    if character=='king_shark':
        plates=[{'label':'Gray character and mounting back','instances':[body_inst]},
                {'label':'Red tray / print flat','instances':[dict(tray_inst,xy_mm=[53,100])]}]
    else:
        plates=[{'label':'Black body and tray','instances':[body_inst,tray_inst]}]
    if accent_solids:
        inst=[];x=45
        for name in accent_solids:
            extent=tm(accent_solids[name]).extents
            inst.append(dict(name=name,rotation=R,xy_mm=[x,45],settings={'layer_height':'.16','brim_width':'2'}))
            x+=extent[0]+10
        plates.append(dict(label='White eyes and chest emblem / flat backs',instances=inst))
    layout=dict(bed_margin_mm=3,max_height_mm=250,palette=['#72777C' if character=='king_shark' else '#15171A','#EFEDE4','#BB1424'],plates=plates)
    (dst/'layout.json').write_text(json.dumps(layout,indent=2))
    report=dict(character=character,unrated_mounting_prototype=True,
        flat_back_mm=[W,H],clear_strip_zones_mm={'size':[25,100],'centers_x':[-30,30],'z_start':10},
        strip_mount_note='3M does not recommend picture-hanging strips for shelves. No adhesive load rating claimed.',
        screw_alternative={'entry_diameter_mm':9.2,'neck_width_mm':4.7,'centers_x_mm':[-54,54]},
        tray_outer_mm=[150,55],tray_floor_mm=4.2,tray_rim_height_mm=4.8,
        two_gusset_thickness_mm=6,key_side_clearance_mm=.22,
        sources={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths},
        overlaps=overlaps,tray_insertion_samples=paths,parts=rows,
        design_intent='Light accessory catchall; prototype requires physical assembly and mounting verification.')
    (dst/'geometry_validation.json').write_text(json.dumps(report,indent=2))
    print(character,json.dumps(rows),flush=True)

if __name__=='__main__':
    for character in sys.argv[1:] or ['king_shark','venom']:build(character)
