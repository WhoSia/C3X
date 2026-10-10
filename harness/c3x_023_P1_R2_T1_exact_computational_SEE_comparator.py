#!/usr/bin/env python3
"""C3X023-P1-R2-T1: compare real native SEE call state AFTER TT FIRST source.

Four previously changed May broadcast games plus two unchanged controls.
This is post-outcome DEVELOPMENT, not new predictive validation. No SEE flip.
SEE-occupied bitboard recorded from capture overload is an *output*, never
misrepresented as native SEE input. Actual native search alpha and beta at
call-site are pointers into active C++ search frames.
"""
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev import (
 SELECTED,STUDY as PRIOR_T0_STUDY,cold,source_lines,SCHEMA as PRIOR_T0_SCHEMA)
from c3x_023_P1_same_descendant_SEE_node_matcher import candidates,identity
from c3x_023_P1_R1_licensed32_TT_FIRST_native_common_SEE_node_court import (
 SOURCE_SHA,STAGEA_SHA,frozen)
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_022_P2_two_stage_exact_move_scout import native_world
from c3x_018_native_TT_lineage_factorial_6_8 import need

SCHEMA="c3x023-P1-R2-T1-native-same-search-state-SEE-after-TT-source-v1"
STUDY="POST_R1_DEVELOPMENT_NATIVE_COMPUTATIONAL_STATE_OBSERVER_NOT_HELDOUT"
SEARCH_FIELDS=("t1_ply","t1_depth","t1_alpha","t1_beta","t1_pv","t1_qsearch","t1_rule50")
SEE_FIELDS=("t1_occupied_present","t1_occupied_out")
ALL_REQUIRED=("t1_path",)+SEARCH_FIELDS+SEE_FIELDS
SITES=("quiet_prune","qsearch_prune")

def temporal_common(original,treated,target):
    weak=candidates(original["native_see_events"],treated["native_see_events"],True)
    x=source_lines(original,"TT_value_used","used",target)
    x+=source_lines(original,"TT_value_used","main_cutoff",target)
    x+=source_lines(original,"TT_value_used","qsearch_cutoff",target)
    y=source_lines(treated,"physical_TT","reader_block",target)
    if not x or not y:
        return {"status":"HOLD_REAL_TT_SOURCE_USE_OR_BLOCK_MISSING",
                "common_event_count":len(weak["matched"]),"exact_state_events":[],
                "reason_census":{}}
    min_obs=min(z["line_ordinal"] for z in x)
    min_tr=min(z["line_ordinal"] for z in y)
    def chronological(events):
        out={}
        for line in events:
            if line["source"]!="native_SEE" or line["fields"].get("kind")!="witness":
                continue
            key=identity(line["fields"])
            out.setdefault(key,[]).append(line["line_ordinal"])
        return out
    o_order=chronological(original["ordered_source_operator_trace"])
    v_order=chronological(treated["ordered_source_operator_trace"])
    states=[]
    counts=Counter()
    for m in weak["matched"]:
        idx=m["untreated_prefix_event_index"]
        jdx=m["TT_FIRST_prefix_event_index"]
        before=original["native_see_events"][idx]
        after=treated["native_see_events"][jdx]
        key=identity(before)
        o_serial=o_order.get(key,[])
        v_serial=v_order.get(key,[])
        if len(o_serial)!=1 or len(v_serial)!=1:
            counts["CHRONOLOGY_SOURCE_AMBIGUOUS"]+=1
            continue
        if o_serial[0]<=min_obs or v_serial[0]<=min_tr:
            counts["PRE_TT_SOURCE_EVENT_NONMEDIATING"]+=1
            continue
        if any(k not in before or k not in after for k in ALL_REQUIRED):
            raise ValueError("T1_NATIVE_SEE_FULL_COMPUTATIONAL_SOURCE_FIELDS_MISSING")
        if before["t1_path"]=="NONE" or before["t1_path"]!=after["t1_path"]:
            counts["SAME_HASH_DIFFERENT_EXACT_ANCESTRY"]+=1
            continue
        path_keys=before["t1_path"].split(",")
        if not path_keys or path_keys[-1]!=str(before["key64"]):
            raise ValueError("T1_FULL_ANCESTRY_PATH_DOES_NOT_END_AT_POSITION_KEY")
        if any(before[k]!=after[k] for k in SEARCH_FIELDS):
            counts["SAME_CHESS_PATH_DIFFERENT_COMPUTATIONAL_WINDOW"]+=1
            continue
        if any(before[k]!=after[k] for k in SEE_FIELDS):
            counts["SAME_CALL_STATE_DIFFERENT_NATIVE_SEE_OCCUPANCY_OUTPUT"]+=1
            continue
        if before["original"]!=after["original"] or before["delivered"]!=after["delivered"]:
            raise ValueError("T1_DETERMINISTIC_SAME_INPUT_DIFFERENT_NATIVE_SEE_BOOL")
        same={"site":before["site"],
              "key64":before["key64"],
              "parent_key64":before["parent_key64"],
              "path_hash":before["path_hash"],
              "path_length":before["path_length"],
              "t1_exact_ancestor_path":before["t1_path"],
              "move":before["move"],
              "threshold":before["threshold"],
              "original_native_SEE_Boolean":before["original"],
              "source_root_call":before["root_call"],
              "source_root_move":before["root_move"],
              "native_search_state":{f:before[f] for f in SEARCH_FIELDS+SEE_FIELDS},
              "t1_source_line_ordinal_original":o_serial[0],
              "t1_source_line_ordinal_TT_FIRST":v_serial[0],
              "actual_source_TT_score_used_before_SEE":True,
              "actual_selected_TT_first_reader_blocked_before_SEE":True,
              "natural_TT_SEE_mediation_proved":False}
        states.append(same)
        counts["EXACT_SEARCH_CALL_STATE_AFTER_SOURCE"]+=1
    states.sort(key=lambda e:(e["t1_source_line_ordinal_original"],
                              e["t1_source_line_ordinal_TT_FIRST"]))
    return {"status":"EXACT_SEARCH_STATE_COMMON_SEE_AFTER_SOURCE" if states
             else "HOLD_CENSORED_NO_IDENTICAL_STATE_IN_LOGGED_PREFIX"
                  if weak["observed_prefix_censored"]
             else "NO_EXACT_SEARCH_STATE_COMMON_SEE_IN_OBSERVED_SCOPE",
      "weak_path_common_events":len(weak["matched"]),
      "search_exact_common_events":len(states),
      "root_call_prefix_censored":weak["observed_prefix_censored"],
      "reason_census":dict(sorted(counts.items())),
      "exact_state_events":states,
      "original_source_native_real_score_witnesses":len(x),
      "counterfactual_real_source_reader_blocks":len(y),
      "full_ancestor_vector_exactly_compared":True,
      "exact_window_level_alpha_beta_compared":True,
      "search_PV_and_depth_and_ply_compared":True,
      "capture_SEE_occupied_output_not_wrongly_treated_as_input":True,
      "pre_intervention_only_no_SEE_operator_mutation":True}

