#!/usr/bin/env python3
"""Native SF16 direct software-causal surgical PIN operator court (still C3X 0.14).

Same 40 pre-score source-only absolute-pin worlds, true chess legal moves never
modified. Directly compare classical SEE pinned recapture and WeakQueen own/
enemy blocker score suppression, with exact 40 OFF vs untouched original sham.
"""
from __future__ import annotations
import argparse,collections,hashlib,json
from pathlib import Path
from c3x_014_official_pin_NNUE_vs_classic_phenotype_court import native

SOURCE_SHA="cfb2c4b0631959cfcdd5bf1eb098f7b41c40468a7b22e434e95ef8936cc43ead"
PARENT_SHA="5f3c64e9ef2ac074786d86be96c404635e269483b1692d3ea1a713f0d0f9e77a"
ARMS={"OFF":0,"SEE_UNMASK":1,"WQ_OWN":2,"WQ_ENEMY":4,"WQ_BOTH":6}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(x,m):
    if not x:raise RuntimeError(m)
def no_intervention_fields(z):
    return {k:v for k,v in z.items() if k!="pin_causal_intervention"}
def main():
    p=argparse.ArgumentParser()
    for k in ("source","parent","engine","out"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    check(sha(a.source)==SOURCE_SHA,"FROZEN_CHESS40_SOURCE")
    check(sha(a.parent)==PARENT_SHA,"PRIOR_160_REAL_NATIVE_PIN_TRACE_SOURCE")
    src=json.loads(Path(a.source).read_bytes())
    parent=json.loads(Path(a.parent).read_bytes())
    worlds=src["source_only_selected_witnesses"]
    previous=parent["per_40_source_root_case_exact_output_and_trace"]
    check(len(worlds)==len(previous)==40,"PIN40_SOURCE_DRIFT")
    rows=[]
    for i,(w,old) in enumerate(zip(worlds,previous),1):
        check(w["board_six_field_FEN"]==old["source_legal_FEN"],"FEN_ROW_DRIFT")
        arms={}
        for name,num in ARMS.items():
            pair=[native(a.engine,w["source_game_history_uci"],w["pinned_square"],"CLASSICAL",
                         capture_pin_trace=True,pin_intervention=name)
                  for cold in range(2)]
            check(pair[0]==pair[1],"SAME_TREATMENT_COLD_NONDETERMINISTIC_"+name)
            obj=pair[0]
            info=obj["pin_causal_intervention"]
            check(info["mode"]==num,"NATIVE_SF16_ENVIRONMENT_MODE_MISMATCH")
            if name=="OFF":
                check(info["SEE_unmask_fired"]==0 and info["WQ_own_skip_fired"]==0 and
                     info["WQ_enemy_skip_fired"]==0,"NATIVE_OFF_ACTUALLY_TREATED")
                check(no_intervention_fields(obj)==old["native_runtime_by_mode"]["CLASSICAL"],
                    "NATIVE_CLASSIC_OFF_NOT_IDENTICAL_TO_ORIGINAL_STOCKFISH_UCI_AND_OPERATOR_STATS")
            if name=="SEE_UNMASK":
                check(info["WQ_own_skip_fired"]==info["WQ_enemy_skip_fired"]==0,"SEE_BRANCH_CROSSTALK")
            if name=="WQ_OWN":
                check(info["SEE_unmask_fired"]==info["WQ_enemy_skip_fired"]==0,"OWN_BRANCH_CROSSTALK")
            if name=="WQ_ENEMY":
                check(info["SEE_unmask_fired"]==info["WQ_own_skip_fired"]==0,"ENEMY_BRANCH_CROSSTALK")
            if name=="WQ_BOTH":
                check(info["SEE_unmask_fired"]==0,"WQ_BOTH_BRANCH_CROSSTALK")
            arms[name]=obj
        untreated=arms["OFF"]
        diffs={}
        for name in ARMS:
            if name=="OFF":continue
            r=arms[name]
            info=r["pin_causal_intervention"]
            fired=(info["SEE_unmask_fired"] if name=="SEE_UNMASK" else
                   info["WQ_own_skip_fired"] if name=="WQ_OWN" else
                   info["WQ_enemy_skip_fired"] if name=="WQ_ENEMY" else
                   info["WQ_own_skip_fired"]+info["WQ_enemy_skip_fired"])
            changed_best=(r["bestmove"]!=untreated["bestmove"])
            changed_score=(r["score_kind"]!=untreated["score_kind"] or
                           r["value_root_stm"]!=untreated["value_root_stm"] or
                           r["score_flag"]!=untreated["score_flag"])
            changed_nodes=(r["nodes"]!=untreated["nodes"])
            changed_pv=(r["pv"]!=untreated["pv"])
            # Direct gating falsifier: if no branch fired under treatment,
            # whole engine output should match untreated exactly, including nodes/PV.
            if not fired:
                check(not(changed_best or changed_score or changed_nodes or changed_pv),
                     "NONFIRED_PIN_CAUSAL_ARM_CHANGED_CHESS_OUTPUT_"+name)
            diffs[name]={"actual_software_branch_fire_count":fired,
                         "score_changed":changed_score,
                         "bestmove_changed":changed_best,
                         "PV_changed":changed_pv,
                         "nodes_changed":changed_nodes,
                         "treated_root_bestmove":r["bestmove"],
                         "treated_root_score_root_STM":r["value_root_stm"],
                         "off_root_score_root_STM":untreated["value_root_stm"],
                         "whole_eval_or_SEE_branch_treatment":True,
                         "pin_root_specific_causal_effect_claimed":False}
        rows.append({"source_game":w["game_index"],"root_pin_law_subtype":w["source_chess_law_subtype"],
                     "root_pin_square":w["pinned_square"],"root_original_FEN":w["board_six_field_FEN"],
                     "all_real_native_SF16_classic_five_arms":arms,
                     "direct_software_causal_branch_vs_OFF":diffs})
        print("C3X014_SF16_CAUSAL_PIN_ROLE_NATIVE",i,w["game_index"],
              w["pinned_piece"],w["pinning_piece"],
              "interventions",json.dumps({name:{"fired":v["actual_software_branch_fire_count"],
                     "bestmove_changed":v["bestmove_changed"],"score_changed":v["score_changed"]}
                         for name,v in diffs.items()}),flush=True)
    check(len(rows)==40,"NOT_FROZEN_40_WORLDS")
    stats={}
    for name in ARMS:
        if name=="OFF":continue
        dd=[r["direct_software_causal_branch_vs_OFF"][name] for r in rows]
        stats[name]={"native_worlds":40,
                     "source_site_actually_fired_root_worlds":sum(x["actual_software_branch_fire_count"]>0 for x in dd),
                     "actual_source_branch_treated_calls":sum(x["actual_software_branch_fire_count"] for x in dd),
                     "actual_bestmove_reversed":sum(x["bestmove_changed"] for x in dd),
                     "score_changed":sum(x["score_changed"] for x in dd),
                     "PV_changed":sum(x["PV_changed"] for x in dd),
                     "node_count_changed":sum(x["nodes_changed"] for x in dd),
                     "branch_not_fired_negative_control_worlds":sum(x["actual_software_branch_fire_count"]==0 for x in dd)}
    result={"schema":"c3x-014-legal-chess-stable-native-SEE-pin-and-classical-WeakQueen-blocker-role-surgical-five-arm-court-v1",
        "formal_research_unit":"C3X 0.14","P_substages_not_formal":True,
        "source_SHA256":SOURCE_SHA,"prior_native_original_branch_SHA256":PARENT_SHA,
        "frozen_original_chess_law_pin_root_worlds":40,
        "evaluator_mode":"Original SF16 Use NNUE=false classical",
        "native_source_Stockfish16_commit":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
        "site_conditions":["OFF","SEE_UNMASK","WQ_OWN","WQ_ENEMY","WQ_BOTH"],
        "actual_SF16_software_treatment_native_processes":400,
        "cold_repeats_per_world_treatment":2,
        "source_PIN_legal_move_generator_unchanged":True,
        "untreated_OFF_whole_native_search_output_and_site_counters_exact_vs_previous":"40/40",
        "cold_repeat_all_treatments":"200/200",
        "zero_branch_fired_means_zero_UCI_mutation_gate":"PASS",
        "treatment_summary":stats,
        "all_40_root_worlds_and_5_original_native_treatment_runs":rows,
        "procedural_P1_sealed_four_games_opened":False,
        "claim_independent_NNUE_learned_hidden_pin_categories":False,
        "claim_isolated_source_root_pin_causal_effect":False,
        "interpretation_limits":[
          "Direct C++ surgery modifies SEE pinned recapture filter or classical WeakQueen evaluation penalty while never altering king-ray chess legal move generation.",
          "The targeted native source condition can fire at OTHER positions in the global search tree, not necessarily for the particular pinned piece in initial root.",
          "Therefore causal effects on engine root output are causes of whole search computation, not proof source-law pin subtype causes move preferences.",
          "No NNUE native latent feature code is intervened on; this is source-version/classical-role behavioral evidence only.",
          "Four legal pin subtype within-source group repeat count modest. Study results limited to original 40 source-specific positions and Stockfish16 version.",
          "This is not an experiment on human chess teaching, training or learning."
        ]}
    f=Path(a.out);f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("C3X014_DIRECT_SEE_PIN_AND_WEAKQUEEN_ROLE_NATIVE_CAUSAL_VERDICT",json.dumps(stats),flush=True)
if __name__=="__main__":main()
