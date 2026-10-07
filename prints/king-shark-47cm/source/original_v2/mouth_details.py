"""Dental insert engineering for the realistic King Shark, millimeter space.

This module owns only the two dental arches and their recommended removal and
socket tools. The assembly engineer applies the tools to its repaired solid.
"""
from pathlib import Path
import json
import numpy as np
import trimesh
import manifold3d as mf

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dental_parts'

# Measured from source sections and an orthographic first-surface depth map.
# The snout is subtly turned, so the depth coordinates intentionally differ
# left/right. Mirroring the teeth would detach them from this generated jaw.
UPPER = np.array([
    [-27,-63.5,382.0],[-24,-67.2,380.9],[-20,-73.0,380.4],
    [-15,-82.0,379.8],[-10,-88.6,379.2],[-5,-94.0,378.7],
    [0,-97.0,378.3],[5,-99.0,378.1],[10,-99.0,378.2],
    [15,-97.5,378.3],[20,-95.0,378.7],[25,-89.5,379.5],
    [29,-83.0,380.8],[31,-78.0,382.0]])
LOWER = np.array([
    [-27,-62.5,378.4],[-24,-65.5,376.1],[-20,-70.5,373.9],
    [-15,-75.5,372.0],[-10,-79.5,370.8],[-5,-83.0,370.0],
    [0,-85.0,369.1],[5,-86.0,369.0],[10,-85.4,369.4],
    [15,-83.5,370.1],[20,-80.0,371.4],[25,-74.8,373.7],
    [29,-69.0,377.8],[31,-66.0,380.3]])

def curve(points, x):
    from scipy.interpolate import PchipInterpolator
    return np.stack((np.asarray(x),PchipInterpolator(points[:,0],points[:,1])(x),
                     PchipInterpolator(points[:,0],points[:,2])(x)),axis=-1)

def capsules(points,radius=1.4):
    spheres=[mf.Manifold.sphere(radius,12).translate(p) for p in points]
    return [mf.Manifold.batch_hull([a,b]) for a,b in zip(spheres[:-1],spheres[1:])]

def unite(solids):
    return mf.Manifold.batch_boolean(solids,mf.OpType.Add)

def tooth(center,tangent,width,length,upper,lean=.0):
    # Cross sections give a lenticular enamel blade rather than a circular cone.
    # The terminal 0.9 mm width survives a 0.4 mm nozzle more reliably than a
    # mathematical point, with one short straight tip that remains shark-like.
    t=np.array(tangent,float);t[2]=0;t/=np.linalg.norm(t)
    n=np.array([t[1],-t[0],0.0])
    points=[]
    direction=-1 if upper else 1
    for fraction,w,d in [(0,width,2.7),(.22,width*.84,2.5),(.7,width*.39,1.6),(1,.95,.95)]:
        c=np.array(center)+[lean*fraction,.9*fraction,direction*length*fraction]
        # Eight-sided rounded rectangle gives thickness and a subtle mid-ridge.
        for tx,ny in [(-.5,-.22),(-.34,-.5),(.34,-.5),(.5,-.22),(.5,.22),(.34,.5),(-.34,.5),(-.5,.22)]:
            points.append(c+t*(w*tx)+n*(d*ny))
    return mf.Manifold.hull_points(np.asarray(points))

