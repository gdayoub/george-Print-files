# Print one module first

[← Emberwing + Rift](../README.md)

The STL files are **experimental print parts**, checked as single closed solids and supplied in millimetres. They have not been sliced or physically printed. There is no verified Bambu profile, print-time estimate, or rated wall installation.

## Choose your first part

Start with **one Rift pod** to judge the finish and useful space. Print five only after the first succeeds. For Emberwing, start with **EW_BOTTOM_L** to check the ledge, braces and rear surface before committing to the full arrangement. The crest is a quick cosmetic sample.

| Design | Files / quantity | Approximate assembled W × H × D |
|---|---|---|
| Emberwing | Each of the 10 files in `files/stl/emberwing/`, once | 536 × 371 × 98 mm |
| Rift | `files/stl/rift/RIFT_POD_01.stl`, five times | 511 × 298 × 91 mm as pictured |

Rift is a repeated independent module. The five pod positions in the scene are an arrangement, not a mechanical connection. Emberwing's five ledges likewise require independent support; its wings and crest are decorative.

| Part | Supplied print X × Y × Z, mm |
|---|---|
| Emberwing bottom ledge, each | 199 × 110 × 90 |
| Emberwing middle ledge, each | 159 × 110 × 80 |
| Emberwing top ledge | 205 × 110 × 73 |
| Emberwing lower wing, each | 213.1 × 179.2 × 7.5 |
| Emberwing upper wing, each | 204.2 × 170.5 × 7.5 |
| Emberwing crest | 67.9 × 80.1 × 8 |
| Rift pod | 167.5 × 145.5 × 91 |

The longest dimension is approximately 213.1 mm. Every part fits a 246 mm bounding box, leaving room inside a 256 mm P1S build volume for placement and a modest brim. These are individual parts, not an instruction to place the whole assembly on one plate.

## PLA / P1S starting settings

Assume a standard 0.4 mm nozzle. Use your actual filament and plate profile. These are starting points for evaluation, not tested presets.

| Setting | Suggested start |
|---|---|
| Orientation | Keep the supplied rear-face-down orientation |
| Layer height | 0.28 mm for speed; 0.24 mm for a smoother bevel |
| Wall loops | 4 for ledges/pods; 3 for wings/crest |
| Top / bottom layers | 4 / 4 |
| Infill | 10–15% gyroid for ledges/pods; 10% for decorations |
| Supports | Initially off; inspect the layer preview and add local support if required |
| Brim | Only if the first sample lifts; allow sufficient clearance |
| Speed | Normal mode, within the calibrated PLA flow limit |
| Ironing / multicolour | Off for the fastest single-colour version |

Rear-face-down places the wall-facing plane on the plate; plate texture will transfer to it. Confirm the actual contact finish before selecting adhesive. Check the shallow rear edge bevel, the wing ribs and seams, the front rim and lip overhangs, and the first layer of every part in Bambu Studio. Do not send an unchecked auto-generated toolpath to the printer.

The Rift frame tapers behind its broad front bevel to save material while retaining the chunky outline. Its radial thickness is approximately 5–8 mm behind that bevel. The floor is a hexagon segment, not a full-width rectangular shelf. The narrowest front floor segment is about 72 mm wide, with about 87 mm depth to the rear interior; edge bevels reduce useful space slightly.

Emberwing ledge depths behind the front lip and in front of the back are approximately **82 / 72 / 65 mm** for bottom / middle / top. The centre gaps remain between the two wider tiers. A mouse may fit sideways on a lower ledge if its entire base fits one module. Measure first; do not bridge the centre seam with a load.

## Dry assembly

Use the model-only GLBs to inspect the arrangement. Match the names `L/R` and `UPPER/LOWER`; do not mirror a printed part by turning its decorative face toward the wall.

1. Lay the pieces on a protected flat surface and check the arrangement before applying any glue.
2. Keep each ledge's rear wall-contact face unobstructed. The wing panels touch the **front** of the ledge backs and are decorative overlays.
3. Trial-fit the four wing panels around the ledges. The panel seams and rib ends are not snap joints; trim or sand a seam locally if the printed tolerances require it.
4. The crest sits against the front of the bottom ledges. Do not use it to connect the two ledges structurally.
5. Any permanent decoration bond needs a PLA-compatible adhesive and a small offcut trial. Follow its label. No calibrated snap fit or load-bearing glued joint is included.

## Mounting is still unresolved for textured paint

The user reports textured walls with thin paint. A flat printed back does not make the wall or paint suitable for Command strips. No adhesive product, quantity, or safe working load is specified for this larger design. Shelf mass and outward leverage both count, even with lightweight contents.

Read the earlier [mounting research and manufacturer references](../../dragon-pixel-shelves/docs/PRINTING_ASSEMBLY.md#research-and-model-references). Those findings inform this work but do not validate the new shelves. Do not install the full arrangement until the exact wall, paint, adhesive product and removal access have been assessed and a representative module has been physically tested. Decorative wings are not substitute wall anchors.

## What the checks establish

[Mesh validation](../validation/mesh_validation.json) records a single connected, watertight, positive-volume solid for each candidate part, STL round-trip checks for the 11 distributed files, and their dimensions. It also records solid-equivalent PLA masses, **not slicer filament consumption**. Print time, actual material use, strength, creep, assembly fit and mounting performance remain unmeasured.

Record your first print's filament, layer height, time, mass and photos before preparing a MakerWorld print profile. The listing draft stays unpublished until you have real photos and testing results.
