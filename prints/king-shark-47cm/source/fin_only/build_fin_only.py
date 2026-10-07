"""Package the unchanged original dorsal fin as its own printer plate."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'king_shark_v2/final_parts/Dorsal_fin.npz'
ORIGINAL=json.loads((ROOT.parent/'king_shark_v2/layout.json').read_text())
instance=next(i for p in ORIGINAL['plates'] for i in p['instances'] if i['name']=='Dorsal_fin')
ROOT.mkdir(exist_ok=True)
manifest=[dict(name='Dorsal_fin',color='Black',mesh=str(SOURCE),settings=dict(wall_loops='3',sparse_infill_pattern='gyroid',sparse_infill_density='8%',brim_width='3'))]
layout=dict(bed_margin_mm=3,max_height_mm=250,palette=ORIGINAL['palette'],plates=[dict(label='Original 47 cm King Shark dorsal fin — one part',instances=[instance],preview='fin_plate.png')])
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2))
(ROOT/'layout.json').write_text(json.dumps(layout,indent=2))
report=dict(source_npz=str(SOURCE),source_npz_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),geometry_changed=False,source_rotation_and_placement_from_original_plate=instance,original_plate_number=4,original_assembly_joint='J05: Torso male key to Dorsal_fin socket; approximately 0.18 mm radial allowance.',intended_geometry='Exactly the original King Shark fin for the 47 cm statue, no scaling or reshaping.')
(ROOT/'provenance.json').write_text(json.dumps(report,indent=2))
print('Prepared original fin manifest/layout',flush=True)
