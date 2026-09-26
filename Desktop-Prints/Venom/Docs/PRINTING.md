# Venom V4 — faster print projects

Use the three **FAST_COLOR** 3MF projects in `Print/FullColor` to keep the red, black and pink appearance. Open them as projects in Bambu Studio so their process settings, part assignments and height modifiers are retained.

All three projects were sliced successfully for **Bambu Lab P1S / 0.4 mm nozzle / Textured PEI Plate**. No print was started.

| Assembly | V4 baseline estimate | Faster full-color estimate |
|---|---:|---:|
| Body | 19 h 38 m | 14 h 55 m |
| Head | 26 h 18 m | 22 h 09 m |
| Feet / storage | 2 h 52 m | 2 h 40 m |
| **Total** | **48 h 48 m** | **39 h 44 m** |

This saves approximately **9 hours (19%)** while keeping every color and the same model geometry. These are Bambu Studio estimates from a controlled comparison, not measured print times. The baseline uses the previously recommended 0.20 mm / four-wall / 10% gyroid setup, with automatic tree supports. Both variants use identical machine and filament assumptions.

## What was optimized

- Body: 0.28 mm layers through the decorative middle, with **0.20 mm layers and four walls** at the lower storage thread and original top thread.
- Head: 0.24 mm layers above the original threaded socket; the lower 10 mm stays at **0.20 mm / four walls**.
- Feet and storage connection: remain at **0.20 mm / four walls** throughout.
- Decorative regions: three walls and **5% adaptive cubic infill**, with at least 1.2 mm top and bottom thickness. The original case and lid parts retain four-wall overrides.
- Tree-support threshold reduced from 30° to 25° to target the steeper overhangs. Automatic supports are still enabled, including internal supports where the slicer finds them necessary. Existing support can receive purge material; flushing into model infill remains off.
- The original case geometry, device cavity, five accessory slots, both original mating threads, added storage thread, overall size and colors are unchanged. No part was scaled or hollowed by editing its fit surfaces.

Expect more visible layer lines on the decorative body and slightly reduced stiffness from the lighter decorative infill. The threaded areas retain the finer layers. Support removal, physical fit and durability still need a real print check; successful slicing alone does not establish them.

## Before printing

1. Open **01_BODY_FAST_COLOR.3mf**, **02_HEAD_FAST_COLOR.3mf**, or **03_FEET_STORAGE_FAST_COLOR.3mf** as a project. Print the assemblies separately; keep their multipart color alignment and 100% scale.
2. Assign the actual red, black and pink AMS spools. The estimate uses generic PLA assumptions: 220°C nozzle, 55°C textured bed and a 12 mm³/s volumetric limit. Select your calibrated Soyelin/Creality/pink PLA profiles and **re-slice**. The embedded G-code is a benchmark snapshot, not calibration for your particular spools.
3. Check layer preview and support-removal access around the fists, tendrils, dome, cup interior and threads. The original source base's overlapping internal pieces and tiny degenerate faces remain in the source geometry; inspect their sliced union.
4. Keep the height modifiers. Importing only the geometry into a different project may discard the speed setup and threaded-area overrides.

No high-speed machine override, increased volumetric limit or reduced black-to-pink purge volume was used for the comparison. Color changes still dominate: preserving every marking limits how much time process settings alone can save.

## Optional: maximum time savings

`Print/SingleColor` uses the same shape and fast settings, with one color per assembly: red body, red head and black feet. It removes the contrasting markings rather than adding separate glue-in or snap-in decorations. Paint details afterward if desired.

| Assembly | Single-color estimate |
|---|---:|
| Body | 5 h 49 m |
| Head | 4 h 24 m |
| Feet | 1 h 03 m |
| **Total** | **11 h 16 m** |

This is approximately 77% less time than the full-color baseline. It is optional; the main folder retains all colors.

## Verification and source

`Reports/time_comparison.json` contains detailed times, material estimates and filament-change counts. `Reports/verification.json` records unchanged mesh XML in the optimized inputs, retained source triangle counts in the Bambu exports, archive checks and actual generated layer-height checks in the threaded bands. Each native project sliced with no reported slicer warning.

Original case: ROADBLOCK, “Core Case for Puffco Proxy Core.” The unchanged original 3MF and its attribution/license metadata are in `Foundations`. The editable V4 CAD/Blender source is in `CAD`; these optimized projects change printing configuration only. The benchmark Python scripts refer to that local V4 workspace and are included for reproducibility.

The height-modifier serialization follows [Bambu Studio's 3MF implementation](https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/Format/bbs_3mf.cpp), and the saved modifiers were checked in the exported projects and generated layers.
