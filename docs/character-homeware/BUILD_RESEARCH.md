# Build research: King Shark sculpture, print revisions and reusable lessons

Recorded October 6, 2026 from the retained construction reports, delivered files, source scripts and user feedback. Links below target this document's published location under `docs/character-homeware/`. This document explains the decisions; the linked JSON reports retain the detailed measurements.

## User constraints and strongest evidence

The user wants recognizable, muscular character pieces with efficient support use, low material consumption, and P1S/P2S compatibility. Whole arms and lower legs are preferred when they fit the printer. Non-AMS plates with separate color parts avoid repeated color changes. Matching glue-locating keys and close exterior seams matter more than optional test coupons.

The user physically printed the large Venom successfully, then reported that the King Shark chest/head printed and looked excellent. Those successes are user reports, not a physical test of every later derivative. The King Shark torso is now a fixed interface: do not reshape, scale, remesh or replace it just to optimize another part. The all-red replacement shorts must fit the existing waist and legs, and the faster legs preserve the original meshes. The latest homeware designs are independent scaled adaptations; they do not alter the full statue.

[Current statue status](../../prints/king-shark-47cm/docs/VALIDATION_STATUS.md) distinguishes torso/head success, digital checks and still-unreported physical tests.

## From the approved image to printable geometry

The accepted reference was uploaded to Microsoft TRELLIS.2 after the user approved it and signed in. The retained generation record specifies resolution 1024, fixed seed 20261006, target 500000 faces, and texture resolution 2048. The raw GLB is 18,717,068 bytes with SHA-256 `031a509823168c16d7e075fa9751d10552ac0909003afcba3b5858fab4c01d1b`. It is a generated source asset, not the final printing solid. The model's back is an interpretation from image-to-3D generation; photographic skin color/pores do not all become geometry.

[Generation record](../../prints/king-shark-47cm/validation/original_v2/trellis_status.json) · [Source credits](../../prints/king-shark-47cm/CREDITS.md) · [Original raw/source assets](../../prints/king-shark-47cm/source/original_v2/)

The source was normalized to millimeters, front toward −Y and up toward +Z, with a nominal 470 mm height. Initial reconstruction used 0.45 mm voxel pitch, a minimal closing step, section-loop/enclosed-cavity filling, marching cubes, limited Taubin smoothing and simplification. It intentionally removed the generated internal shell; lightweight printing is controlled by slicer walls and sparse infill rather than retaining an unreliable generated hollow skin.

Additional polishing removed voxel stair-step artifacts. The report records no further scale or translation at this polishing stage, approximately 0.164% volume reduction, and preserved gross anatomy. Neutral actual-mesh views were inspected for the head, shoulders, hands, muscles and cloth. Texture alone must never be used as proof of printable surface detail.

[Initial repair report](../../prints/king-shark-47cm/validation/original_v2/repair_report.json) · [Polishing report](../../prints/king-shark-47cm/validation/original_v2/polish_report.json)

## Critical source pitfall: watertight can still contain unwanted internal gaps

Both early intermediates, `repaired_solid.npz` and `repaired_polished.npz`, passed ordinary closed/manifold checks but were not the final manufacturing source. Hidden slit cavities remained. A later protected-core union filled those gaps using orthogonal enclosed-loop filling and a 1.8 mm eroded core. It protected the mouth region and low outer hand region so fingers and the visible mouth were not sealed indiscriminately.

The final correct workspace source is **`work/king_shark_v2/repaired_polished_filled.npz`**. The final core report records 659,904 triangles, one component, `Manifold NoError`, watertight/outward geometry, volume 7,507,149.683 mm³ and unchanged bounds. Approximately 214,404.561 mm³ of unwanted internal void space was filled. That figure is CAD solid volume, not grams of added printed filament; low infill is applied later.

Do not restart manufacturing from one of the similarly named early repair intermediates. For existing printed parts, use the already engineered assembly meshes under [statue source/geometry](../../prints/king-shark-47cm/source/geometry/) rather than recutting a new source. The repaired intermediate file remains in the original workspace; it is not asserted to be included in every publication bundle.

[Internal-core report](../../prints/king-shark-47cm/validation/original_v2/internal_core_report.json)

## Cuts and joints: preserve surfaces after engineering

The final statue measures **469.541 mm tall × 323.268 mm wide × 237.934 mm deep**. The soles share a flat level. Arms/hands remain whole; lower legs/feet remain whole. Curved waist and hem seams follow the cloth instead of arbitrary visible horizontal cuts. Concealed central seam areas are flattened for the keys. The dark waistband belongs to the torso.

The glue joint uses an asymmetric 64-point profile, nominal 0.18 mm radial root allowance, 0.84 peg-tip scale, and additional blind socket depth. It locates parts and takes glue; it is not a flexible snap latch. The thigh keys use 13 mm half-width and 16 mm peg length. The waist key uses 19 mm half-width and 16 mm length. Shoulder keys use 13 mm half-width and 12 mm length; the fin has a smaller key. Exact coordinates and profiles are recorded in the linked joint data.

