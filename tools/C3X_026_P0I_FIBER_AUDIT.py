#!/usr/bin/env python3
"""C3X P0-I: read-only bounded observational comparison; no chess-engine calls."""
import argparse, collections, hashlib, json
from pathlib import Path

EXPECTED = "18c2f25551a5a929e7cd95ec7c207837a79ea7f5c3df75e96109884ed168b9d2"

def read(path):
    data = Path(path).read_bytes()
    return json.loads(data), hashlib.sha256(data).hexdigest()

def audit(state_path, legal_path):
    s, sh = read(state_path)
    f, fh = read(legal_path)
    assert s["rows"] == f["rows"] == 144
    assert s["unique_arms"] == f["unique_arms"] == 72
    assert s["source_sha256"] == f["input_sha256"] == EXPECTED
    groups = collections.defaultdict(list)
    for row in f["comparisons"]:
        groups[row["index"]].append(row)
    assert len(groups) == 9 and all(len(v) == 4 for v in groups.values())
    cases = {}
    for idx, arr in sorted(groups.items()):
        variants = {json.dumps(r["delta_first_minus_second"], sort_keys=True) for r in arr}
        assert len(variants) == 1, ("noninvariant root feature", idx)
        sample = arr[0]
        overlaps = []
        for row in arr:
            a = {x["reply"] for x in row["rootA"]["reported_replies"]}
            b = {x["reply"] for x in row["rootB"]["reported_replies"]}
            overlaps.append({"mode": row["mode"], "reply_depth": row["reply_depth"],
                             "shared_top2": len(a & b)})
        cases[str(idx)] = {
            "roots": sample["roots"],
            "role": "development" if idx in (42, 43) else "negative_control" if idx in (47, 99) else "other",
            "root_feature_delta": sample["delta_first_minus_second"],
            "reply_top2_overlaps": overlaps}
    return {
        "status": "P0I_BOUNDED_OBSERVATION_NOT_CAUSAL", "source_sha256": EXPECTED,
        "audit_sha256": {"p0_state": sh, "p0f_legal": fh},
        "counts": {"rows": 144, "unique_arms": 72, "positions": 9,
                   "root_pairs_by_mode_depth": 36,
                   "within_board_turn": s["within_two_reply_arms"]["board_turn"],
                   "within_fen4": s["within_two_reply_arms"]["fen4"],
                   "within_fen6": s["within_two_reply_arms"]["fen6"],
                   "between_fen6": s["between_first_root_comparisons"]["fen6"]},
        "cases": cases,
        "boundaries": ["FEN6 equality excludes repetition-history identity",
                       "PV reunion does not imply equivalence of reachable continuations",
                       "Mobility counts and MultiPV2 overlaps are not chess causal reasons",
                       "P10 outcome-selected development cohort, not heldout"]}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--state-audit", required=True)
    p.add_argument("--affordance-audit", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    result = audit(a.state_audit, a.affordance_audit)
    Path(a.output).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print("P0I_PASS 144 72 9 36", a.output)
