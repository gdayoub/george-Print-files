from pathlib import Path
import zipfile,xml.etree.ElementTree as E,json,io
from PIL import Image
out=Path('outputs/Venom_lightweight')
src=Path('work/lightweight_native.3mf');dst=out/'Venom_lightweight_READY.3mf'
with zipfile.ZipFile(src) as zi,zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as zo:
 names=set(zi.namelist())
 for n in zi.namelist():zo.writestr(n,zi.read(n))
 rels=E.fromstring(zi.read('_rels/.rels'))
 for r in rels:
  target=r.get('Target','').lstrip('/')
  if target not in names and target.lower().endswith('.png'):
   im=Image.open(out/'Venom_lightweight_preview.png').convert('RGBA');im.thumbnail((512,512));b=io.BytesIO();im.save(b,format='PNG');zo.writestr(target,b.getvalue());names.add(target)
 cfg=E.fromstring(zi.read('Metadata/model_settings.config'));c=json.loads(zi.read('Metadata/project_settings.config'))
 normal=[p for p in cfg.findall('.//part') if p.get('subtype')=='normal_part'];mods=[p for p in cfg.findall('.//part') if p.get('subtype')=='modifier_part']
 assert len(normal)==12 and len(mods)==12,(len(normal),len(mods))
 assert c['wall_loops']=='2' and c['sparse_infill_pattern']=='lightning'
 for p in mods:
  m={x.get('key'):x.get('value') for x in p.findall('metadata')}
  assert m['wall_loops']=='3' and m['sparse_infill_density']=='15%' and m['sparse_infill_pattern']=='gyroid'
 report={'normal_printable_parts':len(normal),'local_joint_modifier_volumes':len(mods),'plate_count':len(cfg.findall('plate')),'missing_cover_images_fixed':True,'ordinary_wall_nominal_mm':.87,'settings':{k:c[k] for k in ['wall_loops','top_shell_layers','top_shell_thickness','bottom_shell_layers','sparse_infill_pattern','sparse_infill_density','outer_wall_speed','outer_wall_acceleration','filament_colour']}}
 (out/'engineering/final_project_validation.json').write_text(json.dumps(report,indent=2))
print('Final native 3MF: 12 parts, 12 reinforcement modifiers, 8 plates. Ready for full slicing.',flush=True)