def arch(which):
    upper=which=='Upper_teeth';profile=UPPER if upper else LOWER
    # Rails sit inside the jaws, above/below the visible mouth opening. A short
    # angled exit lets each arch clear its lip without exposing a white bar.
    x=np.linspace(-24.0 if upper else -23.0,26.0 if upper else 22.0,61)
    rail=curve(profile,x);rail[:,1]+=10.5 if upper else 9.3
    rail[:,2]+=1.55 if upper else -1.55
    pieces=capsules(rail,1.25 if upper else 1.35)
    coords=[-23.5,-19.5,-15.1,-10.5,-5.5,-.3,5.0,10.4,15.6,20.5,25.0] if upper else [-21.8,-17.4,-12.6,-7.5,-2.2,3.4,9.0,14.5,19.5]
    specs=[]
    for i,x in enumerate(coords):
        p=curve(profile,x)
        p[1]+=3.8 if upper else 4.7
        p[2]+=.35 if upper else -.35
        tangent=curve(profile,x+.1)-curve(profile,x-.1)
        centerfactor=max(0,1-((x-4)/29)**2)
        width=(3.1+1.25*centerfactor) if upper else (2.8+.85*centerfactor)
        length=(2.2+4.0*centerfactor) if upper else (1.6+3.0*centerfactor)
        # Controlled individual variation avoids mechanical zipper repetition.
        length*=1+[.015,-.04,.02,-.025,.0,.025,-.025,.02,-.035,.025,0,.01][i]
        if not upper:length=min(length,float(curve(UPPER,x)[2]-p[2]-4.0-.8))
        lean=np.clip((x-4)*.016,-.38,.38)
        s=tooth(p,tangent,width,length,upper,lean)
        pieces.append(s)
        anchor=curve(profile,x);anchor[1]+=10.5 if upper else 9.3;anchor[2]+=1.55 if upper else -1.55
        root=p+np.array([0,0,-.10 if upper else .10])
        t=tangent.copy();t[2]=0;t/=np.linalg.norm(t);n=np.array([t[1],-t[0],0])
        start=np.array([root+t*(width*tx)+n*(2.4*ny) for tx,ny in [(-.34,-.5),(.34,-.5),(.34,.5),(-.34,.5)]])
        ball=mf.Manifold.sphere(1.1,12).translate(anchor).to_mesh64().vert_properties[:,:3]
        pieces.append(mf.Manifold.hull_points(np.vstack((start,ball))))
        specs.append({'root_mm':p.tolist(),'width_mm':width,'length_mm':length,'tip_width_mm':.95})
    # Deliberately make the roots asymmetrically keyed by the existing curve,
    # without additional thin pegs that could break during assembly.
    result=unite(pieces).simplify(.006)
    inflation=mf.Manifold.sphere(.2,8)
    clearance_pieces=[s.minkowski_sum(inflation) for s in pieces]
    seated=unite(clearance_pieces).simplify(.008)
    path_points=np.array([[0,0,0],[0,-14,-4.7],[0,-65,-4.7]] if upper else [[0,0,0],[0,-10,4],[0,-65,4]],float)
    sweeps=[mf.Manifold.batch_hull([s.translate(a),s.translate(b)]) for s in clearance_pieces for a,b in zip(path_points[:-1],path_points[1:])]
    insertion=unite(sweeps).simplify(.01)
    return result,seated,insertion,rail,specs,path_points

def removal_tool():
    # The rear wall is a rounded, arch-following cavity rather than a planar
    # box wall. Taper both commissures smoothly to zero opening so no exposed
    # triangular saw-cut remains beyond the terminal teeth.
    xs=np.linspace(-26.4,28.8,91);up=curve(UPPER,xs);lo=curve(LOWER,xs)
    rings=[]
    for u,l in zip(up,lo):
        fade=min(1.,max(0.,(u[0]+26.4)/2.2),max(0.,(28.8-u[0])/2.6))
        fade=np.sin(fade*np.pi/2)
        mid=(u[2]+l[2])/2;half=max(0.,(u[2]-.18-l[2]-.1)/2)*fade
        center_factor=max(0,1-((u[0]-3)/29)**2)
        cy=u[1]+5;ry=6+22*center_factor
        arc=[[u[0],cy+ry*np.cos(t),mid+half*np.sin(t)] for t in np.linspace(np.pi/2,-np.pi/2,23)]
        rings.append(np.array([[u[0],-132,mid+half]]+arc+[[u[0],-132,mid-half]]))
    return unite([mf.Manifold.hull_points(np.vstack((a,b))) for a,b in zip(rings[:-1],rings[1:])]).simplify(.01)

