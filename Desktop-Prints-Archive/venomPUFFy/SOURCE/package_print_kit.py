"""Validate and package only the current plain screw-on revision without extra hardware."""
from pathlib import Path
import sys,json,zipfile,hashlib,shutil,math
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
for parent in [ROOT]+list(ROOT.parents):
 if (parent/'.deps').is_dir():sys.path.insert(0,str(parent/'.deps'));break
import numpy as np
import trimesh
from PIL import Image,ImageDraw,ImageFont
OUT=ROOT/'outputs';KIT=ROOT.parent/'Symbiote_Core_PLAIN_SCREW_V3'
for name in ['TEST_PRINT_FIRST','STL_BACKUPS','SOURCE','REFERENCE','PREVIEWS','PROCESS_PRESETS']:(KIT/name).mkdir(parents=True,exist_ok=True)
r=json.loads((OUT/'validation.json').read_text());c=r['checks']
assert c['separate_hardware_required'] is False
assert abs(c['head_flat_seat_missing_material_mm3'])<1e-5 and abs(c['base_flat_seat_missing_material_mm3'])<1e-5
assert c['source_file_unchanged'] and c['embedded_original_vertex_error_mm']==0
assert c['protected_cup_interior_envelope_overlap_mm3']<1e-6
assert not c['head_motion_collisions'] and not c['base_motion_collisions']
assert abs(c['head_closed_overlap_mm3'])<1e-4 and abs(c['base_closed_overlap_mm3'])<1e-4
assert c['head_clocking_stop_overlap_at_2deg_overturn_mm3']>.1
assert c['base_clocking_stop_overlap_at_2deg_overturn_mm3']>.1
assert c['provisional_jar_straight_exit_overlap_mm3']<1e-5
assert all(v['watertight'] and v['winding_consistent'] and v['positive_volume'] for v in r['parts'].values())
assert all(v['watertight'] and v['winding_consistent'] for v in r['test_prints'].values())
assert all(n==1 for n in c['assembly_solid_component_counts_before_color_partition'].values())
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',NS);q=lambda s:'{'+NS+'}'+s
manifest=json.loads((OUT/'geometry_manifest.json').read_text())
with zipfile.ZipFile(OUT/'Symbiote_Core_PLAIN_SCREW_V3.3mf') as z:
 xml=z.read('3D/3dmodel.model');types=z.read('[Content_Types].xml');rels=z.read('_rels/.rels')
def bcm(objects):
 # Bambu part-level filament indexes accompany standard 3MF base materials.
 config=ET.Element('config')
 for oid,name,parts in objects:
  o=ET.SubElement(config,'object',{'id':str(oid)})
  for key,value in [('name',name),('extruder','2' if name=='BASE_02_FEET_RING' else '1')]:ET.SubElement(o,'metadata',{'key':key,'value':value})
  for pid,pname,color in parts:
   part=ET.SubElement(o,'part',{'id':str(pid),'subtype':'normal_part'})
   for key,value in [('name',pname),('extruder',str(color))]:ET.SubElement(part,'metadata',{'key':key,'value':value})
 plate=ET.SubElement(config,'plate');ET.SubElement(plate,'metadata',{'key':'plater_id','value':'1'})
 for oid,name,parts in objects:
  inst=ET.SubElement(plate,'model_instance')
  for key,value in [('object_id',str(oid)),('instance_id','0'),('identify_id',str(oid))]:ET.SubElement(inst,'metadata',{'key':key,'value':value})
 return ET.tostring(config,encoding='utf-8',xml_declaration=True)
def save3mf(path,root,metadata,filament_colors=None):
 content_types=ET.fromstring(types)
 ET.SubElement(content_types,'{http://schemas.openxmlformats.org/package/2006/content-types}Default',{'Extension':'config','ContentType':'application/xml'})
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('[Content_Types].xml',ET.tostring(content_types,encoding='utf-8',xml_declaration=True));z.writestr('_rels/.rels',rels)
  z.writestr('3D/3dmodel.model',ET.tostring(root,encoding='utf-8',xml_declaration=True))
  z.writestr('Metadata/model_settings.config',metadata)
  if filament_colors is not None:z.writestr('Metadata/project_settings.config',json.dumps({'filament_colour':filament_colors,'filament_type':['PLA']*len(filament_colors)}))
