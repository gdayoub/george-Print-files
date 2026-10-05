# Printing and assembly

Open the `.3mf` for your exact printer as a **project**, keeping its project settings. All files contain full geometry; none contain ready-to-send G-code. PLA, 0.4 mm standard-flow nozzle, Textured PEI plate, 0.20 mm layers. Select your actual filament and bed surface, then slice. Keep the custom process `Venom Shelf 0.20mm Lightweight` for Size 1 or `Venom Size 2 0.20mm separate/ams` for Size 2.

## Choose a version

- **Size 1 / 464.74 mm:** eight single-color plates, twelve glue-together pieces. This is the corrected lightweight edition, with a continuous torso and whole arms/legs.
- **Size 2 / 232.37 mm, SEPARATE:** four single-color plates, twelve pieces. Recommended for speed and material economy; no AMS required.
- **Size 2 / 232.37 mm, AMS:** two plates, seven assembly pieces. White accents print as attached material in the torso/right arm. A separate red tongue shares the first plate. You still glue the body sections together.

Keep the supplied print orientations. The arms print on their shoulder faces, legs feet-down, torso on the waist cut, and accents on their prepared orientation. The projects retain support where the pose needs it. This is not a support-free model.

## Material assignments

Slot 1: black PLA. Slot 2: white PLA. Slot 3: red PLA. For the AMS project, map these to your loaded AMS slots before sending a job. Both AMS colors are normal PLA, not dedicated support material.

For separate-color STLs, print `L_arm`, `R_arm`, `L_leg`, `R_leg`, `Pelvis`, and `Torso` in black. Print both `Chest_*` inserts, both `Eye_*` inserts, and `Teeth_Torso_01` in white. Print `Tongue` in red. STL contains geometry only; it cannot preserve the 3MF colors, wall/infill settings, plate arrangements, or joint reinforcement modifiers.

## Lightweight settings

Two walls (nominal outer 0.42 mm + inner 0.45 mm), four top layers / 0.8 mm, three bottom layers / 0.6 mm, 10% lightning infill. Legs use 2% gyroid. Small local joint modifiers use three walls, 15% gyroid and five top layers. Automatic tree supports, 30-degree threshold, 0.20 mm support Z gap, 0.35 mm XY gap, and 3 mm brim. Outer walls print at 120 mm/s with 3000 mm/s² acceleration.

The geometry remains a closed solid surface; Bambu creates the lightweight internal structure from the 3MF settings. Importing the STL and choosing heavy infill will produce a heavier, slower print.

AMS enables a prime tower and nonzero directional purge volumes. The first plate contains all three colors; the second plate is black. White details need clean black-to-white transitions, so the AMS edition uses more filament and time than the separate-color edition. Purge settings are starting values, not a guarantee against color contamination with every filament.

## Assemble

1. Remove supports and brims, and clear the socket interiors and mating faces.
2. Seat the left and right legs into the pelvis, then seat the torso on the pelvis. Each asymmetric tapered key has one intended orientation.
3. Attach each complete arm at its shoulder and the tongue at the mouth.
4. On the separate-color edition, glue the five white accents into their matching recesses. The AMS edition already includes these accents.
5. Use a small amount of super glue on the internal key/socket contact surfaces and hold the outer mating faces together while it sets. Keep glue off visible details.

There is no intentional gap between the exterior body mating faces. Keys have 0.18 mm nominal radial allowance at the root; white glue inserts have about 0.20 mm allowance. Size 2 preserves these absolute allowances by enlarging its receiving cavities rather than simply halving every clearance. Parts from different sizes do not mate. These are glue joints, not spring snap clips.

The joint style follows the Buu reference, but these are engineered Venom joints, not exact Buu copies. A fit coupon is optional. Printer calibration, filament, supports, and glue application still affect physical fit and visible seams; digital checks do not establish a physically tested fit.

## Validation

Closed, consistently oriented meshes; all six joint pairs checked for interference; all small assembly parts checked for overlaps. Twelve small STL files were reloaded and checked after binary export. Two STLs use a maximum 0.00003 mm numerical separation to prevent coincident edges from collapsing during float32 export; this is far below printable resolution. The original pose and muscle proportions remain.

Full-size and small projects were sliced with the installed Bambu Studio 02.08.02.61 engine. Estimates include supports, preparation, and AMS purge/prime where applicable. Model/support/brim/prime-tower extrusion paths are checked against the bed volume; P1S checks also exclude its front-left reserved corner. Printer startup/wiping motions are not model toolpaths. No jobs were sent to either printer during release preparation. The user’s earlier experience with the source/Buu is not a physical test of these new editions.