def make_parts():
    registration={'uniform_scale':1.0,'translation_mm':[0,0,0],
                  'target':'raw normalized_mesh.npz'}
    if (ROOT/'repair_report.json').exists():
        r=json.loads((ROOT/'repair_report.json').read_text())
        sc=r['uniform_height_scale'];tz=-sc*r['bounds_before_height_normalization'][0][2]
        registration={'uniform_scale':sc,'translation_mm':[0,0,tz],
                      'target':'repaired_solid.npz','source_report':'repair_report.json'}
    scale=registration['uniform_scale'];shift=np.array(registration['translation_mm'])
    def points(p):return np.asarray(p)*scale+shift
    def solid(s):return s.scale((scale,scale,scale)).translate(shift)
    params={'units':'mm','source':'normalized_mesh.npz','source_height_mm':470,
            'registration':registration,
            'front_vector':[0,-1,0],
            'insertion_path':'Reverse each part withdrawal_path_offsets_mm polyline; angled lip clearance first/last, straight front travel outside mouth.',
            'withdrawal_length_mm':65,'socket_per_side_clearance_mm':.2,
            'assembly_order':['Lower_teeth','Upper_teeth'],
            'assembly_order_reason':'Lower teeth are set behind upper teeth in Y. Insert lower first, pressing rearward and down into the lower jaw; insert upper second, pressing rearward and up under the upper lip. Reverse each recorded withdrawal polyline.',
            'upper_lip_measured_points':points(UPPER).tolist(),'lower_lip_measured_points':points(LOWER).tolist(),
            'method':'Connected curved gum rails with triangular lenticular blades; geometry is separately printed white. Do not split individual teeth.',
            'required_integration':'Subtract Old_teeth_removal plus both swept socket tools from repaired head. Keep largest resulting component to discard detached generated dental remnants. Check actual intersection/withdrawal and visually inspect. Socket tools include the seated final shape; do not union cutters into the model.',
            'print_orientation':'Rotate the arch onto its rear gum-rail side or use shallow organic support; retain 0.95 mm tooth tips. Arrange both white arches on one plate.',
            'parts':[]}
    for name in ['Upper_teeth','Lower_teeth']:
        dental,socket,path,rail,specs,path_points=arch(name)
        row=save_mesh(name,solid(dental));save_mesh(name+'_socket',solid(socket));save_mesh(name+'_insertion_sweep',solid(path))
        for spec in specs:spec['root_mm']=points(spec['root_mm']).tolist()
        row.update({'gum_rail_centers_mm':points(rail).tolist(),'gum_rail_radius_mm':1.25 if name=='Upper_teeth' else 1.35,
                    'tooth_specs':specs,'withdrawal_path_offsets_mm':(path_points*scale).tolist(),
                    'insertion_path_offsets_mm':(path_points[::-1]*scale).tolist(),
                    'root_normal_toward_cavity':[0,1,0]})
        params['parts'].append(row)
    params['removal_tool']=save_mesh('Old_teeth_removal',solid(removal_tool()))
    (ROOT/'mouth_parameters.json').write_text(json.dumps(params,indent=2))
    print(json.dumps([{k:r[k] for k in ('name','status','components','volume_mm3','bbox')} for r in params['parts']],indent=2))

def preview():
    import sys
    sys.path.insert(0,str(ROOT.parent/'blender_runtime'))
    import bpy
    from mathutils import Vector
    def read(p):
        a=np.load(p);return mf.Manifold(mf.Mesh64(a['vertices'],np.asarray(a['faces'],dtype=np.uint64)))
    source=ROOT/'repaired_polished_filled.npz'
    if not source.exists():source=ROOT/'repaired_solid.npz'
    head=read(source).trim_by_plane((0,0,1),352)
    cutters=[read(OUT/(n+'.npz')) for n in ['Old_teeth_removal','Upper_teeth_insertion_sweep','Lower_teeth_insertion_sweep']]
    cleared_parts=(head-unite(cutters)).decompose()
    cleared_parts.sort(key=lambda p:p.volume(),reverse=True)
    cleared=cleared_parts[0]
    teeth=[read(OUT/(n+'.npz')) for n in ['Upper_teeth','Lower_teeth']]
    params=json.loads((ROOT/'mouth_parameters.json').read_text())
    paths=[]
    for spec in params['parts']:
        path=[];pp=np.array(spec['withdrawal_path_offsets_mm'])
        for a,b in zip(pp[:-1],pp[1:]):
            count=int(np.ceil(np.linalg.norm(b-a)/.5))+1
            path.extend(a+(b-a)*t for t in np.linspace(0,1,count))
        paths.append(path)
    collision={'arch_vs_head_mm3':[(t^cleared).volume() for t in teeth],
               'arch_pair_mm3':(teeth[0]^teeth[1]).volume(),
               'upper_withdrawal_vs_lower_max_mm3':max((teeth[0].translate(p)^teeth[1]).volume() for p in paths[0]),
               'withdrawal_vs_head_max_mm3':[max((t.translate(p)^cleared).volume() for p in path) for t,path in zip(teeth,paths)],
               'head_status':str(cleared.status()),'head_components':len(cleared.decompose()),
               'detached_old_fragments_removed':[p.volume() for p in cleared_parts[1:]],
               'head_removed_volume_mm3':head.volume()-cleared.volume()}
    (ROOT/'mouth_integration_check.json').write_text(json.dumps(collision,indent=2))
    save_mesh('Preview_cleared_head',cleared)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='MATERIAL';s.display.shading.light='STUDIO'
    s.display.shading.show_cavity=True;s.display.shading.cavity_type='WORLD'
    s.world=bpy.data.worlds.new('World');s.world.color=(.04,.05,.06)
    s.view_settings.view_transform='Standard';s.render.resolution_x=1500;s.render.resolution_y=1150;s.render.resolution_percentage=100
    for n,solid,c in [('Head',cleared,(.22,.25,.27,1)),('Upper teeth',teeth[0],(.88,.84,.73,1)),('Lower teeth',teeth[1],(.88,.84,.73,1))]:
        mesh=solid.to_mesh64();data=bpy.data.meshes.new(n);data.from_pydata(mesh.vert_properties[:,:3].tolist(),[],mesh.tri_verts.tolist())
        mat=bpy.data.materials.new(n);mat.diffuse_color=c;data.materials.append(mat)
        ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob)
        bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
        bpy.ops.object.shade_smooth_by_angle(angle=.65)
    cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.clip_end=10000;cam.data.ortho_scale=112
    for n,loc in [('front',(6,-1000,380)),('three_quarter',(300,-1000,500))]:
        cam.location=loc;cam.rotation_euler=(Vector((3,-64,380))-cam.location).to_track_quat('-Z','Y').to_euler()
        s.render.filepath=str(ROOT/('mouth_proposed_'+n+'.png'));bpy.ops.render.render(write_still=True)
    print(json.dumps(collision,indent=2))

