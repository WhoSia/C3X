"""C3X 0.30 R36: receipt-bounded explanatory claims, not a new chess run.

Consumes *published derived* R33 and R35 JSON receipts. It does not verify
the underlying Drive ZIP bytes or identify unlogged causal mediators.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


class EvidenceError(ValueError):
    """A required observation or scope boundary was not met."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise EvidenceError(reason)


R33_ZIP_SHA = {
    "R29": "f6ed3cfc7755cee49f6f13a4bc86ac116bd947dd963cc3465a7658ee5c5ff6e3",
    "R30": "b42d19601f98fb00ff00e03fb7881bff3bd93114dc9c7b3bcd5876263727449e",
}
R35_ZIP_SHA = "c4f01a19665e7bb8781316e4f1a13d9a91c2cf4b0bf35eea5d962851c53f697a"


def verify_r33(receipt: dict) -> dict:
    require(receipt.get("classification") == "RETROSPECTIVE_CROSS_COHORT_AUDIT",
            "R33 classification changed")
    require(receipt.get("new_engine_experiment") is False, "R33 is not a new engine experiment")
    require(receipt.get("human_results") is None, "unexpected R33 human-result field")
    counts = receipt["counts"]
    require(set(counts) == {"R29", "R30", "all"}, "R33 cohorts absent or duplicated")
    first, second, total = (counts[key] for key in ("R29", "R30", "all"))
    require(set(first) == set(second) == set(total), "R33 count schema mismatch")
    for key, value in total.items():
        require(type(value) is int and value >= 0, "bad aggregate count " + key)
        require(value == first[key] + second[key], "cohort sum mismatch " + key)
    require((first["interventions"], second["interventions"], total["interventions"])
            == (25, 32, 57), "wrong physical-intervention denominator")
    require(total["direct_child_return_changed"] == 28, "changed child count mismatch")
    require(total["direct_child_return_changed_unobserved"] == 2,
            "unobserved child comparisons must not become negative observations")
    require(total["changed_child_invisible_in_score_pv"] == 15,
            "public-trace counterexample count mismatch")
    require(total["local_leader_changed_but_final_move_stable"] == 2,
            "local-leader null-effect witness count mismatch")
    require(total["final_recommendation_changed"] == 3, "final-choice denominator mismatch")
    require(total["post_intervention_third_move"] == 1, "third-move coverage gap lost")
    for key, expected in R33_ZIP_SHA.items():
        frozen = receipt["frozen_cohorts"][key]
        require(frozen["zip_sha256"] == expected, "wrong R33 source ZIP SHA: " + key)
        require(frozen["positions"] == 32, "source game-position denominator changed")
        require(frozen["tested_positions"] == counts[key]["positions"],
                "selected-position denominator mismatch")
    witnesses = receipt.get("witnesses")
    require(isinstance(witnesses, list), "R33 witness table absent")
    lookup = {row["id"]: row for row in witnesses}
    require(len(lookup) == len(witnesses), "duplicate R33 witness identity")
    stable_leaders = {"R29-018", "R30-028"}
    changed_choices = {"R29-029", "R29-030", "R30-017"}
    require(stable_leaders | changed_choices <= set(lookup), "required R33 witness missing")
    for key in stable_leaders:
        row = lookup[key]
        require(row["root_candidate_leader_update_changed"] is True,
                "not a changed local-leader witness: " + key)
        require(row["final_recommendation_changed"] is False,
                "not a stable final-choice witness: " + key)
    for key in changed_choices:
        row = lookup[key]
        require(row["final_recommendation_changed"] is True,
                "not an intervened final-choice witness: " + key)
        require(row["independent_reference_judge_label"] == "unresolved",
                "reference judge was post hoc promoted: " + key)
    third = lookup["R30-017"]
    require(third["post_intervention_third_move"] is True,
            "R30-017 third winner was omitted")
    require(third["post_intervention_independent_judge_coverage"] is False,
            "third winner improperly reported as referee-covered")
    require(third["final_bestmove"] == {"before": "e2f3", "after": "e2d3"},
            "R30-017 final moves mismatch")
    return {
        "physical_interventions": 57,
        "direct_child_return_changed": 28,
        "direct_child_comparison_unobserved": 2,
        "child_changed_with_identical_public_score_bound_pv_and_final_move": 15,
        "local_leader_flip_without_final_move_flip": 2,
        "final_choice_flip": 3,
        "unjudged_new_winner": "R30-017:e2d3",
        "cohort_independence": "two TWIC issues, nonrandom event selection; not 57 independent games",
    }


