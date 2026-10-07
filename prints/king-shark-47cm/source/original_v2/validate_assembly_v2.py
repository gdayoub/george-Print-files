"""Independent validation of the final King Shark glue assembly.

Reads exported final geometry, not the engineer's in-memory operands. Rigid
joint paths are checked until the pair's projection intervals fully separate.
Dental paths use the actual angled installation polylines. A result can pass
only after every expected part, joint and insert has been inspected.
"""
from pathlib import Path
import argparse
import json
import time
import numpy as np
import manifold3d as mf

ROOT=Path(__file__).resolve().parent
NUMERICAL_TOLERANCE_MM3=.02

def save(path, solid):
    m=solid.to_mesh64()
    np.savez_compressed(path,vertices=m.vert_properties[:,:3],faces=m.tri_verts)

def load(path):
    a=np.load(path)
    vertices=np.ascontiguousarray(a['vertices'],dtype=np.float64)
    faces=np.ascontiguousarray(a['faces'],dtype=np.uint64)
    solid=mf.Manifold(mf.Mesh64(vertices,faces))
    if solid.status()!=mf.Error.NoError:
        raise RuntimeError(f'{path.name}: {solid.status()}')
    return solid,vertices

def disjoint(a,b):
    aa=np.asarray(a.bounding_box()).reshape(2,3)
    bb=np.asarray(b.bounding_box()).reshape(2,3)
    return bool(np.any(aa[1]<bb[0]) or np.any(bb[1]<aa[0]))

def overlap(a,b):
    if disjoint(a,b):return 0.0,None
    intersection=a^b
    return max(0.0,float(intersection.volume())),intersection

