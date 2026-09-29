# Higgsfield scene source

`build_higgsfield_scene.py` creates the Emberwing and Rift visual concepts in Higgsfield 3D Jutsu’s Blender 5.2 worker. Its `bpy` and `artifacts` objects are supplied by that service. It is not a standalone plain-Python or OpenSCAD generator.

The script builds a new scene, replacing that scene’s objects. Do not run it against unrelated work. Use the included `.blend` to edit the delivered models directly without rebuilding. Core units are metres; a 0.2-unit length means 200 mm.

The geometry uses named objects, editable bevels, curves and materials. Candidate physical groups have a `part_id` property. The studio collection is presentation-only and must be excluded from printable exports.

Renders and source models are visual-development deliverables. A GLB or Blender export does not prove a watertight printable solid, an assembly fit, or a safe wall mount.

## Local prototype export

`export_prototypes.py` reads the committed revision-3 GLB, welds export seams, consolidates each part with Manifold, and creates millimetre STLs with their rear face on Z=0. It checks watertightness, positive volume, connected components, STL round trips and bounding-box fit. It also writes two model-only GLBs in metres and the mesh validation report. The separate Blender components remain editable.

`render_parts.py` renders the labelled footprint sheet from the actual STLs.

From this project directory:

```sh
python -m pip install -r source/requirements.txt
python source/export_prototypes.py
python source/render_parts.py
```

These commands overwrite the generated prototype exports, mesh report and footprint image. They do not slice or physically test the models. The presentation Blender/GLB and hero render are downloaded separately from Higgsfield; see `validation/higgsfield_project.json` for provenance.
