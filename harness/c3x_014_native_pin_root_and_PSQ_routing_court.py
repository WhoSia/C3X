#!/usr/bin/env python3
"""C3X 0.14 Exact native root-position pin operator and PSQ fallback court.

Same previously tested original 40 source-only king-pin worlds with original
160-run unmodified engine evidence; now parent 160-run branch trace baseline.
"""
from __future__ import annotations
import argparse,hashlib,json,collections
from pathlib import Path
from c3x_014_official_pin_NNUE_vs_classic_phenotype_court import native
from c3x_014_pin_root_eval_trace_fields import PIN_ROOT_FIELDS

SOURCE_SHA="cfb2c4b0631959cfcdd5bf1eb098f7b41c40468a7b22e434e95ef8936cc43ead"
PARENT_SHA="5f3c64e9ef2ac074786d86be96c404635e269483b1692d3ea1a713f0d0f9e77a"
MODES=("NNUE","CLASSICAL")
SITE_KEYS=("root_legal_pin_rejects","root_see_pinned_masks","root_mobility_pin_blockers","root_WeakQueen_hits")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def insist(x,msg):
    if not x:raise RuntimeError(msg)
def sites(g):return tuple(int(g[k]>0) for k in SITE_KEYS)
def main():
    a=argparse.ArgumentParser()
    for arg in ("source","previous","engine","out"):a.add_argument("--"+arg,required=True)
    x=a.parse_args()
    insist(sha(x.source)==SOURCE_SHA,"CHESS_LAW_SOURCE_SHA_DRIFT")
    insist(sha(x.previous)==PARENT_SHA,"ACTUAL_NATIVE_PIN_SITE_PANEL_SHA_DRIFT")
    raw=json.loads(Path(x.source).read_bytes())
    parent=json.loads(Path(x.previous).read_bytes())
    assert parent["exact_match_against_prior_unmodified_SF16_UCI_cells"]==80
    original=raw["source_only_selected_witnesses"]
    historical=parent["per_40_source_root_case_exact_output_and_trace"]
    insist(len(original)==len(historical)==40,"PARENT_ROOT_WORLD_COUNT_DRIFT")
    cases=[]
    for i,(w,b) in enumerate(zip(original,historical),1):
        insist(b["source_game_index"]==w["game_index"] and
                b["source_legal_FEN"]==w["board_six_field_FEN"],"ROOT_LAW_NATIVE_CASE_MISMATCH")
        results={}
        for mode in MODES:
            trials=[native(x.engine,w["source_game_history_uci"],w["pinned_square"],
                    mode,True,True) for cold in (1,2)]
            insist(trials[0]==trials[1],"ROOT_BRANCH_OR_PSQ_FALLBACK_COLD_NONREPRODUCIBLE")
            r=trials[0]
            data=r.pop("native_pin_root_eval")
            insist(r==b["native_runtime_by_mode"][mode],"ROOT_PSQ_PATCH_CHANGED_PRIOR_NATIVE_SEARCH_OUTCOME_OR_SITE_COUNTS")
            insist(set(data)==set(PIN_ROOT_FIELDS) and all(isinstance(v,int) and v>=0 for v in data.values()),
                   "ROOT_EVAL_NATIVE_SOURCE_FIELDS_INVALID")
            insist(data["root_key"]>0,"INVALID_ENGINE_ROOT_KEY")
            insist(data["root_legal_pin_rejects"]<=data["root_legal_pinned_checks"],"ROOT_PIN_GUARD")
            insist(data["root_see_pinned_masks"]<=r["native_pin_trace"]["see_masked_recapture_episodes"],
                   "ROOT_SEE_EXCEEDS_TREE")
            insist(data["root_mobility_pin_blockers"]<=r["native_pin_trace"]["classical_mobility_nonzero_pin_blockers"],
                   "ROOT_MOBILITY_EXCEEDS_TREE")
            insist(data["root_WeakQueen_hits"]<=r["native_pin_trace"]["classical_WeakQueen_hits"],
                   "ROOT_WEAKQUEEN_EXCEEDS_TREE")
            insist(data["eval_calls"]==data["eval_selected_classical"]+data["eval_selected_NNUE"],
                   "ACTUAL_EVAL_MODE_BRANCH_EXHAUSTIVENESS")
            insist(data["eval_NNUE_option_PSQ_classic_fallback"]<=data["eval_selected_classical"],
                   "PSQ_CLASSICAL_FALLBACK_INVALID")
            if mode=="CLASSICAL":
                insist(data["eval_NNUE_option_PSQ_classic_fallback"]==0,"FALLBACK_WITH_NNUE_FALSE_INVALID")
                insist(data["eval_selected_NNUE"]==0,"NATIVE_CLASSICAL_SWITCH_STILL_NNUE")
            results[mode]=data
        cases.append({"source_game":w["game_index"],"source_round":w["source_round"],
             "root_pin_square":w["pinned_square"],
             "law_subtype":w["source_chess_law_subtype"],
             "root_six_field_FEN":w["board_six_field_FEN"],
             "per_evaluator_mode":results,
             "root_specific_actual_call_site_signature":{mode:sites(results[mode]) for mode in MODES},
             "reference_whole_tree_native_case":b})
        print("C3X014_NATIVE_ROOT_PIN_PSQ_ACTUAL",i,
             "game",w["game_index"],"root",w["pinned_square"],
             "key",results["NNUE"]["root_key"],
             "root_sites",sites(results["NNUE"]),sites(results["CLASSICAL"]),
             "NNUE_classic_PSQ_fallback",results["NNUE"]["eval_NNUE_option_PSQ_classic_fallback"],
             flush=True)
    grp=collections.defaultdict(list)
    for r in cases:grp[json.dumps(r["law_subtype"],sort_keys=True)].append(r)
    reps={g:xs for g,xs in grp.items() if len(xs)>1}
    insist(len(grp)==30 and len(reps)==4 and sum(map(len,reps.values()))==14,"SOURCE_LAW_REPEAT_CENSUS")
    distinct={mode:sum(len({sites(v["per_evaluator_mode"][mode]) for v in arr})>1
              for arr in reps.values()) for mode in MODES}
    result={"schema":"c3x-014-sf16-actual-root-key-pin-site-evaluator-routing-frozen40-v1",
       "formal_research_unit":"C3X 0.14","P_checkpoints_informal":True,
       "original_source_sha256":SOURCE_SHA,"prior_160_native_operator_panel_sha256":PARENT_SHA,
       "frozen_source_worlds":40,"repeated_source_game_law_subtype_groups":4,
       "same_law_different_source_game_cases":14,
       "actual_native_SF16_new_processes":160,"strict_prior_UCI_and_all_native_site_counters_exact":80,
       "cold_repeat_all_exact":80,
       "root_fullkey_mode_difference_cases":sum(a["per_evaluator_mode"]["NNUE"]["root_key"]!=a["per_evaluator_mode"]["CLASSICAL"]["root_key"] for a in cases),
       "root_key_matched_legal_pin_operator_signature_divergent_repeated_law_groups":distinct,
       "native_NNUE_option_PSQ_classic_fallback_invocations":{
           "total":sum(a["per_evaluator_mode"]["NNUE"]["eval_NNUE_option_PSQ_classic_fallback"] for a in cases),
           "number_of_root_worlds_with_fallback":sum(a["per_evaluator_mode"]["NNUE"]["eval_NNUE_option_PSQ_classic_fallback"]>0 for a in cases)},
       "NNUE_setting_native_evaluator_source_route_totals":{
           "Eval_calls":sum(a["per_evaluator_mode"]["NNUE"]["eval_calls"] for a in cases),
           "actual_classical_selected":sum(a["per_evaluator_mode"]["NNUE"]["eval_selected_classical"] for a in cases),
           "actual_NNUE_selected":sum(a["per_evaluator_mode"]["NNUE"]["eval_selected_NNUE"] for a in cases)},
       "per_world_root_and_evaluator_route_exact_events":cases,
       "four_precommitted_P1_holdout_games_accessed":False,
       "new_chess_pin_strategy_latent_subtypes_causally_identified":False,
       "limitations":[
         "root position full key test only measures actual Position::legal, SEE and classical eval call sites at exact fullkey; zero may reflect search already handled root legal moves before resetting counter.",
         "Whole evaluator route PSQ threshold is independently source-verified, not a chess pin manipulation.",
         "No source-disjoint prospective new chess game validation. 14 repeated subtype cases from just 4 source-law tuples.",
         "Even if exact root-key source site signatures vary within a law type, the other pieces/moves at same root may explain behavior. Pin-specific causal manipulation is still HOLD."
       ]}
    dst=Path(x.out);dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("C3X014_ROOT_KEY_PIN_EVAL_PSQ_ROUTE_VERDICT",json.dumps({
       "worlds":40,"native_runs":160,"prior_source_exact":80,"cold_exact":80,
       "NNUE_PSQ_fallback":result["native_NNUE_option_PSQ_classic_fallback_invocations"],
       "NNUE_path_totals":result["NNUE_setting_native_evaluator_source_route_totals"],
       "distinct_within_law_root_signatures":distinct,
       "root_key_arms_differ":result["root_fullkey_mode_difference_cases"]}),flush=True)
if __name__=="__main__":main()
