"""Build the two-color RedGengarPuffy geometry and native P1S AMS projects."""
from pathlib import Path
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "GengarPuffco"
GEOMETRY = ROOT / "Geometry"
P1S = ROOT / "P1S"
REPORTS = ROOT / "Reports"
WORK = ROOT / "slice_work"
for directory in (GEOMETRY, P1S, REPORTS, WORK):
    directory.mkdir(parents=True, exist_ok=True)

CORE_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
ET.register_namespace("", CORE_NS)
Q = lambda name: f"{{{CORE_NS}}}{name}"

JOBS = {
    "01_RED_BODY_AMS": "01_BODY_EXACT_FOUNDATION.3mf",
    "02_RED_HEAD_AMS": "02_GENGAR_HEAD_COLOR.3mf",
    "03_BLACK_DAB_HOLDER": "03_BOTTOM_CAP.3mf",
}
FAST = "--fast" in sys.argv
if FAST:
    JOBS = {
        "01_RED_BODY_FAST_AMS": "01_BODY_EXACT_FOUNDATION.3mf",
        "02_RED_HEAD_FAST_AMS": "02_GENGAR_HEAD_COLOR.3mf",
        "03_BLACK_DAB_HOLDER_FAST": "03_BOTTOM_CAP.3mf",
    }


def is_black_accent(name):
    return any(token in name for token in ("eyes_red", "grin_pink", "george_red", "bottom_cap_red"))


def remap_archive(source, target, holder=False):
    with zipfile.ZipFile(source) as archive:
        content = {name: archive.read(name) for name in archive.namelist()}

    model = ET.fromstring(content["3D/3dmodel.model"])
    materials = model.find(f".//{Q('basematerials')}")
    bases = materials.findall(Q("base"))
    palette = (("Black", "#1C1B26FF"), ("Black", "#1C1B26FF"), ("Black", "#1C1B26FF")) if holder else (("Red", "#CE1834FF"), ("Black", "#1C1B26FF"), ("Black", "#1C1B26FF"))
    for base, (name, color) in zip(bases, palette):
        base.set("name", name)
        base.set("displaycolor", color)
    for obj in model.findall(f".//{Q('object')}"):
        name = obj.get("name", "")
        if obj.get("pindex") is not None:
            obj.set("pindex", "0" if holder else "1" if is_black_accent(name) else "0")
    content["3D/3dmodel.model"] = ET.tostring(model, encoding="utf-8", xml_declaration=True)

    config = ET.fromstring(content["Metadata/model_settings.config"])
    for part in config.findall(".//part"):
        metadata = {item.get("key"): item for item in part.findall("metadata")}
        name = metadata.get("name").get("value", "") if metadata.get("name") is not None else ""
        if metadata.get("extruder") is not None:
            metadata["extruder"].set("value", "1" if holder else "2" if is_black_accent(name) else "1")
    content["Metadata/model_settings.config"] = ET.tostring(config, encoding="utf-8", xml_declaration=True)

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in content.items():
            archive.writestr(name, data)
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None


for output_name, source_name in JOBS.items():
    remap_archive(SOURCE / "Print" / "Geometry" / source_name, GEOMETRY / f"{output_name}.3mf", holder=output_name.startswith("03_"))
if not FAST:
    remap_archive(
        SOURCE / "Print" / "Geometry" / "ASSEMBLED_VIEW_ONLY.3mf",
        GEOMETRY / "ASSEMBLED_RED_BLACK_VIEW_ONLY.3mf",
    )

if len(sys.argv) < 2:
    print("Geometry generated. Pass the Bambu Studio executable to also create native AMS projects.")
    raise SystemExit(0)

