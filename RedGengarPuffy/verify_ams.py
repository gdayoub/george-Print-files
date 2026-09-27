"""Validate RedGengarPuffy native projects, geometry, colors, and source fidelity."""
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "GengarPuffco"
N = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
PRODUCTION = "{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}"
checks = json.loads((SOURCE / "Reports" / "geometry_validation.json").read_text())
reports = {}


def transform(value):
    numbers = np.array([float(item) for item in value.split()])
    result = np.eye(4)
    result[:3, :3] = numbers[:9].reshape(3, 3).T
    result[:3, 3] = numbers[9:]
    return result


def expected_extruder(name):
    return "2" if any(token in name for token in ("eyes_red", "grin_pink", "george_red", "bottom_cap_red")) else "1"


for path in sorted((ROOT / "P1S").glob("*.3mf")):
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        model = ET.fromstring(archive.read("3D/3dmodel.model"))
        config = ET.fromstring(archive.read("Metadata/model_settings.config"))
        settings = json.loads(archive.read("Metadata/project_settings.config"))
        slice_report = json.loads((ROOT / "Reports" / path.name.replace("_P1S.3mf", "_slice.json")).read_text())
        assert slice_report["exit_code"] == 0
        assert not slice_report["result"]["sliced_plates"][0]["warning_message"]
        holder = path.name.startswith("03_")
        expected_colors = ["#1C1B26"] if holder else ["#CE1834", "#1C1B26"]
        assert settings["filament_colour"][:len(expected_colors)] == expected_colors, settings["filament_colour"]
        report = {"archive_valid": True, "parts": {}, "originals": {}, "warnings": []}
        for item in model.find("m:build", N):
            matrix = transform(item.get("transform"))
            scale = np.linalg.svd(matrix[:3, :3], compute_uv=False)
            assert np.max(np.abs(scale - 1)) < 1e-6
        for obj in config.findall("object"):
            resource = next(item for item in model.findall("m:resources/m:object", N) if item.get("id") == obj.get("id"))
            for part in obj.findall("part"):
                metadata = {item.get("key"): item.get("value") for item in part.findall("metadata")}
                name = metadata.get("name", "")
                expected = "1" if holder else expected_extruder(name)
                # Bambu omits the redundant part-level extruder for a one-color object.
                assert metadata.get("extruder", expected) == expected, (path, name, metadata.get("extruder"))
                stat = part.find("mesh_stat")
                assert stat is not None
                assert all(int(value) == 0 for key, value in stat.attrib.items() if key != "face_count"), (path, name, stat.attrib)
                if name in checks["new_meshes"]:
                    assert int(stat.get("face_count")) == checks["new_meshes"][name]["triangles"], (path, name)
                report["parts"][name] = {
                    "extruder": int(metadata.get("extruder", expected)),
                    "color": "black" if holder or metadata.get("extruder") == "2" else "red",
                    "triangles": int(stat.get("face_count")),
                    "repairs": {key: int(value) for key, value in stat.attrib.items() if key != "face_count"},
                }
                if not name.startswith("ORIGINAL"):
                    continue
                component = next(item for item in resource.findall("m:components/m:component", N) if item.get("objectid") == part.get("id"))
                submodel = ET.fromstring(archive.read(component.get(PRODUCTION + "path").lstrip("/")))
                subobject = next(item for item in submodel.findall("m:resources/m:object", N) if item.get("id") == part.get("id"))
                mesh = subobject.find("m:mesh", N)
                vertices = np.array([[float(item.get(axis)) for axis in "xyz"] for item in mesh.find("m:vertices", N)])
                faces = mesh.find("m:triangles", N)
                matrix = transform(component.get("transform"))
                vertices = vertices @ matrix[:3, :3].T + matrix[:3, 3]
                role = "base" if "BASE" in name else "lid"
                source = np.load(SOURCE / "Foundations" / f"{role}_exact.npz")
                expected_matrix = np.array(checks[f"{role}_transform"])
                expected = source["vertices"] @ expected_matrix[:3, :3].T + expected_matrix[:3, 3]
                recenter = (expected.min(0) + expected.max(0) - vertices.min(0) - vertices.max(0)) / 2
                if len(obj.findall("part")) > 1:
                    assert np.max(np.abs(recenter)) < 0.0001
                vertices += recenter
                error = float(max(cKDTree(expected).query(vertices)[0].max(), cKDTree(vertices).query(expected)[0].max()))
                assert len(faces) == len(source["faces"])
                assert error < 0.0001
                report["originals"][name] = {
                    "triangles": len(faces),
                    "max_bidirectional_vertex_distance_mm": error,
                    "rigid_build_scale": True,
                }
        assert str(settings["xy_hole_compensation"]) == "0"
        assert str(settings["xy_contour_compensation"]) == "0"
        gcode = archive.read("Metadata/plate_1.gcode").decode(errors="replace")
        heights = [float(item) for item in re.findall(r"; layer height: ([0-9.]+)", gcode)]
        if heights:
            assert max(heights) <= 0.20001
        report["layer_height_values_mm"] = sorted(set(heights))
        report["zero_XY_compensation"] = True
        reports[path.name] = report

(ROOT / "Reports" / "native_verification.json").write_text(json.dumps(reports, indent=2))
print(json.dumps({name: {"parts": data["parts"], "originals": data["originals"]} for name, data in reports.items()}, indent=2))
