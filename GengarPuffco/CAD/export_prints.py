from pathlib import Path
import json,zipfile,xml.etree.ElementTree as E,shutil
import numpy as np,trimesh
R=Path(__file__).resolve().parent.parent;O=R/'CAD/outputs';D=R/'Print/Geometry';D.mkdir(exist_ok=True,parents=True)
manifest=json.loads((O/'manifest.json').read_text());checks=json.loads((R/'Reports/geometry_validation.json').read_text())
assert not checks['head_collisions'] and not checks['bottom_collisions']
assert all(x['watertight'] for x in checks['new_meshes'].values())
assert all(v==1 for v in checks['combined_components'].values())
meshes={}
for e in manifest:
 a=np.load(O/e['file']);meshes[e['name']]=trimesh.Trimesh(a['vertices'],a['faces'],process=False)
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';E.register_namespace('',NS);q=lambda x:'{'+NS+'}'+x
def add(p,t,a=None):return E.SubElement(p,q(t),a or {})
reports={}
def export(filename,entries,assembled=False,mono=False,custom=None):
 rt=E.Element(q('model'),{'unit':'millimeter','xml:lang':'en-US'});add(rt,'metadata',{'name':'Title'}).text=filename
 add(rt,'metadata',{'name':'Description'}).text='Local Gengar case prototype. Exact Core Case base/lid by ROADBLOCK; Gengar bowl exterior by tom3Dmodel. Original source metadata retained in Foundations.'
 res=add(rt,'resources');mats=add(res,'basematerials',{'id':'1'})
 for n,c in [('Black','#1C1B26FF'),('Red','#CE1834FF'),('Pink','#F481B3FF')]:add(mats,'base',{'name':n,'displaycolor':c})
 build=add(rt,'build');cfg=E.Element('config');ids={};report={};exported={}
 for i,e in enumerate(entries,2):
  n=e['name'];m=(custom or meshes)[n];ids[n]=i;exported[n]=m
  ci=0 if mono else (1 if 'red' in n else 2 if 'pink' in n else 0)
  ob=add(res,'object',{'id':str(i),'name':n,'type':'model','pid':'1','pindex':str(ci)});me=add(ob,'mesh');vs=add(me,'vertices');fs=add(me,'triangles')
  for v in m.vertices:add(vs,'vertex',{k:repr(float(a)) for k,a in zip('xyz',v)})
  for f in m.faces:add(fs,'triangle',{k:str(int(a)) for k,a in zip(['v1','v2','v3'],f)})
 for i,g in enumerate(['body','head','bottom','test'],30):
  es=[e for e in entries if e['group']==g]
  if not es:continue
  T=np.eye(4)
  if not assembled and g=='head':T=trimesh.transformations.rotation_matrix(np.pi,[1,0,0])
  m=trimesh.util.concatenate([exported[e['name']] for e in es]);mm=m.copy();mm.apply_transform(T)
  if not assembled:T[:3,3]=[128-(mm.bounds[:,0].mean()),128-(mm.bounds[:,1].mean()),-mm.bounds[0,2]]
  ob=add(res,'object',{'id':str(i),'name':g.upper(),'type':'model'});cs=add(ob,'components');cf=E.SubElement(cfg,'object',{'id':str(i)});E.SubElement(cf,'metadata',{'key':'name','value':g.upper()})
  for e in es:
   n=e['name'];add(cs,'component',{'objectid':str(ids[n])});part=E.SubElement(cf,'part',{'id':str(ids[n]),'subtype':'normal_part'})
   ci=1 if mono else 2 if 'red' in n else 3 if 'pink' in n else 1
   for k,v in [('name',n),('extruder',str(ci)),('wall_loops','4')]:E.SubElement(part,'metadata',{'key':k,'value':v})
  vals=list(T[:3,:3].T.flat)+list(T[:3,3]);add(build,'item',{'objectid':str(i),'transform':' '.join(repr(float(x)) for x in vals)})
  report[g]={'assembled_bounds_mm':m.bounds.tolist(),'print_transform':T.tolist(),'parts':[e['name'] for e in es]}
 content={'[Content_Types].xml':'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/xml"/></Types>',
 '_rels/.rels':'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>',
 '3D/3dmodel.model':E.tostring(rt,encoding='utf-8',xml_declaration=True),'Metadata/model_settings.config':E.tostring(cfg,encoding='utf-8',xml_declaration=True)}
 with zipfile.ZipFile(D/filename,'w',zipfile.ZIP_DEFLATED) as z:
  for n,data in content.items():z.writestr(n,data)
 with zipfile.ZipFile(D/filename) as z:
  assert z.testzip() is None;r=E.fromstring(z.read('3D/3dmodel.model'))
  for e in entries:
   n=e['name']
   if not n.startswith('ORIGINAL'):continue
   ob=next(o for o in r.find(q('resources')).findall(q('object')) if o.get('name')==n);me=ob.find(q('mesh'))
   v=np.array([[float(a.get(k)) for k in 'xyz'] for a in me.find(q('vertices'))]);f=np.array([[int(a.get(k)) for k in ['v1','v2','v3']] for a in me.find(q('triangles'))])
   assert np.array_equal(v,meshes[n].vertices) and np.array_equal(f,meshes[n].faces)
   role='base' if 'BASE' in n else 'lid';a=np.load(R/'Foundations'/f'{role}_exact.npz')
   restored=trimesh.transform_points(v,np.linalg.inv(checks[role+'_transform']))
   err=float(np.max(np.abs(restored-a['vertices'])));assert err<1e-10;assert np.array_equal(f,a['faces'])
   report[n]={'scale':1,'max_source_vertex_error_mm':err,'triangles_identical':True}
 reports[filename]=report
for g,fn in [('body','01_BODY_EXACT_FOUNDATION.3mf'),('head','02_GENGAR_HEAD_COLOR.3mf'),('bottom','03_BOTTOM_CAP.3mf')]:export(fn,[e for e in manifest if e['group']==g])
export('02b_GENGAR_HEAD_SINGLE_COLOR.3mf',[e for e in manifest if e['group']=='head'],mono=True)
export('ASSEMBLED_VIEW_ONLY.3mf',manifest,assembled=True)
# Full-height unmodified foundation base/lid test: no decorative material.
export('00a_ORIGINAL_BASE_ONLY.3mf',[e for e in manifest if e['name']=='ORIGINAL_CASE_BASE_EXACT'])
export('00b_ORIGINAL_LID_ONLY.3mf',[e for e in manifest if e['name']=='ORIGINAL_CASE_LID_EXACT'])
(R/'Reports/export_verification.json').write_text(json.dumps(reports,indent=2))
print('EXPORTED: exact foundation vertices and triangles verified in final geometry 3MFs.')
