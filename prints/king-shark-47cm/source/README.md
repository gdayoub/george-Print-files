# Editable sources

`original_v2/King_Shark_realistic_47cm.blend` preserves the original assembled/exploded/plate scenes. `all_red_shorts/King_Shark_all_red_shorts_47cm.blend` is the editable assembled model with the integrated red shorts. Blender units are millimeters.

The original raw TRELLIS GLB and approved concept are provenance assets, not substitutes for the engineered print meshes. `geometry/` contains NPZ vertices/faces in common assembly coordinates. `all_red_shorts/assembly_meshes/Shorts.npz` replaces only the original shorts group. The fast-leg process keeps the original geometry exactly.

Archived construction scripts and profile JSONs are included for investigation and continuation. They retain assumptions and paths from the original Windows workspace. Their dependent mesh-repair intermediates and bundled Python/Blender runtime are not all duplicated here; the scripts are not represented as a fully portable one-command regeneration kit. Prefer the editable Blender file or documented NPZ geometry when continuing in another environment. No original geometry was regenerated during publication staging.
