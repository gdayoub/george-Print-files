from pathlib import Path
import numpy as np, manifold3d as mf, trimesh, json, hashlib, io, time
ROOT=Path(__file__).resolve().parent
SRC=ROOT.parents[1]/'king_shark_v2/final_parts'
def load(path):
 d=np.load(path);return mf.Manifold(mf.Mesh64(np.ascontiguousarray(d['vertices'],dtype=np.float64),np.ascontiguousarray(d['faces'],dtype=np.uint64)))
def mesh(s):
 d=s.to_mesh64();return trimesh.Trimesh(d.vert_properties[:,:3],d.tri_verts,process=False)
def log(*s):print(*s,flush=True)
def save(s,name):
 a=s.to_mesh64();np.savez_compressed(ROOT/(name+'.npz'),vertices=a.vert_properties[:,:3],faces=a.tri_verts)
 # The STL is export-rounded then revalidated; no post-export hole repair.
 tm=mesh(s);dat=tm.export(file_type='stl');loaded=trimesh.load_mesh(io.BytesIO(dat),file_type='stl',process=True)
 check=mf.Manifold(mf.Mesh64(np.ascontiguousarray(loaded.vertices),np.ascontiguousarray(loaded.faces,dtype=np.uint64)))
 assert loaded.is_watertight and loaded.is_winding_consistent and check.status()==mf.Error.NoError,(name,'STL roundtrip')
 (ROOT/(name+'.stl')).write_bytes(dat)
 return tm,dict(stl_sha256=hashlib.sha256(dat).hexdigest(),stl_roundtrip_watertight=True,stl_roundtrip_manifold_status=str(check.status()),stl_roundtrip_components=len(check.decompose()))
log('LOAD')
torso=load(SRC/'Torso.npz')
# Use the successful sculpt, removing neck/body and old shoulder keys.
head=torso.trim_by_plane((0,0,1),350).trim_by_plane((0,-1,0),-12).trim_by_plane((1,0,0),-85).trim_by_plane((-1,0,0),-85)
log('HEAD',head.num_tri(),len(head.decompose()))
for name in ['Upper_teeth','Lower_teeth']:
 tooth=load(SRC/(name+'.npz'))
 # 0.32mm before reduction joins the old 0.20mm glue clearances and blunts
 # the small tips slightly for a one-colour functional print.
 log('THICKEN',name)
 tooth=tooth.minkowski_sum(mf.Manifold.sphere(.32,8))
 head=head+tooth
log('JOINED_HEAD',head.num_tri(),len(head.decompose()))
# Modest depth relief, same successful front-view x/z proportion.
head=head.scale((.70,.55,.70)).translate((0,-20,-245))
# Broad clean elliptical liner, explicit 2.6mm normal offset, flat 2.8mm floor.
# Offset rather than separately scaling ellipses preserves minimum normal wall.
profile=mf.CrossSection.circle(1,192).scale((70,48)).translate((0,10))
inside=profile.offset(-2.6,join_type=mf.JoinType.Round,circular_segments=192)
outer=mf.Manifold.extrude(profile,57)
cavity=mf.Manifold.extrude(inside,70).translate((0,0,2.8))
liner=outer-cavity
# Subtract from decorative head first; separate unbroken liner seals the mouth.
# Rounded crop removes cut-off neck/shoulder corners while keeping the real face.
mask=mf.Manifold.sphere(1,96).scale((58,52,34)).translate((0,-46,31))
face=(head^mask)-cavity
combined=(liner+face).as_original().simplify(.012)
# Remove tiny detached former sculpt fragments; none can be silently delivered.
components=combined.decompose(); log('COMPONENTS',[(c.volume(),c.num_tri()) for c in components])
removed=[]
if len(components)>1:
 main=max(components,key=lambda a:a.volume());removed=[dict(volume_mm3=c.volume(),triangles=c.num_tri()) for c in components if c is not main]
 combined=main
