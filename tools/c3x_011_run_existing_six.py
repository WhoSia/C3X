#!/usr/bin/env python3
"""C3X 0.11: run existing six-PGN custody and FEN audits without outcome access.

Requires python-chess==1.999 and a complete historical JSON corpus at --history-root.
An absent path or any mismatched source fails closed; successful execution is still
AUDIT_ONLY, and never constitutes scientific source preseal.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

SOURCE_NAMES = ("Charlotte","NZ","Golders","Radnicki","Berjaya","Milton")
SOURCE_FILES = {
    "Charlotte":"C3X_G10_P25_Charlotte_Spring_Norm_2026_GM_Lichess_0zfikbXR.pgn",
    "NZ":"NZ.pgn", "Golders":"Golders.pgn", "Radnicki":"Radnicki.pgn",
    "Berjaya":"Berjaya_Masters.pgn", "Milton":"Milton.pgn",
}

def run(args: list[str]) -> None:
    subprocess.run(args, check=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pgn-dir", type=Path, required=True)
    p.add_argument("--history-root", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--expect-history-json-min", type=int, default=1)
    a=p.parse_args()
    if a.expect_history_json_min<1: p.error("INVALID_HISTORY_COVERAGE_LOWER_BOUND")
    if not a.history_root.is_dir(): p.error("HISTORY_ROOT_MISSING")
    historic=[p for p in a.history_root.rglob("*") if p.is_file() and p.suffix.lower() in (".json",".jsonl",".epd")]
    if len(historic)<a.expect_history_json_min:
        p.error("HISTORICAL_WORLD_FILE_INVENTORY_BELOW_PRECOMMITTED_MINIMUM")
    sources = {}
    for name in SOURCE_NAMES:
        path=a.pgn_dir/SOURCE_FILES[name]
        if not path.is_file(): p.error(f"RAW_SOURCE_NOT_FOUND:{name}:{path}")
        sources[name]=path
    a.out_dir.mkdir(parents=True, exist_ok=True)
    here=Path(__file__).resolve().parent
    flags=[f"--source={sid}={sources[sid]}" for sid in SOURCE_NAMES]
    raw=a.out_dir/"raw_custody.json"
    fen=a.out_dir/"historical_fen_collision.json"
    run([sys.executable,str(here/"c3x_011_raw_preflight.py"), *flags,"--out",str(raw)])
    if json.loads(raw.read_text())["verdict"]!="RAW_CUSTODY_PASS_ONLY":
        raise RuntimeError("RAW_CUSTODY_NOT_PASS")
    run([sys.executable,str(here/"c3x_011_fen_collision_audit.py"), *flags,
         "--history-root",str(a.history_root), "--out",str(fen)])
    data=json.loads(fen.read_text())
    if data["source_preseal_granted"] or data["outcomes_opened"]:
        raise RuntimeError("SCIENTIFIC_AUTHORITY_FIREWALL_VIOLATION")
    receipt={
        "stage":"C3X 0.11", "type":"ACTUAL_SIX_SOURCE_PREOUTCOME_AUDIT",
        "raw_custody_verdict":"RAW_CUSTODY_PASS_ONLY",
        "fen_audit_verdict":data["verdict"],
        "historical_world_file_inventory_present":len(historic),
        "history_coverage_certified":False,
        "source_preseal_granted":False,
        "activation_outcomes_opened":False,
        "q0_authority":"DENIED",
        "source_roles":"LOCKED_FROM_P25",
        "artifact_files":["raw_custody.json","historical_fen_collision.json"],
    }
    (a.out_dir/"execution_receipt.json").write_text(
        json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("ACTUAL_SIX_SOURCE_AUDIT_COMPLETED_NOT_PRESEAL",len(historic))
if __name__=="__main__":
    main()
