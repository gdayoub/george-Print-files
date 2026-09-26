# venomPUFFy — plain screw-on V3

The whole head screws onto the body. Both feet screw off together to open the bottom storage. Everything closes directly against printed plastic seats. **No rubber rings, glue, or extra hardware are required.**

This replaces V1 and V2. The original sleeve geometry remains unchanged at its original size. The head and base have new full screw threads around it; these are not claimed to be an exact copy of an absent original cap.

## Start with the small fit tests

For fewer AMS changes, open `TEST_PRINT_FIRST` and print:

1. **RED_3_TEST_PARTS_V3.3mf** — all three objects in your red Soyelin Ultra PLA.
2. **BLACK_1_TEST_PART_V3.3mf** — the one object in your black Creality Hyper PLA.

Or use **01_SCREW_TESTS_V3.3mf** for all four on one bed. These are the same parts; print only one option. Each separate job uses filament slot 1, so select the intended physical filament in Bambu Studio/AMS.

Use P1S, 0.4 mm nozzle, **100% scale**, and the supplied **PROCESS_PRESETS/SCREW_TEST_020.json** (0.20 mm layers, four walls, 1.2 mm top/bottom shells). Use the same layer height for the matching full-model connections. Keep your calibrated filament profiles. The single-color jobs avoid repeated AMS swaps. Actual print time appears after slicing; no time estimate or G-code is supplied.

The tests are oriented with their closed disks on the bed. Leave supports off for these small parts and inspect the sliced thread overhangs. Do not scale the parts to adjust fit.

Pair the two `HEAD` parts together. Pair the two `BASE` parts together (one red, one black). Screw each pair together gently through multiple full rotations until it reaches its flat seat and stop, then unscrew. Start squarely and do not force a cross-threaded or rough fit. If either pair binds, report which pair before printing the character.

## Print and assemble the character

After the fit tests pass:

- **02_BODY_PLAIN_SCREW_V3.3mf** — body including the original cup sleeve; no separate liner installation.
- **03_HEAD_PLAIN_SCREW_V3.3mf** — entire head, eyes, grin and tendrils together.
- **04_FEET_BASE_PLAIN_SCREW_V3.3mf** — both feet and jar cradle together.

Keep each as one multipart object, with its colors aligned. Assign red, black and pink to the matching AMS filaments. The head tightens clockwise viewed from above. The feet tighten clockwise viewed from underneath. Printed terminal stops set their nominal forward alignment. Each closure opens independently. Hand-tight only.

For the full character, check supports and removal access around the head dome, tendrils and fists in the slicer. Keep support contact away from the original cup cavity, screw threads and flat closing faces. Native Bambu import, supports and actual printing have not been verified.

## What is verified

Digital checks cover the new meshes, full helical opening motion for both closures (sampled every 2 degrees over four turns), nominal closed alignment, terminal stops, jar exit and the restored solid flat closing seats. Seven new color meshes and four test parts are watertight and consistently oriented. This does not establish physical fit or smell-proof performance.

The original STL remains byte-identical in `REFERENCE`. All 7,745 original triangles are included in the body at scale 1 with rigid translation only and zero measured coordinate error. Its existing mesh defects are retained and reported separately; check its sliced cavity and union with the outer body. The new connections do not modify its fit surfaces.

Storage remains 50 mm clear diameter × 33 mm high, with a 3.6 mm separator beneath the original cup cavity. The placeholder jar is 46 × 30 mm; its actual height was not contained in the supplied sleeve file. Actual jar fit and whether the device projects below the original sleeve still need physical checking.

**Odor containment has not been tested.** A tight printed closure is not a verified smell-proof seal. This revision follows the requested all-printed closure without added sealing hardware.

## Editable files and previews

`SOURCE` contains Python CAD, parameters, rendering/package scripts, and the Blender scene. `STL_BACKUPS` holds aligned color parts. `PREVIEWS` and `VIEW_MODEL.html` show the actual V3 geometry. `REFERENCE/digital_validation.json` records the checks. The previous revisions are archived separately and should not be used for this version.

To rebuild, install numpy, scipy, trimesh, manifold3d and Pillow, run `build_symbiote.py`, render with Blender using `render_symbiote.py`, then run `package_print_kit.py`. The source path is configurable in `parameters.json`; the unmodified reference STL is the fallback.
