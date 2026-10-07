# Editable source and reproducibility

The Blender file contains the actual printable geometry, assembly views and (for shelves) plate-layout scenes. STLs are the print-oriented delivery; the NPZ arrays in `geometry/` retain assembly-coordinate vertices/faces. All dimensions are millimeters. The manifest and layout preserve per-part settings and print transforms.

`scripts/` contains the construction/rendering code as a research snapshot. It still expects the original workspace directory layout and supporting sculpture files, Blender Python runtime, and scientific Python dependencies. It is **not a standalone installed application**. See the shared agent handoff for source locations and dependency details. The original King Shark geometry is archived with the statue; Venom retains the existing credited source. Open the Blender model directly when a full pipeline reconstruction is unnecessary.

After edits, repeat manifold checks on the actual exported STL and embedded 3MF, joint clearance/insertion checks, both printer slices, and build-volume checks. Recalculate estimates, update Markdown notes, then publish matching file hashes. Do not reuse previous validation for changed files.
