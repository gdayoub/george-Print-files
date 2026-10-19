from pathlib import Path
import json,numpy as np,trimesh,math,zipfile,io,xml.etree.ElementTree as E,uuid,shutil
root=Path.cwd();src=root/'work/venom_lightweight/final_parts';out=root/'outputs/Venom_lightweight';out.mkdir(exist_ok=True);(out/'STL_parts').mkdir(exist_ok=True);(out/'fit_test').mkdir(exist_ok=True);(out/'engineering').mkdir(exist_ok=True)
records=json.loads((src/'manifest.json').read_text());colors={'Black':1,'White':2,'Red':3};Rwhite=np.array([[1,0,0],[0,0,1],[0,-1,0]],dtype=float);arrays={}
for r in records:
 a=np.load(src/(r['name']+'.npz'));v=a['vertices'];f=a['faces'];arrays[r['name']]=(v,f);R=Rwhite if r['color'] in ['White','Red'] else np.eye(3)
 if r['name'] in ['L_arm','R_arm']:
  R=np.array(next(c['rotation'] for c in json.loads(Path('work/orientation_trials/candidates.json').read_text()) if c['name']==r['name'] and c['orientation']=='shoulder_down'))
 pv=v@R.T;lo=pv.min(0);hi=pv.max(0);r['print_rotation']=R.tolist();r['print_min_before_translation']=lo.tolist();r['print_dimensions_mm']=(hi-lo).tolist();r['extruder']=colors[r['color']]
 # STL is a single printable part, in millimeters, oriented with its minimum Z on the bed.
 stlmesh=trimesh.Trimesh(np.asarray(pv-lo,dtype=np.float32),f,process=True)
 if not stlmesh.is_watertight:
  components=stlmesh.split(only_watertight=False);primary=max(components,key=lambda c:abs(c.volume))
  assert primary.is_watertight and all(abs(c.volume)<.001 for c in components if c is not primary),r['name']
  stlmesh=primary
 stlmesh.export(out/'STL_parts'/f"{r['id']:02}_{r['color']}_{r['name']}.stl")
# Shelf pack each color separately with a 7.5mm outer margin and 8mm spacing.
plates=[]
for color in ['Black','White','Red']:
 candidates=sorted([r for r in records if r['color']==color],key=lambda r:-r['print_dimensions_mm'][1]);local=[]
 for r in candidates:
  w,h,_=r['print_dimensions_mm'];placed=False
  for plate in local:
   for shelf in plate['shelves']:
    if h<=shelf['height']+.001 and shelf['x']+w<=241+.001:
     r['plate_xy']=[7.5+shelf['x'],7.5+shelf['y']];shelf['x']+=w+8;plate['names'].append(r['name']);placed=True;break
   if placed:break
   ny=sum(s['height']+8 for s in plate['shelves'])
   if ny+h<=241+.001:
    plate['shelves'].append(dict(x=w+8,y=ny,height=h));r['plate_xy']=[7.5,7.5+ny];plate['names'].append(r['name']);placed=True;break
  if not placed:
   assert w<=241+.001 and h<=241+.001 and r['print_dimensions_mm'][2]<=244,(r['name'],r['print_dimensions_mm']);plate=dict(color=color,shelves=[dict(x=w+8,y=0,height=h)],names=[r['name']]);local.append(plate);r['plate_xy']=[7.5,7.5]
 for plate in local:plate['id']=len(plates)+1;plates.append(plate)
for plate in plates:
 group=[r for r in records if r['name'] in plate['names']]
 lo=np.min([r['plate_xy'] for r in group],axis=0);hi=np.max([np.array(r['plate_xy'])+r['print_dimensions_mm'][:2] for r in group],axis=0)
 delta=np.array([128,128])-(lo+hi)/2
 for r in group:r['plate_xy']=(np.array(r['plate_xy'])+delta).tolist()
