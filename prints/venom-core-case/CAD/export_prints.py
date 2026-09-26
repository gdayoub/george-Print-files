"""Copy successfully sliced benchmark projects into the current release folders."""
from pathlib import Path
import json,shutil,zipfile
ROOT=Path(__file__).parent;REPO=ROOT.parent
names={'body':'01_BODY','head':'02_HEAD','feet':'03_FEET_STORAGE'}
for mode,target,suffix in [('fast','FullColor','FAST_COLOR'),('fastmono','SingleColor','SINGLE_COLOR')]:
 dest=REPO/'Print'/target;dest.mkdir(parents=True,exist_ok=True)
 for group,prefix in names.items():
  work=ROOT/'speed_work'/(mode+'_'+group)
  report=json.loads((work/'summary.json').read_text())
  assert report['exit_code']==0 and report['error']=='Success.'
  assert all(not p.get('warning_message') for p in report['plates'])
  with zipfile.ZipFile(work/'SLICED.3mf') as archive:
   assert archive.testzip() is None
   assert 'Metadata/layer_config_ranges.xml' in archive.namelist()
  shutil.copyfile(work/'SLICED.3mf',dest/(prefix+'_'+suffix+'.3mf'))
print('Exported six checked projects. Recreate comparison reports if settings changed.')
