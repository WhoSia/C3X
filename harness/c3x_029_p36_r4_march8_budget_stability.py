#!/usr/bin/env python3
"""P36/R4 prospective-to-48k/96k *exploratory* native candidate stability check.

All eight fixed March cases are analyzed. Two 24k near-gap cases were selected
from earlier exposed engine results; R4 tests precommitted higher-budget
stability, never independent explanatory advantage or minimax correctness.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from c3x_029_p36_r3_march8_native_multipv2 import (
    run_case, MARCH_SOURCE_SHA256, EXPECTED_CASES,
)

FROZEN_MANIFEST_SHA256 = "e9b041d52e2622cb2caf085cdeb21132c06da37c68dde51fb56540d5d06b9ff3"
FROZEN_24K_JSON_SHA256 = "5ce8ec253c95075cbba3a1b273236886756968778259363f1f1214fdb1c12d3f"
BUDGETS = (48000, 96000)
NOMINAL_NEAR_IDS = frozenset({
    "00470a57672750d1",
    "01af9df4f5e8e39f",
})
PREVIOUS_GAME_OVERLAP_ID = "00f04cd20636fdc2"


def require(ok, label):
    if not ok:
        raise ValueError("P36_R4_HOLD_" + label)


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pair_roots(observation):
    vals = observation["two_candidate_search"]
    require(len(vals) == 2, "TWO_CANDIDATES")
    roots = [r["root_uci"] for r in vals]
    require(len(set(roots)) == 2, "DUPLICATE_ROOTS")
    return roots


def near_stability(original, higher_by_budget):
    """Required exact 2-move identity + winner + nonnegative gap across budgets."""
    original_pair = pair_roots(original)
    all_failures = []
    budget_receipts = []
    for budget in BUDGETS:
        new = higher_by_budget[budget]
        pair = pair_roots(new)
        changes = {
            "candidate_identity_changed": set(pair) != set(original_pair),
            "winner_changed": pair[0] != original_pair[0],
            "native_pv_order_discordant": bool(new["reported_root_order_discordant"]),
            "not_near": new["candidate_margin_stratum"] != "near",
        }
        all_failures.extend([f"{budget}:{key}" for key, yes in changes.items() if yes])
        budget_receipts.append({
            "budget_nodes": budget,
            "two_root_uci": pair,
            "root1_minus_root2_cp": new["reported_pv1_minus_pv2_signed_cp"],
            "abs_score_gap_cp": new["candidate_margin_cp"],
            "reported_root_order_discordant": new["reported_root_order_discordant"],
            "all_rejection_flags": changes,
        })
    if all_failures:
        status = "REJECTED_AS_BUDGET_STABLE_NEAR_CASE"
    else:
        last = higher_by_budget[96000]["two_candidate_search"][0]
        flagged = last["score_lowerbound"] or last["score_upperbound"]
        status = ("BUDGET_STABLE_NEAR_BUT_PV1_SCORE_BOUND_HOLD"
                  if flagged else "BUDGET_STABLE_NEAR_FINITE_DEPTH_ONLY")
    return {"status": status, "failure_reasons": all_failures,
            "budget_receipts": budget_receipts}


def court(manifest_path: Path, previous_path: Path, source_path: Path,
          engine_path: str):
    require(file_sha(source_path) == MARCH_SOURCE_SHA256, "SOURCE_SHA")
    require(file_sha(manifest_path) == FROZEN_MANIFEST_SHA256, "MANIFEST_SHA")
    require(file_sha(previous_path) == FROZEN_24K_JSON_SHA256, "PREVIOUS_24K_SHA")
    manifest = json.loads(manifest_path.read_text())
    prev = json.loads(previous_path.read_text())
    require(prev["status"] == "P36_R3_MARCH8_NATIVE_MULTIPV_SCREEN_DONE_NOT_EXPLANATION_ADVANTAGE",
            "PREVIOUS_STATUS")
    cases = manifest["case_selection"]
    require(tuple(c["case_id"] for c in cases) == EXPECTED_CASES, "FROZEN_CASE_IDS")
    old = prev["observations"]
    require(tuple(r["case_id"] for r in old) == EXPECTED_CASES, "PREVIOUS_SAME_EIGHT")
    require({r["case_id"] for r in old
             if r["candidate_margin_stratum"] == "near"} == NOMINAL_NEAR_IDS,
            "PREDECLARED_NEAR_CASES")
    records = []
    for case, original in zip(cases, old):
        require(case["full_game_uci_sha256"] == original["original_game_uci_sha256"],
                "PREVIOUS_GAME_IDENTITY")
        higher = {}
        for budget in BUDGETS:
            value = run_case(engine_path, case, nodes=budget)
            higher[budget] = value
            print("P36_R4_REAL_SF16", case["case_id"], budget,
                  value["candidate_margin_stratum"],
                  value["candidate_margin_cp"], flush=True)
        verdict = near_stability(original, higher) if case["case_id"] in NOMINAL_NEAR_IDS else None
        records.append({
            "case_id": case["case_id"],
            "old_march16_game_overlap": case["case_id"] == PREVIOUS_GAME_OVERLAP_ID,
            "nominal_near_at_24k": case["case_id"] in NOMINAL_NEAR_IDS,
            "original_24k": original,
            "native_48k": higher[48000],
            "native_96k": higher[96000],
            "strict_near_stability": verdict,
        })
    require(len(records) == 8, "EIGHT_GAME_DENOMINATOR")
    return {
        "status": "P36_R4_8_GAME_FINITE_NODE_STABILITY_EXECUTED_NO_EXPLANATION_CLAIM",
        "source_sha256": MARCH_SOURCE_SHA256,
        "precommitted_24k_json_sha256": FROZEN_24K_JSON_SHA256,
        "new_budgets_per_game": list(BUDGETS),
        "new_original_sf16_processes": len(records) * len(BUDGETS),
        "predeclared_nominal_near_cases": sorted(NOMINAL_NEAR_IDS),
        "known_prior_march_game_overlap": PREVIOUS_GAME_OVERLAP_ID,
        "historical_holdout_status": "NOT_INDEPENDENT_CONFIRMATORY",
        "claim_ceiling": "Finite-node native MultiPV candidate identity, rank, and budget instability. No chess explanation advantage or true minimax value.",
        "records": records,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--previous-24k", required=True, type=Path)
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--engine", required=True)
    p.add_argument("--out", required=True, type=Path)
    args=p.parse_args()
    result=court(args.manifest,args.previous_24k,args.source,args.engine)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("P36_R4_NATIVE_BUDGET_STABILITY_COURT_COMPLETE",flush=True)

if __name__=="__main__":
    main()
