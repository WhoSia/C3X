#!/usr/bin/env python3
"""C3X S4-H2: lock experimental arms and identity before unseen engine outcomes.

Researcher-authored legal opening cohort, NOT population-random human games.
The first eligible ply-one *physical* TT-hit key must be chosen by a
pre-treatment source-probe-only eligibility scan (no bestmove, score, PV,
response or label may enter the key-selection code).
"""
import argparse
import hashlib
import json
from pathlib import Path

H0_SHA = "1741592a52675c5170fdb076bb96b6842cbdced43e40c8a85c82f80c4ba0d247"
UPSTREAM = "68e1e9b3811e16cad014b590d7443b9063b3eb52"
ARMS = ("original", "sham", "zero", "one", "two", "many")
MASK_CAPS = {"original": None, "sham": 10000, "zero": 0, "one": 1, "two": 2, "many": 10000}
SEEDS_AND_BRANCHES = "game-id sorted; ply8 before ply10; frozen arm order; 2 consecutive trials per arm"
SCHEMA = "c3x030-s4h2-preoutcome-native-execution-protocol-v1"

def make(raw: bytes) -> dict:
    if hashlib.sha256(raw).hexdigest() != H0_SHA:
        raise ValueError("S4H2_HOLD_NOT_ORIGINAL_FROZEN_S4H0_BYTES")
    d = json.loads(raw)
    if d.get("schema") != "c3x030-f2-blind-holdout-manifest-v1":
        raise ValueError("S4H2_HOLD_COHORT_SCHEMA")
    dev = d.get("development_entries")
    hold = d.get("entries")
    if not isinstance(dev, list) or len(dev) != 8 or not isinstance(hold, list) or len(hold) != 16:
        raise ValueError("S4H2_HOLD_FROZEN_CASE_COUNTS")
    def cases(rows, split):
        out = []
        for x in sorted(rows, key=lambda r:(r["game_id"], len(r["history_uci"]))):
            if set(x) != {"case_id","game_id","fen","history_uci"}:
                raise ValueError("S4H2_HOLD_OUTCOME_LEAK_OR_MUTATED_IDENTITY")
            out.append({"case_id":x["case_id"], "game_id":x["game_id"],"split":split,
                        "fen":x["fen"], "history_uci":x["history_uci"][:]})
        return out
    positions=cases(dev,"development")+cases(hold,"holdout")
    plan={
        "schema":SCHEMA,
        "frozen_h0_manifest_raw_sha256":H0_SHA,
        "stockfish16_original_source_commit":UPSTREAM,
        "cohort_kind":"researcher-authored-deterministic-legal-opening-histories",
        "random_human_game_population_sample":False,
        "dependent_fens_within_game":True,
        "split_order":["development","holdout"],
        "development_decisions_must_be_frozen_before_holdout_execution":True,
        "arm_order":list(ARMS),
        "mask_hit_caps":MASK_CAPS,
        "primary_negative_controls":["original","sham","zero"],
        "trial_count_per_arm":2,
        "number_of_positions":24,
        "holdout_positions":16,
        "development_positions":8,
        "planned_native_searches":24*6*2,
        "planned_holdout_native_searches":16*6*2,
        "engine_protocol":{
            "threads":1,"hash_megabytes":16,"use_nnue":False,
            "skill_level":20,"limit_strength":False,
            "new_game_before_each_arm":True,"go_nodes":12000,
            "same_modified_binary_for_sham_zero_one_two_many":True,
            "original_binary_pinned_to_exact_upstream":True,
            "instrumented_native_source":True
        },
        "key_eligibility_policy":{
            "selection_rule":"first chronological ply=1 TT probe hit_before=1 in a pre-treatment probe-only trace",
            "eligible_only_after_pre_treatment_physical_hit":True,
            "forbid_bestmove_score_pv_or_labels_during_key_choice":True,
            "no_source_hit":"record ineligible, retain in denominator, do not substitute another case",
            "key_shared_by_all_source_mask_arms_for_a_case":True,
            "do_not_reselect_after_treatment":True
        },
        "predefined_measures":{
            "primary":"paired root bestmove changes versus sham for each arm, including ineligible cases",
            "secondary":["physical_mask_receipt_counts","source_probes",
                         "within_run_signed_child_parent_root_links",
                         "search_nodes","score","depth","pv",
                         "per_case_eligibility","truncation_counts"],
            "uncertainty_unit":"game_id",
            "never_equate_tt_miss_to_physical_mask":True,
            "absence_of_trace_is_not_evidence_of_absent_value_flow":True,
            "no_full_mediation_claim_from_matching_negamax_arithmetic":True
        },
        "cases":positions,
        "outcome_or_effect_values_present":False,
        "holdout_effects_observed":False,
        "method_superiority":"HOLD",
        "fixed_schedule_note":SEEDS_AND_BRANCHES
    }
    return plan

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True)
    p.add_argument("--out",required=True)
    x=p.parse_args()
    result=make(Path(x.manifest).read_bytes())
    dest=Path(x.out)
    dest.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n").encode()
    dest.write_bytes(raw)
    print("C3X_S4H2_FROZEN_PROTOCOL",hashlib.sha256(raw).hexdigest(),
          "PLANNED_ONLY",result["planned_native_searches"],
          "NO_ENGINE_SEARCHES",not result["holdout_effects_observed"])

if __name__=="__main__":
    main()
