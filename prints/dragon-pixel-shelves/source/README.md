# Editable source

STL downloads can be inspected without running these scripts. Use this directory to edit or regenerate geometry.

## Python

Use Python 3.11 or newer in a virtual environment:

```sh
python -m venv .venv
# Activate .venv with your shell's activation command.
python -m pip install -r requirements.txt
python build_shelves.py
```

The generator writes to `../files/stl/`, `../images/design_preview.png`, `../validation/mesh_validation.json`, and `shelves_editable.scad` here. Back up manual edits before regenerating. It prefers Windows Segoe UI or Linux DejaVu fonts, with a Pillow fallback.

Core dimensions are near the start of the script. Decorative geometry and offsets also depend on those dimensions; changing one constant is not a complete redesign. Regenerate, inspect and physically test modifications.

## OpenSCAD

Open `shelves_editable.scad`, choose a `part` index, render, and export STL. Modules use printing orientations. OpenSCAD compilation has not been separately verified.

| Index | Part |
|---|---|
| 0 | Ledge core |
| 1 | Pixel core |
| 2 | Right wing |
| 3 | Left wing |
| 4 | Crest |
| 5 | Pixel frame |
| 6 | Coupon |
