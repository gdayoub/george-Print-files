from pathlib import Path
import subprocess,json,zipfile,re,sys,copy
import xml.etree.ElementTree as ET
R=Path(__file__).parent;W=R/'speed_work';W.mkdir(exist_ok=True)
S=R.parent/'Print'/'Geometry';P=R.parent/'Profiles'
machine=json.loads((P/'machine.json').read_text());process=json.loads((P/'baseline_process.json').read_text());filament=json.loads((P/'filament_1.json').read_text())
jobs={'body':'01_VENOM_BODY_V4.3mf','head':'02_VENOM_HEAD_ORIGINAL_LID_V4.3mf','feet':'03_VENOM_FEET_STORAGE_V4.3mf'}
mode=sys.argv[1] if len(sys.argv)>1 else 'baseline'
groups=sys.argv[2:] or list(jobs)
for group in groups:
 work=W/(mode+'_'+group);work.mkdir(exist_ok=True)
 p=copy.deepcopy(process)
 p.update({'name':'Venom '+mode,'print_settings_id':'Venom '+mode,'layer_height':'0.20','initial_layer_print_height':'0.2','wall_loops':'4','sparse_infill_density':'10%','sparse_infill_pattern':'gyroid','top_shell_layers':'6','bottom_shell_layers':'6','top_shell_thickness':'1.2','bottom_shell_thickness':'1.2','enable_prime_tower':'1','print_sequence':'by layer','enable_support':'1','support_type':'tree(auto)','support_style':'default','support_threshold_angle':'30','support_on_build_plate_only':'0','support_top_z_distance':'0.2','support_bottom_z_distance':'0.2','brim_type':'auto_brim','brim_width':'3','brim_object_gap':'0.15','elefant_foot_compensation':'0.15','enable_arc_fitting':'0','flush_into_infill':'0','flush_into_support':'1'})
 if mode!='baseline':p.update({'wall_loops':'3','sparse_infill_density':'5%','sparse_infill_pattern':'adaptivecubic','support_threshold_angle':'25'})
 if mode.startswith('fast'):
  p.update({'layer_height':'0.28' if group=='body' else '0.24' if group=='head' else '0.20','top_shell_layers':'5','bottom_shell_layers':'5'})
  if group=='feet':p.update({'wall_loops':'4','top_shell_layers':'6','bottom_shell_layers':'6'})
  if mode=='fastmono':p['enable_prime_tower']='0'
 if mode=='draft' and group!='feet':p.update({'layer_height':'0.24','top_shell_layers':'5','bottom_shell_layers':'5','support_top_z_distance':'0.24','support_bottom_z_distance':'0.24'})
 (work/'machine.json').write_text(json.dumps(machine));(work/'process.json').write_text(json.dumps(p))
 files=[]
 for i,col in enumerate(['#CD1225','#18191D','#F482A0']):
  if mode=='fastmono' and group=='feet' and i==0:col='#18191D'
  f=copy.deepcopy(filament);f.update({'filament_colour':[col],'filament_max_volumetric_speed':['12'],'nozzle_temperature':['220'],'nozzle_temperature_initial_layer':['220'],'additional_cooling_fan_speed':['30'],'filament_retract_when_changing_layer':['nil']})
  fp=work/f'filament_{i+1}.json';fp.write_text(json.dumps(f));files.append(str(fp))
 input_path=S/jobs[group]
 if mode.startswith('fast'):
  input_path=work/'INPUT_FAST.3mf'
  with zipfile.ZipFile(S/jobs[group]) as src:
   contents={n:src.read(n) for n in src.namelist()}
  cfg=ET.fromstring(contents['Metadata/model_settings.config'])
  for part in cfg.findall('object/part'):
   name=next((m.get('value','') for m in part.findall('metadata') if m.get('key')=='name'),'')
   if name.startswith('ORIGINAL'):ET.SubElement(part,'metadata',{'key':'wall_loops','value':'4'})
   if mode=='fastmono':
    for md in part.findall('metadata'):
     if md.get('key')=='extruder':md.set('value','1')
  contents['Metadata/model_settings.config']=ET.tostring(cfg,encoding='utf-8',xml_declaration=True)
  ranges=ET.Element('objects');obj=ET.SubElement(ranges,'object',{'id':'1'})
  for low,high in ([(0,15.6),(78.0,88.0)] if group=='body' else [(0,10.0)] if group=='head' else [(0,24)]):
   ran=ET.SubElement(obj,'range',{'min_z':str(low),'max_z':str(high)})
   ET.SubElement(ran,'option',{'opt_key':'layer_height'}).text='0.20'
   ET.SubElement(ran,'option',{'opt_key':'wall_loops'}).text='4'
  contents['Metadata/layer_config_ranges.xml']=ET.tostring(ranges,encoding='utf-8',xml_declaration=True)
  with zipfile.ZipFile(input_path,'w',zipfile.ZIP_DEFLATED) as dest:
   for n,data in contents.items():dest.writestr(n,data)
 args=[r'C:\Program Files\Bambu Studio\bambu-studio.exe',str(input_path),'--load-settings',str(work/'machine.json')+';'+str(work/'process.json'),'--load-filaments',';'.join(files),'--curr-bed-type','Textured PEI Plate','--arrange','1','--slice','0','--debug','2','--export-3mf',str(work/'SLICED.3mf')]
 print('SLICING',mode,group,flush=True)
 result=subprocess.run(args,cwd=work,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=600)
 (work/'slicer.log').write_bytes(result.stdout+b'\n'+result.stderr)
 report=json.loads((work/'result.json').read_text()) if (work/'result.json').exists() else {'return_code':result.returncode}
 summary={'mode':mode,'group':group,'exit_code':result.returncode,'error':report.get('error_string'),'plates':report.get('sliced_plates')}
 if result.returncode==0 and (work/'SLICED.3mf').exists():
  with zipfile.ZipFile(work/'SLICED.3mf') as z:
   if 'Metadata/plate_1.gcode' in z.namelist():
    gc=z.read('Metadata/plate_1.gcode').decode(errors='replace')
    summary['gcode_summary']={key:(m.group(1) if (m:=re.search(pattern,gc)) else None) for key,pattern in {'time':r'total estimated time: ([^\n]+)','filament_g':r'total filament weight \[g\] : ([^\n]+)','layers':r'; total layer number: (\d+)'}.items()}
   for n in ['Metadata/plate_1.png','Metadata/model_settings.config','Metadata/project_settings.config']:
    if n in z.namelist():(work/Path(n).name).write_bytes(z.read(n))
 (work/'summary.json').write_text(json.dumps(summary,indent=2))
 print(json.dumps({k:v for k,v in summary.items() if k!='plates'}),flush=True)
