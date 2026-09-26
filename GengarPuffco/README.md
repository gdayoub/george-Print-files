# GengarPuffco — Rounded V3

A fuller Gengar silhouette around the **complete original Core Case**: rounded belly, tucked hands, short feet, red eyes and a pink grin. The head twists off, and the deeper red bottom cap is a removable storage cup. The functional foundation remains at its original size.

| Assembly | Width × depth × height |
|---|---|
| Complete original foundation | 57.4 × 57.4 × 96.0 mm |
| **Current Gengar Rounded V3** | **84.5 × 71.7 × 122.9 mm** |
| Previous Slim V2 | 65.7 × 61.7 × 109.8 mm |
| Superseded first Gengar | 94.7 × 79.6 × 127.7 mm |

The body is deliberately wider than Slim V2. Overall it is **27.1 mm wider, 14.3 mm deeper and 26.9 mm taller than the complete original case**. The original case starts 24 mm above the bottom to accommodate the deeper cup; the ear tips add about 2.9 mm above its lid. The generator limits the assembly to 85 × 80 × 124 mm. This added height is the tradeoff for usable storage underneath the unchanged foundation.

![Both models at the same scale](Previews/06_size_comparison.png)

Black case, red eyes and bottom cap, pink grin. The face, ears and side ridges come from your actual `GengarBowlRef.3mf` mesh, with a rounded lower body and short feet added around the foundation. Only the decorative mesh changes shape; the original functional case is never scaled.

## Closures and storage

- **Head:** the decorated upper half twists off on the original approximately 2.5 mm-pitch thread. Turn counterclockwise viewed from above while holding the lower half.
- **Bottom:** an independent red screw cup opens the deeper accessory compartment. Turn counterclockwise viewed from underneath.
- **Storage:** 50 mm clear diameter × **18 mm** clear height, three times the previous 6 mm depth. The cup has a 3 mm floor and a 21 mm overall height. A nominal 50 mm cavity is not a guarantee that a particular 50 mm jar will fit; a specific jar has not been measured.
- The original head thread is preserved with no added stop. Its final tightened facing direction still requires a physical test.

## Fit first

The earlier printed Venom was reported too tight. Its unsliced source geometry audit found no scaling error, so the physical cause was not established. This revision preserves the original base, lid, device cavity, accessory slots and mating threads at 100% scale. New material is checked against the original internal free space, not just a nominal bore size.

If the original foundation has not already been printed successfully, start with `Print/P1S/00a_ORIGINAL_BASE_ONLY_P1S.3mf` and `00b_ORIGINAL_LID_ONLY_P1S.3mf`. These contain only the unmodified original geometry. Check full-depth insertion, removal and closure after cooling. If your original case already fits correctly, skip repeating that test and compare the new body directly.

Print the actual new body next, then its bottom cap, before spending filament on the colored head. Never scale the whole assembly to fix a tight fit. Exact CAD dimensions do not establish physical fit with a particular printer, filament, flow setting or support cleanup.

## Print projects

Open these **as projects** in Bambu Studio. Keep 100% scale and the saved orientation:

1. `Print/P1S/01_BODY_EXACT_FOUNDATION_P1S.3mf` — black, original base surrounded by the fuller body, hands, feet and deeper storage housing.
2. `Print/P1S/02_GENGAR_HEAD_COLOR_P1S.3mf` — black/red/pink, original lid with the Gengar exterior. It prints inverted, with the original cavity facing upward.
3. `Print/P1S/03_BOTTOM_CAP_P1S.3mf` — red, independent removable storage cup.

`02b_GENGAR_HEAD_SINGLE_COLOR_P1S.3mf` is an optional all-black head with identical geometry. The colored face regions are aligned multipart AMS regions, not separate snap-in inserts. Estimates are in [PRINT_ESTIMATES.md](PRINT_ESTIMATES.md).

Benchmark: P1S, 0.4 mm nozzle, textured PEI; 0.20 mm layers, four walls, 8% gyroid, zero XY hole/contour compensation. Generic PLA at 220°C, bed 55°C and 12 mm³/s is a benchmark assumption, not a calibrated profile for your spools. Choose the actual red, black and pink filament profiles and re-slice. Inspect exterior head supports and support removal through the open bottom compartment. No printer job has been sent.

`Print/Geometry` contains exact unsliced 3MFs. `ASSEMBLED_VIEW_ONLY.3mf` is for inspection, not print-in-place. All current files in this folder are Rounded V3; earlier versions are retained in Git history.

## Checked digitally

The original archive hash is preserved. Both original meshes retain their triangle topology and source vertices under rigid placement in the geometry exports. Native Bambu exports are checked for unit scale, triangle counts, serialization precision and zero XY compensation. New meshes are checked for closed surfaces, consistent winding and positive volume.

The head, lower case and cap each form one combined connected solid. Both screw-opening paths are sampled every 5° through four full turns, followed by head-lift and compartment-exit checks. New material is tested against free space inside the original source envelopes. Physical fit, face alignment, durability, sealing and support removal remain unverified.

Reports are in `Reports/`. In the section preview, green highlights the unchanged original case for clarity; it is not a separate filament color.

## Source and editing

`CAD/Gengar_Compact_EDITABLE.blend` contains the current Rounded V3 mesh and studio scene. `build_gengar.py` rebuilds it; `export_prints.py` writes checked geometry; `render_gengar.py` creates the previews and size comparison; `render_section.py` creates the cutaway. Run `slice_p1s.py <path-to-bambu-studio.exe>` for native projects, then `verify_native.py`. Dependencies are in `CAD/requirements.txt`.

Original complete case: **ROADBLOCK**, “Core Case for Puffco Proxy Core,” embedded MakerWorld Exclusive License. Gengar bowl: **tom3Dmodel**, “Gengar pokemon Bowl,” embedded Standard Digital File License. Original archives and their metadata are retained in `Foundations`. This derivative does not assert additional redistribution rights.