Do not apply blanket voxel remeshing, smoothing, separate-part decimation, or scaling after fitting joints. Such operations can move two complementary seam surfaces independently and alter connector clearance. The final engineer used only a very small **0.00005 mm** cleanup on the torso and shorts to remove numerical microedges that collapsed during float32 STL export. That is a serialization repair, not a license to soften mating faces. Revalidate actual exported files after any change.

Three distinct checks are required: manifold geometry, a seated collision check, and a sampled full insertion/withdrawal path. A part can have zero seated overlap yet be impossible to insert. The white tooth arches are installed in a defined order and direction, using hidden gum rails; do not discard those rails as unwanted geometry.

[Joint definitions](../../prints/king-shark-47cm/validation/original_v2/joints.json) · [Assembly validation](../../prints/king-shark-47cm/validation/original_v2/assembly_validation.json) · [Mouth geometry and insertion details](../../prints/king-shark-47cm/validation/original_v2/mouth_parameters.json) · [Assembly instructions](../../prints/king-shark-47cm/docs/PRINTING_ASSEMBLY.md)

## Why the all-red shorts were rebuilt the way they were

The user reported an “infill failed” problem on the original shorts and wanted one red print instead of gray/black side inserts. The available Bambu engine did not reproduce the exact original error. Do not retroactively claim a proven single root cause.

Simply joining the old shorts and loose side panels would retain their designed fitting clearances as thin cavities. The replacement restored the original unpaneled side material outside |X| = 74.5 mm and unioned it with the existing shorts. The central region containing all three connectors was protected. Saved Boolean checks record **zero removed original material and zero change in the protected connector core**. The other eight part meshes and joint-definition file remained byte-identical. The result is one closed manifold component with no separate side panels.

The replacement retains 0.20 mm layers, two walls, 3% gyroid in the main body, and original local three-wall/15% gyroid connector reinforcement. The selected orientation is waist-down. It preserves the physical torso compatibility while changing the shorts' color breakup and interior slicing behavior.

| P1S shorts trial | Time, including preparation/supports | Filament | Decision |
|---|---:|---:|---|
| 3% gyroid, original 10° tilt | 10 h 17 min | 221.6 g | More time/material |
| 3% gyroid, upright | 9 h 59 min | 223.1 g | More material |
| **3% gyroid, waist-down** | **9 h 57 min** | **217.9 g** | Selected |
| 2% gyroid, waist-down | 9 h 35 min | 198.9 g | Rejected roof-span tradeoff |

The 2% candidate saved around 19 g and 22 minutes but produced much longer sampled roof spans near the leg-seam caps. The retained 3% choice is a printability tradeoff, not a claim that every gyroid bridge becomes shorter as density increases. The saved selected P2S estimate is 10 h 07 min / 217.8 g. Neither replacement's physical print is established by the later records available here.

The original separate shorts alone were estimated at 8 h 39 min / 168.8 g, but that excluded the two separately printed side panels on another plate. Do not compare that isolated figure with the new complete one-piece shorts as if they were the same job, and do not promise the new color simplification is inherently faster.

[Shorts repair](../../prints/king-shark-47cm/validation/all_red_shorts/geometry_repair.json) · [Exact original-mate fit review](../../prints/king-shark-47cm/validation/all_red_shorts/replacement_fit_review.json) · [Orientation/infill comparison](../../prints/king-shark-47cm/validation/all_red_shorts/orientation_and_infill_selection.json) · [Final shorts verification](../../prints/king-shark-47cm/validation/all_red_shorts/print_verification.json)

## Faster legs: settings experiments mattered more than fewer supports

The selected fast-leg version keeps the original geometry and connector dimensions exactly. It uses 0.28 mm layers, initial 0.20 mm, two walls, 2% gyroid, the original local three-wall/15% gyroid connector reinforcement, feet-down orientation and 6 mm brims. Original 30-degree tree-support coverage remains. Larger layer steps are the visual tradeoff.

| P1S legs-only setup | Estimated time | Filament |
|---|---:|---:|
| Original 0.20 mm benchmark | 6 h 38 min | 153.8 g |
| 0.24 mm | 6 h 00 min | 154.0 g |
| Mixed/variable-layer candidate | 7 h 08 min | 174.0 g |
| 0.24 mm with slim-tree candidate | 7 h 08 min | 181.9 g |
| 0.28 mm with slim-tree candidate | 7 h 27 min | 174.2 g |
| **Selected 0.28 mm, original tree coverage** | **5 h 33 min** | **151.2 g** |

The selected process saves **3,919.410 seconds / 16.3947%** against the original P1S legs-only slice. A lower support-threshold candidate was also evaluated but not selected because preserving coverage was preferred. Mixed layer heights and narrower trees did not automatically make the print faster; support paths and related travel outweighed the apparent simplification.