# Keep actual analytic mounting/base plane exactly at Z0. Cap any numerical below-floor detail.
combined=combined.trim_by_plane((0,0,1),0).as_original().simplify(.00005)
assert combined.status()==mf.Error.NoError and len(combined.decompose())==1
# Boolean unions can leave edge-only tooth contacts which STL welding exposes.
# Add tiny local solid bridges centred on those contacts, outside the cavity.
local_bridges=[]
for attempt in range(5):
    tm=mesh(combined)
    rt=trimesh.load_mesh(io.BytesIO(tm.export(file_type='stl')),file_type='stl',process=True)
    counts=np.bincount(rt.edges_unique_inverse);bad=np.flatnonzero(counts!=2)
    if not len(bad):break
    for i in bad:
        edge=rt.vertices[rt.edges_unique[i]];center=edge.mean(axis=0);radius=float(np.linalg.norm(edge[1]-edge[0])/2+.11)
        assert radius<.75,(center,radius,'nonlocal defect')
        combined=combined+mf.Manifold.sphere(radius,16).translate(tuple(center))
        local_bridges.append(dict(center_mm=center.tolist(),radius_mm=radius))
    combined=combined.as_original().simplify(.00005)
else:raise RuntimeError('STL contacts did not resolve')
log('LOCAL_CONTACT_BRIDGES',local_bridges)
# Prove that the full independent liner and its floor survive and the cavity is clear.
# Original cavity above floor is tested with a tolerance inset to ignore touching boundaries.
interior=mf.Manifold.extrude(inside.offset(-.03),67).translate((0,0,2.83))
leak=(liner-combined).volume();obstruction=(interior^combined).volume()
log('CHECKS liner_missing',leak,'obstruction',obstruction)
# Numerical simplification affects only sub-.012mm surfaces. Quantify rather than claim exact.
assert leak<1 and obstruction<1,(leak,obstruction)
# Conservative 2.4mm uninterrupted wall ring inside the nominal 2.6mm liner.
protected_ring=profile.offset(-.03)-profile.offset(-2.43)
protected_wall=mf.Manifold.extrude(protected_ring,54.19).translate((0,0,2.8))
protected_floor=mf.Manifold.extrude(profile.offset(-.03),2.8)
wall_missing=(protected_wall-combined).volume()
floor_missing=(protected_floor-combined).volume()
assert wall_missing<.001 and floor_missing<.001,(wall_missing,floor_missing)
log('MINIMUM_WALL_FLOOR_PROOF',wall_missing,floor_missing)
tm,stl=save(combined,'King_Shark_Catchall_Bowl')
rec=dict(name='King_Shark_Catchall_Bowl',color='Black',mesh='King_Shark_Catchall_Bowl.npz',settings={'sparse_infill_pattern':'gyroid','sparse_infill_density':'5%','wall_loops':'3','top_shell_layers':'4','bottom_shell_layers':'4'})
(ROOT/'manifest.json').write_text(json.dumps([rec],indent=2))
report=dict(design='King Shark catchall bowl prototype',purpose='Keys and accessories; not specified as foodware',source_geometry=[str(SRC/n) for n in ['Torso.npz','Upper_teeth.npz','Lower_teeth.npz']],source_hashes={n:hashlib.sha256((SRC/n).read_bytes()).hexdigest() for n in ['Torso.npz','Upper_teeth.npz','Lower_teeth.npz']},units='millimetres',orientation='upright, flat bottom on Z=0; front -Y',dimensions_mm=tm.extents.tolist(),bounds_mm=tm.bounds.tolist(),volume_mm3=tm.volume,triangles=len(tm.faces),watertight=tm.is_watertight,winding_consistent=tm.is_winding_consistent,manifold_status=str(combined.status()),components=len(combined.decompose()),nominal_liner_normal_wall_mm=2.6,verified_minimum_liner_wall_mm=2.4,minimum_wall_band_missing_volume_mm3=wall_missing,protected_2_8mm_floor_missing_volume_mm3=floor_missing,nominal_floor_mm=2.8,internal_clear_height_mm=54.2,internal_mouth_bounds_mm=inside.bounds(),inner_cross_section_area_mm2=inside.area(),capacity_ml_approx=inside.area()*54.2/1000,independent_liner_missing_volume_after_simplification_mm3=leak,interior_obstruction_mm3=obstruction,maximum_simplification_tolerance_mm=.012,removed_small_fragments=removed,local_contact_bridges=local_bridges,geometry_operations=['Successful printed head cropped above original Z350 and in X to +/-85; rear Y12','Dental arches expanded0.32mm to join print-clearance gaps into one-color relief','X/Z70%, depth55%; translated into bowl front','Independent 2.6mm normal-offset liner and 2.8mm floor','Decorative face cut clear of inner cavity before liner union'],support_and_time_status='Not yet sliced; root task will optimize settings and verify supports/time',physical_print_test=False,**stl)
(ROOT/'engineering_validation.json').write_text(json.dumps(report,indent=2))
log(json.dumps(report,indent=2))
