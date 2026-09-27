"""Render the actual RedGengarPuffy CAD color assignment."""
from pathlib import Path
import math
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "GengarPuffco"
bpy.ops.wm.open_mainfile(filepath=str(SOURCE / "CAD" / "Gengar_Compact_EDITABLE.blend"))


def set_color(material, color):
    rgb = tuple((int(color[i:i + 2], 16) / 255) ** 2.2 for i in (0, 2, 4))
    material.diffuse_color = (*rgb, 1)
    material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*rgb, 1)


black_tokens = ("eyes_red", "grin_pink", "george_red", "bottom_cap_red")
for obj in bpy.context.scene.objects:
    if obj.type != "MESH" or not obj.data.materials or obj.name == "STUDIO_NOT_FOR_PRINT":
        continue
    color = "1C1B26" if any(token in obj.name for token in black_tokens) else "CE1834"
    set_color(obj.data.materials[0], color)

scene = bpy.context.scene
camera = scene.camera
camera.location = (145, -280, 145)
camera.rotation_euler = (Vector((0, 0, 61)) - camera.location).to_track_quat("-Z", "Y").to_euler()
camera.data.type = "ORTHO"
camera.data.ortho_scale = 190
scene.render.resolution_x = 1200
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
(ROOT / "Preview").mkdir(exist_ok=True)
scene.render.filepath = str(ROOT / "Preview" / "RedGengarPuffy_actual_CAD.png")
bpy.ops.render.render(write_still=True)
camera.location = (0, 300, 108)
camera.rotation_euler = (Vector((0, 0, 67)) - camera.location).to_track_quat("-Z", "Y").to_euler()
camera.data.ortho_scale = 180
scene.render.filepath = str(ROOT / "Preview" / "RedGengarPuffy_rear_George.png")
bpy.ops.render.render(write_still=True)
