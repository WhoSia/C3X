#!/usr/bin/env python3
"""Recover immutable C3X source-only JSON inputs for I10-P6-R3 auditing.

This script reads prior GitHub Actions artifacts. It never invokes an engine.
"""
from __future__ import annotations

import hashlib
import io
import json
import subprocess
import zipfile
from pathlib import Path


REPO = "WhoSia/C3X"
SOURCES = [
    ("october", 37981820261, "C3X018_INDEPENDENT_BLIND16_PGN_SOURCE.json", "6520672aabab7f525872169085f19bdd81e27a4473f0c58ba9c9aa428937104c"),
    ("november", 37985213908, "C3X018_NOVEMBER_12_BLIND_GAMES.json", "2971fe617f39fbba6d40fb0b09d8a18ce247d5865dc807fcdab9a594e3473402"),
    ("december", 37987794988, "C3X018_DECEMBER12_INDEPENDENT_GAMES.json", "51366a480fe2631005dbded7992e870443ef6dd2dfd785fd10952d6eeff5e7cd"),
    ("january", 37991871987, "C3X018_JAN26_BLIND16_SOURCE.json", "5b49818e4678c12d0e5e73eba39eff2d50742b070a0ed870cba1d3e94afe0533"),
    ("february", 37998190878, "C3X019_FEB26_BLIND16_SOURCE.json", "2942b1933030227f36b669faff41f15ff234c27127dbf2403bf2e8e4f12ebdc8"),
    ("march", 38038059013, "C3X020_C2_MARCH_BLIND16_SOURCE.json", "d79e48633be2b683176f1a6d4650aeea1b7584f11c85c2349a5bddda113febee"),
    ("april", 38045636805, "C3X022_P0_APRIL16_SOURCE.json", "0e5516fc0cd49203bf7cc366f4133d6c9b20a2f21de0667468f121e398d2fa93"),
    ("twic1656puzzles", 38047000932, "C3X022_P2_TWIC1656_PUZZLE_SOURCE32.json", "ebe6648f43f64c6f31e0d547845bec3d87c663093fd68298acf2ebe4c0287554"),
    ("twic1664", 38050910527, "C3X022_P2_R1_TWIC1664_BLIND16_SOURCE.json", "3cc4c788eec55960921e653604b2fbb3113163862e2652271b939fb12fb9eeb3"),
    ("may2026puzzles", 38059784922, "C3X023_P1_MAY_BROADCAST_CC0_NONMATE32_SOURCE_ONLY.json", "0ff43e28dcb3a5e48dea6b61e4450fc8bb9e1f96363871c33c4b73524664db61"),
    ("august2025", 38075786357, "C3X024_P0_AUG2025_ENGINEBLIND_16.json", "76391058cae1fad8d23e3ae8556e48b63a0d991a051c59fef2df15e11c73f529"),
    ("september2025", 38079947147, "C3X024_P3_SEPT2025_ENGINEBLIND_128.json", "ee8265f96b055645428f2fa87b36647e1931c86c848db5725a8b0ec63596dacb"),
    ("july2025", 38083154595, "C3X024_P4_JULY2025_ENGINEBLIND_256.json", "d2c50a1293e68c3feb8571d1ee1be6ba1a7ee539a12dd1a98378adfa9b54fb58"),
]


def gh_json(url: str) -> object:
    result = subprocess.run(["gh", "api", url], check=True, capture_output=True)
    return json.loads(result.stdout)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    rows = []
    failures = []
    for name, run_id, filename, expected in SOURCES:
        try:
            metadata = gh_json(f"repos/{REPO}/actions/runs/{run_id}/artifacts")
            matches = [a for a in metadata["artifacts"] if filename in str(a["name"]) or a["name"].startswith("c3x-")]
            found = None
            for artifact in matches:
                raw_zip = subprocess.run(
                    ["gh", "api", f"repos/{REPO}/actions/artifacts/{artifact['id']}/zip"],
                    check=True,
                    capture_output=True,
                ).stdout
                with zipfile.ZipFile(io.BytesIO(raw_zip)) as archive:
                    members = [m for m in archive.namelist() if Path(m).name == filename]
                    if len(members) != 1:
                        continue
                    raw_json = archive.read(members[0])
                if sha(raw_json) == expected:
                    found = (artifact, raw_json, raw_zip)
                    break
            if found is None:
                raise ValueError("PINNED_JSON_NOT_FOUND_IN_RUN")
            artifact, raw_json, raw_zip = found
            (args.out / filename).write_bytes(raw_json)
            (args.out / f"{name}_artifact_{artifact['id']}.zip").write_bytes(raw_zip)
            rows.append({"name": name, "run_id": run_id, "artifact_id": artifact["id"],
                         "json_file": filename, "json_sha256": sha(raw_json),
                         "zip_sha256": sha(raw_zip)})
            print(name, artifact["id"], "VERIFIED", flush=True)
        except Exception as exc:
            failures.append({"name": name, "run_id": run_id, "error": str(exc)})
            print(name, "FAILED", str(exc), flush=True)
    p4 = args.repo_root / "c3x/cohorts/c3x-016-P4-12-independent-Lichess-legal-root-order-sourceonly-frozen.json"
    if not p4.is_file():
        failures.append({"name": "p4", "error": "COMMITTED_SOURCE_MISSING"})
    else:
        raw = p4.read_bytes()
        actual_blob = subprocess.run(["git", "hash-object", str(p4)], check=True,
                                     capture_output=True, text=True).stdout.strip()
        if actual_blob != "b0634c9f65ce31e4eb3f29d73fe77b84cdb5b7df":
            failures.append({"name": "p4", "error": "PINNED_GIT_BLOB_MISMATCH", "actual": actual_blob})
        (args.out / "P4_SOURCE.json").write_bytes(raw)
        rows.append({"name": "p4", "json_file": "P4_SOURCE.json", "json_sha256": sha(raw),
                     "git_blob_sha": actual_blob})
    index = {"schema": "c3x-i10-p6-r3-history-inventory-v1", "sources": rows,
             "failures": failures, "complete_14_parent_sources": len(rows) == 14 and not failures}
    (args.out / "history_index.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n")
    print("HISTORY_INVENTORY", len(rows), "failures", len(failures))


if __name__ == "__main__":
    main()