verification={'source_sha256':r['source_sha256'],'source_byte_identical':True,'assemblies':{},'coupons':{},'slicer_status':'Unsliced. Generic 3MF geometry reloaded; Bambu part-extruder metadata included but native Bambu UI import and support layout not verified.'}
for g,filename in [('body','02_BODY_PLAIN_SCREW_V3.3mf'),('head','03_HEAD_PLAIN_SCREW_V3.3mf'),('bottom','04_FEET_BASE_PLAIN_SCREW_V3.3mf')]:
 es=[e for e in manifest if e['group']==g]
 ms={e['name']:trimesh.load_mesh(OUT/e['path']) for e in es}
 together=trimesh.util.concatenate(list(ms.values()));lo,hi=together.bounds
 move=np.array([128,128,0])-np.array([(lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2]])
 root=ET.fromstring(xml);res=root.find(q('resources'));build=root.find(q('build'))
 group=next(o for o in res.findall(q('object')) if o.get('name')==g.upper()+'_ASSEMBLY')
 keep={x.get('objectid') for x in group.find(q('components'))};keep.add(group.get('id'))
 specs=[]
 for o in list(res.findall(q('object'))):
  if o.get('id') not in keep:res.remove(o)
  elif o.find(q('mesh')) is not None:
   name=o.get('name');color=3 if 'pink' in name else 2 if 'black' in name else 1
   specs.append((o.get('id'),name,color))
 for item in list(build):
  if item.get('objectid')!=group.get('id'):build.remove(item)
  else:item.set('transform','1 0 0 0 1 0 0 0 1 '+' '.join(repr(float(a)) for a in move))
 for m in root.findall(q('metadata')):
  if m.get('name')=='Title':m.text=filename[:-4]+' - Symbiote Core V3 - test joints first'
 dest=KIT/filename;save3mf(dest,root,bcm([(group.get('id'),g.upper(),specs)]))
 scene=trimesh.load(dest)
 assert np.allclose(scene.extents,together.extents,atol=.00002)
 assert abs(scene.bounds[0,2])<.00002
 assert np.all(scene.bounds[0,:2]>20) and np.all(scene.bounds[1,:2]<236)
 for e in es:
  translated=ms[e['name']].copy();translated.apply_translation(move)
  target=KIT/'STL_BACKUPS'/g;target.mkdir(exist_ok=True)
  (target/(e['name']+'.stl')).write_text(trimesh.exchange.stl.export_stl_ascii(translated))
  reloaded=trimesh.load_mesh(target/(e['name']+'.stl'))
  if not e['name'].startswith('ORIGINAL_CORE'):assert reloaded.is_watertight
 verification['assemblies'][g]={'file':filename,'parts':len(es),'bed_translation_mm':move.tolist(),'size_mm':together.extents.tolist(),'bounds_on_bed_mm':scene.bounds.tolist(),'original_source_included':g=='body'}
# Four coupons use the same interface colors as the full model.
root=ET.Element(q('model'),{'unit':'millimeter'});res=ET.SubElement(root,q('resources'));build=ET.SubElement(root,q('build'))
mat=ET.SubElement(res,q('basematerials'),{'id':'1'})
ET.SubElement(mat,q('base'),{'name':'Red test parts','displaycolor':'#CD1225FF'})
ET.SubElement(mat,q('base'),{'name':'Black feet test','displaycolor':'#18191DFF'})
names=['HEAD_01_BODY_RING','HEAD_02_CAP_RING','BASE_01_BODY_RING','BASE_02_FEET_RING'];spec=[]
for i,(name,pos) in enumerate(zip(names,[(76,77,0),(170,77,0),(76,172,0),(170,172,0)]),2):
 f=OUT/'TEST_PRINT_FIRST'/(name+'.stl');m=trimesh.load_mesh(f);assert m.is_watertight
 shutil.copyfile(f,KIT/'TEST_PRINT_FIRST'/f.name)
 ob=ET.SubElement(res,q('object'),{'id':str(i),'name':name,'type':'model','pid':'1','pindex':'1' if name=='BASE_02_FEET_RING' else '0'});me=ET.SubElement(ob,q('mesh'));vs=ET.SubElement(me,q('vertices'));fs=ET.SubElement(me,q('triangles'))
 for v in m.vertices:ET.SubElement(vs,q('vertex'),{k:repr(float(a)) for k,a in zip('xyz',v)})
 for f in m.faces:ET.SubElement(fs,q('triangle'),{k:str(int(a)) for k,a in zip(['v1','v2','v3'],f)})
 ET.SubElement(build,q('item'),{'objectid':str(i),'transform':'1 0 0 0 1 0 0 0 1 '+' '.join(map(str,pos))})
 spec.append((i,name,[]));verification['coupons'][name]={'watertight':True,'size_mm':m.extents.tolist()}
