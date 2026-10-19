# How the full-size Venom statue was made

This is the build record for the approximately **464.74 mm** edition, prepared for Bambu P1S/P2S. Venom followed a different route from King Shark: **no image-to-3D service generated its base sculpt**. George supplied a 3MF titled `Venom Marvel Rivals (Exclusive)`, credited inside the file to **OVERRIDE3D_5884368**. The original sculpture, pose and muscular proportions belong to that source. The work here modified and engineered it for printing; see [credits and license](../CREDITS.md). The source says **Standard Digital File License**, and public redistribution permission has not been established. This repository is a private backup, not a grant to republish or sell the derivative. To recreate from scratch, obtain an authorized original source file first.

## 1. Extract and inspect the supplied 3MF

The original input was `black+venom+marvelrivals.3mf`. It is a ZIP container with printable mesh XML, transforms, triangle paint data and slicer metadata. The archived process inspected its object/build references and color attributes, extracted the principal mesh, restored its upright orientation, centered X/Y, put the feet at Z=0 and scaled uniformly to an initial **480 mm** engineering height. A valid geometry-bearing 3MF was essential because an earlier broken export showed “no geometry data”/invalid geometry in Bambu Studio. The finished large edition is **464.738 mm**, as the final assembly geometry was prepared later.

The first checks were watertightness, winding, component count, physical bounds and actual rendered views. The goal was to **preserve the original pose, muscle size and symmetry** while removing the floating symbiote material around the shoulders/back. The retained [size-1 Blender archive](../source/Venom_Size1_Blender.zip?raw=true) and [12-part STL archive](../Size_1_465mm/Venom_Size1_STL_parts.zip?raw=true) are the editable/printable geometry available in this folder. The supplied original 3MF is not part of this curated statue folder. The original scripts relied on workspace intermediates and local profile JSONs; this document is a faithful reconstruction of the process, not a claim of one-command regeneration from these downloads alone.

## 2. Remove the external tendrils while keeping the anatomy

The saved `remove_venom_tendrils.py` process voxelized the upper region at **0.65 mm** pitch and distinguished thin projections from broad muscle by distance to an 18 mm interior core. It preserved the lower body and protected the front face/tongue. A later `smooth_muscle_envelope.py` pass softened the mask boundary before Boolean intersection with the original sculpture. The resulting closed, muscular source retained the major torso/arm contours rather than replacing them with a new generic body. For a new character, inspect the removal mask and the actual result from every side before making any cuts. A high-level instruction like “remove tendrils” is insufficient: it can erase shoulder muscle or facial geometry if the protection zones are wrong.

## 3. Cut for P1S/P2S and build concealed glue joints

Initial Boolean cuts divided torso, pelvis, legs and arms so the printer could handle a roughly 46.5 cm figure. The final version merged each arm back into **one continuous arm/hand piece** and kept each lower leg/foot whole, reducing visible arm seams and support/handling. White eye, chest and tooth regions and a red tongue were extracted as separate prints; their receiving recesses were cut in the black host parts. White insert sockets have approximately **0.20 mm** nominal allowance.

The major assembly uses **six asymmetric 64-sided tapered glue keys**. The key narrows to **0.84** of root size at the tip. The intended radial root allowance is **0.18 mm**, with extra blind socket depth. The asymmetric shape registers orientation and leaves a close outer seam; it is a locating/gluing joint, not a flexible snap clip. [The saved joint record](../validation/Size1_joints.json) gives the actual centers, normals, sizes and collision results; [insert record](../validation/Size1_inserts.json) gives the color-part fits. An earlier Buu print informed the glue-joint strategy, but these are engineered Venom joints, not copied Buu connectors. Once cut and fitted, protect the mating faces and edges from global smoothing, remeshing or uniform shrink operations.

The user later requested an optional **two-printer torso-split** edition. That was a separate derivative with upper/lower torso registration. The [current full-size release](../Size_1_465mm/) documented here keeps its torso continuous. Do not interchange torso halves, joints or plates between different Venom revisions without checking exact geometry and scale.

## 4. Smooth conservatively and make it light in the slicer

