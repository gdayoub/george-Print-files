# Proxy Pal — NO GLUE Snap Print Kit

This kit adds the character to your original sleeve and uses clips for every separate decorative piece. **The whole head and feet/base now snap on and pull off; they do not screw on.** The supplied sleeve geometry and original file are preserved. Paws print as part of the red body. No glue, screws, magnets or other bought hardware are required.

## Print this first

Open **00_PRINT_FIT_TEST_FIRST.3mf** in Bambu Studio and print the two split pins and six receivers. The receivers have one, two or three small dots: 1 = tighter (0.15 mm clearance per side), 2 = nominal (0.20 mm), 3 = looser (0.25 mm). The small pin tests the face details; the larger pin tests the head/base closures. Try the two-dot receivers first. The full kit uses that nominal clearance. Both sizes should click in, hold, and pull apart without whitening or cracking. These are clearance coupons, not fatigue or final retention tests. If nominal does not work with your actual filament/settings, adjust the clearance and regenerate before the full print. Do not glue a failed fit.

## Print files and estimates

The five root-level 3MF files are sliced Bambu Studio projects for a **P1S, 0.4 mm nozzle, Textured PEI plate**. Each plate uses one color, so all five have zero filament changes and no purge tower. Select the appropriate AMS spool when sending each plate.

| Plate | Estimated time | Filament |
| --- | ---: | ---: |
| 00_FIT_TEST_FIRST | 15m 37s | 2.6 g |
| 01_RED_BODY | 4h 16m | 144.7 g |
| 02_RED_HEAD | 2h 56m | 73.8 g |
| 03_BLACK_PARTS | 1h 33m | 37.5 g |
| 04_PINK_TONGUE | 8m 53s | 0.5 g |

Main kit total, excluding the fit test: **8h 54m and approximately 256 g**. These are Bambu Studio estimates, not measured print times. Red body/head use Soyelin red PLA, black pieces use Creality Hyper PLA, and the tongue uses pink PLA. The projects use conservative PLA starting settings: 220°C and a 12 mm³/s flow limit, derived from the bundled PLA profile. They are not brand-calibrated profiles; use your calibrated filament settings and re-slice if they differ.

Red body/head: 0.24 mm layers, 3 walls, 8% rectilinear infill. Small black/pink parts: 0.20 mm layers, 3 walls, 15% infill. Fit coupons: 0.20 mm, 100% infill. The shell-like head is about 2.4 mm thick, with thicker clip receivers. The body uses a solid CAD envelope with sparse infill, **not a solid 100% print**. Low infill, coarse main-body layers and separate color plates reduce print time. The crest is laid on its side to keep its print height low. Main plates include tree supports where needed; coupons have no supports.

## Glue-free assembly

1. Remove brims/supports and clear every slot/socket. Clear support inside the head and both body openings before assembly. Keep the split pins free to flex.
2. With the red head separate, press in the black eyes, eyebrows and smile along their pins. The smile has three parallel pins. The brows use rectangular keyed pins to prevent rotation.
3. Press the crest along its two parallel pins; it approaches diagonally down and toward the face. The exploded preview shows that direction. Squeeze pin ends from inside the detached head if a detail needs to be released.
4. Press the pink tongue into the red body. The original sleeve is already incorporated into the red body project; it is not a loose insert to glue in. Do not print the source sleeve again for this assembly.
5. Align the head's face with the paws and tongue and press it straight down. Three asymmetrically spaced split clips and bearing pads locate it in one orientation. Open by pulling the head straight upward with an even grip around its lower shell. Do not twist it.
6. Put the closed jar into the lower storage space, align the feet forward and press the base upward. Its three keyed clips locate the base. Remove by pulling evenly on the base; do not use one foot as a long lever or twist the pins.

## Fit and checks

The original source STL is unchanged and its 7,745 faces are retained in the body slicer project. The 3MF uses shared indices for exactly coincident source vertices; this moves no vertex and removes no face, but prevents erroneous slicer infill across the cup. Bambu reported zero removed/reversed facets or fixed edges on import. All ten NEW meshes are watertight, each forms one connected solid, and the assembled parts have no significant intersections. Cup keep-out clearance checks passed. Straight insertion/removal was checked every 0.5 mm using a geometrically compressed-barb envelope. This verifies motion space, not elastic force, fatigue or guaranteed PLA durability. Clip strength and retention require the fit print and handling test.

All five projects sliced successfully without reported warnings. Model/support extrusion coordinates were checked within the 256 mm build volume. Central probes in both cup and storage cavities found no non-support print paths blocking them. These probes do not replace a full physical cup/jar fit test. The unchanged input mesh retains its pre-existing defects, so the statement that meshes are watertight applies to the ten new parts, not to the original sleeve.

Storage still assumes **one closed jar about 46 mm wide and 30 mm high**. The upper storage bore is 58 mm, lower access recess 67 mm, and a continuous 3.5 mm floor separates storage from the cup. Jar dimensions were estimated, not measured. Test jar removal and that the full head clears the actual inserted cup/device. The base and head can be opened independently.

## Other folders

- `STL_BACKUPS`: individually oriented pieces plus the grouped body/core input 3MF. Use the root-level P1S projects for the prepared print settings. The exterior-only red body STL is under REFERENCE, not offered as a standalone print because it would omit your sleeve.
- `REFERENCE`: assembled/exploded/section previews, aligned CAD parts, source STL, checks and estimated slicing reports. The assembled review 3MF is a reference, not a print-in-place layout.
- `EDITABLE`: Blender mesh model, build/render/verification scripts, parameters and input meshes. Install the listed Python dependencies to regenerate. Generated files appear inside that folder's `outputs/snap_print_kit`. The original fitted sleeve is never a Boolean operand.

Clip clearances, smooth transitions and print orientation need physical calibration; the design approach follows the [Makers Making Change snap-fit guide](https://makersmakingchange.github.io/OpenAT_Design_Guide/Design_Elements_For_3D_Printed_Parts/Snap_Fits.html). No physical test print has been performed by Codex.
