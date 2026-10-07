from pathlib import Path
import json,hashlib,re
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]/'outputs/Character_Catchalls_and_Shelves_v1/repo'
slugs=['king-shark-47cm','king-shark-catchall-bowl','king-shark-accessory-shelf','venom-accessory-shelf']
images=['images/all_red_shorts/assembly_all_red_shorts.png','images/three_quarter.png','images/preview.png','images/preview.png']
titles=['King Shark / 47 cm statue','King Shark / catchall bowl','King Shark / red-tray shelf','Venom / accessory shelf']
copy=['Preserved printed torso, compatible all-red replacement shorts, and faster whole legs.','A compact one-color accessory bowl with an open, smooth cavity.','Gray character relief and a separate red tray, arranged for fast non-AMS printing.','Black character and tray with separate white eyes and chest emblem.']
block='''### King Shark + Venom / character homewares

Compact catchalls and shelves, plus the documented 47 cm King Shark statue. Each folder contains printer-specific projects, STLs, editable geometry, actual-mesh previews and research notes.

<table>
'''
for i,(slug,img,title,desc) in enumerate(zip(slugs,images,titles,copy)):
 if i%2==0:block+='<tr>\n'
 block+=f'<td width="50%" valign="top">\n<a href="prints/{slug}/"><img src="prints/{slug}/{img}" alt="{title} — actual geometry CAD render" width="100%"></a>\n<h4>{title}</h4>\n<p>{desc}</p>\n<a href="prints/{slug}/">Files, printing and validation →</a>\n</td>\n'
 if i%2==1:block+='</tr>\n'
block+='''</table>

**Homewares: digitally checked and sliced; physical printing and mounting remain untested.** The statue torso/head has user-reported printing success. The shelves have no assigned load rating; picture-hanging strips are not recommended for shelves by 3M. Read the [mounting research](docs/character-homeware/MOUNTING_RESEARCH.md).

[Research and agent handoff](docs/character-homeware/AGENT_HANDOFF.md) · [Progress record](docs/character-homeware/PROGRESS.md)

'''
readme=(ROOT/'review/remote_README.md').read_text(encoding='utf-8')
marker='## Fresh from the workbench\n\n';assert marker in readme
(REPO/'README.md').write_text(readme.replace(marker,marker+block,1),encoding='utf-8')
catalog=json.loads((ROOT/'review/remote_catalog.json').read_text(encoding='utf-8'))
catalog['projects']=[p for p in catalog['projects'] if p['id'] not in slugs]
add=[]
for slug,img in zip(slugs,images):
 d=json.loads((REPO/'prints'/slug/'project.json').read_text(encoding='utf-8'))
 recommendation=d.get('recommended')
 if not isinstance(recommendation,str):recommendation='README.md'
 add.append(dict(id=slug,title=d.get('title',slug),path='prints/'+slug,preview=f'prints/{slug}/{img}',status=d.get('status','see-project-validation'),recommended=f'prints/{slug}/{recommendation}',makerworld_url=None))
catalog['projects']=add+catalog['projects']
(REPO/'catalog.json').write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
files=[]
for p in sorted(REPO.rglob('*')):
 if p.is_file() and p.name!='PUBLICATION_MANIFEST.json':
  b=p.read_bytes();assert len(b)<100_000_000,p
  files.append(dict(path=p.relative_to(REPO).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),git_blob_sha=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()))
(REPO/'docs/character-homeware/PUBLICATION_MANIFEST.json').write_text(json.dumps(files,indent=2))
print('Staged files',len(files)+1,'bytes',sum(f['bytes'] for f in files))
# Existing-root gallery refers to many untouched remote paths, so check new docs.
errors=[];checked=0
for folder in [REPO/'prints'/s for s in slugs]+[REPO/'docs/character-homeware']:
 for path in folder.rglob('*.md'):
  for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
   if '://' in target or target.startswith('#'):continue
   target=unquote(target.split('?',1)[0].split('#',1)[0])
   resolved=(path.parent/target).resolve()
   # References to the established Venom statue exist on the remote tree.
   if not resolved.exists() and 'venom-muscular-statue' not in target:errors.append(dict(file=str(path.relative_to(REPO)),target=target))
   checked+=1
(ROOT/'review/link_validation.json').write_text(json.dumps(dict(checked=checked,missing=errors),indent=2))
assert not errors,errors
print('New Markdown links checked',checked)
