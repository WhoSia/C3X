#!/usr/bin/env python3
"""P25 outcome-blind cross-source collision ledger; descriptive only."""
import argparse
import json
from collections import defaultdict
from pathlib import Path

def audit(rows, historical):
    owners = defaultdict(set)
    source_sizes = {}
    for row in rows:
        source = row["source_id"]
        if source in source_sizes:
            raise ValueError("DUPLICATE_SOURCE_ID")
        hashes = set(row["canonical_fen_hashes"])
        source_sizes[source] = len(hashes)
        for value in hashes:
            owners[value].add(source)
    overlaps = {h: sorted(s) for h, s in owners.items() if len(s) > 1}
    excluded = {h for h in owners if h in historical}
    return {
        "schema": "c3x-g10-p25-cross-source-collision-ledger-v1",
        "authority": "PREOUTCOME_DESCRIPTIVE_FEN_AUDIT_ONLY",
        "legacy_fen_exclusion_changed": False,
        "activation_outcomes_opened": False,
        "sources": source_sizes,
        "historical_fen_collision_count": len(excluded),
        "cross_source_fen_collision_count": len(overlaps),
        "cross_source_fen_owners": overlaps,
        "tier_T": "NOT_MEASURED",
        "tier_W": "NOT_MEASURED",
        "verdict": "AUDIT_ONLY_NO_SOURCE_PRESEAL"
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--inventory",action="append",required=True,help="SOURCE_ID|JSON")
    p.add_argument("--historical",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    rows=[]
    for spec in a.inventory:
        sid,path=spec.split("|",1)
        record=json.loads(Path(path).read_text())
        record["source_id"]=sid
        rows.append(record)
    historical=set(Path(a.historical).read_text().splitlines())
    result=audit(rows,historical)
    Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("P25_FEN_LEDGER",result["cross_source_fen_collision_count"])

if __name__=="__main__":
    main()
