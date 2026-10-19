# Full-size Venom build script record

These eleven scripts are copies of the original workspace construction stages. They preserve method and numeric choices for another agent; **they are not a portable one-command build**. They use relative `work/...` paths, the user-supplied original 3MF, generated intermediate `.npz` meshes, a particular Python/Blender/Bambu environment and local profile JSONs that are not all included here. Use the [full-size build guide](../../docs/HOW_THE_FULL_SIZE_STATUE_WAS_MADE.md) and [editable Blender source](../Venom_Size1_Blender.zip?raw=true) first.

| Stage | Script | Retained purpose |
|---|---|---|
| 3MF intake | `parse_venom.py` | Extract upright mesh and normalize to the initial 480 mm working size |
| Muscle cleanup | `remove_venom_tendrils.py`, `smooth_muscle_envelope.py` | Generate/review a protective envelope and remove external tendrils |
| Part engineering | `cut_venom_64.py`, `engineer_venom_64.py`, `update_muscular_parts.py`, `merge_full_arms.py` | Cut, color-separate, key, then restore whole arms |
| Light geometry | `lightweight_geometry.py` | Cap surface movement and protect muscle/connector details |
| Bambu delivery | `package_lightweight.py`, `finalize_lightweight_project.py`, `stage_venom_release.py` | Construct, correct and stage the checked 3MF release |

Do not run these against a different sculpt without rewriting cut locations, masks, color extraction and print layout. Do not infer a public redistribution right from these script copies; see [the source credit/license](../../CREDITS.md).
