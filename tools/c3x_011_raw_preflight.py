#!/usr/bin/env python3
"""C3X 0.11 outcome-blind PGN custody preflight. No chess/engine outcomes."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

EXPECTED = {
    "Charlotte": ("642da2f6fe6e6989af299c603056b3e821bc8c4001d53561ff10be5a06a52028", "calibration"),
    "NZ": ("32475990f7c7a62a73379104189c61628a4b2014ddb287ad125c0b2a372993f8", "calibration"),
    "Golders": ("596374245025a1eee7242b451c12014d7d5f1f9ccfaf1f5625329a0945b59a57", "calibration"),
    "Radnicki": ("2f2a9a9608418d831e6bdcfc71b586abd1472af7fafca14fd9e5d8e2af3716ae", "transfer"),
    "Berjaya": ("a6778cfea89596cbe9ebf2a45c594c352a2e279f3cd9c1fc04ead9dc20625ba9", "transfer"),
    "Milton": ("c0e8e8a322d8e444824168dcd3c47283b7bce66e9041b30cc92b7e2a4d52a19e", "transfer"),
}
TAG = re.compile(r'^\[([A-Za-z][A-Za-z0-9_]*)\s+"((?:\\.|[^"\\])*)"\]\s*$')
REQUIRED = ("Event", "White", "Black", "Result")
def inspect(path: Path):
    digest = hashlib.sha256()
    count = 0
    missing = []
    headers = {}
    issues = []
    begun = False
    def finish():
        nonlocal count, headers, begun
        if begun:
            count += 1
            absent = [x for x in REQUIRED if not headers.get(x)]
            if absent:
                missing.append({"game": count, "missing": absent})
            headers = {}
            begun = False
    with path.open("rb") as f:
        for raw in f:
            digest.update(raw)
            line = raw.decode("utf-8-sig", errors="replace").strip()
            if line.startswith("[") and line.endswith("]"):
                match = TAG.fullmatch(line)
                if match:
                    key, val = match.groups()
                    if key == "Event" and begun and headers.get("Event"):
                        finish()
                    headers[key] = val
                    begun = True
                else:
                    issues.append("MALFORMED_TAG")
    finish()
    return {"sha256": digest.hexdigest(), "game_header_blocks": count,
            "required_header_missing": missing[:20], "malformed_tag_count": len(issues)}
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", action="append", required=True, help="SOURCE_ID=PATH")
    p.add_argument("--out", required=True)
    a = p.parse_args()
    if len(a.source) != len(EXPECTED):
        p.error("EXACT_SIX_SOURCES_REQUIRED")
    results = {}
    for arg in a.source:
        sid, sep, location = arg.partition("=")
        if not sep or sid not in EXPECTED or sid in results:
            p.error("UNKNOWN_OR_DUPLICATE_SOURCE")
        record = inspect(Path(location))
        record["role"] = EXPECTED[sid][1]
        record["raw_bytes_sha256_match"] = (record["sha256"] == EXPECTED[sid][0])
        results[sid] = record
    custody_pass = all(r["raw_bytes_sha256_match"] and
                      not r["required_header_missing"] and
                      r["malformed_tag_count"] == 0 for r in results.values())
    report = {"schema": "c3x-0.11-raw-preflight-v1", "legacy": "G10-P26",
              "verdict": "RAW_CUSTODY_PASS_ONLY" if custody_pass else "RAW_CUSTODY_HOLD",
              "source_roles_inherited": True, "outcomes_opened": False,
              "legal_san_verified": False, "historical_fen_disjointness_verified": False,
              "source_preseal_granted": False, "sources": results}
    Path(a.out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(report["verdict"], sum(r["game_header_blocks"] for r in results.values()))
    if not custody_pass:
        raise SystemExit(2)
if __name__ == "__main__":
    main()
