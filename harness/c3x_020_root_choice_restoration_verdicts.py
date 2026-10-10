#!/usr/bin/env python3
"""C3X020 read-only classification of frozen C3X019 K1-K7 receipt.

No engine replay, no extrapolation, no counterfactual mediation claim.
"""
import argparse
import hashlib
import json
from pathlib import Path

EXPECTED = {
    3: ("STRICT", "a1c1", "e1e3"),
    6: ("STRICT", "g2g4", "e3d2"),
    7: ("BROAD", "g8e7", "e8f7"),
    10: ("STRICT", "d8b8", "b7a6"),
}
EXPECTED_VERDICTS = {
    "K1_EVENT_CONTACT": "PASS_4_OF_4",
    "K2_LOCAL_RETURN": "PASS_4_OF_4",
    "K3_BETA_GATE_TRANSPORT": "PASS_GAME6",
    "K4_FINAL_ROOT_RESCUE": "FAIL_0_OF_4",
    "K5_SHAM_NONINTERFERENCE": "PASS_4_OF_4",
    "K6_SOURCE_COUNTERFACTUAL_IDENTITY": "PASS",
    "K7_FULL_DENOMINATOR": "PASS",
}

def analyze(receipt):
    if receipt.get("schema") != "c3x019-four-frozen-february-first-observed-root-return-source-edge-rescue-v1":
        raise ValueError("INVALID_FROZEN_SCHEMA")
    if receipt.get("verdicts") != EXPECTED_VERDICTS:
        raise ValueError("FROZEN_VERDICT_DRIFT")
    cases = receipt["cases"]
    if len(cases) != 4 or [c["game"] for c in cases] != list(EXPECTED):
        raise ValueError("FROZEN_CASE_DENOMINATOR")
    rows = []
    for c in cases:
        gid = c["game"]
        role, f_move, v_move = EXPECTED[gid]
        if (c["role"], c["F_bestmove"], c["FIRST_bestmove"]) != (role, f_move, v_move):
            raise ValueError("FROZEN_REFERENCE_DRIFT_" + str(gid))
        local = c["REPAIR_return"] == c["F_return"]
        final = c["REPAIR_bestmove"] == c["F_bestmove"]
        unchanged = c["REPAIR_bestmove"] == c["FIRST_bestmove"]
        if not local or final or not unchanged:
            raise ValueError("UNEXPECTED_K4_RESCUE_OR_LOCAL_DRIFT_" + str(gid))
        boundary = bool(c.get("root_depth10_beta_boundary_repaired", False))
        if boundary != (gid == 6):
            raise ValueError("BETA_BOUNDARY_DRIFT_" + str(gid))
        rows.append({
            "game": gid, "role": role,
            "local_return_restored": local,
            "beta_boundary_restored": boundary,
            "final_F_bestmove_restored": final,
            "repair_final_equals_FIRST": unchanged,
            "source_trial_exit_changed_by_repair": c["source_trial_exit_REPAIR"] != c["source_trial_exit_FIRST"],
            "classification": "BOUNDARY_RECOVERED_NOT_FINAL" if boundary else "LOCAL_ONLY",
        })
    return {
        "schema": "c3x020-frozen-single-edge-restoration-verdicts-v1",
        "evidence": "ADAPTIVE_FOUR_POST_OUTCOME_SELECTED_CASES",
        "independent_F19_5": "FAIL_RETAINED",
        "K4": "FAIL_0_OF_4",
        "rows": rows,
        "limit": "Restored local child return never identifies a unique causal path to final root choice.",
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--receipt", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    raw = Path(args.receipt).read_bytes()
    data = json.loads(raw)
    report = analyze(data)
    report["input_sha256"] = hashlib.sha256(raw).hexdigest()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("C3X020_FROZEN_K4_FAIL_PRESERVED", report["input_sha256"])

if __name__ == "__main__":
    main()