slicer = Path(sys.argv[1]).resolve()
profiles = SOURCE / "Profiles"
summaries = {}
for job in JOBS:
    work = WORK / job
    work.mkdir(exist_ok=True)
    machine = json.loads((profiles / "machine.json").read_text())
    process = json.loads((profiles / "baseline_process.json").read_text())
    process.update({
        "name": "RedGengarPuffy Fast AMS 0.28" if FAST else "RedGengarPuffy AMS 0.20",
        "print_settings_id": "RedGengarPuffy Fast AMS 0.28" if FAST else "RedGengarPuffy AMS 0.20",
        "layer_height": "0.28" if FAST else "0.20",
        "initial_layer_print_height": "0.24" if FAST else "0.2",
        "wall_loops": "3" if FAST else "4",
        "sparse_infill_density": "5%" if FAST else "8%",
        "sparse_infill_pattern": "gyroid",
        "top_shell_layers": "5" if FAST else "6",
        "bottom_shell_layers": "5" if FAST else "6",
        "top_shell_thickness": "1.2",
        "bottom_shell_thickness": "1.2",
        "enable_prime_tower": "1" if job.endswith("AMS") else "0",
        "print_sequence": "by layer",
        "enable_support": "1" if job.endswith("AMS") else "0",
        "support_type": "tree(auto)",
        "support_style": "default",
        "support_threshold_angle": "30" if FAST else "25",
        "support_on_build_plate_only": "1",
        "support_top_z_distance": "0.2",
        "support_bottom_z_distance": "0.2",
        "brim_type": "outer_only" if job.endswith("AMS") else "auto_brim",
        "brim_width": "5",
        "brim_object_gap": "0.15",
        "elefant_foot_compensation": "0.15",
        "xy_hole_compensation": "0",
        "xy_contour_compensation": "0",
        "enable_arc_fitting": "0",
        "flush_into_infill": "1" if FAST else "0",
        "flush_into_support": "1",
    })
    machine_path = work / "machine.json"
    process_path = work / "process.json"
    machine_path.write_text(json.dumps(machine))
    process_path.write_text(json.dumps(process))
    filament_paths = []
    colors = ("#1C1B26",) if job.startswith("03_") else ("#CE1834", "#1C1B26")
    for index, color in enumerate(colors):
        filament = json.loads((profiles / "filament_1.json").read_text())
        filament.update({
            "filament_colour": [color],
            "filament_max_volumetric_speed": ["12"],
            "nozzle_temperature": ["220"],
            "nozzle_temperature_initial_layer": ["220"],
            "additional_cooling_fan_speed": ["30"],
            "filament_retract_when_changing_layer": ["nil"],
        })
        path = work / f"filament_{index}.json"
        path.write_text(json.dumps(filament))
        filament_paths.append(str(path))
    target = P1S / f"{job}_P1S.3mf"
    args = [
        str(slicer), str(GEOMETRY / f"{job}.3mf"),
        "--load-settings", f"{machine_path};{process_path}",
        "--load-filaments", ";".join(filament_paths),
        "--curr-bed-type", "Textured PEI Plate",
        "--arrange", "1", "--slice", "0", "--debug", "2",
        "--export-3mf", str(target),
    ]
    result = subprocess.run(args, cwd=work, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=900)
    (work / "slicer.log").write_bytes(result.stdout + b"\n" + result.stderr)
    detail = json.loads((work / "result.json").read_text()) if (work / "result.json").exists() else {}
    report = {
        "exit_code": result.returncode,
        "result": detail,
        "filament_order": ["red", "black"],
        "settings": {"layer_mm": 0.28 if FAST else 0.2, "walls": 3 if FAST else 4, "infill": "5% gyroid" if FAST else "8% gyroid", "XY_compensation_mm": 0},
    }
    if result.returncode == 0 and target.exists():
        with zipfile.ZipFile(target) as archive:
            assert archive.testzip() is None
            gcode = archive.read("Metadata/plate_1.gcode").decode(errors="replace")
            report["gcode_summary"] = {
                key: (match.group(1) if (match := re.search(pattern, gcode)) else None)
                for key, pattern in {
                    "time": r"total estimated time: ([^\n]+)",
                    "filament_g": r"total filament weight \[g\] : ([^\n]+)",
                    "layers": r"; total layer number: (\d+)",
                }.items()
            }
    (REPORTS / f"{job}_slice.json").write_text(json.dumps(report, indent=2))
    if result.returncode != 0:
        raise RuntimeError(f"Slice failed for {job}; inspect {work / 'slicer.log'}")
    summaries[job] = report["gcode_summary"]
    print(job, report["gcode_summary"], flush=True)
(REPORTS / ("slice_summary_fast.json" if FAST else "slice_summary.json")).write_text(json.dumps(summaries, indent=2))
