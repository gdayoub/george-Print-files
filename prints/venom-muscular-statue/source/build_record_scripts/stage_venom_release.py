from pathlib import Path
import shutil,zipfile,json
root=Path.cwd();out=root/'outputs/Venom_release';src=root/'outputs/Venom_lightweight'
for p in ['Size_1_465mm','Size_2_232mm','images','source','docs','validation']:(out/p).mkdir(parents=True,exist_ok=True)
for old,new in [('Venom_lightweight_READY.3mf','Venom_Size1_P1S_SEPARATE.3mf'),('Venom_lightweight_P2S_READY.3mf','Venom_Size1_P2S_SEPARATE.3mf')]:shutil.copy2(src/old,out/'Size_1_465mm'/new)
with zipfile.ZipFile(out/'Size_1_465mm/Venom_Size1_STL_parts.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in (src/'STL_parts').glob('*.stl'):z.write(p,p.name)
with zipfile.ZipFile(out/'source/Venom_Size1_Blender.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:z.write(src/'Venom_lightweight.blend','Venom_Size1_465mm.blend')
for name in ['Venom_lightweight_preview.png','Venom_front.png','Venom_back.png','Venom_face_detail.png','Venom_exploded.png','Print_plate_layout.png']:shutil.copy2(src/name,out/'images'/name)
shutil.copy2(src/'Plate_estimates.csv',out/'validation/Size1_plate_estimates.csv')
for name in ['joints.json','inserts.json','smoothing_report.json']:shutil.copy2(src/'engineering'/name,out/'validation'/('Size1_'+name))
(out/'CREDITS.md').write_text('''# Credits and source license

Original sculpture: **OVERRIDE3D_5884368**, MakerWorld user ID 588436866.
Source title embedded in the supplied 3MF: **Venom Marvel Rivals (Exclusive)**.
Source file: `black+venom+marvelrivals.3mf`.
Embedded model identifier: `US4ad1cb0be6b0ff`; profile ID `995753619`.
The source identifies its license as **Standard Digital File License**.
Creator link embedded in that file: https://www.tiktok.com/@override3d

George Dayoub directed the print preparation, with AI assistance: shoulder/back tendril removal, preservation of the original muscle proportions and pose, whole-arm/whole-leg assembly, keyed glue joints, separate white accents/red tongue, lightweight slicing profiles, and the smaller/AMS editions. The original character sculpture is not claimed as George's original design.

This package is a private project backup. Permission to redistribute this derivative model publicly has not been established. No new open-source or commercial license is granted to the source sculpture. Do not treat availability in this repository as permission for public reupload or sale. No MakerWorld listing has been published for this modification.
''',encoding='utf-8')
print([(str(p.relative_to(out)),p.stat().st_size) for p in out.rglob('*') if p.is_file()],flush=True)
