"""Package the revised shorts without modifying any original King Shark files.

This writes complete nine-part projects and a one-part replacement project for
each printer. Geometry and the three shorts reinforcement volumes are shared.
Actual revised renders are used when available; fallback thumbnails are logged.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parent
ORIGINAL = ROOT.parent / "king_shark_v2"
SLICE_ENTRIES = ("3D/3dmodel.model", "Metadata/model_settings.config",
                 "Metadata/project_settings.config")
sys.path.insert(0, str(ORIGINAL))
import package_v2 as p


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, default=p.serializable), encoding="utf-8")


def slice_entry_hashes(path):
    if not path.is_file():
        return None
    with zipfile.ZipFile(path) as z:
        return {name: hashlib.sha256(z.read(name)).hexdigest() for name in SLICE_ENTRIES}


def choose_image(candidates, fallback, image_log, use):
    chosen = next((path for path in candidates if path.is_file()), fallback)
    image_log.append({"use": use, "file": str(chosen),
                      "revised_render": chosen != fallback})
    return chosen


def write_project(path, model, config, profile, previews, cover):
    temporary = path.with_suffix(".building.3mf")
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.writestr("[Content_Types].xml", p.CONTENT_TYPES)
        z.writestr("_rels/.rels", p.RELATIONSHIPS)
        z.writestr("3D/3dmodel.model", model)
        z.writestr("Metadata/model_settings.config", config)
        z.writestr("Metadata/project_settings.config", json.dumps(profile, indent=2))
        z.writestr("Metadata/cut_information.xml", '<?xml version="1.0"?><objects/>')
        z.writestr("Metadata/thumbnail.png", p.png_bytes(cover, 1200))
        for index, preview_path in previews.items():
            z.writestr(f"Metadata/plate_{index}.png", p.png_bytes(preview_path, 1200))
            z.writestr(f"Metadata/plate_{index}_small.png", p.png_bytes(preview_path, 256))
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "packages")
    parser.add_argument("--renders", type=Path, default=ROOT / "renders")
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "STL_parts").mkdir(exist_ok=True)
    parts = p.load_parts(ROOT / "final_parts/manifest.json")
    joints = p.load_joints(ROOT / "final_parts/joints.json", parts)
    assert len(parts) == 9 and parts["Shorts"]["color"] == "Red"
    assert parts["Shorts"]["settings"] == {
        "sparse_infill_pattern": "gyroid", "sparse_infill_density": "3%"}

    images = []
    cover = choose_image([args.renders / "assembly_all_red_shorts.png",
                          args.renders / "three_quarter.png", args.renders / "front.png"],
                         ORIGINAL / "renders/three_quarter.png", images, "assembly")
    layout = copy.deepcopy(p.read_json(ORIGINAL / "layout.json"))
    layout.update(status="Revised all-red shorts; pending fresh slicing checks",
                  source_parts=str(ROOT / "final_parts"),
                  notes=["Nine non-AMS parts. The original torso, arms, legs, fin and teeth are unchanged.",
                         "Shorts are a single red solid, with 3% Gyroid and original joint reinforcements.",
                         "Original shorts side panels are no longer needed.",
                         "Only the enlarged shorts have been recentered; other plate positions are unchanged."])
    layout.pop("selection_evidence", None)
    layout.pop("verification_report", None)
    for index, plate in enumerate(layout["plates"], 1):
        plate["instances"] = [inst for inst in plate["instances"]
                              if not inst["name"].startswith("Shorts_panel_")]
        if index == 4:
            plate["label"] = "Original legs and dorsal fin"
        if index == 5:
            plate["label"] = "Replacement all-red shorts / hems down"
            instance = plate["instances"][0]
            assert instance["name"] == "Shorts"
            rotated = parts["Shorts"]["vertices"] @ np.asarray(instance["rotation"]).T
            instance["xy_mm"] = ((256 - np.ptp(rotated, axis=0)[:2]) / 2).tolist()
        fallback = ORIGINAL / f"renders/plate_{index}.png"
        candidates = [args.renders / f"plate_{index}.png"]
        if index == 4:
            candidates.append(args.renders / "assembly_all_red_shorts.png")
        elif index == 5:
            candidates.append(args.renders / "shorts_waist_key.png")
        image = choose_image(candidates, fallback,
                             images, f"full_plate_{index}")
        plate["preview"] = str(image)
    save_json(ROOT / "layout.json", layout)
    _, plates, palette = p.load_layout(ROOT / "layout.json", parts)

    original_parts = p.load_parts(ORIGINAL / "final_parts/manifest.json")
    _, original_plates, _ = p.load_layout(ORIGINAL / "layout.json", original_parts)
    original_groups = {g["name"]: g for plate in original_plates for g in plate["groups"]}
    preserved = []
    stl_reports = []
    for plate in plates:
        for group in plate["groups"]:
            name = group["name"]
            if name != "Shorts":
                assert parts[name]["source_sha256"] == original_parts[name]["source_sha256"]
                assert np.array_equal(group["local_transform"], original_groups[name]["local_transform"])
                assert group["settings"] == original_groups[name]["settings"]
                preserved.append(name)
            data, report = p.roundtrip_stl(parts[name], group)
            (out / "STL_parts" / f"{name}.stl").write_bytes(data)
            stl_reports.append({"file": f"{name}.stl", **report})

    shorts_plate = copy.deepcopy(next(plate for plate in plates if plate["id"] == 5))
    shorts_plate.update(id=1, origin=[0., 0., 0.], label="ALL RED SHORTS / replacement only")
    for group in shorts_plate["groups"]:
        group.update(plate=1, transform=group["local_transform"].copy())
    shorts_cover = choose_image([args.renders / "shorts_waist_key.png",
                                args.renders / "shorts.png", args.renders / "plate_5.png"],
                               ORIGINAL / "renders/plate_5.png", images, "shorts_only")
    shorts_plate["preview"] = shorts_cover
    save_json(ROOT / "shorts_only_layout.json", {
        "bed_margin_mm": 3, "max_height_mm": 250, "palette": palette,
        "plates": [{"label": shorts_plate["label"], "preview": str(shorts_cover),
                    "instances": copy.deepcopy(layout["plates"][4]["instances"])}]})

    project_reports = []
    variants = [("King_Shark_ALL_RED_SHORTS_ONLY", {"Shorts": parts["Shorts"]}, [shorts_plate],
                 "King Shark all-red replacement shorts - original body fit", shorts_cover),
                ("King_Shark_47cm_ALL_RED_SHORTS_FULL", parts, plates,
                 "King Shark 47cm - all-red shorts, complete nine-part project", cover)]
    for stem, selected_parts, selected_plates, title, thumbnail in variants:
        model, config, normals, modifiers = p.build_model(selected_parts, selected_plates, joints, title)
        if "ONLY" in stem:
            assert normals == 1 and modifiers == 3
        else:
            assert normals == 9 and modifiers == sum(
                2 for j in joints if j.get("reinforce", True))
        for printer in p.PROFILE_NAMES:
            profile = p.profile_config(printer, p.PROJECT / "outputs/Venom_lightweight", palette,
                                       "King Shark Shelf 0.20mm - red shorts 3% Gyroid")
            if "ONLY" in stem:
                profile.update(sparse_infill_pattern="gyroid", sparse_infill_density="3%")
                profile["different_settings_to_system"] = [";".join(sorted(profile))] * 5
            assert profile["wall_loops"] == "2"
            dest = out / f"{stem}_{printer}_NON_AMS.3mf"
            prior_slice_entries = slice_entry_hashes(dest)
            if prior_slice_entries is not None:
                generated = dict(zip(SLICE_ENTRIES, (model, config,
                    json.dumps(profile, indent=2).encode("utf-8"))))
                assert prior_slice_entries == {
                    name: hashlib.sha256(data).hexdigest() for name, data in generated.items()}, \
                    "Existing slicing inputs changed; do not replace a project during slicing"
            write_project(dest, model, config, profile,
                          {plate["id"]: plate["preview"] for plate in selected_plates}, thumbnail)
            report = p.validate_project(dest, normals, modifiers, len(selected_plates))
            report.update(scope="replacement shorts only" if "ONLY" in stem else "complete project",
                          shorts_sparse_pattern="gyroid", shorts_sparse_density="3%",
                          body_fit_geometry_unchanged=True,
                          previous_slice_entry_sha256=prior_slice_entries,
                          slice_entry_sha256=slice_entry_hashes(dest),
                          only_thumbnails_changed=prior_slice_entries is not None)
            project_reports.append(report)
            print(f"READY: {dest}", flush=True)
    save_json(out / "project_validation.json", project_reports)
    save_json(out / "stl_roundtrip.json", stl_reports)
    save_json(out / "parts_and_plates.json", {
        "parts": [{k: v for k, v in part.items() if k not in ("vertices", "faces")}
                  for part in parts.values()],
        "plates": plates, "shorts_only_plate": shorts_plate,
        "unchanged_geometry_positions_and_settings": preserved,
        "thumbnail_sources": images,
        "temporary_old_thumbnails_need_replacement": any(
            not row["revised_render"] for row in images
            if row["use"] in {"assembly", "full_plate_4", "full_plate_5", "shorts_only"}),
        "sliced": False})
    print(json.dumps({"projects": project_reports, "unchanged_parts": preserved,
                      "shorts_print_dimensions_mm": shorts_plate["groups"][0]["dimensions_mm"],
                      "thumbnail_sources": images}, indent=2))


if __name__ == "__main__":
    main()
