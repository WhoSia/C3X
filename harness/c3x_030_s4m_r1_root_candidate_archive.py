#!/usr/bin/env python3
"""C3X S4-M/R1: independent root-score candidate alignment on archived S4-L bytes.

Match a root candidate across Sham / two-hit arms only if its signature
(move, depth, move-count, alpha, beta) occurs exactly once IN THAT TRIAL
in each source trace. Candidate is NOT proven identical causal execution:
prior TT state and unlogged branches remain uncontrolled.

Only seven VALUE disagreements appear in the original S4-L *logged* unique
candidate pairs; those are descriptive search-score differences, NOT
seven statistically independent causal mediators or proof that any
specific TT mask caused the root bestmove change.
"""
import argparse, hashlib, json
from collections import defaultdict
from pathlib import Path

ORIGINAL_SHA="a27b961985d2ba4475f51916c41be3426d8a32d3130bce0fab04497ca2eac5c9"
SOURCE_SCHEMA="c3x030-s4l-root-update-trace-development-v1"
FIELDS=("root_move_raw","depth","move_count","alpha","beta")
SCHEMA="c3x030-s4m-r1-archived-root-candidate-state-audit-v1"

def digest(b):return hashlib.sha256(b).hexdigest()

def pair_epoch(sham,two):
    def classify(trace):
        root=trace["root_score_receipts"]
        total=trace["root_score_total_at_this_site"]
        if len(root)!=min(total,512):
            raise ValueError("S4M_R1_FALSE_SOURCE_LOG_COVERAGE")
        by=defaultdict(list)
        for idx,row in enumerate(root):
            if row["ordinal"]!=idx:
                raise ValueError("S4M_R1_BROKEN_SOURCE_LOG_ORDINAL")
            if (row["alpha"]>=row["beta"] or
                row["will_update_best"]!=(row["value"]>row["old_best"]) or
                row["will_update_root_pv"]!=(row["move_count"]==1 or row["value"]>row["alpha"])):
                raise ValueError("S4M_R1_BAD_SOURCE_PREDICATE")
            by[tuple(row[k] for k in FIELDS)].append(row)
        return by
    a=classify(sham);b=classify(two)
    common=a.keys()&b.keys()
    exact_pairs=[]
    ambiguous=[]
    for state in sorted(common):
        if len(a[state])!=1 or len(b[state])!=1:
            ambiguous.append({"candidate_state":list(state),
                "sham_occurrences":len(a[state]),"two_occurrences":len(b[state])})
            continue
        sa,tb=a[state][0],b[state][0]
        exact_pairs.append({"candidate_state":list(state),
            "sham_value":sa["value"],"two_value":tb["value"],
            "value_delta":tb["value"]-sa["value"],
            "sham_previous_best":sa["old_best"],
            "two_previous_best":tb["old_best"],
            "changed_value":sa["value"]!=tb["value"],
            "sham_will_update_best":sa["will_update_best"],
            "two_will_update_best":tb["will_update_best"],
            "cross_run_identity_or_mediation_proven":False})
    return {"shared_state_signatures":len(common),
      "unique_singleton_candidate_pairs":len(exact_pairs),
      "ambiguous_state_signatures":len(ambiguous),
      "different_value_candidates":sum(p["changed_value"] for p in exact_pairs),
      "unique_candidate_details":exact_pairs,
      "repeated_ambiguous_state_details":ambiguous,
      "sham_only_signatures":len(a.keys()-b.keys()),
      "two_only_signatures":len(b.keys()-a.keys()),
      "any_detail_log_censored":bool(sham["root_score_right_censored"] or two["root_score_right_censored"]),
      "complete_root_search_coverage":bool(not sham["root_score_right_censored"] and not two["root_score_right_censored"]),
      "causal_mediator_identity_proven":False}