def save_mesh(name, solid):
    OUT.mkdir(exist_ok=True)
    m = solid.to_mesh64()
    np.savez_compressed(OUT/(name+'.npz'), vertices=m.vert_properties[:,:3], faces=m.tri_verts)
    return {'name':name, 'status':str(solid.status()), 'components':len(solid.decompose()),
            'volume_mm3':solid.volume(), 'bbox':list(solid.bounding_box())}

def debug_source():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    a=np.load(ROOT/'normalized_mesh.npz');v=a['vertices'];f=a['faces']
    mesh=trimesh.Trimesh(v,f,process=False)
    fig,axs=plt.subplots(2,3,figsize=(15,9))
    for ax,x in zip(axs.ravel(),[-35,-20,0,15,30,42]):
        sec=mesh.section(plane_origin=[x,0,0],plane_normal=[1,0,0])
        for p in sec.discrete:
            ax.plot(p[:,1],p[:,2],linewidth=.65)
        ax.set_xlim(-120,-35);ax.set_ylim(358,394);ax.set_title(f'X = {x} mm');ax.grid();ax.set_aspect('equal')
        ax.set_xlabel('Y / mm');ax.set_ylabel('Z / mm')
    fig.tight_layout();fig.savefig(ROOT/'mouth_source_sections.png',dpi=150)
    fig,ax=plt.subplots(figsize=(14,6))
    tri=v[f]
    mask=(tri[:,:,2].max(1)>=360)&(tri[:,:,2].min(1)<=394)&(tri[:,:,1].min(1)<-40)&(tri[:,:,0].min(1)<60)&(tri[:,:,0].max(1)>-60)
    tri=tri[mask]
    xs=np.arange(-60,60.001,.22);zs=np.arange(360,394.001,.22)
    depths=np.full((len(zs),len(xs)),np.inf)
    for t in tri:
        u=t[:,[0,2]]
        i0=max(0,int(np.ceil((u[:,0].min()-xs[0])/.22)));i1=min(len(xs),int(np.floor((u[:,0].max()-xs[0])/.22))+1)
        j0=max(0,int(np.ceil((u[:,1].min()-zs[0])/.22)));j1=min(len(zs),int(np.floor((u[:,1].max()-zs[0])/.22))+1)
        if i0>=i1 or j0>=j1:continue
        A=np.column_stack((u[1]-u[0],u[2]-u[0]));det=np.linalg.det(A)
        if abs(det)<1e-9:continue
        xx,zz=np.meshgrid(xs[i0:i1],zs[j0:j1]);p=np.stack((xx-u[0,0],zz-u[0,1]),axis=-1)
        b=p@np.linalg.inv(A).T
        hit=(b[:,:,0]>=-1e-8)&(b[:,:,1]>=-1e-8)&(b.sum(2)<=1+1e-8)
        y=t[0,1]+b[:,:,0]*(t[1,1]-t[0,1])+b[:,:,1]*(t[2,1]-t[0,1])
        old=depths[j0:j1,i0:i1];old[hit]=np.minimum(old[hit],y[hit])
    depths[~np.isfinite(depths)]=np.nan
    im=ax.imshow(depths,origin='lower',extent=[xs[0],xs[-1],zs[0],zs[-1]],aspect='equal',vmin=-105,vmax=-45,cmap='gray')
    ax.set_xticks(np.arange(-60,61,5));ax.set_yticks(np.arange(360,395,2));ax.grid(alpha=.3)
    ax.set_xlabel('X mm');ax.set_ylabel('Z mm');fig.colorbar(im,ax=ax,label='First visible Y / mm')
    fig.tight_layout();fig.savefig(ROOT/'mouth_source_front_depth.png',dpi=180)
    np.savez_compressed(ROOT/'mouth_depth.npz',x=xs,z=zs,y=depths)

if __name__=='__main__':
    import sys
    if '--debug' in sys.argv:debug_source()
    elif '--preview' in sys.argv:preview()
    else:make_parts()
