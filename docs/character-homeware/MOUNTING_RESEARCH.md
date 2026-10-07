# Mounting research for character accessory shelves

Research checked October 6, 2026. These notes support the King Shark and Venom shelf prototypes; they do not assign a working load.

## What the manufacturer supports

3M's picture-hanging-strip guidance says **“Not recommended for mounting shelves, tapestry or shadow boxes.”** A strip's picture-frame capacity is therefore not a capacity for this projecting printed shelf. The prototype's own weight and anything placed on its tray act away from the wall. This introduces a turning load; making the back flat does not remove that load. The latter explanation is an engineering inference, not a 3M load calculation. [Official 3M document, Usage Tips](https://multimedia.3m.com/mws/media/1792217O/command-a-online-content-file-picture-hanging-strips-en.pdf)

No official validation of Command adhesive on FDM-printed PLA was found. Do not describe the printed shelf as Command-approved, guaranteed damage-free, or rated for the numerical weight printed on a picture-strip package.

## Geometry allowances

The official regional size table lists large picture-hanging strips as **93 mm long × 19 mm wide**. The custom shelves reserve two clear areas, each **100 × 25 mm**, on a **148 × 156 mm** flat back. The contact-zone centers are X = −30 and +30 mm, beginning at Z = 10 mm. The extra space is a design allowance rather than a manufacturer specification. Use the dimensions and directions on the specific package in hand. [Official Command dimensions](https://www.command.com.hk/3M/en_HK/command-hk/how-to-use/product-weight-limits/)

Do not place lettering, texture, glue residue, or ribs in an adhesive-contact area. A textured print-bed finish may need smoothing; this is a practical design consideration, not proof of reliable adhesion.

US picture-strip instructions say to remove the object from the paired strips, then stretch each strip downward against the wall for **at least 15 inches / 38 cm**. Leave the tabs accessible. This is clearance along the wall after removing the model, not a 380 mm channel to add inside the print. Follow the package's installation sequence, including cleaning with rubbing alcohol, firm pressure, and the one-hour wait. [Official application and removal instructions](https://www.command.com/3M/en_US/command/how-to-use/picture-hanging-strips/)

The two visible, through-cut mechanical keyhole slots have 9.2 mm entry diameters, 4.7 mm neck widths, and centers 108 mm apart. They are an alternate mounting interface in the current CAD. Their presence does not establish a structural rating or select suitable wall anchors. The user's preferred adhesive mounting face remains clear.

## Use conditions and intended objects

The design intent is a small catchall for light accessories. No mass limit, adhesive endurance, printed bracket strength, or wall-finish compatibility has been physically established. The trays are 150 × 55 mm, with a 4.2 mm floor and 4.8 mm rim above it. The two support gussets are 6 mm thick. Geometry dimensions alone do not establish a working load.

3M calls for smooth, clean, dry surfaces and product-specific application directions. Its FAQ explains that adding strips does not automatically increase capacity. Ordinary indoor products are not intended for rough walls or all humid environments; bathrooms require appropriate water-resistant products. [Official 3M FAQ](https://www.command.com/3M/en_US/command/contact-us/faqs/)

A manufacturer-designed Command display ledge is a possible future platform for a decorative character surround. Such an adaptation would need the actual ledge measured and the surround's mass included in use of the manufacturer's limit. It would retain the ledge's original mounting system. No such adaptation is included in this prototype. [Official display ledge](https://www.command.com/3M/en_US/p/d/b5005604121/)

## Bowl distinction

The King Shark bowl is a freestanding keys/accessories catchall. It does not require a wall mount. Food use has not been specified or evaluated; the current project does not claim food-contact approval or watertightness under liquid testing.

## Evidence and future updates

Machine-readable research: `work/character_homeware/review/mounting_research.json` in the original workspace. Shelf CAD measurements: each design's `geometry_validation.json`. Record future physical checks separately from slicer and mesh results, including exact wall finish, mounting product, object weight, elapsed test period, printed material, and observed outcome. Do not convert a successful short trial into a manufacturer-approved or long-term load rating.