def sample_polyline(points,spacing):
    points=np.asarray(points,dtype=float)
    if points.ndim!=2 or points.shape[1]!=3 or len(points)<2:
        raise ValueError('A path requires at least two XYZ offsets')
    if not np.allclose(points[0],0,atol=1e-8):
        raise ValueError('A withdrawal path must begin at the seated offset [0,0,0]')
    samples=[points[0]]
    for a,b in zip(points[:-1],points[1:]):
        count=max(1,int(np.ceil(np.linalg.norm(b-a)/spacing)))
        samples.extend(a+(b-a)*f for f in np.linspace(0,1,count+1)[1:])
    return samples

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--parts',type=Path,default=ROOT/'final_parts')
    ap.add_argument('--output',type=Path,default=ROOT/'assembly_validation.json')
    args=ap.parse_args();started=time.time()
    manifest_path=args.parts/'manifest.json'
    if not manifest_path.is_file():
        raise SystemExit('Final manifest is not ready; no validation result was written.')
    manifest=json.loads(manifest_path.read_text())
    joints=json.loads((args.parts/'joints.json').read_text())
    inserts=json.loads((args.parts/'inserts.json').read_text())
    mouth=json.loads((ROOT/'mouth_parameters.json').read_text())
    dental_specs={p['name']:p for p in mouth['parts']}
    parts={};vertices={};mesh_rows=[]
    diagnostics=ROOT/'assembly_validation_diagnostics'
    report={'status':'running','source_directory':str(args.parts.resolve()),
            'method':'Exported Manifold meshes; exact boolean volume with conservative bounding-box rejection.',
            'numerical_volume_tolerance_mm3':NUMERICAL_TOLERANCE_MM3,
            'physical_print_tested':False,
            'path_scope':'Connector pair motion. Other attached body parts are not treated as independent stationary obstacles when their host moves.',
            'meshes':mesh_rows,'seated_pairs':[],'joint_paths':[],'insert_paths':[],
            'dental_assembly_order':['Lower_teeth','Upper_teeth'],
            'failures':[]}
    def failure(message):
        report['failures'].append(message)
    def diagnostic(label,moving,fixed,offset,intersection):
        diagnostics.mkdir(exist_ok=True)
        if intersection is not None and not intersection.is_empty():
            save(diagnostics/(label+'_intersection.npz'),intersection)
        save(diagnostics/(label+'_moving_at_failure.npz'),moving.translate(offset))
        save(diagnostics/(label+'_fixed.npz'),fixed)
    for row in manifest:
        name=row['name'];solid,v=load(args.parts/(name+'.npz'))
        parts[name]=solid;vertices[name]=v
        rec={'name':name,'triangles':solid.num_tri(),'volume_mm3':solid.volume(),
             'manifold_status':str(solid.status()),'components':len(solid.decompose())}
        mesh_rows.append(rec)
        if rec['components']!=1:failure(f'{name}: {rec["components"]} disconnected components')
    required={'Torso','Shorts','L_arm','R_arm','L_leg','R_leg','Dorsal_fin',
              'Upper_teeth','Lower_teeth','Shorts_panel_L','Shorts_panel_R'}
    if required!=set(parts):failure(f'Unexpected part inventory: missing={sorted(required-set(parts))}; extra={sorted(set(parts)-required)}')
    if len(joints)!=6:failure(f'Expected six main joints, found {len(joints)}')
    if len(inserts)!=4:failure(f'Expected four color inserts, found {len(inserts)}')
    names=list(parts)
    for i,a in enumerate(names):
        for b in names[i+1:]:
            vol,intersection=overlap(parts[a],parts[b])
            report['seated_pairs'].append({'a':a,'b':b,'intersection_volume_mm3':vol,'passed':vol<=NUMERICAL_TOLERANCE_MM3})
            if vol>NUMERICAL_TOLERANCE_MM3:
                failure(f'Seated overlap {a}/{b}: {vol:.6f} mm³')
                diagnostic(f'seated_{a}_{b}',parts[a],parts[b],np.zeros(3),intersection)
    print('SEATED',len(report['seated_pairs']),'pairs; max',max(r['intersection_volume_mm3'] for r in report['seated_pairs']),flush=True)

    def validate_path(label,moving_name,fixed_name,path,spacing):
        samples=sample_polyline(path,spacing)
        worst=0.0;worst_offset=[0.,0.,0.];first_failure=None;worst_intersection=None
        moving=parts[moving_name];fixed=parts[fixed_name]
        positive_samples=0
        for i,offset in enumerate(samples):
            vol,intersection=overlap(moving.translate(offset),fixed)
            if vol>1e-8:positive_samples+=1
            if vol>worst:
                worst=vol;worst_offset=offset.tolist();worst_intersection=intersection
            if first_failure is None and vol>NUMERICAL_TOLERANCE_MM3:
                first_failure={'sample_index':i,'offset_mm':offset.tolist(),'interference_mm3':vol}
        passed=worst<=NUMERICAL_TOLERANCE_MM3
        row={'name':label,'moving_part':moving_name,'fixed_part':fixed_name,
             'withdrawal_path_offsets_mm':np.asarray(path).tolist(),
             'max_sample_spacing_mm':spacing,'sample_count':len(samples),
             'max_interference_mm3':worst,'worst_offset_mm':worst_offset,
             'positive_volume_samples':positive_samples,'first_failed_sample':first_failure,
             'passed':passed}
        if not passed:
            failure(f'Path {label}: {worst:.6f} mm³ interference at {worst_offset}')
            diagnostic(label,moving,fixed,np.array(worst_offset),worst_intersection)
        print('PATH',label,'max',worst,'samples',len(samples),flush=True)
        return row

    for joint in joints:
        male=joint['male'];female=joint['female'];n=np.asarray(joint['normal'],float)
        if np.linalg.norm(n)<1e-9:raise ValueError(f'Zero joint normal: {joint["id"]}')
        n/=np.linalg.norm(n)
        separation=float(max(vertices[male]@n)-min(vertices[female]@n))+2.0
        distance=max(separation,float(joint['length_mm'])+3.0)
        if distance>600:raise ValueError(f'Unexpectedly long joint path: {joint["id"]}: {distance}')
        row=validate_path(joint['id'],female,male,[[0,0,0],n*distance],1.0)
        row.update({'male':male,'female':female,'normal':n.tolist(),
                    'full_projection_separation_distance_mm':separation,
                    'tested_distance_mm':distance,'peg_length_mm':joint['length_mm']})
        report['joint_paths'].append(row)

    for inset in inserts:
        name=inset['name'];host=inset['host']
        if name in dental_specs:
            path=inset.get('withdrawal_path_offsets_mm',dental_specs[name]['withdrawal_path_offsets_mm'])
            if not np.allclose(path,dental_specs[name]['withdrawal_path_offsets_mm'],atol=1e-7):
                failure(f'{name}: engineer path differs from dental design path')
            row=validate_path(name,name,host,path,.5)
        else:
            direction=np.asarray(inset['direction'],float);direction/=np.linalg.norm(direction)
            separation=float(max(vertices[host]@direction)-min(vertices[name]@direction))+2.0
            distance=max(65.0,separation)
            row=validate_path(name,name,host,[[0,0,0],direction*distance],1.0)
            row['full_projection_separation_distance_mm']=separation
        report['insert_paths'].append(row)
    report['upper_insertion_with_lower_installed']=validate_path(
        'Upper_teeth_vs_installed_lower','Upper_teeth','Lower_teeth',
        dental_specs['Upper_teeth']['withdrawal_path_offsets_mm'],.5)
    report['status']='passed' if not report['failures'] else 'failed'
    report['checks']={'meshes':len(mesh_rows),'seated_pairs':len(report['seated_pairs']),
                      'joint_paths':len(report['joint_paths']),'insert_paths':len(report['insert_paths']),
                      'inter_arch_paths':1}
    report['duration_seconds']=time.time()-started
    args.output.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'status':report['status'],'checks':report['checks'],
                      'failures':report['failures'],'duration_seconds':report['duration_seconds']},indent=2),flush=True)
    if report['failures']:raise SystemExit(2)

if __name__=='__main__':main()
