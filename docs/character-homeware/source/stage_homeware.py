"""Stage the verified homeware collection and readable research for publication."""
from pathlib import Path
import json, shutil, hashlib, csv, sys

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
REPO=PROJECT/'outputs/Character_Catchalls_and_Shelves_v1/repo'
PRODUCTS={
 'bowl':('king-shark-catchall-bowl','King Shark catchall bowl','King_Shark_Catchall_Bowl','three_quarter.png'),
 'king_shark':('king-shark-accessory-shelf','King Shark accessory shelf','King_Shark_Shelf','preview.png'),
 'venom':('venom-accessory-shelf','Venom accessory shelf','Venom_Shelf','preview.png')}

def copy(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 assert hashlib.sha256(src.read_bytes()).digest()==hashlib.sha256(dst.read_bytes()).digest()
def write(path,text):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')
def duration(s):
 m=round(s/60);return f'{m//60} h {m%60:02d} min'
def slice_summary(src):
 result={}
 for printer in ['P1S','P2S']:
  r=json.loads((src/f'slice_{printer}/result.json').read_text())
  assert r['return_code']==0
  plates=[]
  for p in r['sliced_plates']:
   assert not p['warning_message'] and p['filament_change_times']==0
   plates.append(dict(id=p['id'],names=[o['name'] for o in p['objects']],seconds=p['total_predication'],grams=sum(f['total_used_g'] for f in p['filaments']),filaments=p['filaments'],feature_type_times=p['feature_type_times'],warning='',filament_changes=0))
  result[printer]=dict(return_code=0,seconds=sum(p['seconds'] for p in plates),grams=sum(p['grams'] for p in plates),plates=plates)
 return result

def stage(product):
 slug,title,stem,preview=PRODUCTS[product];src=ROOT/product;dst=REPO/'prints'/slug
 estimates=slice_summary(src)
 for path in (src/'packages').glob('*.3mf'):copy(path,dst/'files/3mf'/path.name)
 for path in (src/'packages/STL_parts').glob('*.stl'):copy(path,dst/'files/stl'/path.name)
 for path in src.glob('*.png'):copy(path,dst/'images'/path.name)
 for path in src.glob('*.blend'):copy(path,dst/'source'/path.name)
 for path in (src/'packages').glob('*.json'):copy(path,dst/'validation'/path.name)
 for path in (src/'validation').glob('*.json'):copy(path,dst/'validation'/path.name)
 for name in ['engineering_validation.json','geometry_validation.json','serialization_repair.json','serialization_validation.json','render_validation.json']:
  if (src/name).exists():copy(src/name,dst/'validation'/name)
 copy(src/'layout.json',dst/'source/layout.json')
 geometry=src if product=='bowl' else src/'final_parts'
 for path in geometry.glob('*.npz'):
  if path.name!='relief_cache.npz':copy(path,dst/'source/geometry'/path.name)
 copy(geometry/'manifest.json',dst/'source/geometry/manifest.json')
 write(dst/'validation/slicer_estimates.json',json.dumps(estimates,indent=2))
 for name in ['PRINT_VALIDATION.md']:
  if (src/name).exists():copy(src/name,dst/'docs'/name)
 write(dst/'validation/README.md','''# Validation record

`project_validation.json` is the package-build snapshot and therefore can say `sliced: false`. The later `slicer_estimates.json` and toolpath reports document completed slicing of the delivered project. Physical print/mount/load fields remain untested. Neither a clean mesh nor an empty plate-warning field proves a physical print or safe load.

The source geometry report may predate submicron serialization cleanup. The actual exported STL/embedded-project checks and any serialization/assembly reports describe the final files. Source hashes, exact digital overlap values and method details are retained. See the shared [engineering record](../../../docs/character-homeware/HOMEWARE_ENGINEERING.md).
''')
 for name in ['build_bowl.py','render_bowl.py'] if product=='bowl' else ['build_shelves.py','render_shelves.py']:
  copy((src if product=='bowl' else ROOT)/name,dst/'source/scripts'/name)
 table='\n'.join(f"| {printer} | {duration(r['seconds'])} | {r['grams']:.1f} g | {len(r['plates'])} |" for printer,r in estimates.items())
 if product=='bowl':
  text=(src/'README.md').read_text().replace('(three_quarter.png)','(images/three_quarter.png)').replace('(packages/','(files/3mf/').replace('(King_Shark_Catchall_Bowl.stl)','(files/stl/King_Shark_Catchall_Bowl.stl)').replace('(King_Shark_Catchall_Bowl.blend)','(source/King_Shark_Catchall_Bowl.blend)').replace('(engineering_validation.json)','(validation/engineering_validation.json)').replace('(CHANGELOG.md)','(docs/CHANGELOG.md)')
  text=text.replace('same King Shark sculpture used for the successful large statue','same King Shark sculpture whose chest/head the user printed successfully').replace('zero slicer warnings','empty plate warning messages')
  text+='\nSee [agent handoff](../../docs/character-homeware/AGENT_HANDOFF.md), [source notes](source/README.md), and [credits](CREDITS.md).\n'
  copy(src/'CHANGELOG.md',dst/'docs/CHANGELOG.md')
  dimensions=[140,143.425,59.399];colors=['Gray']
 else:
  king=product=='king_shark';colors=['Gray','Red'] if king else ['Black','White'];dimensions=[150,58.2,156]
  palette='gray character/back and a red tray' if king else 'black character/back and tray, with three separate white eye/chest inserts'
  text=f'''# {title}

[← Print gallery](../../README.md)

![Actual printable geometry, CAD render](images/{preview})

A compact character relief with a shallow tray for keys, earbuds or a small collectible. It uses {palette}. The sculpt is adapted from the existing statue, with compressed depth and simplified contours to keep printing practical. It is a **new, physically untested prototype**.

## Download and print

- [P1S non-AMS project](files/3mf/{stem}_P1S_NON_AMS.3mf?raw=true)
- [P2S non-AMS project](files/3mf/{stem}_P2S_NON_AMS.3mf?raw=true)
- [Individual STLs](files/stl/)
- [Editable Blender scene](source/{'King_Shark' if king else 'Venom'}_Shelf.blend?raw=true)

Open the matching 3MF **as a project**. Each plate uses one color; change the spool between plates. Standard 0.4 mm nozzle, PLA, 0.28 mm main layers, three walls, 8% gyroid, four top/bottom layers with 1.12 mm minimum thickness. {'The white inserts use 0.16 mm object layers.' if not king else ''} Both the character back and tray print flat. Generated support is disabled; their orientation avoids major undercuts. The supplied slicer checks do not establish physical print quality or load capacity.

| Printer | Estimated total time | Filament | Plates |
|---|---:|---:|---:|
{table}

These are Bambu Studio 02.08.02.61 estimates, including preparation. Different calibrated filament or cooling settings can change them. [Per-plate data](validation/slicer_estimates.json)

## Dimensions and assembly

Overall assembled envelope: **150 mm wide × 58.2 mm projection × 156 mm high**. The mounting back is 148 × 156 mm; the tray is 150 × 55 mm, with a 4.2 mm floor and 4.8 mm raised lip. Two 6 mm gussets carry the tray; registration keys locate it with 0.22 mm nominal side clearance. There is no flexible snap latch.

Remove brims and clean the mating surfaces. Approach from the front with the tray 16 mm above its seated position, slide it toward the backplate, then lower it over both locating keys. Bond the broad gusset seats and back contact with a suitable plastic adhesive; let it cure before handling. {'The white inserts fit their matching pockets from the front; use a small amount of glue and keep the eyes in their left/right positions.' if not king else ''} See the [exploded assembly](images/exploded.png). Fit and assembly have been checked geometrically, not physically.

## Mounting

The rear is flat at Y=0 with two nominal 25 × 100 mm clear pad zones. **3M does not recommend picture-hanging strips for shelves**, so this model has no assigned adhesive load rating. See the [official guidance](https://multimedia.3m.com/mws/media/1792217O/command-a-online-content-file-picture-hanging-strips-en.pdf) and [mounting research](../../docs/character-homeware/MOUNTING_RESEARCH.md).

Two visible keyhole slots provide a screw-mounting alternative: 108 mm center spacing, 9.2 mm entry diameter and 4.7 mm neck width. Choose hardware appropriate to the wall and check the printed slots. The keyholes, glue joint, material and wall attachment have **not been load-tested**; no safe working load is claimed. Do not use a picture-strip weight label as a shelf rating. For a no-screw version with an established manufacturer rating, a later design can surround a rated ledge after its dimensions are measured.

## Checks and files

Closed manifold solids; actual float32 STL reimport and embedded 3MF geometry checked; assembly overlaps and tray insertion sampled; both printers sliced successfully with empty plate warning messages and no filament changes. Extrusion paths include brims and stay inside the compatible build envelope. Read [validation](validation/), [source notes](source/README.md), [credits](CREDITS.md), and [agent handoff](../../docs/character-homeware/AGENT_HANDOFF.md).

This shelf does not change the successful large statue or its connectors. No physical print, mounting or load test has been completed for this shelf.
'''
 write(dst/'README.md',text)
 write(dst/'source/README.md','''# Editable source and reproducibility

The Blender file contains the actual printable geometry, assembly views and (for shelves) plate-layout scenes. STLs are the print-oriented delivery; the NPZ arrays in `geometry/` retain assembly-coordinate vertices/faces. All dimensions are millimeters. The manifest and layout preserve per-part settings and print transforms.

`scripts/` contains the construction/rendering code as a research snapshot. It still expects the original workspace directory layout and supporting sculpture files, Blender Python runtime, and scientific Python dependencies. It is **not a standalone installed application**. See the shared agent handoff for source locations and dependency details. The original King Shark geometry is archived with the statue; Venom retains the existing credited source. Open the Blender model directly when a full pipeline reconstruction is unnecessary.

After edits, repeat manifold checks on the actual exported STL and embedded 3MF, joint clearance/insertion checks, both printer slices, and build-volume checks. Recalculate estimates, update Markdown notes, then publish matching file hashes. Do not reuse previous validation for changed files.
''')
 if product=='venom':
  credits='''# Credits

Original sculpture: OVERRIDE3D_5884368, “Venom Marvel Rivals (Exclusive),” from the user's `black+venom+marvelrivals.3mf`. The embedded source identifies Standard Digital File License. Creator link: https://www.tiktok.com/@override3d

George Dayoub directed the AI-assisted conversion to a shallow functional shelf, supported hands, separate tray and white glue inserts. This private project backup does not establish permission for public redistribution or sale of the source or derivative. No new mesh license or character rights are granted. The existing [statue source credits](../venom-muscular-statue/CREDITS.md) remain applicable.
'''
 else:
  credits='''# Credits

Unofficial King Shark fan interpretation. The base sculpture was generated through Microsoft TRELLIS.2 from the user-approved reference image, then repaired and engineered for printing. It is not a production movie asset. George Dayoub directed the AI-assisted print preparation and homeware adaptation.

Character rights remain with their owners. No blanket open-source mesh license, commercial character license, or permission for public redistribution is asserted. This upload is a private project backup. See the [47 cm statue record](../king-shark-47cm/CREDITS.md) for retained source details.
'''
 write(dst/'CREDITS.md',credits)
 record=dict(id=slug,title=title,dimensions_mm=dimensions,colors=colors,status='digitally-checked-and-sliced-physical-print-assembly-and-mount-untested' if product!='bowl' else 'digitally-checked-and-sliced-physical-print-untested',recommended=f'files/3mf/{stem}_P1S_NON_AMS.3mf',printers=['Bambu P1S','Bambu P2S'],nozzle_mm=.4,ams_required=False,preview=f'images/{preview}',mounting_load_rating=None if product!='bowl' else 'not-applicable',estimates=estimates)
 write(dst/'project.json',json.dumps(record,indent=2))
 print(slug,'staged',sum(p.stat().st_size for p in dst.rglob('*') if p.is_file()),flush=True)

def shared():
 for path in (ROOT/'docs').glob('*.md'):copy(path,REPO/'docs/character-homeware'/path.name)
 for name in ['package_homeware.py','build_shelves.py','render_shelves.py','serialize_shelves.py','canonicalize_venom.py','check_assembly.py','stage_homeware.py','stage_statue_publication.py','finalize_gallery.py','blob_upload_io.py']:
  copy(ROOT/name,REPO/'docs/character-homeware/source'/name)
 copy(ROOT.parent/'king_shark_v2/package_v2.py',REPO/'docs/character-homeware/source/package_v2.py')
 for name in ['bambu_cli.py','check_size2_paths.py']:
  copy(ROOT.parent/name,REPO/'docs/character-homeware/source'/name)

if __name__=='__main__':
 for p in sys.argv[1:] or list(PRODUCTS):stage(p)
 shared()
