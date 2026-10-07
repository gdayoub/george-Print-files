"""Add a convenient, exact-geometry fin-only edition to the statue release."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
DEST=PROJECT/'outputs/Character_Catchalls_and_Shelves_v1/repo/prints/king-shark-47cm'
def copy(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 assert hashlib.sha256(src.read_bytes()).digest()==hashlib.sha256(dst.read_bytes()).digest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
original=DEST/'files/stl/original_v2/Dorsal_fin.stl'
export=ROOT/'packages/STL_parts/Dorsal_fin.stl'
assert original.read_bytes()==export.read_bytes(),'Fin-only STL differs from original statue fin'
for printer in ['P1S','P2S']:
 name=f'King_Shark_Original_Dorsal_Fin_ONLY_{printer}_NON_AMS.3mf'
 copy(ROOT/'packages'/name,DEST/'files/3mf/04_fin_only'/name)
 result=json.loads((ROOT/f'slice_{printer}/result.json').read_text())
 assert result['return_code']==0 and len(result['sliced_plates'])==1
 plate=result['sliced_plates'][0]
 assert not plate['warning_message'] and plate['filament_change_times']==0
 summary=dict(printer=printer,return_code=0,seconds=plate['total_predication'],grams=sum(f['total_used_g'] for f in plate['filaments']),plates=1,warning_message=plate['warning_message'],filament_changes=0,support_seconds=sum(v for n,v in plate['feature_type_times'].items() if n.startswith('Support')),source_stl_sha256=hashlib.sha256(original.read_bytes()).hexdigest())
 write(DEST/f'validation/fin_only/{printer}_slice_summary.json',json.dumps(summary,indent=2))
 copy(ROOT/f'validation/slice_{printer}_toolpaths.json',DEST/f'validation/fin_only/{printer}_toolpaths.json')
for path in (ROOT/'packages').glob('*.json'):copy(path,DEST/'validation/fin_only'/path.name)
for name in ['provenance.json','render_validation.json','manifest.json','layout.json']:copy(ROOT/name,DEST/'validation/fin_only'/name)
for name in ['fin_preview.png','fin_socket_view.png','fin_plate.png','fin_on_upper_back.png','fin_from_side.png']:copy(ROOT/name,DEST/'images/fin_only'/name)
copy(ROOT/'King_Shark_Original_Dorsal_Fin.blend',DEST/'source/fin_only/King_Shark_Original_Dorsal_Fin.blend')
for name in ['build_fin_only.py','render_fin_only.py','render_mount.py','stage_fin_only.py']:copy(ROOT/name,DEST/'source/fin_only'/name)
readme='''# The dorsal fin for the 47 cm King Shark body

[← Main statue files](../README.md)

![Original fin highlighted orange at its upper-back attachment point; print the part in gray/black](../images/fin_only/fin_on_upper_back.png)

The original statue's fin is a **separate glue-on part** called `Dorsal_fin`. Its socket fits the matching key on the **center of the torso's upper back, just behind the head**. The illustration highlights its location in orange; the one-color projects print it in gray/charcoal or black PLA. Joint `J05` has the original tapered glue fit with about 0.18 mm nominal root allowance. The fin geometry and torso geometry have not been scaled or reshaped.

## Print only the fin

- [Bambu P1S fin-only project](../files/3mf/04_fin_only/King_Shark_Original_Dorsal_Fin_ONLY_P1S_NON_AMS.3mf?raw=true)
- [Bambu P2S fin-only project](../files/3mf/04_fin_only/King_Shark_Original_Dorsal_Fin_ONLY_P2S_NON_AMS.3mf?raw=true)
- [Original dorsal fin STL](../files/stl/original_v2/Dorsal_fin.stl?raw=true)
- [Fin preview](../images/fin_only/fin_preview.png) · [plate layout](../images/fin_only/fin_plate.png) · [editable Blender fin](../source/fin_only/King_Shark_Original_Dorsal_Fin.blend?raw=true)

Open the matching 3MF **as a project**. It contains the exact original fin in the same print orientation as original plate 4, isolated on one plate. The fin-only export STL is byte-identical to the original `Dorsal_fin.stl` (SHA-256 `01f29d8a901a86d78268d0af8dbb54606f518a8c6cb60805dd4175c405e07b34`). The isolated plate uses 0.20 mm layers, three walls, 8% gyroid, a 3 mm brim, and generated support at its small overhangs. No AMS or color changes are needed.

| Printer | Estimated time | Filament |
|---|---:|---:|
| P1S | 51 min | 13.7 g |
| P2S | 51 min | 13.6 g |

The original full statue project also includes this exact fin on **plate 4**, mixed with old legs and shorts side panels. If you use the newer fast-leg and all-red shorts projects, print this fin-only project as well. If you already printed the original plate 4, keep that fin and skip this one.

After removing supports/brim from the socket, apply a little super glue to the hidden contact face and seat the fin on the torso's upper-back key. The fin-only edition and its fit have digital checks, but this separate print and glue assembly have not been physically tested. Do not cut off the torso key or enlarge the socket preemptively.

[Validation](../validation/fin_only/) · [Full assembly order](PRINTING_ASSEMBLY.md)
'''
write(DEST/'docs/FIN_ONLY.md',readme)
status=json.loads((DEST/'project.json').read_text());status['variants'].append('original_dorsal_fin_only') if 'original_dorsal_fin_only' not in status['variants'] else None
status['fin_only_project']='files/3mf/04_fin_only/King_Shark_Original_Dorsal_Fin_ONLY_P1S_NON_AMS.3mf'
status['fin_only_source_geometry_unchanged']=True
write(DEST/'project.json',json.dumps(status,indent=2)+'\n')
print('Staged fin-only projects, source, preview and validation; original STL identical',flush=True)
