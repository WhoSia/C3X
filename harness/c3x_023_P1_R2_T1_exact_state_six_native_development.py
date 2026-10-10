#!/usr/bin/env python3
"""T1 real Stockfish16 TT→SEE search-state match in 6 prereg dev games.

T0 observed 21 common late source path events. T1 compares original
complete ordered ancestor chess-key vector, live alpha/beta/PV/depth/ply,
rule50, occupancy and actual source chronology. ONLY passive SEE observations.
"""
import argparse,hashlib,json
from pathlib import Path
from collections import Counter
from c3x_018_native_TT_lineage_factorial_6_8 import need
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_022_P2_two_stage_exact_move_scout import native_world
from c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev import (
  SELECTED, cold, source_lines, SOURCE_SHA, STAGEA_SHA, frozen)
from c3x_023_P1_R2_T1_native_search_state_matcher import compare_original_treated

SCHEMA="c3x023-P1-R2-T1-source-exact-native-alpha-beta-SEE-window-six-development-v1"

def classify(original,first,target):
    used=[]
    for kind in ("used","main_cutoff","qsearch_cutoff"):
        used.extend(source_lines(original,"TT_value_used",kind,target))
    blocked=source_lines(first,"physical_TT","reader_block",target)
    if not used or not blocked:
        return {"status":"HOLD_NO_NATIVE_SOURCE_TT_SCORE_USE_OR_PHYSICAL_BLOCK",
                "real_native_score_uses_or_cutoffs":len(used),"real_physical_reader_block":len(blocked),
                "post_TT_full_search_window_state_matches":0}
    orig_serial=min(z["line_ordinal"] for z in used)
    block_serial=min(z["line_ordinal"] for z in blocked)
    x=compare_original_treated(original,first,orig_serial,block_serial)
    x["original_actual_TT_source_line"]=orig_serial
    x["suppressed_actual_TT_source_line"]=block_serial
    x["native_original_score_use_count"]=len(used)
    x["actual_treated_physical_reader_block_count"]=len(blocked)
    x["root_move_did_flip"]=first["UCI"]["bestmove"]!=original["UCI"]["bestmove"]
    return x

def scan(source,stagea,engine):
    out={"schema":SCHEMA,"study":"T1_POST_R1_OUTCOME_CONDITIONED_DEVELOPMENT_SIX",
         "source_sha256":SOURCE_SHA,"untreated_stageA_sha256":STAGEA_SHA,
         "actual_SEE_result_interventions":0,"cases":[]}
    for gid,order,role in SELECTED:
        src=source["per_ecology"]["may2026_broadcast"]["selected"][gid-1]
        prior=stagea["ecologies"]["may2026_broadcast"]["cases"][gid-1]
        need(src["id"]==prior["id"]==gid,"T1_SOURCE_GAME_ID")
        tar=prior["worlds"][order]["roles"][role]
        need(tar["status"]=="FIRST_SOURCE_PAIR_PRE_OUTCOME","T1_SOURCE_PAIR_NOT_FROZEN")
        board,clocks,_=native_world(src)
        scope={"key64":tar["physical"]["key64"],"root_call":tar["root_calls"][0]}
        before=cold(engine,board,clocks,order,"OBS",watch=scope)
        need(before["UCI"]==prior["worlds"][order]["baseline_UCI"],
             "T1_PASSIVE_PROBE_CHANGED_ORIGINAL_FROZEN_UCI")
        pair={"physical":tar["physical"],"root_calls":tar["root_calls"],
              "root_candidate_native":tar["root_candidate_native"]}
        after=cold(engine,board,clocks,order,"V",tar["physical"],
                    filter=mask_filters(RULES[role],pair,"FIRST"),watch=scope)
        block=[x for x in after["blocks"] if x["kind"]=="reader_block"]
        need(block and all(x["key64"]==tar["physical"]["key64"] and
             x["slot"]==tar["physical"]["slot"] and
             x["epoch"]==tar["physical"]["epoch"] and
             x["root_call"]==tar["root_calls"][0] and
             x["root_move"]==tar["root_candidate_native"] for x in block),
             "T1_WRONG_NATIVE_TT_PHYSICAL_FIRST_SOURCE_EVENT")
        lineage=verified_reader_lineage(after)
        need(lineage["all_valid"] and lineage["count"]>=len(block),
             "T1_NATIVE_TT_WRITER_TO_FIRST_READER_SOURCE_FAIL")
        need(all(e["altered"]==0 and e["original"]==e["delivered"]
                 for x in (before,after) for e in x["native_see_events"]
                 if e["kind"]=="witness"),"T1_SEE_NOT_PASSIVE")
        c=classify(before,after,tar)
        out["cases"].append({"game_id":gid,"original_source_order":order,
           "source_TT_role":role,"actual_native_first_TT_block":True,
           "actual_original_source_use":c.get("native_original_score_use_count",0),
           "SEE_native_search_state_comparison":c,
           "bestmove_changed":before["UCI"]["bestmove"]!=after["UCI"]["bestmove"],
           "baseline_native_UCI_invariant":True,
           "SEE_Boolean_actuations":0})
        print("C3X023_P1_R2_T1_STATE_COURT",gid,order,role,
              "full_node_state_matches",c.get("post_TT_full_search_window_state_matches",0),
              "path_but_different",c.get("post_TT_same_chess_path_but_different_state",0),
              "status",c["status"],
              "actual_root_bestmove_flip",before["UCI"]["bestmove"]!=after["UCI"]["bestmove"],
              flush=True)
    case=out["cases"]
    out["summary"]={"source_games_development_count":len(case),
      "true_TT_first_reader_block_cases":sum(z["actual_native_first_TT_block"] for z in case),
      "post_real_TT_source_strict_window_matched_case_count":sum(
        x["SEE_native_search_state_comparison"].get("post_TT_full_search_window_state_matches",0)>0
        for x in case),
      "post_real_TT_source_strict_window_matched_episodes":sum(
        x["SEE_native_search_state_comparison"].get("post_TT_full_search_window_state_matches",0)
        for x in case),
      "post_TT_same_chess_path_different_search_state_events":sum(
        x["SEE_native_search_state_comparison"].get("post_TT_same_chess_path_but_different_state",0)
        for x in case),
      "mismatch_dimension_counts":dict(sorted(sum(
        (Counter(x["SEE_native_search_state_comparison"].get("differences_by_field",{}))
         for x in case),Counter()).items())),
      "T1_first32_censored_cases":sum(
        x["SEE_native_search_state_comparison"].get("first32_prefix_censored",False) for x in case),
      "TT_first_reader_final_bestmove_changed_cases":sum(z["bestmove_changed"] for z in case),
      "native_SEE_boolean_actuations":0,
      "scope":"POST_OUTCOME_DEVELOPMENT_ONLY",
      "matched_state_is_bounded_to_explicit_live_fields_not_all_engine_state":True,
      "natural_causal_TT_SEE_mediation_claimed":False}
    return out

def main():
    p=argparse.ArgumentParser()
    for key in ("source","stagea","engine","out"):p.add_argument("--"+key,required=True)
    a=p.parse_args()
    x=scan(frozen(a.source,SOURCE_SHA),frozen(a.stagea,STAGEA_SHA),a.engine)
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
    print("C3X023_P1_R2_T1_SEARCH_WINDOW_COMMON_NATIVE_SEE_VERDICT",
          x["summary"],hashlib.sha256(path.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
