# Agent handoff — current project state

## What the user wants

A character-shaped carrying case for their Puffco Proxy/Core: an entire screw-off character head, muscular body and independently removable joined feet opening a jar compartment. Earlier work used the wrong sleeve-only model. The user supplied `Core_Case.3mf` and explicitly directed us to use that complete case, including its top, as the foundation.

The completed design is a red/black/pink Venom-inspired symbiote. The user next requested a **two-color Hulk version optimized for printing time and presentation**, then interrupted that turn to request cleanup, preservation, a Foundations folder and repository handoff documentation. No Hulk geometry was built before the interruption. See `HULK_BRIEF.md`.

## Locations and authoritative files

- Repository: `C:\Users\george\Documents\ChatGPT\Venom`
- Clean Desktop delivery: `C:\Users\george\Desktop\Prints\Venom`
- Mechanical master: `Foundations/Core_Case.3mf`
- Latest print projects: `Print/FullColor/`; optional speed-only color simplification: `Print/SingleColor/`
- Exact unsliced CAD exports: `Print/Geometry/`
- Editable Blender: `CAD/Venom_Core_Case_V4_EDITABLE.blend`
- Generator: `CAD/build_venom_v4.py`; parameters: `CAD/parameters.json`
- Render: `CAD/render_venom_v4.py`; geometry export: `CAD/export_geometry.py`
- Slicing benchmark: `CAD/speed_benchmark.py`; completed-slice exporter: `CAD/export_prints.py`

Read the root README, Foundations README, `DESIGN.md` and `PRINTING.md`. Do not use archived V1/V2/V3 packages or the prior source project's stale top-level README as the current specification.

## Current mechanics

The original base and lid retain their vertices/faces under rigid placement at scale 1. The base is bonded to newly generated outside material and a shallow underside bond within its existing solid floor. The complete Venom head is bonded to the outside of the original lid. The original body/lid thread is approximately 2.5 mm pitch. V3's invented head thread was removed.

The separate feet/base keeps the custom 4 mm-pitch storage thread. Storage remains **50 mm clear diameter × 33 mm height** around a **provisional 46 × 30 mm jar**; actual jar dimensions were never provided. The storage separator is 3.6 mm. The assembled Venom is approximately **160 × 87 × 175.24 mm**.

Head opening: counterclockwise viewed from above. Feet opening: counterclockwise viewed from below. No new head alignment stop was added. The CAD uses a collision-free 20-degree phase, but the physical tightened face angle is unverified. The head and feet open independently.

## Completed verification

- Foundation SHA-256 matches the original Downloads file.
- Source triangle counts: 88,278 base and 52,836 lid.
- Exact original meshes retained in unsliced 3MFs; native Bambu exports retain original triangle counts.
- Seven newly generated Venom color meshes pass watertightness/winding/positive-volume checks.
- One connected combined analysis solid per assembled body/head/feet after union of overlapping source shells.
- No added material in protected original cavity envelopes.
- Both opening paths sampled every 5 degrees for four turns; no detected collisions. Head lift and jar exit checked.
- All three full-color and three optional single-color projects sliced successfully in Bambu Studio with no reported slicer warning.
- Generated layers retain 0.20 mm in the protected thread bands. Exact geometry XML in the speed-input files matches V4.

Reports are in `Reports/`. These checks do not prove physical fit, support accessibility, strength, stability, odor sealing or printed seating angle. No physical print was performed or printer job sent.

## Printing optimization already implemented

P1S / 0.4 mm / textured PEI. Body decorative middle uses 0.28 mm layers; original top-thread and lower storage-thread bands retain 0.20 mm and four walls. Head uses 0.24 mm above the socket, with its lower 10 mm at 0.20 mm/four walls. Feet remain 0.20 mm/four walls. Decorative infill is 5% adaptive cubic; decorative walls are three. Original case/lid parts retain four-wall overrides. Automatic tree supports are enabled, with a 25-degree threshold.

Controlled estimates: baseline 48 h 48 m; optimized full color 39 h 44 m; optional single-color assemblies 11 h 16 m. Full-color material estimate about 679 g; single-color about 359 g. Most remaining time is AMS changing/purging. These use generic PLA at 220°C, textured plate 55°C and 12 mm³/s flow limit. The user owns red Soyelin Ultra PLA, black Creality Hyper PLA and unspecified pink PLA; their actual calibrated filament profiles must be selected before re-slicing/printing. Hulk filament brands are not specified.

## Build workflow

Install `CAD/requirements.txt` into Python (a local `.venv` or `.deps` is ignored by Git). Run the generator, then Blender in background mode with the render script, then export geometry. Scripts use paths relative to this repository. `CAD/outputs/` and `CAD/speed_work/` are generated and ignored.

On this machine Blender is `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`, with Python at `5.2\python\bin\python.exe`. Existing scientific dependencies were previously installed in `C:\Users\george\Documents\ChatGPT\Proxy-CaseScrewOn\.deps`; use a local environment for future portability rather than relying on that unrelated project. Bambu CLI is `C:\Program Files\Bambu Studio\bambu-studio.exe`.

Benchmark commands: `python CAD/speed_benchmark.py baseline`, `python CAD/speed_benchmark.py fast`, `python CAD/speed_benchmark.py fastmono`. CLI logs/results are written into generated cache directories. `export_prints.py` checks successful slice reports and copies current native projects into the tracked release directories.

## Cleanup and Git status

Old Desktop Venom folders, duplicate workspace packages/ZIPs and development scripts/logs were preserved under ignored `_archive/2026-09-26_cleanup/`. Other Desktop print projects were not modified. The Downloads original was copied, not moved.

The user directed us to use GitHub CLI. It authenticated as `gdayoub` (George Dayoub). Local commits use the GitHub no-reply address `182448914+gdayoub@users.noreply.github.com`. The existing private gallery is `https://github.com/gdayoub/george-Print-files`, with this project under `prints/venom-core-case`.

This project workspace has its own local Git snapshot history. The gallery checkout used to publish it is ignored `_repo_sync/`, with the gallery's `origin` remote. For later gallery updates, copy only current tracked project files into that project subfolder; preserve all unrelated projects and catalog entries. Fetch current remote changes before pushing. Inspect local Git history and the remote gallery history for the final publication commit rather than assuming both checkouts share the same root layout.
