# Character homeware and King Shark publication handoff

Snapshot: October 6, 2026. Read the latest completion section in `PROGRESS.md`; early snapshots below preserve the reasoning and repository state before publication. Physical homeware tests remain pending.

## User intent and fixed constraints

The user requested practical King Shark and Venom-inspired objects: a bowl/catchall and flat-backed figures holding shallow shelves, with fast printing favored over fine surface detail. P1S/P2S compatibility, low material consumption, recognizable characters, and non-AMS color-separated printing remain priorities. The user prefers Command-strip mounting on a flat rear surface. The present wall products are explicitly unrated prototypes because the manufacturer's picture-strip directions do not recommend shelves.

The user also requested GitHub publication to the existing prints repository, separate organized folders for each design, the existing King Shark statue included, and Markdown progress/handoff documentation for continued work. Publication should preserve the repository's existing visibility and the source attribution for every design.

The 47 cm King Shark torso/chest and head have been successfully printed according to the user's report. Do not change their scale, key geometry, mating surfaces, or proportions. The all-red shorts replace the prior separate black side panels while preserving waist and leg interfaces. The fast-leg edition changes slicing settings, not the original leg/foot meshes. New homeware designs do not replace or modify the successful statue.

## Workspace and important sources

Original workspace: `C:/Users/Panduh/Documents/Codex/2026-10-02/i-m-giving-you`.

| Asset | Workspace location | Role |
|---|---|---|
| Original engineered statue | `work/king_shark_v2/final_parts/` | Assembly-coordinate NPZ meshes and joint metadata |
| Final repaired source | `work/king_shark_v2/repaired_polished_filled.npz` | Correct closed source; earlier repaired intermediates contained hidden gaps |
| Original delivered statue | `outputs/KingShark_realistic_47cm_v2/` | Full projects, STLs, source, reports and previews |
| Red-shorts delivery | `outputs/KingShark_ALL_RED_SHORTS_FIX/` | Replacement projects compatible with printed torso |
| Faster legs delivery | `outputs/KingShark_FAST_LEGS_FEET/` | Exact original legs with faster process and parallel-printer option |
| Shelf generator | `work/character_homeware/build_shelves.py` | Root agent's King Shark and Venom derivative designs |
| Shelf render script | `work/character_homeware/render_shelves.py` | Actual mesh previews and editable Blender scenes |
| Bowl construction | `work/character_homeware/bowl/build_bowl.py` | One-piece King Shark catchall |
| Homeware packager | `work/character_homeware/package_homeware.py` | Reuses checked 3MF helpers without modifying original profiles |
| Mount research | `work/character_homeware/docs/MOUNTING_RESEARCH.md` | Official sources and CAD allowances |

Desktop counterparts remain under `C:/Users/Panduh/Desktop/Prints/`. The staged statue copies those delivered files without regeneration. Workspace construction scripts can contain original absolute paths; editable Blender/GLB/STL assets remain usable separately. Do not promise that archived scripts are a standalone one-command build until their dependencies have been assembled and checked.

## Current prototype geometry

King Shark shelf: 148 × 54 × 156 mm body; separate 150 × 55 × 9 mm red tray; two parts. Venom shelf: body and tray of the same envelopes, black body/tray plus three white face/chest inserts, five parts. Both rear faces reserve two 25 × 100 mm adhesive zones and optional keyholes. Tray registration uses 0.22 mm side allowance. Recorded seated/intermediate tray overlap checks are numerically near zero. These are CAD checks, not proof of a physically loaded joint.

Bowl: 140 × 143.425 × 59.399 mm overall, including the projecting face. One gray component, upright printing, nominal 2.6 mm normal-offset wall and 2.8 mm floor. The generated wall-band check protects at least 2.4 mm. Approximate internal capacity is 520 ml; liquid containment has not been tested. Purpose is keys/accessories. The original source head and tooth meshes were copied/cropped for the relief; the original statue files were not changed.

## Packaging and checks

The packager accepts `--manifest`, `--layout`, `--preview`, `--out`, `--stem`, `--title`, and optional `--joints`. Mesh paths may be absolute or manifest-relative. Each plate must have one color. An actual geometry render is mandatory; a concept image is insufficient.