cols=math.ceil(math.sqrt(len(plates)))
for plate in plates:
 plate['origin']=[((plate['id']-1)%cols)*307.2,-((plate['id']-1)//cols)*307.2,0]
 for name in plate['names']:
  r=next(x for x in records if x['name']==name);r['plate']=plate['id'];T=np.eye(4);T[:3,:3]=r['print_rotation'];T[:3,3]=np.array([*r['plate_xy'],0])+plate['origin']-r['print_min_before_translation'];r['print_transform']=T.tolist()
# Uniformly configure a single-color-per-plate PLA project. No sliced G-code is included.
with zipfile.ZipFile(root/'work/color_trials/native3.3mf') as z:base=json.loads(z.read('Metadata/project_settings.config'))
base.update(wall_loops='2',top_shell_layers='4',top_shell_thickness='0.8',bottom_shell_layers='3',sparse_infill_pattern='lightning',sparse_infill_density='10%',outer_wall_speed=['120','120'],outer_wall_acceleration=['3000','3000'])
base.update(filament_self_index=['1','2','3'],filament_nozzle_map=['1']*3,filament_volume_map=['0']*3,extruder_nozzle_stats=['Standard#1'],print_settings_id='Venom Shelf 0.20mm Lightweight',print_compatible_printers=['Bambu Lab P1S 0.4 nozzle','Bambu Lab P2S 0.4 nozzle'])
base['different_settings_to_system']=[';'.join(sorted(base.keys()))]*5
ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';pns='http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
def matstr(T):return ' '.join(f'{x:.12g}' for x in np.asarray(T)[:3,:].T.reshape(-1))
def xmlbytes(e):return E.tostring(e,encoding='utf-8',xml_declaration=True)
def project(path,rs,pls,arr):
 main=E.Element('model',{'unit':'millimeter','xmlns':ns,'xmlns:p':pns,'requiredextensions':'p','xmlns:BambuStudio':'http://schemas.bambulab.com/package/2021'});E.SubElement(main,'metadata',{'name':'Application'}).text='BambuStudio-02.08.02.61';E.SubElement(main,'metadata',{'name':'BambuStudio:3mfVersion'}).text='1';E.SubElement(main,'metadata',{'name':'Title'}).text=path.stem;E.SubElement(main,'metadata',{'name':'Description'}).text='Prepared multipart model; review and slice with the actual printer and filament profile. No G-code included.';resources=E.SubElement(main,'resources');build=E.SubElement(main,'build',{'p:UUID':str(uuid.uuid4())});cfg=E.Element('config');ass=E.SubElement(cfg,'assemble');rels=E.Element('Relationships',{'xmlns':'http://schemas.openxmlformats.org/package/2006/relationships'})
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for i,r in enumerate(rs):
   oid=2*i+2;mid=oid-1;r['object_id']=oid;v,f=arr[r['name']];filename=f'3D/Objects/object_{mid}.model';obj=E.SubElement(resources,'object',{'id':str(oid),'type':'model','p:UUID':str(uuid.uuid4())});co=E.SubElement(obj,'components');E.SubElement(co,'component',{'p:path':'/'+filename,'objectid':str(mid),'transform':matstr(np.eye(4)),'p:UUID':str(uuid.uuid4())});E.SubElement(build,'item',{'objectid':str(oid),'transform':matstr(r['print_transform']),'p:UUID':str(uuid.uuid4())});E.SubElement(rels,'Relationship',{'Target':'/'+filename,'Id':f'rel-{i+1}','Type':'http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel'})
   with z.open(filename,'w') as raw:
    with io.TextIOWrapper(raw,encoding='utf-8',newline='\n') as stream:
     stream.write(f'<?xml version="1.0" encoding="UTF-8"?><model xmlns="{ns}" xmlns:p="{pns}" unit="millimeter"><resources><object id="{mid}" type="model" p:UUID="{uuid.uuid4()}"><mesh><vertices>\n')
     for start in range(0,len(v),10000):stream.write(''.join('<vertex x="%.10g" y="%.10g" z="%.10g"/>\n'%tuple(x) for x in v[start:start+10000]))
     stream.write('</vertices><triangles>\n')
     for start in range(0,len(f),10000):stream.write(''.join('<triangle v1="%d" v2="%d" v3="%d"/>\n'%tuple(x) for x in f[start:start+10000]))
     stream.write('</triangles></mesh></object></resources><build/></model>')
   c=E.SubElement(cfg,'object',{'id':str(oid)});E.SubElement(c,'metadata',{'key':'name','value':r['name']});E.SubElement(c,'metadata',{'key':'extruder','value':str(r['extruder'])});E.SubElement(c,'metadata',{'face_count':str(len(f))});E.SubElement(c,'metadata',{'key':'enable_support','value':'1'})
   if r['name'] in ['L_leg','R_leg']:E.SubElement(c,'metadata',{'key':'sparse_infill_density','value':'2%'});E.SubElement(c,'metadata',{'key':'sparse_infill_pattern','value':'gyroid'})
   part=E.SubElement(c,'part',{'id':str(mid),'subtype':'normal_part'});E.SubElement(part,'metadata',{'key':'name','value':r['name']});E.SubElement(part,'metadata',{'key':'matrix','value':'1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1'});E.SubElement(part,'mesh_stat',{'face_count':str(len(f)),'edges_fixed':'0','degenerate_facets':'0','facets_removed':'0','facets_reversed':'0','backwards_edges':'0'});E.SubElement(ass,'assemble_item',{'object_id':str(oid),'instance_id':'0','transform':matstr(np.eye(4)),'offset':'0 0 0'})
  for pl in pls:
   e=E.SubElement(cfg,'plate')
   for k,val in [('plater_id',str(pl['id'])),('plater_name',pl['color']),('locked','false'),('filament_map_mode','Auto For Flush')]:E.SubElement(e,'metadata',{'key':k,'value':val})
   for name in pl['names']:
    r=next(x for x in rs if x['name']==name);mi=E.SubElement(e,'model_instance')
    for k,val in [('object_id',str(r['object_id'])),('instance_id','0'),('identify_id',str(100+r['object_id']))]:E.SubElement(mi,'metadata',{'key':k,'value':val})
  z.writestr('3D/3dmodel.model',xmlbytes(main));z.writestr('3D/_rels/3dmodel.model.rels',xmlbytes(rels));z.writestr('Metadata/model_settings.config',xmlbytes(cfg));z.writestr('Metadata/project_settings.config',json.dumps(base,indent=2));z.writestr('Metadata/cut_information.xml','<?xml version="1.0"?><objects/>');z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="png" ContentType="image/png"/></Types>');z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
project(out/'Venom_lightweight_base.3mf',records,plates,arrays)
(out/'engineering/parts_and_plates.json').write_text(json.dumps(dict(parts=records,plates=plates),indent=2))
for filename in ['joints.json','inserts.json','assembly_intersections.json','smoothing_report.json']:shutil.copy2(src/filename,out/'engineering'/filename)
print('Packaged lightweight 12 parts /',len(plates),'plates',flush=True)
