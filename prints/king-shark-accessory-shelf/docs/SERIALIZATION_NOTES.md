# Serialization checks

The final print-oriented binary STLs were reopened and checked for watertightness, winding, nonmanifold edges, degenerate faces, and connected components. The revised fin/body was canonicalized in its float32 print coordinates before packaging. Maximum coordinate rounding was 0.0000077 mm; no voxel remesh or connector redesign was used. The STL roundtrip, embedded 3MF meshes, seated tray and assembly travel all passed. See `serialization_repair.json`, `serialization_validation.json`, and `validation/assembly_insertion.json` for measurements and hashes.
