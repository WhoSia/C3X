"""Retrospective coverage-only audit of source-observed TT move hints.

Never count a newly selectable event as a successful source intervention.
"""
import argparse
from collections import Counter
import json
from pathlib import Path


def parse_ply_one(lines):
    rows = []
    for line in lines:
        if not line.startswith("C3X_R29_PLY1 "):
            continue
        parts = line.split()[1:]
        if any("=" not in part for part in parts):
            raise ValueError("Malformed native trace")
        row = dict(part.split("=", 1) for part in parts)
        required = {"seq", "attempt", "root", "hit", "hint", "excluded"}
        if len(row) != len(parts) or not required <= row.keys():
            raise ValueError("Incomplete or duplicate trace fields")
        rows.append(row)
    return rows


def nominate(case, rows):
    foil = case["source"]["alternative"]
    producer = int(case["source_attempt"])
    eligible = [row for row in rows if row["root"] == foil and row["hit"] == "1"
                and row["excluded"] == "0" and row["hint"] not in ("(none)", "0000")
                and int(row["attempt"]) <= producer]
    if not eligible:
        return None
    # Producing attempt first, otherwise latest earlier attempt.
    # Physical sequence breaks same-attempt ties; never select by observed effect.
    latest = max(int(row["attempt"]) for row in eligible)
    chosen = min((row for row in eligible if int(row["attempt"]) == latest),
                 key=lambda row: int(row["seq"]))
    return {"seq": chosen["seq"], "attempt": latest, "hint": chosen["hint"],
            "root": chosen["root"], "same_original_producer": latest == producer,
            "candidate_count": len(eligible)}


def coverage(unseen, abstentions, folder):
    by_id = {case["id"]: case for case in unseen["positions"]}
    if len(by_id) != len(unseen["positions"]):
        raise ValueError("Duplicate cases")
    rows, counts = [], Counter()
    for record in abstentions:
        case = by_id[record["case"]]
        if case["arms"]:
            raise ValueError("Cannot re-nominate an already tested case")
        path = folder / case["id"] / "sham" / "stderr.txt"
        chosen = nominate(case, parse_ply_one(path.read_text().splitlines()))
        counts["abstained"] += 1
        if chosen:
            counts["potential_new_events"] += 1
            if case["stratum"] == "depth-reversal":
                counts["depth_reversal_covered"] += 1
        rows.append({"case": case["id"], "stratum": case["stratum"],
                     "old_independent_reply": case["independent_reply"],
                     "source_observed_candidate": chosen,
                     "intervention_executed": False, "effect_observed": None})
    return {"status": "RETROSPECTIVE COVERAGE ONLY, NO NEW MASK REPLAY",
            "counts": dict(counts), "cases": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("unseen_result", "abstentions", "log_folder", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    result = coverage(json.loads(args.unseen_result.read_text()),
                      json.loads(args.abstentions.read_text()), args.log_folder)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
