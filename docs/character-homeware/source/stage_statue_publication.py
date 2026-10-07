"""Stage the delivered statue and compatible revisions; no mesh regeneration or upload."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[2]
DESKTOP = Path('C:/Users/Panduh/Desktop/Prints')
OUT = ROOT / 'outputs/Character_Catchalls_and_Shelves_v1/repo/prints/king-shark-47cm'
COPIES = []


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cp(source, relative):
    target = OUT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    sha = digest(source)
    assert sha == digest(target), str(target)
    COPIES.append({'source': str(source), 'path': target.relative_to(OUT).as_posix(),
                   'bytes': target.stat().st_size, 'sha256': sha})


def tree(source, relative):
    for path in sorted(source.rglob('*')):
        if path.is_file():
            cp(path, Path(relative) / path.relative_to(source))


def write(relative, content):
    path = OUT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8', newline='\n')


def main():
    original = DESKTOP / 'KingShark_realistic_47cm_v2'
    red = DESKTOP / 'KingShark_ALL_RED_SHORTS_FIX'
    legs = DESKTOP / 'KingShark_FAST_LEGS_FEET'
    for source in [original, red, legs]:
        assert source.is_dir(), source
    for p in original.glob('*.3mf'):
        cp(p, 'files/3mf/01_original_v2/' + p.name)
    tree(original / 'STL_parts', 'files/stl/original_v2')
    tree(original / 'previews', 'images/original_v2')
    tree(original / 'engineering', 'validation/original_v2')
    tree(original / 'source', 'source/original_v2')
    cp(original / 'King_Shark_realistic_47cm.blend', 'source/original_v2/King_Shark_realistic_47cm.blend')
    cp(original / 'START_HERE.txt', 'docs/history/01_original_v2_START_HERE.txt')
    for p in red.glob('*.3mf'):
        cp(p, 'files/3mf/02_all_red_shorts/' + p.name)
    cp(red / 'Shorts_ALL_RED.stl', 'files/stl/all_red_shorts/Shorts_ALL_RED.stl')
    tree(red / 'Previews', 'images/all_red_shorts')
    tree(red / 'Engineering', 'validation/all_red_shorts')
    tree(red / 'Editable_source', 'source/all_red_shorts')
    cp(red / 'START_HERE.txt', 'docs/history/02_all_red_shorts_START_HERE.txt')
    for p in legs.glob('*.3mf'):
        cp(p, 'files/3mf/03_fast_legs_feet/' + p.name)
    tree(legs / 'Two_printers', 'files/3mf/03_fast_legs_feet/Two_printers')
    tree(legs / 'STL_backup', 'files/stl/fast_legs_feet')
    tree(legs / 'Engineering', 'validation/fast_legs_feet')
    cp(legs / 'legs_and_feet_preview.png', 'images/fast_legs_feet/legs_and_feet_preview.png')
    cp(legs / 'START_HERE.txt', 'docs/history/03_fast_legs_feet_START_HERE.txt')

    # Preserve assembly-coordinate meshes as editable geometry, not replacements
    # for the print-oriented STL/3MF files above.
    tree(ROOT / 'work/king_shark_v2/final_parts', 'source/geometry')
    cp(ROOT / 'work/king_shark_red_shorts_v3/final_parts/Shorts.npz',
       'source/all_red_shorts/assembly_meshes/Shorts.npz')
    for name in ['build_red_shorts.py', 'package_red_shorts.py', 'finalize_3pct_replacement.py']:
        cp(ROOT / 'work/king_shark_red_shorts_v3' / name, 'source/all_red_shorts/' + name)

    write('README.md', '''# King Shark — realistic 47 cm statue

[← Print gallery](../../README.md)

![Actual engineered King Shark geometry with all-red shorts; CAD render](images/all_red_shorts/assembly_all_red_shorts.png)

**469.54 mm tall × 323.27 mm wide × 237.93 mm deep.** Muscular King Shark fan statue with whole arms and lower legs, separate white dental arches, and keyed glue assembly. The current combination uses all-red shorts and faster legs/feet; the original body and its connectors stay unchanged.

**User-reported physical success: torso/chest and head.** The full files and revisions have digital geometry, slicing and plate checks. No physical print or fit result has been reported for the all-red replacement shorts, faster leg process, or complete revised assembly.

## Choose the files

| What you need | P1S project | P2S project |
|---|---|---|
| Original body, arms, fin and teeth; full historical v2 project | [Original v2 P1S](files/3mf/01_original_v2/King_Shark_Realistic_47cm_P1S_NON_AMS.3mf?raw=true) | [Original v2 P2S](files/3mf/01_original_v2/King_Shark_Realistic_47cm_P2S_NON_AMS.3mf?raw=true) |
| **Recommended shorts: one all-red part** | [Red shorts P1S](files/3mf/02_all_red_shorts/King_Shark_ALL_RED_SHORTS_P1S.3mf?raw=true) | [Red shorts P2S](files/3mf/02_all_red_shorts/King_Shark_ALL_RED_SHORTS_P2S.3mf?raw=true) |
| **Recommended legs: both whole legs on one plate** | [Fast legs P1S](files/3mf/03_fast_legs_feet/FAST_BOTH_LEGS_P1S.3mf?raw=true) | [Fast legs P2S](files/3mf/03_fast_legs_feet/FAST_BOTH_LEGS_P2S.3mf?raw=true) |

For the fastest elapsed leg print using both machines, choose [left leg on P1S](files/3mf/03_fast_legs_feet/Two_printers/LEFT_LEG_P1S.3mf?raw=true) and [right leg on P2S](files/3mf/03_fast_legs_feet/Two_printers/RIGHT_LEG_P2S.3mf?raw=true) **instead of** either combined-leg project.

Open the matching 3MF **as a project** and keep its custom process. No AMS is required. Use a standard 0.4 mm nozzle, calibrated PLA and the saved plate orientation/supports. Original full projects contain older shorts and leg layouts: do not print every variant or duplicate parts. Follow the [part-selection and assembly guide](docs/PRINTING_ASSEMBLY.md).

Already printed the chest/head? Keep it. The replacement shorts retain the exact waist-key and leg-socket core. The dark waistband is part of the unchanged torso. Skip the old `Shorts`, `Shorts_panel_L`, and `Shorts_panel_R` when using the replacement.

[Original STL geometry](files/stl/original_v2/) · [All-red shorts STL](files/stl/all_red_shorts/Shorts_ALL_RED.stl?raw=true) · [Fast-leg STL backups](files/stl/fast_legs_feet/) · [Editable all-red Blender assembly](source/all_red_shorts/King_Shark_all_red_shorts_47cm.blend?raw=true) · [Original Blender/source](source/original_v2/)

STLs contain geometry only; they do not retain support settings, color assignments, infill, local joint reinforcement, or optimized print time. Prefer the printer-specific 3MF files.

## Support-inclusive estimates

| Edition | P1S | P2S | Material |
|---|---:|---:|---:|
| Original historical v2, all six plates | 38 h 31 min | 39 h 10 min | about 788 g |
| All-red replacement shorts only | 9 h 57 min | 10 h 07 min | about 218 g |
| Faster pair of legs/feet only | 5 h 33 min | 5 h 38 min | about 151 g |
| Legs split across P1S + P2S | about 2 h 55 min elapsed | simultaneous pair | about 151 g total |

These are Bambu Studio 02.08.02.61 estimates including supports and preparation, not measured completed-print times. The historical total is not a total for the recommended mixed revision. Faster legs save about 65 minutes (16.4%) against the original legs-only P1S benchmark. They use 0.28 mm layers, so printed layer lines are more visible than the original 0.20 mm profile.

## Validation and source

Preserved reports cover closed manifold meshes, STL roundtrips, embedded 3MF geometry, joint/insertion checks, P1S/P2S engine slicing, zero filament changes, and model/support/brim paths within the printer envelope. Publication staging copies the delivered artifacts without changing their geometry. [Current status](docs/VALIDATION_STATUS.md) explains historical report dates and user feedback; [copy inventory](validation/publication_copy_inventory.json) records SHA-256 hashes.

The mesh was generated through Microsoft TRELLIS.2 from the user-approved reference, then repaired and engineered locally. King Shark/Nanaue is an unofficial character interpretation, not an official film asset. No new blanket license or public redistribution permission is asserted. [Credits and provenance](CREDITS.md)

MakerWorld listing: not published. The existing GitHub repository is private; its visibility is unchanged.
''')

    write('docs/PRINTING_ASSEMBLY.md', '''# Printing and assembly

[← Project](../README.md)

## Current compatible combination

Use the unchanged original torso/head, both arms, dorsal fin and white dental arches. Replace the original three-piece shorts group with the single all-red shorts. Use one fast-leg option for the two unchanged whole legs/feet. This makes nine assembly parts instead of the original eleven.

The full historical v2 3MF remains included with all six original plates. Its plates 1, 2, 3 and 6 contain the body/head, left arm, right arm and teeth respectively. Plate 4 contains the old leg layout, fin and shorts panels; plate 5 contains the old shorts. If making the updated combination, use the separate replacement projects for shorts and legs and omit the old shorts panels. Obtain the dorsal fin from its original plate without duplicating the other objects; if you edit a plate, re-slice and review the preview because the saved full-plate estimate does not apply to your edited plate. The original fin STL is also included for a custom arrangement.

Do not reprint a successful torso simply to use the new shorts or faster legs. The shorts' protected connector core is digitally identical to the original, and the leg geometry is exactly unchanged. These are glue-locating joints, not flexible snap clips.

## Materials and settings

Body/arms/legs/fin: gray or black PLA. Shorts: red PLA. Dental arches: white PLA. Every saved plate uses one color. Three logical filament slots in the full projects do not require an AMS; load the current plate's color manually.

Original body/arms/teeth use the original 0.20 mm process. Replacement shorts use 0.20 mm, two walls, 3% gyroid in the body, and local three-wall/15% gyroid reinforcement at the waist key and both leg sockets. The shorts are arranged waist-down with supports and brim.

Fast legs use 0.28 mm layers, an initial 0.20 mm layer, two walls, 2% gyroid, and original three-wall/15% gyroid reinforcement around connectors. They are feet-down, with a 6 mm brim and the original 30-degree tree-support coverage. Keep the support under rounded soles and upper mating seams. The higher layer height trades smoother layer appearance for shorter printing time.

## Assembly order

1. Remove supports and brims carefully from mating faces and sockets.
2. Glue both leg keys into the all-red shorts. Do not add the old side panels.
3. Seat and glue the original torso on the unchanged large waist key.
4. Add both whole arms to the original shoulder keys and attach the fin.
5. Install the lower tooth arch first, approaching from the front/slightly above and moving rearward then down. Install the upper arch from the front/slightly below, moving rearward then up. Keep their hidden connecting gum rails.

Use a small amount of super glue on hidden contact faces. The profile follows the proven large Venom glue-joint approach: nominal 0.18 mm radial root allowance, tapered asymmetric peg and extra blind depth. A digital match does not make printer calibration irrelevant, but no new fit-test coupon is required by this package.

## Archived instructions

The original delivery notes are preserved under `history/` for traceability. They describe the files as originally delivered, including old shorts colors and test status. Use this current guide and `VALIDATION_STATUS.md` for the combined revision and latest user report.
''')

    write('docs/VALIDATION_STATUS.md', '''# Validation status and change history

Current snapshot: October 6, 2026.

| Scope | Evidence | Limit |
|---|---|---|
| Original torso/chest and head | User reports a successful physical print and excellent appearance | No measured time, photos or whole-statue test is recorded here |
| Original realistic v2 files | Saved geometry/STL/3MF checks, digital assembly and insertion paths, successful P1S/P2S engine slices and extrusion-envelope checks | Original notes predate torso feedback; original shorts later had a user-reported infill failure |
| All-red replacement shorts | One closed component, preserved connector core with zero symmetric-difference volume, original mates/path checks, successful slices and toolpaths on both printers | Exact original infill error was not reproduced; replacement physical print/fit not yet reported |
| Faster legs/feet | Byte-identical original geometry, STL checks, four exact project slice/toolpath results, preserved reinforcement | New 0.28 mm process physically untested; timing is estimated |
| Publication package | Source-to-staging SHA-256 equality and project ZIP checks | Publication copying does not add a new physical test |

All original reports are retained under `validation/original_v2`, `validation/all_red_shorts`, and `validation/fast_legs_feet`. They have not been rewritten to erase historical state. In particular, older `physical_print_test: false` entries describe the validation available when the files were made. The later user report applies only to the torso/head.

## Revision details

The all-red shorts restore material in the old side-panel regions. Their protected center, containing the waist key and both leg sockets, has zero change in the saved Boolean comparison. The source report records eight other part meshes byte-identical and an unchanged joint-definition file. Maximum sampled interference against the torso/legs remains below the recorded 0.02 mm³ numerical tolerance. The model remains at its original scale.

Fast legs change only process/layout. The P1S pair estimate is 19,987.211 seconds versus the original legs-only benchmark of 23,906.621 seconds, a 3,919.410-second / 16.3947% reduction. This is a slicer-estimate comparison, even where an archived text file calls it a measured saving. Concurrent left-P1S/right-P2S estimated elapsed time is 10,468.542 seconds (about 2 h 55 min).

Bambu Studio GUI import was not verified for these delivered King Shark projects. Engine parsing/slicing was verified. No printer job is launched by opening this package, and the publication task has not sent a print job.
''')

    write('CREDITS.md', '''# Credits and source provenance

King Shark / Nanaue is the character reference from *The Suicide Squad*. This project is an unofficial fan interpretation, not the film's production model or an official licensed product. Character rights remain with their respective owners; this package makes no claim to grant them.

George Dayoub directed the appearance, colors, size, printing requirements, and iterative modifications. The base 3D geometry was generated through [Microsoft TRELLIS.2](https://huggingface.co/spaces/microsoft/TRELLIS.2) from the exact user-approved reference, then repaired, cut, keyed, colored, arranged and checked locally. A tool's software license is not automatically a license for this character mesh. No blanket CC0, Creative Commons, commercial, or open-source mesh license has been selected or verified for this package.

The retained source record identifies resolution 1024, seed 20261006, target 500000 faces and texture resolution 2048. The raw generated GLB has SHA-256 `031a509823168c16d7e075fa9751d10552ac0909003afcba3b5858fab4c01d1b`. It is included as provenance/editable source and is not the watertight engineered printing solid. The approved reference PNG is explicitly a concept, not a render proving the printable model's details.

This publication preserves the existing private repository's visibility. Authorization to back up files to this repository does not establish a separate public distribution or commercial-use license. No MakerWorld listing has been published for this King Shark project.

The delivered glue-key profile follows the user's successfully printed large Venom approach. This is a dimensional engineering reference; the King Shark source mesh itself is generated from the approved King Shark image rather than copied from the Venom sculpture.
''')

    write('source/README.md', '''# Editable sources

`original_v2/King_Shark_realistic_47cm.blend` preserves the original assembled/exploded/plate scenes. `all_red_shorts/King_Shark_all_red_shorts_47cm.blend` is the editable assembled model with the integrated red shorts. Blender units are millimeters.

The original raw TRELLIS GLB and approved concept are provenance assets, not substitutes for the engineered print meshes. `geometry/` contains NPZ vertices/faces in common assembly coordinates. `all_red_shorts/assembly_meshes/Shorts.npz` replaces only the original shorts group. The fast-leg process keeps the original geometry exactly.

Archived construction scripts and profile JSONs are included for investigation and continuation. They retain assumptions and paths from the original Windows workspace. Their dependent mesh-repair intermediates and bundled Python/Blender runtime are not all duplicated here; the scripts are not represented as a fully portable one-command regeneration kit. Prefer the editable Blender file or documented NPZ geometry when continuing in another environment. No original geometry was regenerated during publication staging.
''')

    project = {
        'id': 'king-shark-47cm', 'title': 'King Shark realistic 47 cm statue',
        'units': 'millimeters', 'assembled_dimensions_mm': {'height': 469.54079667996257, 'width': 323.2682, 'depth': 237.9340},
        'printers': ['Bambu Lab P1S', 'Bambu Lab P2S'], 'nozzle_mm': .4,
        'material': 'PLA', 'ams_required': False, 'recommended_assembly_parts': 9,
        'variants': ['original_v2', 'all_red_replacement_shorts', 'fast_legs_feet'],
        'recommendation': 'Original torso/arms/fin/teeth + all-red shorts + one fast-leg option; do not duplicate original shorts/panels/legs.',
        'status': 'digitally-checked-and-sliced-user-reported-torso-head-print-success',
        'physical_testing': {'torso_and_head': 'user-reported-success', 'all_red_shorts': 'not-reported', 'fast_leg_process': 'not-reported', 'complete_revised_assembly': 'not-reported'},
        'estimated_times_include_supports_and_preparation': True,
        'source_service': 'Microsoft TRELLIS.2', 'character': 'King Shark / Nanaue; unofficial fan interpretation',
        'blanket_mesh_license': 'not-established', 'repository_visibility_at_staging': 'private',
        'makerworld_url': None,
        'preview': 'images/all_red_shorts/assembly_all_red_shorts.png',
        'recommended': 'README.md', 'dated': '2026-10-06'
    }
    write('project.json', json.dumps(project, indent=2) + '\n')

    verification = []
    old_reports = json.loads((original / 'engineering/project_validation.json').read_text())
    for row in old_reports:
        path = OUT / 'files/3mf/01_original_v2' / row['file']
        assert digest(path) == row['sha256']
        verification.append({'file': path.relative_to(OUT).as_posix(), 'matches_prior_checked_sha256': True})
    for pth, branch, rows_key in [(red / 'Engineering/print_verification.json', '02_all_red_shorts', 'printers'),
                                 (legs / 'Engineering/print_verification.json', '03_fast_legs_feet', 'profiles')]:
        for row in json.loads(pth.read_text())[rows_key].values():
            path = OUT / 'files/3mf' / branch / row['file'].replace('\\', '/')
            assert digest(path) == row['sha256'], path
            verification.append({'file': path.relative_to(OUT).as_posix(), 'matches_prior_checked_sha256': True})
    for row in verification:
        with zipfile.ZipFile(OUT / row['file']) as z:
            assert z.testzip() is None
            assert '3D/3dmodel.model' in z.namelist()
        row['zip_and_embedded_model_present'] = True
    write('validation/publication_copy_inventory.json', json.dumps(COPIES, indent=2) + '\n')
    files = [p for p in OUT.rglob('*') if p.is_file()]
    oversize = [str(p.relative_to(OUT)) for p in files if p.stat().st_size >= 100_000_000]
    assert not oversize, oversize
    summary = {'date': '2026-10-06', 'staging_path': str(OUT), 'source_copy_hash_checks_passed': len(COPIES),
               'geometry_regenerated': False, 'existing_project_checks': verification,
               'files_count_before_this_report': len(files), 'total_bytes_before_this_report': sum(p.stat().st_size for p in files),
               'largest_file': max(files, key=lambda p: p.stat().st_size).relative_to(OUT).as_posix(),
               'largest_file_bytes': max(p.stat().st_size for p in files), 'files_at_least_100MB': oversize,
               'raw_gcode_or_logs_included': False, 'published': False}
    write('validation/publication_staging_validation.json', json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()

