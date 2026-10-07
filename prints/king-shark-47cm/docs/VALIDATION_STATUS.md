# Validation status and change history

Current snapshot: October 6, 2026.

| Scope | Evidence | Limit |
|---|---|---|
| Original torso/chest and head | User reports a successful physical print and excellent appearance | No measured time, photos or whole-statue test is recorded here |
| Original realistic v2 files | Saved geometry/STL/3MF checks, digital assembly and insertion paths, successful P1S/P2S engine slices and extrusion-envelope checks | Original notes predate torso feedback; original shorts later had a user-reported infill failure |
| All-red replacement shorts | One closed component, preserved connector core with zero symmetric-difference volume, original mates/path checks, successful slices and toolpaths on both printers | Exact original infill error was not reproduced; replacement physical print/fit not yet reported |
| Faster legs/feet | Byte-identical original geometry, STL checks, four exact project slice/toolpath results, preserved reinforcement | New 0.28 mm process physically untested; timing is estimated |
| Publication package | Source-to-staging SHA-256 equality and project ZIP checks | Publication copying does not add a new physical test |

All original reports are retained under `validation/original_v2`, `validation/all_red_shorts`, and `validation/fast_legs_feet`. They have not been rewritten to erase historical state. In particular, older `physical_print_test: false` entries describe the validation available when the files were made. The later user report applies only to the torso/head.

## Revision details

The all-red shorts restore material in the old side-panel regions. Their protected center, containing the waist key and both leg sockets, has zero change in the saved Boolean comparison. The source report records eight other part meshes byte-identical and an unchanged joint-definition file. Maximum sampled interference against the torso/legs remains below the recorded 0.02 mm³ numerical tolerance. The model remains at its original scale.

Fast legs change only process/layout. The P1S pair estimate is 19,987.211 seconds versus the original legs-only benchmark of 23,906.621 seconds, a 3,919.410-second / 16.3947% reduction. This is a slicer-estimate comparison, even where an archived text file calls it a measured saving. Concurrent left-P1S/right-P2S estimated elapsed time is 10,468.542 seconds (about 2 h 55 min).

Bambu Studio GUI import was not verified for these delivered King Shark projects. Engine parsing/slicing was verified. No printer job is launched by opening this package, and the publication task has not sent a print job.
