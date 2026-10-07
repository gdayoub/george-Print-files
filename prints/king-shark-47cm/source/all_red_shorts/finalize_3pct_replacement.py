"""Finalize only the independently reviewed 3% waist-down replacement shorts."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import package_red_shorts as base
p = base.p

out = ROOT / "final_3pct"
out.mkdir(exist_ok=True)
source = ROOT / "trials/Shorts_P1S_trial_waist_down.3mf"
source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
source_entries = base.slice_entry_hashes(source)
dest_p1s = out / "King_Shark_ALL_RED_SHORTS_ONLY_P1S_NON_AMS.3mf"
shutil.copyfile(source, dest_p1s)
assert hashlib.sha256(dest_p1s.read_bytes()).hexdigest() == source_sha

dest_p2s = out / "King_Shark_ALL_RED_SHORTS_ONLY_P2S_NON_AMS.3mf"
profile = p.profile_config("P2S", p.PROJECT / "outputs/Venom_lightweight", p.DEFAULT_PALETTE,
                           "King Shark Shelf 0.20mm - red shorts 3% Gyroid")
profile.update(sparse_infill_pattern="gyroid", sparse_infill_density="3%")
profile["different_settings_to_system"] = [";".join(sorted(profile))] * 5
with zipfile.ZipFile(source) as zin, zipfile.ZipFile(dest_p2s, "w", zipfile.ZIP_DEFLATED,
                                                  compresslevel=6) as zout:
    for info in zin.infolist():
        data = (json.dumps(profile, indent=2).encode("utf-8")
                if info.filename == "Metadata/project_settings.config" else zin.read(info.filename))
        zout.writestr(info.filename, data)
assert all(base.slice_entry_hashes(dest_p2s)[key] == source_entries[key]
           for key in base.SLICE_ENTRIES[:2])
reports = []
for printer, path in [("P1S", dest_p1s), ("P2S", dest_p2s)]:
    report = p.validate_project(path, 1, 3, 1)
    report.update(printer=printer, scope="replacement shorts only", sparse_infill_density="3%",
                  sparse_infill_pattern="gyroid", orientation="waist_down",
                  slice_entry_sha256=base.slice_entry_hashes(path),
                  source_P1S_trial_file=str(source), source_P1S_trial_sha256=source_sha,
                  source_P1S_trial_slice_entry_sha256=source_entries,
                  exact_copy_of_sliced_P1S_trial=printer == "P1S",
                  source_geometry_and_three_joint_modifiers_unchanged=True)
    reports.append(report)
    print(f"READY: {path}", flush=True)
base.save_json(out / "project_validation.json", reports)

parts = p.load_parts(ROOT / "final_parts/manifest.json")
layout_path = out / "layout.json"
shutil.copyfile(ROOT / "trials/waist_down_layout.json", layout_path)
_, plates, _ = p.load_layout(layout_path, {"Shorts": parts["Shorts"]})
stl_data, stl_report = p.roundtrip_stl(parts["Shorts"], plates[0]["groups"][0])
(out / "Shorts.stl").write_bytes(stl_data)
base.save_json(out / "stl_roundtrip.json", [{"file": "Shorts.stl", **stl_report}])
base.save_json(out / "source_trial_proof.json", {
    "source_file": str(source), "source_sha256": source_sha,
    "final_P1S_file": str(dest_p1s), "final_P1S_sha256": reports[0]["sha256"],
    "exact_archive_copy": True, "source_slice_entry_sha256": source_entries,
    "final_P1S_slice_entry_sha256": reports[0]["slice_entry_sha256"],
    "P2S_only_changed_archive_entry": "Metadata/project_settings.config"})
print("Validation and STL complete", flush=True)