save3mf(KIT/'01_SCREW_TESTS_V3.3mf',root,bcm(spec))
loaded=trimesh.load(KIT/'01_SCREW_TESTS_V3.3mf');assert len(loaded.geometry)==4 and all(m.is_watertight for m in loaded.geometry.values())
assert loaded.bounds[0,2]>-.00002 and loaded.bounds[1,0]<230 and loaded.bounds[1,1]<230
# Optional separate single-color jobs avoid AMS swaps during coupon testing.
for filename,want_black in [('RED_3_TEST_PARTS_V3.3mf',False),('BLACK_1_TEST_PART_V3.3mf',True)]:
 rr=ET.fromstring(ET.tostring(root));rrres=rr.find(q('resources'));rrbuild=rr.find(q('build'));chosen=[]
 for ob in list(rrres.findall(q('object'))):
  if (ob.get('name')=='BASE_02_FEET_RING')!=want_black:rrres.remove(ob)
  else:chosen.append(ob.get('id'))
 for item in list(rrbuild):
  if item.get('objectid') not in chosen:rrbuild.remove(item)
 # A single-color job uses only slot 1, irrespective of the user's previous AMS order.
 mm=rrres.find(q('basematerials'))
 for child in list(mm):mm.remove(child)
 col='#18191D' if want_black else '#CD1225'
 ET.SubElement(mm,q('base'),{'name':'BLACK Creality Hyper PLA' if want_black else 'RED Soyelin Ultra PLA','displaycolor':col+'FF'})
 for ob in rrres.findall(q('object')):ob.set('pindex','0')
 cfg=ET.fromstring(bcm([s for s in spec if str(s[0]) in chosen]))
 for md in cfg.iter('metadata'):
  if md.get('key')=='extruder':md.set('value','1')
 save3mf(KIT/'TEST_PRINT_FIRST'/filename,rr,ET.tostring(cfg,encoding='utf-8',xml_declaration=True),[col])
 ss=trimesh.load(KIT/'TEST_PRINT_FIRST'/filename);assert all(m.is_watertight for m in ss.geometry.values())
