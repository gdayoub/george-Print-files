# Cleanup — September 26, 2026

The active Desktop print folder is now `C:\Users\george\Desktop\Prints\Venom`.

It keeps only the latest optimized full-color projects, the optional single-color projects, presentation previews, current instructions, an agent handoff and a `Foundations` folder containing the original complete `Core_Case.3mf`.

The editable source, original extracted geometry, Blender file, exact unsliced exports, profiles and validation reports are organized in the repository. The private GitHub gallery location is `gdayoub/george-Print-files`, under `prints/venom-core-case`.

The following older Desktop packages were moved intact to the ignored local `_archive/2026-09-26_cleanup/desktop_prints/` folder:

- `venomPUFFy` — superseded V3, using the wrong sleeve foundation.
- `venomPUFFy_V4_CoreCase` — original V4 package; its needed source and geometry now live in the repository.
- `venomPUFFy_V4_FAST` — pre-cleanup fast package; current print projects now live in the single `Venom` folder.

Duplicate workspace packages/ZIPs are archived under `workspace_packages`; old inspection scripts, migration scripts, logs and reference extracts are archived under `development`. Generated geometry and slicer caches are under ignored `CAD/outputs` and `CAD/speed_work`.

Nothing from these historical folders was permanently deleted. Other Desktop print projects were not altered. `Downloads/Core_Case.3mf` was copied into Foundations and remains in Downloads.

The repository tracks current deliverables, not the large duplicate archives or generated caches. `Reports/file_manifest.json` records the SHA-256 hashes and sizes of current delivery/source files. Hulk remains a pending brief, not a release.
