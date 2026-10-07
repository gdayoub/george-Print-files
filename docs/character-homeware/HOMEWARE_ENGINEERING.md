# Homeware engineering record

## Design decisions

The new request was for recognizable, smaller King Shark/Venom household objects with low print time and modest detail. The first set assumes keys, earbuds and small collectibles. The bowl is an accessory catchall. No food-use or heavy-item requirement was confirmed.

The character shelves use a shallow relief derived from the actual previous sculptures. Frontal proportions are retained while depth is compressed. This lets the flat back print on the bed, and keeps the face supported by the backplate. The separate tray prints on its own bottom. Two triangular gussets support it, with non-locking glue registration keys. Colors are divided across plates, so neither shelf needs AMS or a purge tower. King Shark uses a gray back/character and red tray; Venom uses a black back/tray and separate white eyes and chest emblem.

The sculpt is a relief plaque with small sculpted hands beneath the tray, not a newly posed full three-dimensional figure. Actual geometry renders accompany the files; they are not print photographs.

## Geometry and clearances

- Shelf assembled envelope: 150 × 58.2 × 156 mm.
- Rounded backplate: 148 × 156 mm, 3.2 mm nominal base thickness.
- Tray: 150 × 55 mm, 4.2 mm floor, 4.8 mm rim, 2.4 mm rim width.
- Gussets: two, each 6 mm wide, centers X = −54 and +54 mm.
- Keys: broad, ramped registration shapes; 0.22 mm nominal side allowance in tray sockets.
- Venom white pockets: approximately 0.18 mm outline allowance and 0.15 mm extra depth.
- Usage coordinates: X horizontal, +Z up, negative Y projects out from the wall. Back plane is Y = 0.
- Body/insert print rotation: rows `[1,0,0], [0,0,1], [0,-1,0]`. The tray stays upright on its bottom.
- Keyhole slots: centers 108 mm apart, 9.2 mm circular entry and 4.7 mm neck. These are visible through-cut slots, not concealed front holes.

The tray must approach from the front while raised 16 mm, slide toward the backplate, then lower onto the gussets. Lifting it straight up 40–80 mm would intersect the decorative torso and is not an assembly path. The checked reverse path samples the 16 mm lift and forward translation independently. White inserts withdraw straight toward negative Y.

Digital insertion tests tolerate less than 0.05 mm³ of numerical overlap at nominal contact surfaces after serialization cleanup. King Shark's maximum recorded overlap is approximately 0.04413 mm³; Venom's is approximately 0.00005751 mm³. These tiny residuals are recorded rather than described as exact zero. This is not a physical clearance or glue-strength test.

## Visual and serialization findings

An initial 0.5 mm ray grid with only 0.21 mm smoothing produced prominent stepped silhouette edges. Final construction uses an exact 0.25 mm grid, about 0.60 mm smoothing near the silhouette, and much less smoothing inside the face. A separate analytic rounded plate keeps the outer corners smooth. Insert outlines use a small close/open contour rounding, with the same contour used to generate the matching pocket.

Simplification happens on decorative relief before functional gussets and keys are introduced. The tray corridor is analytically cleared after simplification to avoid sub-tolerance protrusions. A slightly inset relief boundary is united with the analytic plate.

Valid double-precision meshes can still fail after binary STL coordinates are rounded to float32. The King Shark back needed an additional 0.0001 mm simplification pass to remove degenerate contacts near the hand/back transition. Venom required canonicalization through Manifold in its actual float32 print-coordinate representation, then restoration to assembly coordinates. Maximum original coordinate rounding was about 0.000007622 mm. Neither correction used a whole-model voxel remesh or changed the intended connectors. The actual resulting STLs and embedded 3MF coordinates were checked again.

The scripts and per-product `serialization` reports retain the method. If rebuilding from the construction script, repeat this export validation; do not assume an NPZ-only manifold check is sufficient. `canonicalize_venom.py` is an explicit finish step when needed.

## Bowl findings

The bowl uses the same source head whose chest/head assembly the user reported printing successfully. The original statue is unchanged. A smooth elliptical liner forms the useful cavity; the decorative face is cut away from that cavity before union. The teeth are joined and slightly blunted at this smaller scale so the bowl stays one connected color/part.

Overall envelope is 140 × 143.425 × 59.399 mm. The clear opening is about 134.8 × 90.8 mm, with approximately 520 mL geometric capacity. Nominal wall thickness is 2.6 mm normal to the oval boundary, with an uninterrupted 2.4 mm band and a 2.8 mm floor checked geometrically. Cavity obstruction is zero. This is not a physical liquid-containment or food-contact test.

It prints upright at 0.28 mm layers, three walls and 5% gyroid. Supports around the small face overhangs add about 6½ minutes and 2.43 g. Full estimated print is about three hours and 113 g on either printer. Those figures include support; the support-only mass comes from positive support extrusion, while the total comes from the slicer's summary.

## Evidence and limits

Each product's `validation/` folder holds source/export checks, plate layout, slicer estimates and actual extrusion-path checks. Slicer pass means `return_code = 0`, empty per-plate warning messages and zero filament changes. Ordinary raw engine diagnostics are not being represented as an entirely empty log.

Both shelves generate zero support paths in the supplied orientations. The bowl intentionally generates limited support. Do not disable bowl support merely because the shelves do not need it. A successfully calculated toolpath is not physical proof of adhesion, surface quality, durability or load capacity.

The shelves remain mounting prototypes with no assigned safe load. The back has clear flat zones, but 3M's picture-strip instructions do not recommend shelves. Read [MOUNTING_RESEARCH.md](MOUNTING_RESEARCH.md) before changing mounting claims or geometry.

## Continuing the project

Preserve the original statue's already printed torso and every mating interface. Record each new observation, experiment, failure and selected revision in Markdown. Keep the product README, actual files, dimensions, color instructions and estimates synchronized. Archive rejected trials as research, not recommended prints. Revalidate the exact exported artifacts after geometry or print-setting changes. Use the GitHub commit and file hashes to identify the version under discussion.

Editable Blender geometry is sufficient to continue modeling. Archived Python scripts document the method but still require their original scientific Python/Blender dependencies and source paths; they are not a promised one-command installer.