def verify_r35(receipt: dict) -> dict:
    require(receipt.get("category") == "RETROSPECTIVE_R34_R33_040_SOURCE_TRANSPORT",
            "R35 retrospective classification changed")
    require(receipt.get("sha256_zip") == R35_ZIP_SHA, "wrong inherited R34 ZIP SHA")
    require(receipt.get("manifest_files_verified") == 185, "R34 manifest count mismatch")
    rows = receipt.get("results")
    require(isinstance(rows, list) and len(rows) == 2, "expected two correlated strata")
    expected = {"0": (32, 20, "a5c7", "401", "952", 363),
                "1": (102, 24, "d4b3", "528", "454", 367)}
    require({row.get("stratum") for row in rows} == set(expected),
            "R35 stratum mismatch")
    for row in rows:
        event, attempt, source_root, before, after, target_value = expected[row["stratum"]]
        require((row["target_event"], row["event_attempt"], row["event_root"]) ==
                (event, attempt, source_root), "wrong physical R35 event")
        require((row["event_before"], row["event_after"]) == (before, after),
                "wrong original R35 event response")
        require(row["matched_root_window"] ==
                {"attempt": 24, "iteration": 12, "alpha": 367, "beta": 407},
                "attempt-24 window not comparable")
        first = row["first_same_window_score_change"]
        require(first["index"] == 1 and first["move"] == "d4b3",
                "h3 incorrectly treated as first candidate changed")
        h3 = row["same_window_h3_competition"]
        require((h3["index"], h3["move"], h3["alpha"]) == (3, "h2h3", "367"),
                "wrong matched h3 competitor")
        require((h3["base_value"], h3["treated_value"],
                 h3["base_update"], h3["treated_update"]) ==
                (392, target_value, "1", "0"), "h3 leader-change witness mismatch")
        require(row["base_attempt24_end"]["move"] == "h2h3" and
                row["treated_attempt24_end"]["move"] == "d4b3",
                "attempt-24 exit differs from source receipt")
        require((row["treated_aspiration_retry_start"]["attempt"],
                 row["treated_aspiration_retry_end"]["move"]) == ("25", "a5c7"),
                "R35 aspiration retry evidence missing")
        require(row["final_moves"] == ["h2h3", "a5c7"], "R35 final choice mismatch")
        require("not yet mapped" in row["comparison_limit"],
                "unidentified mediator restriction removed")
    require("human" in receipt.get("unproven", "").lower(), "human-result HOLD lost")
    return {
        "intervention_arms": 2,
        "independent_game_histories": 1,
        "same_window": [367, 407],
        "local_leader_lost": "h2h3",
        "new_final_recommendation": "a5c7",
        "first_changed_candidate": "d4b3",
        "intervening_state_mediator": "UNIDENTIFIED",
        "bound_semantics": "window-constrained search values; not exact strategic cp",
    }


def audit(r33: dict, r35: dict, input_sha256: dict | None = None) -> dict:
    a, b = verify_r33(r33), verify_r35(r35)
    return {
        "id": "C3X_030_R36_RECEIPT_BOUND_CLAIM_GATE",
        "authority": "DERIVED_RECEIPT_CONSISTENCY_ONLY",
        "raw_zip_rehash_this_run": False,
        "new_native_searches_this_run": 0,
        "human_participants_this_run": 0,
        "source_receipt_sha256": input_sha256 or {},
        "observed": {"R33_cross_cohort": a, "R35_single_game": b},
        "claim_court": [
            {"claim": "public_depth_score_bound_pv_plus_bestmove_determines_internal_returns",
             "verdict": "FALSIFIED_IN_RECORDED_INTERVENTIONS", "witness_count": 15},
            {"claim": "same_alpha_local_leader_update_flip_implies_final_bestmove_flip",
             "verdict": "FALSIFIED_IN_RECORDED_INTERVENTIONS", "witness_count": 2},
            {"claim": "distinct_upstream_source_events_can_converge_to_one_root_outcome",
             "verdict": "LOCAL_TWO_ARM_WITNESS", "independent_games": 1},
            {"claim": "specific_TT_history_or_budget_state_mediates_R35_event_to_root",
             "verdict": "HOLD_UNIDENTIFIED"},
            {"claim": "intervened_move_is_strategically_superior_under_legal_replies",
             "verdict": "HOLD_NO_INDEPENDENT_ALL_WINNER_JUDGE"},
            {"claim": "native_provenance_improves_unseen_reply_learner_performance",
             "verdict": "HOLD_NO_HUMAN_OUTCOME"},
        ],
        "transport_boundary":
            "Development and retrospective evidence; no new prospective population estimate.",
        "next_question":
            "Find a pre-specified, minimally sufficient intervention-stable search state "
            "that predicts root contrasts and independently checked legal reply semantics.",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("r33_receipt", type=Path)
    ap.add_argument("r35_receipt", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()
    inputs = [args.r33_receipt, args.r35_receipt]
    source_bytes = [p.read_bytes() for p in inputs]
    result = audit(*(json.loads(raw) for raw in source_bytes),
                   input_sha256={p.name: hashlib.sha256(raw).hexdigest()
                                 for p, raw in zip(inputs, source_bytes)})
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2,
                                     sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"authority": result["authority"],
                      "claim_verdicts": [c["verdict"] for c in result["claim_court"]]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