# One thread-fit process for both coupons and matching full parts.
stock=Path('C:/Program Files/Bambu Studio/resources/profiles/BBL/process')
parent='0.20mm Standard @BBL X1C';name='venomPUFFy V3 - plain screw 0.20 - P1S'
assert 'Bambu Lab P1S 0.4 nozzle' in json.loads((stock/(parent+'.json')).read_text())['compatible_printers']
settings={'type':'process','name':name,'inherits':parent,'from':'User','instantiation':'true','print_settings_id':name,'compatible_printers':['Bambu Lab P1S 0.4 nozzle'],'layer_height':'0.20','initial_layer_print_height':'0.2','wall_loops':'4','sparse_infill_density':'10%','sparse_infill_pattern':'gyroid','top_shell_layers':'6','top_shell_thickness':'1.2','bottom_shell_layers':'6','bottom_shell_thickness':'1.2','flush_into_infill':'0','flush_into_support':'1','enable_prime_tower':'1'}
(KIT/'PROCESS_PRESETS'/'SCREW_TEST_020.json').write_text(json.dumps(settings,indent=2))
shutil.copyfile(ROOT/'START_HERE.md',KIT/'START_HERE.md')
for name in ['build_symbiote.py','parameters.json','render_symbiote.py','package_print_kit.py']:shutil.copyfile(ROOT/name,KIT/'SOURCE'/name)
(KIT/'SOURCE'/'requirements.txt').write_text('numpy\nscipy\ntrimesh\nmanifold3d\npillow\n')
shutil.copyfile(OUT/'Symbiote_Core_EDITABLE_PLAIN_SCREW_V3.blend',KIT/'SOURCE'/'Symbiote_Core_EDITABLE.blend')
shutil.copyfile(OUT/'original_sleeve_UNCHANGED.stl',KIT/'REFERENCE'/'ORIGINAL_sleeve_UNCHANGED.stl')
assert hashlib.sha256((KIT/'REFERENCE'/'ORIGINAL_sleeve_UNCHANGED.stl').read_bytes()).hexdigest()==r['source_sha256']
shutil.copyfile(OUT/'Symbiote_Core_PLAIN_SCREW_V3.3mf',KIT/'REFERENCE'/'ASSEMBLED_VIEW_ONLY.3mf')
shutil.copyfile(OUT/'validation.json',KIT/'REFERENCE'/'digital_validation.json')
(KIT/'REFERENCE'/'package_verification.json').write_text(json.dumps(verification,indent=2))
for f in (OUT/'previews').glob('*.png'):shutil.copyfile(f,KIT/'PREVIEWS'/f.name)
font=lambda size,bold=False:ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),size)
sheet=Image.new('RGB',(1800,1610),'#12151C');d=ImageDraw.Draw(sheet)
d.text((32,20),'SYMBIOTE CORE  /  PLAIN SCREW V3',font=font(36,True),fill='white')
d.text((32,68),'Three print assemblies - full screw-on head and feet/base - no extra hardware',font=font(24),fill='#F6A9B9')
views=[('01_front','FRONT'),('02_side','SIDE'),('03_back','BACK'),('04_head_removed','HEAD REMOVED / FULL SCREW THREAD'),('05_bottom_open','FEET/BASE REMOVED / JAR CRADLE'),('06_section','SECTION / ORIGINAL CUP + JAR STORAGE')]
for i,(name,title) in enumerate(views):
 x=i%3*600;y=112+i//3*720;im=Image.open(OUT/'previews'/(name+'.png')).convert('RGB');im.thumbnail((580,666),Image.Resampling.LANCZOS)
 sheet.paste(im,(x+(600-im.width)//2,y));d.text((x+16,y+674),title,font=font(17,True),fill='white')
d.text((32,1562),'Original sleeve preserved at 1:1 scale | Digital motion checks passed | Physical fit and odor seal unverified',font=font(21),fill='#BCC7D8')
sheet.save(KIT/'PREVIEWS'/'Symbiote_Core_V3_overview.jpg',quality=94)
html='<!doctype html><meta charset="utf-8"><title>Symbiote Core V3</title><style>body{font:18px system-ui;background:#12151c;color:#eee;margin:28px}img{max-width:100%;height:auto}a{color:#ffa4b7}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:20px}figure{margin:0}</style><h1>Symbiote Core — Plain screw V3</h1><p>Print <b>01_SCREW_TESTS_V3.3mf</b> before the three full assemblies. <a href="START_HERE.md">Assembly and print instructions</a>.</p><p>Both closures are modeled and digitally checked. Physical fit, odor sealing and actual jar height remain unverified. No extra hardware is required.</p><div class="grid">'
for name,title in views+[('07_head_underside','Hidden socket inside the head'),('08_test_rings','Four plain screw-fit tests — print first')]:html+=f'<figure><img src="PREVIEWS/{name}.png"><figcaption>{title}</figcaption></figure>'
(KIT/'VIEW_MODEL.html').write_text(html+'</div>',encoding='utf-8')
zip_path=ROOT.parent/'Symbiote_Core_PLAIN_SCREW_V3.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for f in KIT.rglob('*'):
  if f.is_file():z.write(f,str(f.relative_to(KIT)))
with zipfile.ZipFile(zip_path) as z:assert z.testzip() is None
print(json.dumps({'package':str(zip_path),'bytes':zip_path.stat().st_size,'assemblies':verification['assemblies'],'checks':'Source preserved; all generated meshes/coupons valid; both helical paths clear; nominal seats and terminal alignment stops checked. Seal NOT physically verified.'},indent=2))
