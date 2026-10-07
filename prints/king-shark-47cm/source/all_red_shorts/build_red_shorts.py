"""Restore the original cloth sides without rebuilding any printed mating interface."""
from pathlib import Path
import sys, json, hashlib, shutil
import numpy as np
import manifold3d as mf

ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'king_shark_v2'
sys.path.insert(0,str(OLD))
import engineer_v2 as e

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'final_parts';out.mkdir(parents=True,exist_ok=True)
    old=OLD/'final_parts'
    originals={p.name:digest(p) for p in old.glob('*.npz')}
    whole=e.load(OLD/'repaired_polished_filled.npz')
    upper=whole
    for sign in [1,-1]:
        arm=e.largest(e.plane(upper,(sign,0,0),85))
        upper=upper-arm
    waist,_,_=e.seam_function('waist_skin_seam',-6.5)
    lower=e.main(upper^e.heightfield_below(waist))
    for sign,key in [(1,'hem_positive_x'),(-1,'hem_negative_x')]:
        fn,_,_=e.seam_function(key,.7)
        knife=e.plane(e.heightfield_below(fn),(sign,0,0),0)
        lower=e.main(lower-knife)
    e.save(lower,ROOT/'original_unpaneled_short_shape.npz')
    original=e.load(old/'Shorts.npz')
    # Every original connector fits inside |X|<72. Original panel cavities begin
    # outside |X|=74.82. This overlap plane is safely between those two regions.
    limit=74.5
    sides=e.union([e.plane(lower,(sign,0,0),limit) for sign in [1,-1]])
    combined=e.main((original+sides).as_original().simplify(.00005))
    tm=e.mesh(combined)
    assert combined.status()==mf.Error.NoError
    assert len(combined.decompose())==1 and tm.is_watertight and tm.is_winding_consistent
    e.save(combined,out/'Shorts.npz')
    central=lambda s:e.plane(e.plane(s,(1,0,0),-74),( -1,0,0),-74)
    oldcenter=central(original);newcenter=central(combined)
    lost=max(0.,(original-combined).volume())
    center_diff=max(0.,(oldcenter-newcenter).volume())+max(0.,(newcenter-oldcenter).volume())
    assert lost<.02 and center_diff<.02,(lost,center_diff)
    reports=[]
    rows=json.loads((old/'manifest.json').read_text())
    for row in rows:
        name=row['name']
        if name.startswith('Shorts_panel_'):continue
        if name=='Shorts':
            row.update(color='Red',settings={'sparse_infill_pattern':'gyroid','sparse_infill_density':'3%'},
                       triangles=combined.num_tri(),volume_mm3=combined.volume(),
                       bounds_mm=tm.bounds.tolist(),dimensions_mm=tm.extents.tolist(),
                       components=1,manifold_status=str(combined.status()),watertight=True,winding_consistent=True)
        else:
            shutil.copy2(old/(name+'.npz'),out/(name+'.npz'))
            assert digest(out/(name+'.npz'))==originals[name+'.npz']
        reports.append(row)
    (out/'manifest.json').write_text(json.dumps(reports,indent=2))
    shutil.copy2(old/'joints.json',out/'joints.json')
    inserts=[r for r in json.loads((old/'inserts.json').read_text()) if not r['name'].startswith('Shorts_panel_')]
    (out/'inserts.json').write_text(json.dumps(inserts,indent=2))
    assert originals=={p.name:digest(p) for p in old.glob('*.npz')}
    report=dict(original_geometry_sha256=originals,original_files_untouched=True,
                restored_side_region_abs_x_min_mm=limit,protected_center_abs_x_max_mm=74,
                original_material_removed_mm3=lost,central_symmetric_difference_mm3=center_diff,
                new_shorts_volume_mm3=combined.volume(),added_material_design_volume_mm3=combined.volume()-original.volume(),
                triangles=combined.num_tri(),components=len(combined.decompose()),
                dimensions_mm=tm.extents.tolist(),manifold_status=str(combined.status()),
                other_eight_part_files_byte_identical=True,joint_definition_file_byte_identical=digest(out/'joints.json')==digest(old/'joints.json'))
    (ROOT/'geometry_repair.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':main()