The selected P2S pair estimate is 5 h 38 min / 151.5 g. Running the left leg on P1S and right leg on P2S yields about **2 h 55 min elapsed**, plus handling, with about 151.2 g combined material. Choose that option instead of printing a second duplicate combined-leg plate.

[Trial comparison](../../prints/king-shark-47cm/validation/fast_legs_feet/tested_comparison.json) · [Unchanged geometry proof](../../prints/king-shark-47cm/validation/fast_legs_feet/unchanged_geometry.json) · [Final estimates and verification](../../prints/king-shark-47cm/validation/fast_legs_feet/print_verification.json)

## Full-statue baseline and efficiency limits

The original six-plate v2 was estimated at **38 h 31 min / 788.2 g on P1S**, or **39 h 10 min / 788.2 g on P2S**, including supports and preparation. The recorded two-printer assignment was P1S plates 1/2/3 and P2S plates 4/5/6, about 20 h 32 min elapsed before manual handling. These totals describe the original release, not the later mixed revision of red shorts and faster legs.

For future work, compare total slicer predictions for equivalent part sets. Include support, interface, brim, travel, cooling and startup costs. Do not estimate a saving from infill percentage, triangle count, layer height or number of plates alone. Hollow CAD geometry can introduce roofs, cavities and unsupported spans; a solid external mesh with light slicer fill is often the simpler statue representation. Functional trays and brackets need their own wall/joint choices rather than blindly copying a decorative statue's low infill.

[Original per-plate estimates](../../prints/king-shark-47cm/validation/original_v2/print_estimates.json) · [Original two-printer schedule](../../prints/king-shark-47cm/validation/original_v2/two_printer_schedule.json)

## Valid STL and 3MF delivery: avoid another “no geometry” failure

An STL must be checked after binary float32 export and reimport, in its actual print orientation. A high-precision in-memory Manifold success does not prove that serialized vertices remain nondegenerate. The packaging helpers refuse to fill holes or perturb fitted geometry during export; upstream edits must be deliberate and revalidated.

The working Bambu 3MF stores all normal and modifier meshes inside `3D/3dmodel.model`, with unique IDs, nonempty vertex/triangle lists, valid component/build references and millimeter units. It uses an unprefixed default `Relationships` namespace in `_rels/.rels` and embeds process/model settings and valid previews. Do not distribute a cache, placeholder, thumbnail-only project, or geometry-stripped export as the print file. A raw `.3mf` extension is not sufficient proof of geometry.

Preserve the proven matching P1S/P2S profile structure, including filament-index/nozzle maps, standard-flow nozzle selection, five settings groups and intentionally compound arrays. Do not truncate every array to the number of filament colors. Black/white/red are logical slots; the palette can render slot 1 gray. One color per plate and no prime tower permit manual non-AMS printing. STL cannot retain these settings or joint modifiers.

The new homeware packager adds same-plate solid-intersection checks and re-parses written embedded meshes for manifold validity. Both workflows retain separate evidence for (1) geometry, (2) project structure, (3) engine slicing, (4) full extrusion-envelope checks, (5) GUI import and (6) physical printing. Passing one does not establish the others.

[Archived original packager](../../prints/king-shark-47cm/source/original_v2/package_v2.py) · [Original project checks](../../prints/king-shark-47cm/validation/original_v2/project_validation.json) · [STL roundtrips](../../prints/king-shark-47cm/validation/original_v2/stl_roundtrip.json) · [Common source scripts](source/)

## Engine and continuation procedure

Use absolute paths with the retained `bambu_cli.py` wrapper because it changes working directory. A Python process exit of zero is insufficient: inspect `result.json` for successful `return_code`, the expected plate set, each `warning_message`, zero filament changes and nonempty objects. The path checker must include model, support, interface, brim and any prime-tower extrusion, including arcs, and must respect P1S's excluded front-left corner. Record the actual final-file hash so a report cannot be accidentally attached to an earlier trial.

The King Shark projects have engine validation, but their GUI import was not verified. Do not state that all raw logs are warning-free merely because each plate's warning field is empty. Preserve failed/rejected trials as research, while making one recommended edition obvious to the user.

For a continuation: read the current README and validation-status overlay; identify which physical parts already exist; hash those immutable sources; make isolated candidate outputs; preserve joint surfaces; inspect actual mesh views; export/reimport; compare equivalent support-inclusive slices; check paths; update Markdown and matching evidence; then publish only the final reviewed files. Keep generated-reference images clearly distinguished from CAD renders and print photographs.

See [agent handoff](AGENT_HANDOFF.md), [progress](PROGRESS.md), [mounting research](MOUNTING_RESEARCH.md), and [repository conventions](REPO_PUBLICATION.md) for the rest of the current task.
