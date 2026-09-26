# Venom V4 — built onto the complete original Core Case

This revision uses **Core_Case.3mf**, supplied September 26, 2026, as the actual functional base. Both original meshes are included at scale 1. The Venom body is bonded to the original case exterior; the Venom head is bonded to its original screw-on lid. The original internal cavity, five accessory slots, lid interior and original mating threads are retained. The former sleeve and invented V3 head connection are absent.

Original Core Case design attribution: **ROADBLOCK**, “Core Case for Puffco Proxy Core.” The byte-identical original 3MF, with its original metadata, is in `Foundations/Core_Case.3mf`. Its metadata identifies the MakerWorld Exclusive License. This is a local derivative project; no redistribution permission is asserted.

## Files to use

- `Print/Geometry/01_VENOM_BODY_V4.3mf`: Venom body plus the exact original case base, as one multipart print assembly.
- `Print/Geometry/02_VENOM_HEAD_ORIGINAL_LID_V4.3mf`: Venom head plus the exact original lid, as one multipart print assembly.
- `Print/Geometry/03_VENOM_FEET_STORAGE_V4.3mf`: joined feet and separate screw-off jar cradle.
- `CAD/Venom_Core_Case_V4_EDITABLE.blend`: editable assembled Blender scene.
- `Previews`: renders of these meshes.
- `Print/Geometry/ASSEMBLED_VIEW_ONLY.3mf`: assembled review; **do not print in place**.

Open each print assembly separately in Bambu Studio. Keep its aligned colors and original component together as parts of one object. Red = slot 1, black = slot 2, pink = slot 3 in the supplied metadata; map these to your actual AMS filaments. Keep **100% scale**. Files use millimeters and fit a P1S bed individually.

Use your calibrated PLA profiles. A starting process is 0.20 mm layers, four walls, 10% gyroid infill and 1.2 mm top/bottom thickness. Full-model supports and support-removal access require slicer review, especially beneath the head dome, tendrils and hands. Keep supports off the original device cavity, accessory slots and both threaded joints. These files are unsliced geometry, with no G-code or verified time estimate.

## What changed

The approximately 57.4 mm-wide source case replaces the earlier approximately 45.9 mm sleeve. The original base is 52.5 mm tall; the lid is approximately 51 mm tall before their threaded overlap. Neither is scaled. The surrounding character is approximately 160 × 87 × 175 mm. The hands were raised to maintain clearance as the feet unscrew.

The head uses the original approximately 2.5 mm-pitch right-hand thread. The complete head unscrews counterclockwise viewed from above. The retained custom storage base uses a separate 4 mm-pitch thread; it unscrews counterclockwise viewed from underneath. Each compartment opens independently. No added glue, rubber rings or separate fastening hardware is required.

Storage is still 50 mm clear diameter × 33 mm high for a **provisional** 46 × 30 mm jar. Its dimensions were not supplied by this case model. The case's original floor is retained above a separate 3.6 mm storage separator. A shallow bond extends only into the existing solid underside of the original case floor, without entering its cavity.

## Validation and remaining checks

The source archive is byte-identical. Both original component meshes retain their triangle topology and vertex positions under rigid assembly transforms. They are separately identifiable inside the output 3MFs. The original base contains overlapping internal pieces and a few degenerate source faces; those are preserved in the delivered meshes rather than silently remeshed. Only the temporary analysis copy unions those overlapping shells for collision calculations. Check the original cavity and the union of these parts in Bambu Studio's layer preview.

The new decorative color meshes pass watertightness, winding and positive-volume checks. Added material is excluded from the original cavity and thread region. Sampled checks cover both closures through four full turns, with the original head thread at 2.5 mm pitch and the storage thread at 4 mm pitch, plus head lift and jar exit. These are sampled digital checks, not physical certification. See `Reports/geometry_validation.json`.

The original head thread has no added alignment stop. The preview uses a collision-free assembled phase, but the head's final tightening angle depends on the original thread clearance and your print. Exact forward alignment, physical device fit, actual jar fit, loaded stability, support removal and odor containment remain unverified. Print or test the included original case first if its fit is not already established. The original case photos are reference material, not evidence that this derivative has been printed.

## Rebuilding

The editable Python mesh-CAD source and JSON parameters are in `CAD`. Install the listed Python dependencies, run `build_venom_v4.py`, then run Blender in background mode with `render_venom_v4.py`. The reference meshes are stored as exact double-precision arrays. The `.blend` is for editing and reviewing; exclude reference jar, camera, lights and studio plane when exporting prints.

V3 files remain untouched in their previous folders. Use this V4 package for the corrected complete-case version.
