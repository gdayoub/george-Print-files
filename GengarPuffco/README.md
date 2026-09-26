# Gengar Compact — original Core Case foundation

Digital prototype based on your Gengar bowl, with a twist-off Gengar head and an independently opening bottom compartment. Black body/head, red eyes and bottom cap, pink grin. The foundation remains at **100% scale**.

The character is approximately **94.7 × 79.5 × 127.7 mm**, versus Venom's **160 × 87 × 175.2 mm**: about **41% narrower and 27% shorter**. The complete original case itself is almost 97 mm tall when assembled; it sets a real lower limit on the size. Only the decorative Gengar bowl is uniformly reduced to 65%. Its face and ears retain their source proportions. A slim new body fits around the original lower case.

![Actual model render](Previews/01_assembled.png)

## Start with fit

Your printed Venom was too tight. The audit found its original base/lid vertices and triangles unchanged in the unsliced exports; it did **not** establish the physical cause of the tightness. Printer calibration, slicing, supports, material and the changed surrounding structure remain possible contributors. We do not infer that this new model's physical fit is proven.

If you have not already printed the original foundation successfully, use `Print/P1S/00a_ORIGINAL_BASE_ONLY_P1S.3mf` and `00b_ORIGINAL_LID_ONLY_P1S.3mf` first. These contain only the unmodified original meshes. Check full-depth device insertion, removal and the original screw closure after cooling and removing any brim. If your original case is already a known good print, you can skip repeating it and compare the new body directly.

For the new case, print **01_BODY_EXACT_FOUNDATION** before the decorated head. This tests the actual final body/cavity and includes the lower compartment. Check it with the original lid and your device. Then print the bottom cap to check its new coarse thread. The expensive colored head comes last. Never force a tight part or scale the whole assembly to change its fit.

## Print files

Open the files under `Print/P1S` **as projects**, keep 100% scale and the saved orientations:

1. `01_BODY_EXACT_FOUNDATION_P1S.3mf` — black; original case base plus compact body, arms and feet.
2. `02_GENGAR_HEAD_COLOR_P1S.3mf` — black, red, pink; original lid inside the Gengar head. The head is inverted for printing so the original lid cavity faces up. External supports and a brim are used.
3. `03_BOTTOM_CAP_P1S.3mf` — red; independent lower screw cap.

`02b_GENGAR_HEAD_SINGLE_COLOR_P1S.3mf` is an optional all-black head with the same geometry. It can be used as a simpler prototype or painted afterward. The contrasting face regions in the full-color file are aligned multipart AMS regions, **not** separate snap-in inserts.

Machine benchmark: P1S, 0.4 mm nozzle, textured PEI; 0.20 mm layers, four walls, 8% gyroid, zero XY contour/hole compensation. Generic PLA profiles at 220°C, bed 55°C and 12 mm³/s are assumptions, not calibration for your red, black or pink spools. Select your actual calibrated profiles and re-slice. Inspect support removal around ears, arms and the outside of the inverted head; the original functional cavity is kept upward. No printer job has been sent.

`Print/Geometry` contains exact unsliced 3MF exports. `ASSEMBLED_VIEW_ONLY.3mf` is for inspection, **not print-in-place**. Original functional meshes remain separately identifiable in the body and head assemblies. Geometry files store the originals with double-precision coordinates; final exported source vertices and topology are checked against the foundation arrays.

## Openings and storage

- Hold the lower body and turn the whole Gengar head counterclockwise viewed from above. It uses the original approximately 2.5 mm-pitch thread.
- Turn the recessed red bottom cap counterclockwise viewed from underneath. It uses a separate 3.5 mm-pitch thread, with 0.35 mm modeled radial and 0.22 mm axial clearance.
- Bottom storage has **50 mm clear diameter × 16 mm clear height**. This is a shallow accessory compartment. **The earlier 46 × 30 mm jar placeholder does not fit.** No actual jar dimensions were supplied for this revision.
- The head and bottom cap operate independently. The head's final tightened facing direction still needs a physical test; preserving the original threads does not add an alignment stop.

## Verification and limits

The foundation archive hash is unchanged. Source base: 88,278 triangles; source lid: 52,836 triangles. Exact source mesh identity is checked in the geometry exports after undoing rigid placement. New solids are checked for closed meshes, winding and positive volume; head, body and cap each form one combined connected solid.

New material is checked against the **actual original free space inside each source convex envelope**, not just a guessed bore diameter. The head clears the original base envelope. Both opening paths are sampled every 5° through four turns, followed by a head-lift check and an exit check for a 49 mm-diameter compartment probe. These are digital sampled checks, not physical validation of fit, strength, sealing or support removal.

See `Reports/geometry_validation.json`, `Reports/export_verification.json`, `Reports/*_slice.json`, and `Reports/venom_fit_audit.json`. Actual slicer estimates are summarized in `PRINT_ESTIMATES.md` after slicing.

## Editable source

`CAD/Gengar_Compact_EDITABLE.blend` contains the actual assembled meshes and presentation scene. Keep original case objects unchanged. `CAD/build_gengar.py` rebuilds geometry; `export_prints.py` exports checked 3MFs; `render_gengar.py` renders the actual meshes; `slice_p1s.py <path-to-bambu-studio.exe>` produces the native projects. Python dependencies are in `CAD/requirements.txt`. Blender rendering uses `bpy`.

This project lives in the repository's `GengarPuffco/` folder. Venom is preserved separately. No printer operation was performed.

## Source attribution

Original complete `Core_Case.3mf`: ROADBLOCK, “Core Case for Puffco Proxy Core”; embedded MakerWorld Exclusive License metadata retained. Gengar exterior: tom3Dmodel, “Gengar pokemon Bowl,” supplied as `GengarBowlRef.3mf`; embedded Standard Digital File License metadata retained. Both original archives are retained in `Foundations`. This local derivative does not assert additional redistribution rights.
