from pathlib import Path
import sys,json,zipfile,shutil,hashlib
import xml.etree.ElementTree as ET
for parent in [Path(__file__).parent]+list(Path(__file__).parents):
 if (parent/'.deps').is_dir():sys.path.insert(0,str(parent/'.deps'));break
import numpy as np,trimesh
ROOT=Path(__file__).parent;OUT=ROOT/'outputs';KIT=ROOT.parent/'Print'/'Geometry'
REF=ROOT.parent/'Foundations'
KIT.mkdir(exist_ok=True,parents=True)
validation=json.loads((OUT/'validation.json').read_text())
assert not validation['head_motion_collisions'] and not validation['bottom_motion_collisions']
assert all(v['watertight'] for v in validation['new_meshes'].values())
manifest=json.loads((OUT/'geometry_manifest.json').read_text())
meshes={e['name']:trimesh.load_mesh(OUT/e['path']) for e in manifest if e['group']!='jar' and not e['name'].startswith('ORIGINAL')}
for name,role in [('ORIGINAL_CASE_BASE_EXACT','base'),('ORIGINAL_CASE_LID_EXACT','lid')]:
 a=np.load(REF/(role+'_exact.npz'))
 m=trimesh.Trimesh(a['vertices'],a['faces'],process=False)
 m.apply_transform(np.array(validation['source_'+role+'_transform']))
 meshes[name]=m
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',NS)
q=lambda s:'{'+NS+'}'+s
def add(p,t,attrs=None):return ET.SubElement(p,q(t),attrs or {})
def write_3mf(path,entries,assembled=False):
 root=ET.Element(q('model'),{'unit':'millimeter','xml:lang':'en-US'})
 for k,v in [('Title',path.stem),('Description','Venom exterior added around exact Core_Case.3mf base and lid. Original case by ROADBLOCK; source metadata retained in the included original file.'),('Application','Venom local mesh CAD V4')]:add(root,'metadata',{'name':k}).text=v
 res=add(root,'resources');mat=add(res,'basematerials',{'id':'1'});build=add(root,'build')
 for name,c in [('Red','#CD1225FF'),('Black','#18191DFF'),('Pink','#F482A0FF')]:add(mat,'base',{'name':name,'displaycolor':c})
 config=ET.Element('config');ids={};report={}
 for i,e in enumerate(entries,2):
  name=e['name'];m=meshes[name];ids[name]=i;ci=2 if 'pink' in name else 1 if 'black' in name else 0
  o=add(res,'object',{'id':str(i),'name':name,'type':'model','pid':'1','pindex':str(ci)});mesh_el=add(o,'mesh');vs=add(mesh_el,'vertices');fs=add(mesh_el,'triangles')
  for v in m.vertices:add(vs,'vertex',{k:repr(float(a)) for k,a in zip('xyz',v)})
  for f in m.faces:add(fs,'triangle',{k:str(int(a)) for k,a in zip(['v1','v2','v3'],f)})
 for i,g in enumerate(['body','head','bottom'],30):
  group=[e for e in entries if e['group']==g]
  if not group:continue
  m=trimesh.util.concatenate([meshes[e['name']] for e in group]);lo,hi=m.bounds
  move=np.zeros(3) if assembled else np.array([128,128,0])-np.array([(lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2]])
  o=add(res,'object',{'id':str(i),'name':g.upper()+'_ASSEMBLY','type':'model'});cs=add(o,'components')
  config_ob=ET.SubElement(config,'object',{'id':str(i)})
  ET.SubElement(config_ob,'metadata',{'key':'name','value':g.upper()+'_ASSEMBLY'})
  for e in group:
   name=e['name'];add(cs,'component',{'objectid':str(ids[name])})
   cfgpart=ET.SubElement(config_ob,'part',{'id':str(ids[name]),'subtype':'normal_part'})
   for k,v in [('name',name),('extruder','3' if 'pink' in name else '2' if 'black' in name else '1')]:ET.SubElement(cfgpart,'metadata',{'key':k,'value':v})
  add(build,'item',{'objectid':str(i),'transform':'1 0 0 0 1 0 0 0 1 '+' '.join(repr(float(a)) for a in move)})
  report[g]={'size_mm':m.extents.tolist(),'print_translation_mm':move.tolist(),'parts':[e['name'] for e in group]}
  if not assembled:
   assert np.all(lo[:2]+move[:2]>20) and np.all(hi[:2]+move[:2]<236)
   for e in group:
    target=OUT/'STL_BACKUPS'/g;target.mkdir(exist_ok=True,parents=True)
    mm=meshes[e['name']].copy();mm.apply_translation(move)
    (target/(e['name']+'.stl')).write_text(trimesh.exchange.stl.export_stl_ascii(mm))
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/xml"/></Types>')
  z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
  z.writestr('3D/3dmodel.model',ET.tostring(root,encoding='utf-8',xml_declaration=True))
  z.writestr('Metadata/model_settings.config',ET.tostring(config,encoding='utf-8',xml_declaration=True))
 # Check original triangle topology and every vertex directly in final 3MF XML.
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  rt=ET.fromstring(z.read('3D/3dmodel.model'))
 for e in entries:
  if not e['name'].startswith('ORIGINAL'):continue
  obj=next(o for o in rt.find(q('resources')).findall(q('object')) if o.get('name')==e['name'])
  v=np.array([[float(x.get(k)) for k in 'xyz'] for x in obj.find(q('mesh')).find(q('vertices'))]);f=np.array([[int(x.get(k)) for k in ['v1','v2','v3']] for x in obj.find(q('mesh')).find(q('triangles'))])
  assert np.array_equal(v,meshes[e['name']].vertices) and np.array_equal(f,meshes[e['name']].faces)
 loaded=trimesh.load(path)
 report['reloaded_geometry_count']=len(loaded.geometry)
 return report
entries=[e for e in manifest if e['group']!='jar']
report={}
for group,filename in [('body','01_VENOM_BODY_V4.3mf'),('head','02_VENOM_HEAD_ORIGINAL_LID_V4.3mf'),('bottom','03_VENOM_FEET_STORAGE_V4.3mf')]:
 report[filename]=write_3mf(KIT/filename,[e for e in entries if e['group']==group])
report['assembled']=write_3mf(KIT/'ASSEMBLED_VIEW_ONLY.3mf',entries,True)

(ROOT.parent/'Reports'/'geometry_package_verification.json').write_text(json.dumps(report,indent=2))
print('Geometry exported:',KIT)
