# Dragon + Pixel PLA Shelf Prototypes

**Wall update, September 29:** The user reports textured painted walls, apparently with a thin coat of paint, and intends to display miscellaneous printed objects and occasionally a mouse. The earlier smooth-wall assumption is superseded. Do not treat the Command-style mounting discussion below as a confirmed installation method for this wall. The texture severity and paint condition remain unknown; thin paint does not by itself prove a weak coating. Standard Command strips are not recommended for heavily textured surfaces, according to the linked manufacturer guidance. The shelf geometry remains a prototype while a suitable mount is assessed.

One candidate for further assessment is the [tesa Adjustable Adhesive Screw for Wallpaper & Plaster](https://www.tesa.com/en/consumer/tesa-adjustable-adhesive-screw-for-wallpaper-and-plaster-1kg.html), intended for textured/sensitive surfaces. It adheres to the wall without drilling. Its published hanging rating must not be transferred to this projecting shelf. Paint compatibility, shelf-use guidance and actual hardware dimensions would need verification before a backplate adapter is designed. This is a research candidate, not a purchase recommendation or an included compatible mount.

These are original CAD designs inspired by your two images and the construction ideas linked below. They are small display-shelf prototypes, not verified wall hardware. No downloaded model mesh was copied or remixed. The reference images' 7 lb / 3.2 kg claims are not used.

Open `../images/design_preview.png` to see the actual assembled mesh geometry. The STL files are in millimetres and already oriented for printing. `../source/shelves_editable.scad` is editable in OpenSCAD; change the `part` index to export a part. `../source/build_shelves.py` regenerates the meshes and preview with Python.

## Which one to print

| Design | Print these parts | Assembled size, W x D x H | Usable display space |
|---|---|---|---|
| Plain ledge — fastest complete shelf | 01 | 120 x 64 x 140 mm | 120 x 58.4 mm deck behind lip |
| Dragon wing ledge | 01, both 03 wings, optional 04 crest | 236 x 64 x 186 mm | Same ledge; wings are decorative |
| Pixel display pod | 02 and 05 | 156 x 66.4 x 199 mm | 108 x 106 mm front opening; 58.4 mm deck depth behind lip |
| Adhesive surface coupon | 00 | 30 x 110 x 3.2 mm in use | Checks strip size and print-surface finish |

Depth excludes the wall adhesive. All individual parts fit well inside the P1S's 256 mm build volume. See [Bambu's specifications](https://bambulab.com/en-us/p1p).

For a bigger pixel arrangement, print several independent pods and stagger their heights, leaving at least 5 mm between decorative edges. Three pods side by side need about 478 mm overall. Each needs its own wall attachment. Do not rest a shared shelf across them or assume they share loads. Staggered independent dragon ledges can create a tiered display without a large, deep, heavy backboard.

The pixel roof is decorative enclosure, not an additional rated storage deck. These versions suit small lightweight display objects. Your actual object dimensions, weights and wall finish are still needed to finalise the design.

## Why the geometry changed

The dragon reference is 180 mm deep; these ledges project only 64 mm including the back. A shelf pulls outward on the upper attachment as well as downward. The simple moment relationship is `moment = total weight force x distance of centre of mass from wall`. Cutting that distance reduces the overturning moment, but it does not establish adhesive capacity.

The backplate is 3.2 mm thick; the deck is 4.8 mm thick. A 3.2 mm diagonal shell below the deck connects the front to the low part of the back. The hollow triangular section runs across the width. It prints on its side as a continuous profile, without separate gussets starting in mid-air. The lower shell intentionally uses more material than a minimal unsupported L ledge. The thin, flat decorations avoid sculpted details and multicolour purging.

## P1S starting settings

These are proposed settings, not a physically tested print profile. Assume a standard 0.4 mm nozzle and ordinary PLA. Select your actual PLA and plate profiles in Bambu Studio.

| Setting | Structural core | Wings / frame / crest |
|---|---|---|
| Layer height | 0.28 mm | 0.24 or 0.28 mm |
| Wall loops | 4 | 3 |
| Top / bottom layers | 4 / 4 | 4 / 4 |
| Infill | 10–15% gyroid | 10% gyroid |
| Supports | Off; inspect the entire preview first | Off |
| Brim | 5 mm starting point for narrow side footprint | Only if needed |
| Ironing / variable layers | Off | Off |
| Speed / flow | Normal mode; calibrated PLA profile | Same |

Do not auto-orient the core onto its back. Keep the supplied orientation: the ledge footprint is 64 x 140 mm and its printed height is 120 mm; the pod footprint is 64 x 180 mm with the same height. The decorations lie flat, plain rear face down. The coupon prints on its thin edge to reproduce the core's wall-facing layer texture; use a brim.

The thin shells will be mostly perimeter material, so reducing infill alone will save little. Skip decorations to save the most time; use the plain ledge instead of the pod when an enclosure is unnecessary. Do not scale the STLs down blindly: wall thickness, adhesive area and usable clearances scale too.

Exact print time and filament consumption require slicing. The validation file reports geometric solid-equivalent mass at 1.24 g/cm³, not slicer consumption: approximately 150 g for the bare ledge, 189 g for the decorated dragon, and 234 g for the decorated pixel pod. Brims and extrusion settings affect actual use. No printer-ready G-code or verified slicing project is included.

## Assembly

1. Print the surface coupon first. Check your exact uncut adhesive product against it and inspect the surface quality. This is a fit/finish check, not a shelf strength test.
2. Print one core in its supplied orientation. Check for cracks, missing layers, warping and an uneven back. The wall-facing back must be flat.
3. Dragon: hold each wing against the room-facing side of the backplate, with ribs facing outward. The straight inner wing edge sits 16 mm inboard of the corresponding side of the 120 mm core. Each wing's lowest tip is 42 mm above the core bottom; its highest point is 186 mm above it. Glue only the overlapping wing/backplate area with an adhesive suitable for PLA; cure as directed. The wings must not sit between the backplate and the wall. The optional crest centres on the backplate, bottom at 91 mm and top at 133 mm.
4. Pixel: glue the flat frame to the front of the upper deck and front lip. Centre it across the core; its bottom is 55 mm above the core bottom and its highest step is 199 mm above it. The frame's rear face contacts the core's front plane. It is decoration and does not reinforce the wall connection.
5. Keep glue and decoration off the entire wall-contact surface. Dry-fit everything before gluing. Neither design depends on a precision snap fit.

## Adhesive mounting — final product still to be selected

The backplate deliberately has a continuous flat face instead of a recess sized to an unknown strip SKU. A removable interlocking picture-strip pair is a plausible prototype interface because the shelf can separate from the wall-side strips, exposing their release tabs. This does **not** mean the shelf inherits a picture-frame weight rating or that 3M approves this custom application.

The ledge has a 120 x 140 mm mounting face; the pod has 120 x 180 mm. Two unobstructed 30 x 110 mm vertical fit zones can be placed near the left and right edges, with room between them. These are available geometric areas, not a prescribed number of strips or a universal strip size. Measure the complete adhesive, interlocking stack and release tab of the exact product first. No cutting or stacking strips to force a fit.

3M says to select a product for the actual use and surface, follow its package layout, preparation and wait time, and not assume added strips increase capacity. Smooth, sound surfaces matter; heavily textured walls are unsuitable. Painted surfaces must be fully cured. Follow the removal instructions and preserve access to the stretch-release tabs. [3M Command FAQ](https://www.command.com/3M/en_US/command/contact-us/faqs/)

The core's rear surface is printed vertically. If layer texture prevents complete adhesive contact, make that face flat and smooth without thinning it substantially, then remove all sanding residue and use the adhesive maker's compatible preparation method. Verify on the coupon first. A short coupon trial cannot demonstrate long-term mounting strength.

Check that the installed shelf sits level rather than rocking around a thick strip stack. Do not fit arbitrary hard spacers that tilt the plate or peel the bond. Keep removal travel below each release tab clear after separating the picture-strip pairs. Support and unload the shelf during removal; do not use its deck as a pry bar.

Permanent foam/VHB-style tape is not an equivalent renter-safe substitution. A stronger bond can still detach weak paint or damage it at removal. No universal adhesive or load limit can be chosen until the wall and intended contents are known.

## What is verified, and what is not

All seven exported STL files were reloaded and checked for watertightness, positive volume, a single connected component and bed-size fit. The assembly preview was rendered from the CAD meshes and inspected. `../validation/mesh_validation.json` records these checks. Geometric checks are not mechanical testing.

Not yet verified: Bambu Studio layer preview, actual print quality, adhesive/PLA compatibility, paint strength, sustained loading, long-term PLA creep, or drop resistance. No safe working load is assigned. PLA can creep under sustained bending even below its glass-transition temperature; see this [experimental PLA creep paper](https://arxiv.org/abs/2302.11240).

For physical development, test a single empty shelf low over a padded catch area first, then add known small nonbreakable test masses close to the wall in stages and record weight, position, elapsed time, sag and adhesive lifting. Stop at any movement. A short successful test is not a lifetime rating. Include the shelf and decoration mass in the total supported mass. Until validated, do not use for books, filled plant pots, glass, valuables or a location over people.

## Research and model references

| Source | Relevant observation | How it influenced this kit |
|---|---|---|
| [Reddit: dorm shelf with printed brackets](https://www.reddit.com/r/3Dprinting/comments/e1oc65/cant_put_holes_in_my_dorm_room_walls_so_3d/) | OP reported success after three months; others reported failure after six months or within a year and discussed outward pull. Anecdotes conflict. | Shallow decks; no copied load rating; explicit long-term uncertainty. |
| [Reddit: detachable record shelf](https://www.reddit.com/r/functionalprint/comments/10omgkl/record_shelf_with_detachable_wall_mount/) and its [Printables model](https://www.printables.com/model/384245-record-shelf) | Creator explains the removable mount was intended to conceal release tabs. | Tab access remains a design requirement. Current kit relies on separable picture-strip pairs, not that model's connector. |
| [Printables: shelf with support rib, Jono](https://www.printables.com/model/378887-remixed-command-strip-shelf-with-support-rib) | Creator reports improved rigidity after adding a rib. | A diagonal load path beneath the deck, implemented here as a continuous printable shell. No mesh reused. |
| [Printables: hidden and accessible pull tabs, TacocaT](https://www.printables.com/model/1809336-command-strip-shelf-hiddenaccessible-pull-tabs/related) | Listing describes a removable shelf for small items. | Reinforces the importance of accessible removal. Detailed CAD was not inspected. |
| [Reddit: catch-all shelf](https://www.reddit.com/r/functionalprint/comments/1rtm67c/wallmounted_catch_all_shelf_with_command_strips/) and its [MakerWorld model](https://makerworld.com/en/models/2521979-wall-mounted-catch-all-shelf-no-screws-required) | Creator reports holding a wallet and keys with adhesive strips. | Small display/catch-all scale, rather than full bookshelf scale. Report is anecdotal, not a rating. |

Research checked September 28, 2026. Some direct Printables/MakerWorld pages blocked retrieval; their available indexed descriptions and the creators' Reddit explanations were used. External CAD and print profiles were not downloaded or validated. Observe the original models' own licences if you remix them separately.

## To finalise for your wall

Known: textured painted wall; miscellaneous printed objects and an occasional mouse. Needed: texture severity and paint condition; the heaviest item's weight and base dimensions; desired total display width; exact mounting product; confirmation of nozzle size. The geometry was initially designed around a potentially compatible smooth wall and 0.4 mm nozzle. The smooth-wall assumption no longer applies to this installation. No adhesive installation is finalised.
