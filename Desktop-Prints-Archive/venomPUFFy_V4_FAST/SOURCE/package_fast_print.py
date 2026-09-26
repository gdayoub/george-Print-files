from pathlib import Path
import json,zipfile,shutil,hashlib,re,xml.etree.ElementTree as ET
R=Path(__file__).parent;W=R/'speed_work';K=R/'Venom_V4_FAST_PRINT'
for n in ['OPTIONAL_SINGLE_COLOR','REFERENCE','SOURCE','PREVIEWS']:(K/n).mkdir(exist_ok=True,parents=True)
names={'body':'01_BODY','head':'02_HEAD','feet':'03_FEET_STORAGE'}
original={'body':'01_VENOM_BODY_V4.3mf','head':'02_VENOM_HEAD_ORIGINAL_LID_V4.3mf','feet':'03_VENOM_FEET_STORAGE_V4.3mf'}
summary={};checks={}
for mode in ['baseline','fast','fastmono']:
 summary[mode]={}
 for group,prefix in names.items():
  work=W/(mode+'_'+group);s=json.loads((work/'summary.json').read_text());p=s['plates'][0]
  assert s['exit_code']==0 and s['error']=='Success.'
  assert not p.get('warning_message'),p['warning_message']
  summary[mode][group]={'seconds':p['total_predication'],'display_time':s['gcode_summary']['time'],'filament_g':sum(f['total_used_g'] for f in p['filaments']),'filament_changes':p['filament_change_times'],'warning_message':p['warning_message']}
  if mode=='baseline':continue
  with zipfile.ZipFile(work/'INPUT_FAST.3mf') as z,zipfile.ZipFile(R/'Venom_Core_Case_V4'/original[group]) as old:
   same=z.read('3D/3dmodel.model')==old.read('3D/3dmodel.model');assert same
  with zipfile.ZipFile(work/'SLICED.3mf') as z:
   assert z.testzip() is None
   ranges=z.read('Metadata/layer_config_ranges.xml').decode()
   assert 'layer_height' in ranges and 'wall_loops' in ranges
   gc=z.read('Metadata/plate_1.gcode').decode(errors='replace')
   pairs=[(float(a),float(b)) for a,b in re.findall(r'; CHANGE_LAYER\s*; Z_HEIGHT: ([\d.]+)\s*; LAYER_HEIGHT: ([\d.]+)',gc)]
   # Check thread bands in generated layers, allowing the boundary transition layer.
   protected=lambda z: (z<15.59 or 78.2<z<88.01) if group=='body' else z<9.99 if group=='head' else z<24
   bad=[(a,b) for a,b in pairs if protected(a) and b>.201]
   assert not bad,bad[:10]
   config=ET.fromstring(z.read('Metadata/model_settings.config'))
   counts={next((x.get('value') for x in part.findall('metadata') if x.get('key')=='name'),''):int(part.find('mesh_stat').get('face_count')) for part in config.findall('object/part')}
   if group=='body':assert counts['ORIGINAL_CASE_BASE_EXACT']==88278
   if group=='head':assert counts['ORIGINAL_CASE_LID_EXACT']==52836
  checks[mode+'_'+group]={'input_mesh_xml_byte_identical_to_v4':same,'thread_bands_max_layer_height_mm':max(b for a,b in pairs if protected(a)),'part_triangle_counts':counts,'archive_integrity_pass':True,'slicer_warning':''}
  dest=K if mode=='fast' else K/'OPTIONAL_SINGLE_COLOR'
  shutil.copyfile(work/'SLICED.3mf',dest/(prefix+('_FAST_COLOR.3mf' if mode=='fast' else '_SINGLE_COLOR.3mf')))
  shutil.copyfile(work/'plate_1.png',K/'PREVIEWS'/(mode+'_'+group+'.png'))
  for fname in ['process.json','result.json','summary.json']:
   shutil.copyfile(work/fname,K/'REFERENCE'/(mode+'_'+group+'_'+fname))
for mode in summary:
 summary[mode]['total_seconds']=sum(v['seconds'] for v in summary[mode].values() if isinstance(v,dict))
 summary[mode]['total_filament_g']=sum(v['filament_g'] for v in summary[mode].values() if isinstance(v,dict))
summary['color_time_reduction_percent']=100*(1-summary['fast']['total_seconds']/summary['baseline']['total_seconds'])
summary['mono_time_reduction_percent']=100*(1-summary['fastmono']['total_seconds']/summary['baseline']['total_seconds'])
(K/'REFERENCE'/'time_comparison.json').write_text(json.dumps(summary,indent=2))
(K/'REFERENCE'/'verification.json').write_text(json.dumps(checks,indent=2))
for f in ['speed_benchmark.py','package_fast_print.py']:shutil.copyfile(R/f,K/'SOURCE'/f)
for fn in ['machine.json','filament_1.json','filament_2.json','filament_3.json']:shutil.copyfile(W/'fast_body'/fn,K/'REFERENCE'/fn)
shutil.copyfile(R/'Venom_Core_Case_V4'/'REFERENCE'/'Core_Case_ORIGINAL.3mf',K/'REFERENCE'/'Core_Case_ORIGINAL.3mf')
shutil.copyfile(R/'FAST_PRINT_README.md',K/'START_HERE.md')
with zipfile.ZipFile(R/'Venom_V4_FAST_PRINT.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in K.rglob('*'):
  if f.is_file():z.write(f,str(f.relative_to(K)))
with zipfile.ZipFile(R/'Venom_V4_FAST_PRINT.zip') as z:assert z.testzip() is None
desktop=Path(r'C:\Users\george\Desktop\Prints\venomPUFFy_V4_FAST')
assert not desktop.exists(),'Do not overwrite existing desktop package'
shutil.copytree(K,desktop)
print(json.dumps(summary,indent=2));print('DELIVERED',desktop)