def audit(raw):
    if digest(raw)!=ORIGINAL_SHA:
        raise ValueError("S4M_R1_NOT_THE_ORIGINAL_ARCHIVED_NATIVE_BYTES")
    data=json.loads(raw)
    if (data.get("schema")!=SOURCE_SCHEMA or
        data.get("verdict")!="PASS_ROOT_SCORE_RECEIPT_SITE_ONLY" or
        data.get("native_searches")!=48 or
        data.get("untouched_holdout") is not True or
        data.get("control_noninterference") is not True):
        raise ValueError("S4M_R1_SOURCE_SCOPE")
    cases=data["cases"]
    if len(cases)!=8 or len({c["game_id"] for c in cases.values()})!=4:
        raise ValueError("S4M_R1_FALSE_INDEPENDENT_GAMES")
    totals={"shared_signatures":0,"unique_candidate_pairs":0,
      "ambiguous_signatures":0,"changed_candidate_values":0,
      "root_bestmove_changes":0,"censored_epoch_pairs":0}
    report={}
    descriptive_trial_cross_tab={
      "root_changed_with_observed_score_contrast":0,
      "root_changed_without_observed_score_contrast":0,
      "root_unchanged_with_observed_score_contrast":0,
      "root_unchanged_without_observed_score_contrast":0
    }
    for case_id,case in sorted(cases.items()):
        case_result={"game_id":case["game_id"],"trials":{}}
        if case.get("original_sham_noninterference") is not True:
            raise ValueError("S4M_R1_NEGATIVE_CONTROL_DRIFT")
        for trial in ("1","2"):
            sham=case["cutoff_return_trace"]["sham"]["trials"][trial]
            two=case["cutoff_return_trace"]["two"]["trials"][trial]
            paired=pair_epoch(sham,two)
            idx=int(trial)-1
            changed=case["native_trials"]["sham"][idx]["bestmove"]!=case["native_trials"]["two"][idx]["bestmove"]
            if changed!=case["per_trial_root_changed"][trial]:
                raise ValueError("S4M_R1_ROOT_OUTCOME_CHANGED_POSTHOC")
            paired["root_bestmove_changed"]=changed
            contrast=paired["different_value_candidates"]>0
            cross_tab_key=("root_changed_" if changed else "root_unchanged_")+(
                 "with_observed_score_contrast" if contrast else "without_observed_score_contrast")
            descriptive_trial_cross_tab[cross_tab_key]+=1
            for key,field in (("shared_signatures","shared_state_signatures"),
                              ("unique_candidate_pairs","unique_singleton_candidate_pairs"),
                              ("ambiguous_signatures","ambiguous_state_signatures"),
                              ("changed_candidate_values","different_value_candidates")):
                totals[key]+=paired[field]
            totals["censored_epoch_pairs"]+=int(paired["any_detail_log_censored"])
            totals["root_bestmove_changes"]+=int(changed)
            case_result["trials"][trial]=paired
        if sum(t["root_bestmove_changed"] for t in case_result["trials"].values())!=case["root_move_changes"]:
            raise ValueError("S4M_R1_CASE_ROOT_OUTCOME_MISMATCH")
        report[case_id]=case_result
    if totals["root_bestmove_changes"]!=data["root_change_total"]:
        raise ValueError("S4M_R1_GLOBAL_OUTCOME_MISMATCH")
    return {"schema":SCHEMA,"original_source_sha256":digest(raw),
      "inherited_real_searches":48,"new_engine_searches":0,
      "development_games":4,"development_fens":8,
      "holdout_positions_searched":0,
      "candidate_signature_fields":list(FIELDS),
      "totals":totals,
      "descriptive_trial_cross_tab":descriptive_trial_cross_tab,
      "trial_cross_tab_is_not_out_of_sample_prediction":True,
      "case_results":report,
      "source_traces_censored_unknowns_explicit":True,
      "cross_run_causal_invocation_identity_proven":False,
      "full_tt_to_parent_to_root_causal_mediation_proven":False,
      "paper_superiority":"HOLD",
      "verdict":"PASS_ARCHIVED_ROOT_CANDIDATE_ALIGNMENT_ONLY"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    res=audit(Path(a.original).read_bytes())
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    rendered=(json.dumps(res,indent=2,sort_keys=True)+"\n").encode()
    dest.write_bytes(rendered)
    print("C3X_S4M_R1_ROOT_CANDIDATE_AUDIT",res["totals"],digest(rendered))

if __name__=="__main__":main()
