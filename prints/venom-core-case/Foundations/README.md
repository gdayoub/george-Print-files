# Dimensional foundation

`Core_Case.3mf` is a byte-identical copy of the user's `C:\Users\george\Downloads\Core_Case.3mf`. The Downloads file remains untouched.

SHA-256: `54da47f6ee094b3d39ab7186b99cc710daf0797e67a420f98887727aad5f7c7e`

This is the corrected COMPLETE case: **base and matching screw-on lid**, including five internal accessory/tool slots. The prior `proxy-core-cup-sleeve.stl` was the wrong dimensional foundation and must not be reused for this project.

- Base: approximately 57.4 mm diameter × 52.5 mm high; 88,278 triangles.
- Lid: approximately 57.37 mm diameter × 51.0002 mm high; 52,836 triangles.
- Original joint: approximately 2.5 mm pitch, right-hand screw.
- `base_exact.npz` and `lid_exact.npz`: original XML vertex/face arrays without repair or scaling.
- `inspection.json`: source dimensions and cross sections.
- `joint_alignment.json`: exploratory phase sweep, not a final physical seating calibration. The completed V4 generator uses a 20-degree lid phase; see CAD parameters and validation transforms.

The original base includes overlapping internal solids and tiny degenerate faces. Exact source exports preserve them. The analysis-only copy unions source solids before Boolean collision checks; that is not a modification of the delivered original reference.

Source attribution: ROADBLOCK, “Core Case for Puffco Proxy Core.” Embedded metadata states MakerWorld Exclusive License. Retain the original metadata and do not infer permission to redistribute from possession of the file.