def run(source,stagea,engine):
    cases=[]
    for gid,order,role in SELECTED:
        row=source["per_ecology"]["may2026_broadcast"]["selected"][gid-1]
        stage=stagea["ecologies"]["may2026_broadcast"]["cases"][gid-1]
        need(row["id"]==stage["id"]==gid,"T1_COHORT_DRIFT")
        target=stage["worlds"][order]["roles"][role]
        need(target["status"]=="FIRST_SOURCE_PAIR_PRE_OUTCOME","T1_TARGET_NOT_FROZEN")
        world,clocks,_=native_world(row)
        watch={"key64":target["physical"]["key64"],"root_call":target["root_calls"][0]}
        o=cold(engine,world,clocks,order,"OBS",watch=watch)
        need(o["UCI"]==stage["worlds"][order]["baseline_UCI"],"T1_BASELINE_CHANGED")
        pair={k:target[k] for k in ("physical","root_calls","root_candidate_native")}
        v=cold(engine,world,clocks,order,"V",target["physical"],
               filter=mask_filters(RULES[role],pair,"FIRST"),watch=watch)
        blocks=[z for z in v["blocks"] if z["kind"]=="reader_block"]
        need(blocks and all(z["key64"]==target["physical"]["key64"] and
                     z["slot"]==target["physical"]["slot"] and
                     z["epoch"]==target["physical"]["epoch"] and
                     z["root_call"]==target["root_calls"][0] and
                     z["root_move"]==target["root_candidate_native"] for z in blocks),
             "T1_PHYSICAL_WRITER_READER_SOURCE_NOT_MATCHED")
        lineage=verified_reader_lineage(v)
        need(lineage["all_valid"] and lineage["count"]>=len(blocks),
             "T1_SOURCE_NATIVE_READER_LINEAGE_INVALID")
        match=temporal_common(o,v,target)
        change=o["UCI"]["bestmove"]!=v["UCI"]["bestmove"]
        cases.append({"source_id":gid,"root_order":order,"source_role":role,
            "TT_FIRST_physically_delivered":True,
            "actual_terminal_bestmove_flipped":change,
            "native_SEE_original_delivered_modified":False,
            "causal_observational_state_classification":match})
        print("C3X023_T1_FULL_SEARCH_STATE_COURT",gid,order,role,
              "matched",match.get("search_exact_common_events",0),
              "weak",match.get("weak_path_common_events",0),
              "censored",match.get("root_call_prefix_censored",False),
              "flip",change,flush=True)
    summary={"development_source_games":len(SELECTED),
      "TT_first_reader_physical_contacts":len(cases),
      "distinct_games_with_complete_state_matched_SEE_after_TT":sum(
         bool(x["causal_observational_state_classification"].get("search_exact_common_events")) for x in cases),
      "total_exact_comp_state_and_original_ancestor_after_TT_events":sum(
         x["causal_observational_state_classification"].get("search_exact_common_events",0) for x in cases),
      "total_same_chess_path_but_search_window_different_events":sum(
         x["causal_observational_state_classification"].get("reason_census",{}).get(
           "SAME_CHESS_PATH_DIFFERENT_COMPUTATIONAL_WINDOW",0) for x in cases),
      "censored_prefix_cases":sum(x["causal_observational_state_classification"].get("root_call_prefix_censored",False) for x in cases),
      "actual_final_bestmove_flipped_cases":sum(x["actual_terminal_bestmove_flipped"] for x in cases),
      "native_SEE_operator_mutations":0,
      "not_proven_natural_TT_SEE_mediation":True,
      "study":"POST_R1_DEVELOPMENT_ONLY_NOT_INDEPENDENT_HELDOUT"}
    return {"schema":SCHEMA,"study":STUDY,"new_licensed_source_sha256":SOURCE_SHA,
            "untreated_stageA_sha256":STAGEA_SHA,"cases":cases,"summary":summary}

def main():
    p=argparse.ArgumentParser()
    for arg in ("source","stagea","engine","out"):p.add_argument("--"+arg,required=True)
    a=p.parse_args()
    d=run(frozen(a.source,SOURCE_SHA),frozen(a.stagea,STAGEA_SHA),a.engine)
    dst=Path(a.out);dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(d,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("C3X023_T1_EXACT_SEARCH_STATE_NATIVE_SEE_SOURCE_VERDICT",d["summary"],
          hashlib.sha256(dst.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
