# Character collection progress

## October 6, 2026 — design and packaging snapshot

- User approved functional King Shark/Venom shelf and King Shark bowl exploration, prioritizing recognition and fast printing. Current small objects are distinct from the existing 47 cm statue.
- Official Command research completed. Picture-strip shelf use is not manufacturer-recommended; custom mounting capacity remains unverified. Rear adhesive zones and optional mechanical interfaces are modeled without assigning a load rating.
- Common homeware packager created. Its command line and import were checked; it reuses the earlier validated Bambu packaging helpers and preserves original profiles.
- Bowl geometry and preview packaged for P1S/P2S: one gray part, 140 × 143.425 × 59.399 mm, 71,434 triangles. Source checks, exported STL reimport, embedded 3MF checks and digital bed placement passed. Automatic tree supports remain enabled around the face.
- Subsequent bowl `result.json` files show successful slicing on both printers, empty plate warning messages and zero color changes. Initial support-inclusive estimates: P1S 10,719.955 seconds (about 2 h 59 min), 113.253 g; P2S 10,837.972 seconds (about 3 h 1 min), 113.157 g. Root owns confirmation of the final selected files and toolpath reports.
- King Shark and Venom shelf geometry/render reports exist. Each body is 148 × 54 × 156 mm; the separate trays are 150 × 55 × 9 mm. Root is continuing print preparation and final validation.
- Repository identified as private `gdayoub/george-Print-files`. Current main is `266b5093f6ab01defeaac3ab0bc5da19ca14e681`; no King Shark files are present at that snapshot. No remote mutation was performed by the research/packaging agent.
- User requested organized GitHub folders for each design, including the earlier King Shark statue, plus Markdown handoff records. Statue publication staging is being prepared from the original Desktop Prints deliveries without geometry regeneration.

## User-reported print evidence to preserve

The user reports the large Venom assembly worked perfectly. The user also reports the King Shark chest/head printed successfully and looked excellent. They reported an infill failure on the original shorts; the exact original error was not reproduced. The replacement all-red shorts and fast-leg processes have digital slice/fit validation, but no subsequent user report establishes a physical print of those revisions. Do not expand the torso success into a claim that the whole revised statue or new homeware designs have been physically tested.

## Next update fields

Append the final selected files, any mesh/process revisions, slice/toolpath result locations, support-inclusive estimates, staging inventory/hash result, repository commit/URLs, and any new user physical-test feedback. If an estimate changes after reslicing, identify the changed settings and supersede the earlier figure clearly.

## October 6, 2026 — existing statue staging completed

- Staged `outputs/Character_Catchalls_and_Shelves_v1/repo/prints/king-shark-47cm/` using the three original Desktop Prints deliveries. The original realistic v2, all-red replacement shorts and faster legs/feet have separate named variant directories within this one statue design.
- 128 source-to-staging copies matched SHA-256. All eight delivered 3MFs matched the hashes in their previous validation records and passed ZIP integrity / embedded model presence checks. No statue geometry was regenerated.
- All eleven original assembly-coordinate NPZ meshes and the original joint/manifest metadata are included under `source/geometry/`; the all-red replacement shorts mesh is retained separately. Both original and updated editable Blender assemblies are included.
- The folder contains 136 files, about 251.13 MB. The largest file is the original Blender assembly at 38,339,220 bytes; no file reaches 100 MB. Raw G-code and slice logs are omitted.
- Current README, assembly guide and validation-status document distinguish torso/head user-reported print success from untested revised parts. Older status records are preserved as historical evidence. Credits make no invented blanket mesh or character license claim.
- Twenty local Markdown links were checked. All per-design artifact links resolve; the gallery link awaits root's staged repository README. Publisher agent was notified that statue binaries are immutable and ready for content-addressed upload. This is staging completion, not confirmation of a remote commit.

## October 6, 2026 — homeware completion and publication snapshot

- Final shelf silhouettes use a finer 0.25 mm grid, selective contour smoothing and analytic rounded backplates. Actual-mesh renders were inspected; final colors are gray/red King Shark and black/white Venom.
- Float32 STL checks found tiny tangent/degenerate faces that the original double-precision checks did not catch. King Shark received a 0.0001 mm cleanup; Venom was canonicalized in float32 print coordinates. Re-exported STLs and embedded 3MF geometry pass. The repair methods and assembly checks are preserved in the product validation folders and `HOMEWARE_ENGINEERING.md`.
- Shelf tray installation is front approach at a 16 mm lift, then lowering onto the keys; a straight upward path through the decorative torso is intentionally not an assembly route. White inserts withdraw toward the front. Actual residual numerical overlaps are recorded, below 0.05 mm³.
- Both printers completed all three homeware slices with successful return codes, empty plate warning messages, zero color changes, and extrusion paths within their build volumes. All paths avoid the conservative P1S front-left excluded corner. Raw engine warnings are not described as an empty log.
- Bowl: P1S 2 h 59 min / 113.3 g; P2S 3 h 01 min / 113.2 g. Small supports around its face account for about 6½ minutes and 2.43 g.
- King Shark shelf: P1S/P2S about 3 h 50 min / 130 g over two color plates; zero supports. Using both printers concurrently makes elapsed print time about 2 h 58 min, dominated by the gray back.
- Venom shelf: P1S about 4 h 35 min / 138.7 g; P2S about 4 h 37 min / 138.5 g over black and white plates; zero supports. The white details are separate glue inserts; no AMS is required.
- Four separate curated destinations: `prints/king-shark-47cm`, `prints/king-shark-catchall-bowl`, `prints/king-shark-accessory-shelf`, and `prints/venom-accessory-shelf`. Existing statue artifacts remain byte-identical. Root gallery and catalog entries link to each design.
- Each product includes printer projects, STLs, editable geometry, images, instructions, credits and validation. Shared Markdown records cover original-model research, homeware engineering, mounting, repository conventions and agent continuation. The publication manifest records exact file sizes and hashes; the GitHub commit containing this snapshot identifies the release revision.
- New homewares, revised shorts/legs, and mounting/load capacity have no new physical test result. Only the previously reported Venom assembly and King Shark chest/head successes are treated as user-reported physical evidence.
- GitHub transport completed with 97 verified binary paths, 94 unique Git blobs and 336,704,100 bytes. Every returned Git SHA matched the local file; no binary is missing. The tree publication includes the text files directly and retains all unrelated repository content. See `BINARY_UPLOAD_VERIFICATION.json` and the commit history for the content-addressed record.
- The organized collection was copied to `Desktop/Prints/Character_Collection_2026-10-06/`; the copy was SHA-256 compared against staging. Existing separate statue/shorts/legs deliveries were not overwritten.
