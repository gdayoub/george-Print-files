"""Package character homeware meshes as separate non-AMS P1S/P2S projects.

Example:
  python package_homeware.py --manifest PRODUCT/final_parts/manifest.json \
      --layout PRODUCT/layout.json --preview PRODUCT/preview.png \
      --out PRODUCT/packages --stem King_Shark_Bowl --title "King Shark Bowl"

Manifest/layout formats are those used by king_shark_v2/package_v2.py. NPZ mesh
paths may be absolute or relative to the manifest. Each color occupies its own
plate. Instance settings override part settings, which override the defaults.
Set {"enable_support":"0"} on objects designed to print without supports.
Optional --joints uses the existing registration/reinforcement schema; it does
not create or change connectors. No slicing, upload, or publication occurs here.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

import manifold3d as mf
import numpy as np

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
SOURCE = ROOT.parent / "king_shark_v2" / "package_v2.py"
spec = importlib.util.spec_from_file_location("homeware_package_base", SOURCE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

PROCESS_DEFAULTS = {
    "layer_height": "0.28",
    "initial_layer_print_height": "0.2",
    "wall_loops": "3",
    "sparse_infill_pattern": "gyroid",
    "sparse_infill_density": "8%",
    "top_shell_layers": "4",
    "bottom_shell_layers": "4",
    "top_shell_thickness": "1.12",
    "bottom_shell_thickness": "1.12",
    "enable_prime_tower": "0",
    "enable_support": "1",
    "support_type": "tree(auto)",
    "support_threshold_angle": "30",
    "support_top_z_distance": "0.28",
    "support_bottom_z_distance": "0.28",
    "support_object_xy_distance": "0.35",
    "support_filament": "0",
    "support_interface_filament": "0",
    "infill_combination": "0",
    "brim_width": "3",
}


def profile_config(printer, template_dir, palette, process_name):
    profile = base.profile_config(printer, template_dir, palette, process_name)
    profile.update(PROCESS_DEFAULTS)
    profile["process_notes"] = (
        "Character homeware prototype. Standard 0.4 mm nozzle, 0.28 mm layers; "
        "single-color plates with no prime tower. Geometry/plate validation "
        "does not certify structural strength or adhesive mounting capacity."
    )
    profile["different_settings_to_system"] = [";".join(sorted(profile))] * 5
    return profile


def validate_plate_solids(parts, plates):
    """Catch actual part intersections; supports/brims need a subsequent slice."""
    report = []
    for plate in plates:
        solids = []
        for group in plate["groups"]:
            part = parts[group["name"]]
            v = base.transform_vertices(part["vertices"], group["local_transform"])
            lo, hi = v.min(axis=0), v.max(axis=0)
            # Common envelope covers the P1S cutter exclusion as well as P2S.
            base.require(not (lo[0] < 18 and lo[1] < 28),
                         part["name"] + ": intersects conservative P1S front-left exclusion")
            solid = mf.Manifold(mf.Mesh64(np.ascontiguousarray(v), part["faces"]))
            for name, other, olo, ohi in solids:
                if np.all(hi >= olo) and np.all(ohi >= lo):
                    volume = abs((solid ^ other).volume())
                    base.require(volume < .001,
                                 f"Plate {plate['id']}: {name}/{part['name']} overlap {volume:g} mm3")
                    report.append({"plate": plate["id"], "parts": [name, part["name"]],
                                   "intersection_mm3": volume})
            solids.append((part["name"], solid, lo, hi))
    return report


def validate_embedded_meshes(path):
    """Reparse written coordinates and check every normal and modifier mesh."""
    ns = {"m": base.CORE_NS}
    reports = []
    with zipfile.ZipFile(path) as z:
        model = ET.fromstring(z.read("3D/3dmodel.model"))
        settings = ET.fromstring(z.read("Metadata/model_settings.config"))
        types = {p.get("id"): p.get("subtype") for p in settings.findall(".//part")}
        for obj in model.findall("m:resources/m:object", ns):
            mesh = obj.find("m:mesh", ns)
            if mesh is None:
                continue
            v = np.asarray([[float(e.get(k)) for k in ("x", "y", "z")]
                            for e in mesh.findall("m:vertices/m:vertex", ns)], dtype=np.float64)
            f = np.asarray([[int(e.get(k)) for k in ("v1", "v2", "v3")]
                            for e in mesh.findall("m:triangles/m:triangle", ns)], dtype=np.uint64)
            _, _, report = base.checked_mesh(v, f, f"Embedded object {obj.get('id')}")
            reports.append({"object_id": obj.get("id"), "subtype": types.get(obj.get("id")),
                            "watertight": True, "winding_consistent": True, **report})
    return reports


def package(args):
    base.require(re.fullmatch(r"[A-Za-z0-9_-]+", args.stem), "Output stem must be a safe filename")
    base.require(args.preview.is_file(), "--preview must be an existing actual-geometry render")
    parts = base.load_parts(args.manifest)
    layout, plates, palette = base.load_layout(args.layout, parts)
    joints = base.load_joints(args.joints, parts)
    profiles = {p: profile_config(p, args.template_dir, palette, args.process_name)
                for p in base.PROFILE_NAMES}
    intersections = validate_plate_solids(parts, plates)
    preview = base.png_bytes(args.preview, 1200)
    preview_small = base.png_bytes(args.preview, 256)
    images, stls, stl_reports = {}, {}, []
    for plate in plates:
        if plate["preview"] is not None:
            base.require(plate["preview"].is_file(), f"Plate {plate['id']} preview is missing")
        images[plate["id"]] = ((base.png_bytes(plate["preview"], 1200),
                                base.png_bytes(plate["preview"], 256))
                               if plate["preview"] else (preview, preview_small))
        for group in plate["groups"]:
            data, report = base.roundtrip_stl(parts[group["name"]], group)
            stls[group["name"]] = data
            stl_reports.append({"file": group["name"] + ".stl", **report})
    summary = {"parts": len(parts), "plate_count": len(plates), "joints": len(joints),
               "palette": palette, "input_checks_pass": True, "stl_roundtrip_pass": True,
               "nozzle_mm": .4, "process_defaults": PROCESS_DEFAULTS,
               "geometry_repaired_during_export": False,
               "sliced": False, "load_rating_verified": False}
    if args.check_inputs:
        print(json.dumps(summary, indent=2))
        return summary

    # Strong functional default on optional registration modifiers, independently
    # overridable by each joint's reinforcement_settings.
    base.REINFORCE = {"wall_loops": "4", "sparse_infill_pattern": "gyroid",
                      "sparse_infill_density": "20%", "top_shell_layers": "4",
                      "bottom_shell_layers": "4", "top_shell_thickness": "1.12",
                      "bottom_shell_thickness": "1.12"}
    model, model_config, normals, modifiers = base.build_model(parts, plates, joints, args.title)
    model = model.replace(
        b"Separate single-color glue parts. Lightweight shelf process based on the user-tested large Venom. No AMS required.",
        b"Character homeware prototype. Separate single-color plates; no AMS. Mounting load capacity unverified.")
    args.out.mkdir(parents=True, exist_ok=True)
    stl_dir = args.out / "STL_parts"
    stl_dir.mkdir(exist_ok=True)
    for name, data in stls.items():
        (stl_dir / (name + ".stl")).write_bytes(data)
    reports = []
    for printer, profile in profiles.items():
        path = args.out / f"{args.stem}_{printer}_NON_AMS.3mf"
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            z.writestr("[Content_Types].xml", base.CONTENT_TYPES)
            z.writestr("_rels/.rels", base.RELATIONSHIPS)
            z.writestr("3D/3dmodel.model", model)
            z.writestr("Metadata/model_settings.config", model_config)
            z.writestr("Metadata/project_settings.config", json.dumps(profile, indent=2))
            z.writestr("Metadata/cut_information.xml", '<?xml version="1.0"?><objects/>')
            z.writestr("Metadata/thumbnail.png", preview)
            for i, (large, small) in images.items():
                z.writestr(f"Metadata/plate_{i}.png", large)
                z.writestr(f"Metadata/plate_{i}_small.png", small)
        validation = base.validate_project(path, normals, modifiers, len(plates))
        validation["embedded_mesh_checks"] = validate_embedded_meshes(path)
        reports.append(validation)
        (args.out / f"{printer}_profile.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")
    (args.out / "project_validation.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")
    (args.out / "stl_roundtrip.json").write_text(json.dumps(stl_reports, indent=2), encoding="utf-8")
    report = {**summary, "title": args.title, "source_manifest": str(args.manifest.resolve()),
              "source_layout": str(args.layout.resolve()), "actual_mesh_preview": str(args.preview.resolve()),
              "preview_sha256": hashlib.sha256(args.preview.read_bytes()).hexdigest(),
              "plates": plates, "plate_solid_intersections": intersections,
              "parts": [{k: v for k, v in p.items() if k not in ("vertices", "faces")}
                        for p in parts.values()],
              "requires_next": ["slice each printer project", "check all support/brim extrusion paths",
                                "verify zero filament changes and inspect slice warnings"],
              "desktop_GUI_import_verified": False, "physical_print_test": False}
    (args.out / "parts_and_plates.json").write_text(
        json.dumps(report, indent=2, default=base.serializable), encoding="utf-8")
    print(json.dumps({**summary, "projects": reports}, indent=2))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--layout", type=Path, required=True)
    parser.add_argument("--preview", type=Path, required=True, help="Actual mesh render, not a concept image")
    parser.add_argument("--joints", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--template-dir", type=Path, default=PROJECT / "outputs/Venom_lightweight")
    parser.add_argument("--title", default="Character Homeware Prototype")
    parser.add_argument("--stem", default="Character_Homeware")
    parser.add_argument("--process-name", default="Character Homeware Fast 0.28mm Non-AMS")
    parser.add_argument("--check-inputs", action="store_true",
                        help="Validate sources, layout, preview, profiles and STL roundtrip without writing")
    package(parser.parse_args())


if __name__ == "__main__":
    main()