The final large edition used local Taubin smoothing on the black anatomy to reduce distracting roughness. Sharp muscle/vein ridges, color boundaries, print-bed contacts and connector areas were locked. Recorded maximum movement was **0.06 mm**; white and red inserts were unchanged. [Smoothing report](../validation/Size1_smoothing_report.json) records the per-part result. The sculpt remained a set of closed exterior solids. Lightweight printing came from the 3MF profile, rather than making an arbitrary thick hollow shell that could create infill/roof problems.

Large-edition settings: **0.20 mm layers**, two walls, four top layers/0.8 mm, three bottom layers/0.6 mm and **10% lightning** infill for the main black parts; legs use **2% gyroid**. Local connector modifiers use three walls, 15% gyroid and five top layers. Automatic tree supports use a 30-degree threshold, 0.20 mm support Z gap and 0.35 mm XY gap, with 3 mm brims. The outer-wall target was 120 mm/s and 3000 mm/s² acceleration. These are recorded settings, not universal defaults for a new sculpt; slice and inspect any new overhang/roof geometry.

The arms print on shoulder faces, legs feet-down, torso on its waist cut, and accents in prepared orientations. Colors are single-color plates: **black body/limbs, white inserts, red tongue**, requiring no AMS. The [P1S](../Size_1_465mm/Venom_Size1_P1S_SEPARATE.3mf?raw=true) and [P2S](../Size_1_465mm/Venom_Size1_P2S_SEPARATE.3mf?raw=true) 3MFs contain the actual profile and plate layout. Open them **as projects**. An STL alone loses supports, infill, modifiers, color assignments and layout. The full-size P1S project has eight plates, twelve assembly parts, and an estimated **37 h 58 min / 772.2 g**, including supports and startup; P2S was estimated at **38 h 39 min / 771.7 g**. Those are Bambu Studio 02.08.02.61 estimates.

## 5. Check the files that will actually be printed

Inspect every closed part and seated joint collision, then reimport the **exported binary STL** to catch float32 degeneracy. Reparse the embedded 3MF XML: it must contain nonempty vertices/triangles, valid objects/build references, millimeter units, previews and process settings. Slice each plate with its exact printer profile, require no geometry errors, and check model/support/brim toolpaths against the 256 mm bed and the P1S front-left exclusion. Verify logical filament mapping and zero color changes for non-AMS plates. The published [size-1 slice reports](../validation/) and [per-plate estimates](../validation/Size1_plate_estimates.csv) are the retained checks. A successful Bambu import and digital fit check are not substitutes for a physical print.

George later reported that a large Venom version printed and assembled successfully. The historical validation bundled with this particular released revision predates that report, so it still labels physical fit as untested; the report is useful feedback but does not identify every exact binary/version. For a new model, record the exact file hash, printer, filament and physical assembly result before claiming a variant is proven.

## Reuse this approach for a different source sculpture

1. Obtain a source model you are allowed to use; save its title, creator, license, version and original file hash.
2. Inspect the actual mesh and 3MF metadata; normalize units/orientation and freeze the desired overall scale.
3. Remove only unwanted outer features using a reviewed mask; compare views before and after to protect anatomy and silhouette.
4. Plan cuts from printer envelope, support direction and natural hidden seams; keep limbs whole if they fit efficiently.
5. Make color accents separate manifold pieces and cut slightly larger mating recesses in the host.
6. Add asymmetric glue keys with a stated allowance; validate seated overlap and full insertion paths, then freeze all mating surfaces.
7. Smooth exterior anatomy only under a displacement cap; lock ridges, details, mating faces and bed contacts.
8. Use sparse slicer infill and local joint reinforcement, test orientations with **support-inclusive** Bambu estimates, and keep one color per plate for non-AMS.
9. Reopen both STL and 3MF exports, slice them, check full toolpaths, and save editable source, settings, renders, estimates and a precise physical-test status.

[Printing and assembly details](PRINTING_ASSEMBLY.md) · [Large source Blender file](../source/Venom_Size1_Blender.zip?raw=true) · [Source credit](../CREDITS.md)
