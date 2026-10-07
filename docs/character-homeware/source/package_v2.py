"""Package already-engineered, closed meshes; this does not generate or repair a sculpt.

Inputs and examples are documented in pipeline_notes.json.  All positions are mm.
No slicing, printer operations, external uploads, or publication are performed.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
import zipfile

import manifold3d as mf
import numpy as np
from PIL import Image
import trimesh


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
CORE_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
COLORS = {"Black": 1, "White": 2, "Red": 3}
DEFAULT_PALETTE = ["#25282A", "#EFE7D5", "#BB1424"]
REINFORCE = dict(wall_loops="3", sparse_infill_pattern="gyroid",
                 sparse_infill_density="15%", top_shell_layers="5",
                 top_shell_thickness="1")
PROFILE_NAMES = {"P1S": "Venom_lightweight_READY.3mf",
                 "P2S": "Venom_lightweight_P2S_READY.3mf"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def relative_path(base, value):
    p = Path(value)
    return p.resolve() if p.is_absolute() else (base / p).resolve()


def rigid_matrix(value, label):
    T = np.asarray(value, dtype=np.float64)
    require(T.shape == (4, 4) and np.isfinite(T).all(), f"{label}: invalid 4x4 matrix")
    require(np.allclose(T[3], [0, 0, 0, 1], atol=1e-8), f"{label}: affine last row")
    R = T[:3, :3]
    require(np.allclose(R.T @ R, np.eye(3), atol=1e-6) and
            np.isclose(np.linalg.det(R), 1, atol=1e-6),
            f"{label}: use a rigid rotation, no reflection or scale; scale before engineering joints")
    return T


def transform_vertices(vertices, T):
    return vertices @ T[:3, :3].T + T[:3, 3]


def matrix_3mf(T):
    # 3MF writes the 3x4 affine transform in column order (translation last).
    return " ".join(f"{x:.12g}" for x in T[:3, :].T.reshape(-1))


def metadata(element, key, value):
    require(not isinstance(value, (dict, list, tuple)), f"Metadata {key} must be scalar")
    ET.SubElement(element, "metadata", key=str(key), value=str(value))


def xml_bytes(element):
    return ET.tostring(element, encoding="utf-8", xml_declaration=True)


def frame(normal):
    n = np.asarray(normal, dtype=np.float64)
    require(n.shape == (3,) and np.isfinite(n).all() and np.linalg.norm(n) > 0,
            "Joint normal must be a finite nonzero vector")
    n /= np.linalg.norm(n)
    u = np.array([1., 0, 0]) if abs(n[0]) < .8 else np.array([0., 1, 0])
    u -= n * (u @ n)
    u /= np.linalg.norm(u)
    return np.column_stack((u, np.cross(n, u), n))


def checked_mesh(vertices, faces, label):
    v = np.ascontiguousarray(vertices, dtype=np.float64)
    f = np.asarray(faces)
    require(v.ndim == 2 and v.shape[1] == 3 and len(v) > 3 and np.isfinite(v).all(),
            f"{label}: missing or invalid vertices")
    require(f.ndim == 2 and f.shape[1] == 3 and len(f) > 3 and
            np.isfinite(f).all() and np.equal(f, np.floor(f)).all() and
            f.min() >= 0 and f.max() < len(v), f"{label}: invalid triangle indices")
    f = np.ascontiguousarray(f, dtype=np.uint64)
    mesh = trimesh.Trimesh(v, f, process=False)
    solid = mf.Manifold(mf.Mesh64(v, f))
    require(mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0 and
            solid.status() == mf.Error.NoError, f"{label}: mesh must be closed, outward and manifold")
    return v, f, {"triangles": len(f), "vertices": len(v),
                  "volume_mm3": float(mesh.volume), "manifold_status": str(solid.status())}


def load_parts(manifest_path):
    manifest_path = Path(manifest_path).resolve()
    document = read_json(manifest_path)
    rows = document["parts"] if isinstance(document, dict) else document
    require(isinstance(rows, list) and rows, "Manifest needs a nonempty parts list")
    parts = {}
    for row in rows:
        name = row["name"]
        require(isinstance(name, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_. -]*", name)
                and name not in parts, f"Unsafe or duplicate part name: {name}")
        require(row.get("color") in COLORS, f"{name}: color must be Black, White or Red")
        path = relative_path(manifest_path.parent, row.get("mesh", name + ".npz"))
        require(path.suffix.lower() == ".npz", f"{name}: use NPZ with vertices/faces arrays")
        with np.load(path, allow_pickle=False) as data:
            v, f, report = checked_mesh(data["vertices"], data["faces"], name)
        assembly = rigid_matrix(row.get("assembly_transform", np.eye(4)), name + " assembly")
        # Joint locations share the source coordinate system; assembled transforms
        # only affect the Bambu Assembly view, never the print orientation.
        settings = row.get("settings", {})
        require(isinstance(settings, dict), f"{name}: settings must be an object")
        require("extruder" not in settings, f"{name}: choose extruder via color")
        parts[name] = dict(name=name, color=row["color"], vertices=v, faces=f,
                           settings=settings, assembly_transform=assembly,
                           mesh_path=str(path), source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                           mesh_report=report)
    return parts


def load_layout(layout_path, parts):
    layout_path = Path(layout_path).resolve()
    layout = read_json(layout_path)
    plates = layout.get("plates", [])
    require(bool(plates), "Layout needs at least one plate")
    margin = float(layout.get("bed_margin_mm", 3))
    max_z = float(layout.get("max_height_mm", 250))
    require(0 <= margin < 128 and 0 < max_z <= 256, "Invalid printer envelope")
    used = []
    results = []
    columns = math.ceil(math.sqrt(len(plates)))
    for index, plate in enumerate(plates, 1):
        instances = plate.get("instances", [])
        require(bool(instances), f"Plate {index} is empty")
        groups = []
        origin = np.array([((index - 1) % columns) * 307.2,
                           -((index - 1) // columns) * 307.2, 0.])
        for instance in instances:
            name = instance["name"]
            require(name in parts and name not in used, f"Unknown or multiply arranged part: {name}")
            used.append(name)
            part = parts[name]
            if "transform" in instance:
                require("rotation" not in instance and "xy_mm" not in instance,
                        f"{name}: supply transform OR rotation plus xy_mm")
                T = rigid_matrix(instance["transform"], name + " print")
            else:
                R = np.asarray(instance.get("rotation", np.eye(3)), dtype=float)
                require(R.shape == (3, 3), f"{name}: rotation must be 3x3")
                T = np.eye(4)
                T[:3, :3] = R
                T = rigid_matrix(T, name + " rotation")
                xy = np.asarray(instance["xy_mm"], dtype=float)
                require(xy.shape == (2,) and np.isfinite(xy).all(), f"{name}: invalid xy_mm")
                rotated = part["vertices"] @ R.T
                T[:3, 3] = np.r_[xy, 0.] - rotated.min(axis=0)
            pv = transform_vertices(part["vertices"], T)
            lo, hi = pv.min(axis=0), pv.max(axis=0)
            require((lo[:2] >= margin - 1e-5).all() and
                    (hi[:2] <= 256 - margin + 1e-5).all() and
                    lo[2] >= -.001 and abs(lo[2]) <= .01 and hi[2] <= max_z + 1e-5,
                    f"{name}: out of bed envelope or floating: {lo.tolist()}..{hi.tolist()}")
            global_T = T.copy()
            global_T[:3, 3] += origin
            settings = {**part["settings"], **instance.get("settings", {})}
            require("extruder" not in settings, f"{name}: choose extruder via color")
            groups.append(dict(name=name, plate=index, local_transform=T,
                               transform=global_T, bounds_mm=[lo.tolist(), hi.tolist()],
                               dimensions_mm=(hi - lo).tolist(), settings=settings))
        colors = {parts[g["name"]]["color"] for g in groups}
        require(len(colors) == 1, f"Plate {index}: mixed colors would require AMS")
        image_path = relative_path(layout_path.parent, plate["preview"]) if plate.get("preview") else None
        results.append(dict(id=index, label=plate.get("label", f"Plate {index}"),
                            color=colors.pop(), origin=origin.tolist(), groups=groups,
                            preview=image_path))
    require(set(used) == set(parts), f"Unarranged parts: {sorted(set(parts) - set(used))}")
    palette = layout.get("palette", DEFAULT_PALETTE)
    require(len(palette) == 3 and all(re.fullmatch(r"#[A-Fa-f0-9]{6}", s) for s in palette),
            "Palette needs exactly three #RRGGBB strings, in Black/White/Red slot order")
    return layout, results, palette


def load_joints(joints_path, parts):
    if joints_path is None:
        return []
    rows = read_json(joints_path)
    rows = rows["joints"] if isinstance(rows, dict) else rows
    require(isinstance(rows, list), "Joints must be a list")
    ids = []
    for j in rows:
        require(j["id"] not in ids, "Joint IDs must be unique")
        ids.append(j["id"])
        require(j["male"] in parts and j["female"] in parts and j["male"] != j["female"],
                f"{j['id']}: missing or identical connected parts")
        frame(j["normal"])
        center = np.asarray(j["center_mm"], dtype=float)
        require(center.shape == (3,) and np.isfinite(center).all(), f"{j['id']}: invalid center")
        require(float(j["half_width_mm"]) > 0 and float(j["length_mm"]) > 0,
                f"{j['id']}: invalid joint size")
        if j.get("reinforce", True):
            require(all(np.allclose(parts[p]["assembly_transform"], np.eye(4))
                        for p in (j["male"], j["female"])),
                    f"{j['id']}: auto reinforcement requires common assembly-coordinate meshes")
    return rows


def joint_modifier(joint):
    R = frame(joint["normal"])
    n = R[:, 2]
    radius = float(joint["half_width_mm"]) + float(joint.get("reinforcement_padding_mm", 4))
    length = float(joint["length_mm"])
    require(radius > 0, "Reinforcement radius must be positive")
    cylinder = trimesh.creation.cylinder(radius=radius, height=length + 8, sections=48)
    vertices = np.asarray(cylinder.vertices) @ R.T + np.asarray(joint["center_mm"]) + n * (length / 2 - 1)
    return vertices, cylinder.faces


def profile_config(printer, template_dir, palette, process_name):
    with zipfile.ZipFile(Path(template_dir) / PROFILE_NAMES[printer]) as z:
        config = json.loads(z.read("Metadata/project_settings.config"))
    require(config.get("printer_model") == "Bambu Lab " + printer,
            f"Template printer mismatch: {printer}")
    require(config.get("nozzle_diameter") == ["0.4"], "Expected standard 0.4mm nozzle")
    # Preserve the working template's compound arrays: drying settings intentionally
    # have 6/12 entries and must NOT be naively truncated to the filament count.
    config.update(print_settings_id=process_name, inherits_group=[""] * 5,
                  enable_prime_tower="0", filament_colour=palette,
                  filament_self_index=["1", "2", "3"], filament_nozzle_map=["1"] * 3,
                  filament_volume_map=["0"] * 3,
                  filament_extruder_variant=["Direct Drive Standard"] * 3,
                  extruder_nozzle_stats=["Standard#1"], compatible_printers=[])
    require(config["wall_loops"] == "2" and config["sparse_infill_pattern"] == "lightning",
            "Expected the proven lightweight Venom template")
    config["different_settings_to_system"] = [";".join(sorted(config))] * 5
    return config


def mesh_xml(object_id, vertices, faces):
    buf = io.StringIO()
    buf.write(f'<object id="{object_id}" type="model"><mesh><vertices>')
    for start in range(0, len(vertices), 10000):
        buf.write("".join('<vertex x="%.11g" y="%.11g" z="%.11g"/>' % tuple(v)
                          for v in vertices[start:start + 10000]))
    buf.write("</vertices><triangles>")
    for start in range(0, len(faces), 10000):
        buf.write("".join('<triangle v1="%d" v2="%d" v3="%d"/>' % tuple(f)
                          for f in faces[start:start + 10000]))
    buf.write("</triangles></mesh></object>")
    return buf.getvalue()


def png_bytes(path, max_size=None):
    with Image.open(path) as image:
        image = image.convert("RGB")
        if max_size:
            image.thumbnail((max_size, max_size))
        output = io.BytesIO()
        image.save(output, format="PNG")
    return output.getvalue()


def roundtrip_stl(part, group):
    T = group["local_transform"].copy()
    vertices = transform_vertices(part["vertices"], T)
    vertices -= vertices.min(axis=0)
    source = trimesh.Trimesh(vertices, part["faces"], process=False)
    data = source.export(file_type="stl")
    loaded = trimesh.load_mesh(io.BytesIO(data), file_type="stl", process=True)
    _, _, report = checked_mesh(loaded.vertices, loaded.faces, part["name"] + " STL reimport")
    # No fill-holes, epsilon displacement or repair here; those would silently
    # change the engineered joint geometry after its assembly checks.
    require(np.isfinite(loaded.vertices).all() and loaded.bounds[0, 2] >= -.001,
            part["name"] + ": invalid exported STL")
    report.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                  dimensions_mm=loaded.extents.tolist(), watertight=True,
                  winding_consistent=True, geometry_repaired_during_export=False)
    return data, report


def build_model(parts, plates, joints, title):
    config = ET.Element("config")
    assembly = ET.SubElement(config, "assemble")
    build = ET.Element("build")
    resources = []
    next_id = 1
    normal_count = 0
    modifier_count = 0
    for plate in plates:
        for group in plate["groups"]:
            part = parts[group["name"]]
            object_id = next_id
            next_id += 1
            group["object_id"] = object_id
            parent = ET.Element("object", id=str(object_id), type="model")
            components = ET.SubElement(parent, "components")
            object_config = ET.SubElement(config, "object", id=str(object_id))
            metadata(object_config, "name", part["name"])
            metadata(object_config, "extruder", COLORS[part["color"]])
            metadata(object_config, "enable_support", group["settings"].get("enable_support", 1))
            for key, value in group["settings"].items():
                if key != "enable_support":
                    metadata(object_config, key, value)
            meshes = [(part["name"], part["vertices"], part["faces"], "normal_part", {})]
            for joint in joints:
                if part["name"] in [joint["male"], joint["female"]] and joint.get("reinforce", True):
                    v, f = joint_modifier(joint)
                    meshes.append(("Reinforce " + joint["id"], v, f, "modifier_part",
                                   {**REINFORCE, **joint.get("reinforcement_settings", {})}))
            for name, v, f, subtype, settings in meshes:
                mesh_id = next_id
                next_id += 1
                ET.SubElement(components, "component", objectid=str(mesh_id), transform=matrix_3mf(np.eye(4)))
                item = ET.SubElement(object_config, "part", id=str(mesh_id), subtype=subtype)
                metadata(item, "name", name)
                metadata(item, "matrix", "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1")
                if subtype == "normal_part":
                    normal_count += 1
                    metadata(item, "extruder", COLORS[part["color"]])
                else:
                    modifier_count += 1
                    for key, value in settings.items():
                        metadata(item, key, value)
                ET.SubElement(item, "mesh_stat", face_count=str(len(f)), edges_fixed="0",
                              degenerate_facets="0", facets_removed="0", facets_reversed="0", backwards_edges="0")
                resources.append(mesh_xml(mesh_id, v, f))
            resources.append(ET.tostring(parent, encoding="unicode"))
            ET.SubElement(build, "item", objectid=str(object_id), transform=matrix_3mf(group["transform"]))
            ET.SubElement(assembly, "assemble_item", object_id=str(object_id), instance_id="0",
                          transform=matrix_3mf(part["assembly_transform"]), offset="0 0 0")
    for plate in plates:
        item = ET.SubElement(config, "plate")
        for key, value in [("plater_id", plate["id"]), ("plater_name", plate["label"]),
                           ("locked", "false"), ("filament_map_mode", "Auto For Flush")]:
            metadata(item, key, value)
        for group in plate["groups"]:
            instance = ET.SubElement(item, "model_instance")
            for key, value in [("object_id", group["object_id"]), ("instance_id", 0),
                               ("identify_id", 100 + group["object_id"])]:
                metadata(instance, key, value)
    model = (f'<?xml version="1.0" encoding="utf-8"?><model xmlns="{CORE_NS}" '
             'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" unit="millimeter">'
             '<metadata name="Application">BambuStudio-02.08.02.61</metadata>'
             '<metadata name="BambuStudio:3mfVersion">1</metadata>'
             f'<metadata name="Title">{escape(title)}</metadata>'
             '<metadata name="Description">Separate single-color glue parts. Lightweight shelf process '
             'based on the user-tested large Venom. No AMS required.</metadata><resources>'
             + "".join(resources) + "</resources>" + ET.tostring(build, encoding="unicode") + "</model>")
    return model.encode("utf-8"), xml_bytes(config), normal_count, modifier_count


RELATIONSHIPS = f'''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="{REL_NS}">
 <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
 <Relationship Target="/Metadata/plate_1.png" Id="rel-2" Type="{REL_NS}/metadata/thumbnail"/>
 <Relationship Target="/Metadata/plate_1.png" Id="rel-4" Type="http://schemas.bambulab.com/package/2021/cover-thumbnail-middle"/>
 <Relationship Target="/Metadata/plate_1_small.png" Id="rel-5" Type="http://schemas.bambulab.com/package/2021/cover-thumbnail-small"/>
</Relationships>'''
CONTENT_TYPES = '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
 <Default Extension="png" ContentType="image/png"/>
 <Default Extension="gcode" ContentType="text/x.gcode"/>
</Types>'''


def validate_project(path, expected_parts, expected_modifiers, expected_plates):
    ns = {"m": CORE_NS}
    with zipfile.ZipFile(path) as z:
        require(z.testzip() is None, "Corrupt ZIP")
        require(len(z.namelist()) == len(set(z.namelist())), "Duplicate ZIP entries")
        model = ET.fromstring(z.read("3D/3dmodel.model"))
        config = ET.fromstring(z.read("Metadata/model_settings.config"))
        process = json.loads(z.read("Metadata/project_settings.config"))
        rel = z.read("_rels/.rels")
        require(b"<Relationships xmlns=" in rel and b"ns0:" not in rel,
                "Bambu relationships require an unprefixed default namespace")
        require(model.get("unit") == "millimeter" and not model.get("requiredextensions"),
                "Unsupported units or required extensions")
        objects = model.findall("m:resources/m:object", ns)
        ids = [o.get("id") for o in objects]
        require(len(ids) == len(set(ids)), "Duplicate 3MF object IDs")
        ids = set(ids)
        triangles = 0
        for obj in objects:
            mesh = obj.find("m:mesh", ns)
            if mesh is not None:
                vertices = mesh.findall("m:vertices/m:vertex", ns)
                faces = mesh.findall("m:triangles/m:triangle", ns)
                require(vertices and faces, "Empty embedded mesh")
                for vertex in vertices:
                    require(all(math.isfinite(float(vertex.get(k))) for k in ("x", "y", "z")), "Invalid vertex")
                for face in faces:
                    require(all(0 <= int(face.get(k)) < len(vertices) for k in ("v1", "v2", "v3")), "Invalid index")
                triangles += len(faces)
            for component in obj.findall("m:components/m:component", ns):
                require(component.get("objectid") in ids and not any("path" in k for k in component.attrib),
                        "External or missing component reference")
        builds = model.findall("m:build/m:item", ns)
        require(len(builds) == expected_parts and all(b.get("objectid") in ids for b in builds), "Invalid build")
        require(len(config.findall('.//part[@subtype="normal_part"]')) == expected_parts, "Wrong normal part count")
        require(len(config.findall('.//part[@subtype="modifier_part"]')) == expected_modifiers, "Wrong modifier count")
        require(len(config.findall("plate")) == expected_plates, "Wrong plate count")
        require(process["filament_self_index"] == ["1", "2", "3"] and
                process["filament_nozzle_map"] == ["1"] * 3 and
                process["filament_volume_map"] == ["0"] * 3 and
                process["filament_extruder_variant"] == ["Direct Drive Standard"] * 3 and
                process["extruder_nozzle_stats"] == ["Standard#1"] and
                process["enable_prime_tower"] == "0", "Invalid single-nozzle filament configuration")
        require(len(process["inherits_group"]) == len(process["different_settings_to_system"]) == 5,
                "Wrong printer/process/filament configuration group count")
        for i in range(1, expected_plates + 1):
            with Image.open(io.BytesIO(z.read(f"Metadata/plate_{i}.png"))) as image:
                image.verify()
    return dict(file=Path(path).name, bytes=Path(path).stat().st_size,
                sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),
                embedded_geometry=True, normal_parts=expected_parts,
                joint_modifiers=expected_modifiers, plates=expected_plates, triangles=triangles,
                passes=True, sliced=False, desktop_GUI_import_verified=False, physical_print_test=False)


def serializable(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(type(value).__name__)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--layout", type=Path, required=True)
    parser.add_argument("--joints", type=Path)
    parser.add_argument("--preview", type=Path, help="Actual geometry render; do not use a concept image")
    parser.add_argument("--out", type=Path, default=ROOT / "packages")
    parser.add_argument("--template-dir", type=Path, default=PROJECT / "outputs/Venom_lightweight")
    parser.add_argument("--title", default="King Shark Realistic 47cm Non-AMS")
    parser.add_argument("--stem", default="King_Shark_Realistic_47cm")
    parser.add_argument("--process-name", default="King Shark Realistic Shelf 0.20mm Non-AMS")
    parser.add_argument("--check-inputs", action="store_true", help="Validate input geometry/layout/profiles without writing outputs")
    args = parser.parse_args()
    require(re.fullmatch(r"[A-Za-z0-9_-]+", args.stem), "Output stem must be a safe filename")
    parts = load_parts(args.manifest)
    layout, plates, palette = load_layout(args.layout, parts)
    joints = load_joints(args.joints, parts)
    profiles = {p: profile_config(p, args.template_dir, palette, args.process_name) for p in PROFILE_NAMES}
    summary = dict(parts=len(parts), plates=len(plates), joints=len(joints), palette=palette,
                   input_checks_pass=True, sliced=False, geometry_generated=False)
    if args.check_inputs:
        print(json.dumps(summary, indent=2))
        return
    require(args.preview and args.preview.is_file(), "--preview must reference a current actual-mesh render")
    preview = png_bytes(args.preview, 1200)
    preview_small = png_bytes(args.preview, 256)
    images = {}
    stls = {}
    stl_reports = []
    for plate in plates:
        images[plate["id"]] = ((png_bytes(plate["preview"], 1200), png_bytes(plate["preview"], 256))
                                if plate["preview"] else (preview, preview_small))
        for group in plate["groups"]:
            data, report = roundtrip_stl(parts[group["name"]], group)
            stls[group["name"]] = data
            stl_reports.append({"file": group["name"] + ".stl", **report})
    model, model_config, normals, modifiers = build_model(parts, plates, joints, args.title)
    args.out.mkdir(parents=True, exist_ok=True)
    stl_dir = args.out / "STL_parts"
    stl_dir.mkdir(exist_ok=True)
    for name, data in stls.items():
        (stl_dir / (name + ".stl")).write_bytes(data)
    reports = []
    for printer, profile in profiles.items():
        path = args.out / f"{args.stem}_{printer}_NON_AMS.3mf"
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            z.writestr("[Content_Types].xml", CONTENT_TYPES)
            z.writestr("_rels/.rels", RELATIONSHIPS)
            z.writestr("3D/3dmodel.model", model)
            z.writestr("Metadata/model_settings.config", model_config)
            z.writestr("Metadata/project_settings.config", json.dumps(profile, indent=2))
            z.writestr("Metadata/cut_information.xml", '<?xml version="1.0"?><objects/>')
            z.writestr("Metadata/thumbnail.png", preview)
            for i, (large, small) in images.items():
                z.writestr(f"Metadata/plate_{i}.png", large)
                z.writestr(f"Metadata/plate_{i}_small.png", small)
        reports.append(validate_project(path, normals, modifiers, len(plates)))
        (args.out / f"{printer}_profile.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")
    (args.out / "project_validation.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")
    (args.out / "stl_roundtrip.json").write_text(json.dumps(stl_reports, indent=2), encoding="utf-8")
    report = {**summary, "title": args.title, "source_manifest": str(args.manifest.resolve()),
              "source_layout": str(args.layout.resolve()), "plates": plates,
              "parts": [{k: v for k, v in p.items() if k not in ("vertices", "faces")}
                        for p in parts.values()],
              "requires_next": ["Bambu slice each printer", "check all support/brim extrusion paths",
                                "verify zero filament changes and slice warnings", "inspect GUI import when available"],
              "desktop_GUI_import_verified": False, "physical_print_test": False}
    (args.out / "parts_and_plates.json").write_text(json.dumps(report, indent=2, default=serializable), encoding="utf-8")
    print(json.dumps({**summary, "projects": reports}, indent=2))


if __name__ == "__main__":
    main()
