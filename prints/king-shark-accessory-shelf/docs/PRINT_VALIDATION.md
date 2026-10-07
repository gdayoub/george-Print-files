# King Shark shelf print validation

Revised and validated 2026-10-07. The visible fin uses enlarged geometry from the original Dorsal_fin source and has its own flat backplane extension. This is an unrated mounting prototype; the revised shelf has not been physically printed.

## Delivered projects

- `packages/King_Shark_Shelf_P1S_NON_AMS.3mf`
- `packages/King_Shark_Shelf_P2S_NON_AMS.3mf`

Two single-color plates: gray body/backplate and red tray. The body prints flat on its back; the tray prints on its flat bottom. No AMS or generated supports are required by the supplied slices. Open as a project to retain settings.

## Estimates

| Printer | Body | Tray | Combined time | Combined filament |
| --- | --- | --- | --- | --- |
| P1S | 3 h 02 min / 99.48 g | 52 min / 32.04 g | 3 h 54 min | 131.52 g |
| P2S | 3 h 02 min / 99.37 g | 52 min / 31.95 g | 3 h 54 min | 131.32 g |

Using both printers for the two differently colored plates gives about 3 h 02 min elapsed printing time, plus handling and assembly. The larger fin adds about four minutes compared with the first shelf release.

The projects use 0.28 mm layers, three walls, and 8% gyroid infill. Estimates include brim and startup overhead reported by the slicer. Both projects have empty per-plate warning messages, zero generated support time, and zero filament changes.

## Geometry and paths

The revised body is 179.7 mm tall, including the dorsal fin above the 156 mm backplate. The fin is part of the same supported body solid, so the part still prints flat on its back without generated support. All final NPZ solids, embedded 3MF meshes, and actual print-oriented binary STL reimports are watertight, outward-facing, and one connected component per part. The body needed float32 coordinate canonicalization to remove tiny edges that collapsed in STL serialization; maximum coordinate rounding was 0.0000077 mm. No connector dimensions were intentionally resized.

The toolpath checker covered 257,764 P1S and 256,408 P2S extrusion segments, including circular arcs, model, and brim. Every checked segment fits the build volume and avoids the P1S excluded corner.

## Assembly path

Align the tray approximately 16 mm above its seated position. Move it horizontally toward the backplate, then lower it onto the two keyed support seats. Apply suitable glue to the mating support surfaces. This insertion path was checked digitally in both stages. The maximum measured numerical overlap is 0.04413 mm³, within the declared 0.05 mm³ numerical tolerance associated with submicron cleanup.

A straight vertical lift far above the shelf runs into the decorative bust; use the described two-stage path. The maximum recorded numerical overlap in the final geometry is 0.000617 mm³. The flat back, clear pad zones, and screw keyholes remain present. Neither print checks nor fit calculations establish a mounting load rating.

## Evidence

- `geometry_validation.json`
- `serialization_validation.json`
- `packages/project_validation.json`
- `packages/stl_roundtrip.json`
- `validation/slicer_estimates.json` in the published folder
- `validation/fin_slice_P1S_toolpaths.json` and `validation/fin_slice_P2S_toolpaths.json` in the workspace; the published folder names these `slice_P1S_toolpaths.json` and `slice_P2S_toolpaths.json`
- `validation/assembly_insertion.json`
- `serialization_repair.json`

Current actual-mesh previews are `preview.png`, `front.png`, `back.png`, `side.png`, `exploded.png`, and the plate images. `King_Shark_Shelf.blend` contains the assembly, exploded arrangement, and both print layouts.
