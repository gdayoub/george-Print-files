from pathlib import Path
import sys,json,subprocess,copy,zipfile,re
R=Path(__file__).resolve().parent.parent
SLICER=Path(sys.argv[1]).resolve()
P=R/'Profiles';W=R/'CAD/slice_work';W.mkdir(exist_ok=True)
jobs=['00a_ORIGINAL_BASE_ONLY','00b_ORIGINAL_LID_ONLY','01_BODY_EXACT_FOUNDATION','02_GENGAR_HEAD_COLOR','03_BOTTOM_CAP','01b_BODY_SINGLE_COLOR','02b_GENGAR_HEAD_SINGLE_COLOR']
if len(sys.argv)>2:jobs=sys.argv[2:]
reports={}
for name in jobs:
 work=W/name;work.mkdir(exist_ok=True)
 machine=json.loads((P/'machine.json').read_text());process=json.loads((P/'baseline_process.json').read_text())
 process.update({'name':'Gengar exact foundation 0.20','print_settings_id':'Gengar exact foundation 0.20','layer_height':'0.20','initial_layer_print_height':'0.2','wall_loops':'4','sparse_infill_density':'8%','sparse_infill_pattern':'gyroid','top_shell_layers':'6','bottom_shell_layers':'6','top_shell_thickness':'1.2','bottom_shell_thickness':'1.2','enable_prime_tower':'1' if name in ['01_BODY_EXACT_FOUNDATION','02_GENGAR_HEAD_COLOR'] else '0','print_sequence':'by layer','enable_support':'1' if name.startswith(('01_','01b_','02_','02b_')) else '0','support_type':'tree(auto)','support_style':'default','support_threshold_angle':'25','support_on_build_plate_only':'1','support_top_z_distance':'0.2','support_bottom_z_distance':'0.2','brim_type':'outer_only' if 'GENGAR' in name else 'auto_brim','brim_width':'5','brim_object_gap':'0.15','elefant_foot_compensation':'0.15','xy_hole_compensation':'0','xy_contour_compensation':'0','enable_arc_fitting':'0','flush_into_infill':'0','flush_into_support':'1'})
 (work/'machine.json').write_text(json.dumps(machine));(work/'process.json').write_text(json.dumps(process));fps=[]
 for i,color in enumerate(['#CE1834' if name=='03_BOTTOM_CAP' else '#1C1B26','#CE1834','#F481B3']):
  f=json.loads((P/'filament_1.json').read_text());f.update({'filament_colour':[color],'filament_max_volumetric_speed':['12'],'nozzle_temperature':['220'],'nozzle_temperature_initial_layer':['220'],'additional_cooling_fan_speed':['30'],'filament_retract_when_changing_layer':['nil']});fp=work/f'filament_{i}.json';fp.write_text(json.dumps(f));fps.append(str(fp))
 target=R/'Print/P1S'/(name+'_P1S.3mf')
 args=[str(SLICER),str(R/'Print/Geometry'/(name+'.3mf')),'--load-settings',str(work/'machine.json')+';'+str(work/'process.json'),'--load-filaments',';'.join(fps),'--curr-bed-type','Textured PEI Plate','--arrange','1','--slice','0','--debug','2','--export-3mf',str(target)]
 print('SLICING',name,flush=True)
 result=subprocess.run(args,cwd=work,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=900)
 (work/'slicer.log').write_bytes(result.stdout+b'\n'+result.stderr)
 r=json.loads((work/'result.json').read_text()) if (work/'result.json').exists() else {}
 report={'exit_code':result.returncode,'result':r,'settings':{'layer_mm':.2,'walls':4,'infill':'8% gyroid','XY_compensation_mm':0,'supports':'build plate only, exterior','calibrated_spool_profiles':False}}
 if result.returncode==0 and target.exists():
  with zipfile.ZipFile(target) as z:
   gc=z.read('Metadata/plate_1.gcode').decode(errors='replace')
   report['gcode_summary']={k:(m.group(1) if (m:=re.search(pat,gc)) else None) for k,pat in {'time':r'total estimated time: ([^\n]+)','filament_g':r'total filament weight \[g\] : ([^\n]+)','layers':r'; total layer number: (\d+)'}.items()}
   for p in ['Metadata/plate_1.png','Metadata/project_settings.config']:
    if p in z.namelist():(work/Path(p).name).write_bytes(z.read(p))
 report_path=R/'Reports'/(name+'_slice.json');report_path.write_text(json.dumps(report,indent=2));reports[name]=report
 print(name,json.dumps({'exit_code':result.returncode,'summary':report.get('gcode_summary'),'error':r.get('error_string')}),flush=True)
 if result.returncode!=0:raise RuntimeError('Slice failed; inspect '+str(work/'slicer.log'))
print('ALL REQUESTED SLICES COMPLETE',flush=True)
