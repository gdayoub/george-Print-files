# King Shark shelf print validation

Validated 2026-10-06. This is a compact, unrated mounting prototype, not a physically tested shelf.

## Delivered projects

- `packages/King_Shark_Shelf_P1S_NON_AMS.3mf`
- `packages/King_Shark_Shelf_P2S_NON_AMS.3mf`

Two single-color plates: gray body/backplate and red tray. The body prints flat on its back; the tray prints on its flat bottom. No AMS or generated supports are required by the supplied slices. Open as a project to retain settings.

## Estimates

| Printer | Body | Tray | Combined time | Combined filament |
| --- | --- | --- | --- | --- |
| P1S | 2 h 58 min / 97.82 g | 52 min / 32.04 g | 3 h 50 min | 129.86 g |
| P2S | 2 h 58 min / 97.72 g | 52 min / 31.95 g | 3 h 50 min | 129.66 g |

Using both printers for the two differently colored plates gives about 2 h 58 min elapsed printing time, plus handling and assembly.

The projects use 0.28 mm layers, three walls, and 8% gyroid infill. Estimates include brim and startup overhead reported by the slicer. Both projects have zero slicer warnings, zero generated support time, and zero filament changes.

## Geometry and paths

All final NPZ solids, embedded 3MF meshes, and actual print-oriented binary STL reimports are watertight, outward-facing, and one connected component per part. The body needed a 0.0001 mm cleanup to remove tiny edges that collapsed in float32 STL serialization; this is far below printer resolution. No connector dimensions were intentionally resized.

The toolpath checker covered 247,974 P1S and 247,269 P2S extrusion segments, including circular arcs, model, and brim. Every checked segment fits the build volume and avoids the P1S excluded corner.

## Assembly path

Align the tray approximately 16 mm above its seated position. Move it horizontally toward the backplate, then lower it onto the two keyed support seats. Apply suitable glue to the mating support surfaces. This insertion path was checked digitally in both stages. The maximum measured numerical overlap is 0.04413 mm³, within the declared 0.05 mm³ numerical tolerance associated with submicron cleanup.

A straight vertical lift far above the shelf runs into the decorative bust; use the described two-stage path. The flat back and screw keyholes remain present. Neither print checks nor fit calculations establish a mounting load rating.

## Evidence

- `geometry_validation.json`
- `serialization_validation.json`
- `packages/project_validation.json`
- `packages/stl_roundtrip.json`
- `validation/print_summary.json`
- `validation/slice_P1S_toolpaths.json`
- `validation/slice_P2S_toolpaths.json`
- `validation/tray_assembly_path.json`

Current actual-mesh previews are `preview.png`, `front.png`, `back.png`, `side.png`, `exploded.png`, and the plate images. `King_Shark_Shelf.blend` contains the assembly, exploded arrangement, and both print layouts.