Defaults: standard 0.4 mm nozzle, 0.28 mm layers, initial 0.20 mm, three walls, 8% gyroid, four top/bottom layers and 1.12 mm physical minimum, no prime tower. Tree supports use a 30-degree threshold. Part or instance settings override the defaults; bowl sparse infill is 5%, and shelf parts currently specify support disabled by design. A support setting is not a claim that the geometry has been physically proved support-free.

Validation includes closed/winding/manifold source checks, rigid plate placement, conservative P1S exclusion, same-plate solid intersection checks, binary float32 STL reimport, and re-parsed embedded 3MF geometry. It does not silently repair geometry during export.

Bambu wrapper: `work/bambu_cli.py`. The portable engine is `C:/Users/Panduh/AppData/Local/Programs/BambuStudioPortable-02.08.02.61`. Pass absolute project/output paths because the wrapper changes directory. Read `result.json` rather than relying on process exit code: require `return_code = 0`, inspect each plate's `warning_message`, and verify `filament_change_times = 0`. Use the existing `work/check_size2_paths.py` helper to check model/support/brim extrusion paths. Do not publish the bulky raw G-code or engine logs by default.

## Repository and release work

Confirmed repository: `gdayoub/george-Print-files`; default branch `main`; visibility private at inspection. Main commit: `266b5093f6ab01defeaac3ab0bc5da19ca14e681`. Its commit tree is `b67c18366ebab09b36d4db125ea248c1b770a728`. The recursive listing contained 808 entries, was not truncated, and contained no King Shark paths. Read `REPO_PUBLICATION.md` for conventions. Re-read the branch before publishing so another update is not overwritten.

No local Git checkout or remote was found in the current workspace. GitHub CLI was not available on PATH during inspection. The authenticated GitHub connector can read this repository and reports push permission. This research/preparation agent has not committed, pushed, or changed remote state.

Completed statue staging: `outputs/Character_Catchalls_and_Shelves_v1/repo/prints/king-shark-47cm/`. It contains 136 files, with 128 source copies hash-verified, all eight delivered 3MFs matched to previous checked hashes, and no geometry regeneration. All eleven original assembly meshes plus metadata are under `source/geometry/`; the all-red shorts mesh is retained separately. No file reaches 100 MB. Root agent owns final homeware staging, overall README/catalog integration, publication and final verification. The publisher subagent handles immutable blobs only; do not create a competing commit/ref update.

## Source and licensing facts

King Shark is a fan interpretation generated through Microsoft TRELLIS.2 from the user-approved concept and engineered locally. It is not the movie production asset. The retained source record identifies 1024 resolution, seed 20261006, 500000 target faces, 2048 texture resolution, and raw GLB SHA-256 `031a509823168c16d7e075fa9751d10552ac0909003afcba3b5858fab4c01d1b`. No blanket CC0, Creative Commons, MIT mesh license, or commercial character-rights grant has been established.

The Venom geometry derives from the user's earlier source, credited in the existing repository as OVERRIDE3D_5884368, “Venom Marvel Rivals (Exclusive),” with Standard Digital File License. Public redistribution permission was unverified in the prior release. Preserve that credit and status; the new request to publish to an existing private repository does not establish rights to publicly redistribute the source.

## Completion and continuing work

All three homewares now have validated exported meshes, complete P1S/P2S slices, actual extrusion-path checks and staged product folders. The King Shark shelf takes about 3 h 50 min / 130 g; Venom about 4 h 35–37 min / 139 g; bowl about 3 h / 113 g. Both shelves have zero generated support. Four curated folders include the preserved statue revisions. The root gallery/catalog and handoff documentation are included in the publication snapshot; the GitHub commit history identifies the published revision.

Read [BUILD_RESEARCH.md](BUILD_RESEARCH.md) for original statue/shorts/legs findings, [HOMEWARE_ENGINEERING.md](HOMEWARE_ENGINEERING.md) for new geometry and serialization details, and [MOUNTING_RESEARCH.md](MOUNTING_RESEARCH.md) for mounting evidence. The shelved prototypes need physical print, glue assembly and mounting evaluation before any load rating can be assigned. Future user print feedback should be appended to `PROGRESS.md` and the relevant product status.

The user's ongoing documentation instruction is to keep findings and experiments in Markdown as work progresses, and keep each design's files organized in its own prints-repository folder. Do not reduce the handoff to a final summary without the evidence and failed-trial lessons. Preserve successful statue interfaces and keep actual source attribution.
