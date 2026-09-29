# From bold concept to printable shelf

[← Project](../README.md)

## Visual brief

George asked for bigger, cooler shelves with strong visual impact and manageable detail. The appeal of a simple building block was a reference for clarity and recognisable form, not a request to reproduce LEGO geometry. Both concepts use a single red plastic material per design, broad silhouettes, deliberate edge treatments, and a small number of repeated forms.

Emberwing develops the dragon reference into three tiers with separate wing sections and a crest. Rift moves away from the earlier rectangular frame into a stepped group of five chamfered hexagonal pods. The scene uses real editable geometry rather than a generated product photograph.

## Geometry organisation

- Emberwing: named left/right upper/lower wing groups, five ledge modules, and a crest group.
- Rift: five named pod groups, each with a back and chamfered frame.
- Studio: backdrop, floor, typography, delivery camera and lighting. Exclude this entire collection from model exports.

Bevel and normal modifiers are retained so edge treatments remain editable. Curved wing ribs remain editable curves. The GLB is for preview and exchange; the Blender file is the editable source of record.

## Print development still required

1. Choose a design and final object sizes. An item’s full base must fit the useful deck, not just the outer dimensions.
2. Resolve a mounting method for the actual textured painted wall. Broad backs alone do not validate adhesive capacity.
3. Review the supplied boolean-unioned STL exports in a slicer. Their mesh checks pass; this does not test strength or print behaviour.
4. Engineer the joins and decoration attachments. Panel divisions in this scene have no calibrated interlocks or fasteners.
5. Keep the supplied rear-face-down orientation initially. Bounding-box fit is checked; supports and extrusion behaviour still need a slicer preview.
6. Slice with the actual PLA and nozzle, print fit/finish samples, then record physical results before calling a profile verified.

The earlier prototype STLs remain in their own project with their original validation. The larger prototypes have their own mesh checks. They do not inherit a physical print result or load rating.

## Material refinement

Revision 3 preserves Rift’s silhouette and broad bevel while tapering the frame behind it. Geometric solid volume changed from 671.555 to 314.879 cm³ per pod, a 53.1% reduction. Infill means this does not directly predict filament savings or print duration. Structural performance remains untested.
