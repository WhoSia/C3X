#!/usr/bin/env python3
"""Source log-order diagnostic: does the SAME native SEE event happen AFTER TT?

Post R1 outcome-conditioned 6 May cases: DEVELOPMENT, never heldout.
No SEE actuator. Read-only native SEE tracing. Original TT source as actual
native used-value or cutoff event; treated TT full64 writer-reader block.
"""
import argparse,hashlib,json
from pathlib import Path
from collections import Counter
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_022_P2_two_stage_exact_move_scout import native_world
from c3x_023_P1_same_descendant_SEE_node_matcher import candidates,identity
from c3x_023_P1_R1_licensed32_TT_FIRST_native_common_SEE_node_court import (
   SOURCE_SHA,STAGEA_SHA,frozen)
STUDY="POST_R1_DEVELOPMENT_CHRONOLOGY_NOT_NEW_HELDOUT_FORECAST"
SELECTED=((1,"O","STRICT"),(8,"O","BROAD"),(11,"F","STRICT"),
          (12,"F","STRICT"),(2,"O","STRICT"),(3,"O","STRICT"))
SCHEMA="c3x023-P1-R2-T0-real-TT-source-and-descendant-SEE-log-order-v1"

def cold(engine,world,clocks,order,mode,target=None,filter=None,watch=None):
    kw={"fen_clocks":clocks,"allow_empty_lineage":True,
        "ordered_source_trace":True,
        "native_use_watch":{"key64":watch["key64"],"root_call":watch["root_call"]},
        "see_watch":{**watch,"policy":"OBS","passive_ancestry":True}}
    if filter is not None:kw["tt_reader_filters"]=filter
    a=play(engine,world,order,mode,target,**kw)
    b=play(engine,world,order,mode,target,**kw)
    need(a==b,"P1_R2_T0_COLD_SOURCE_CHRONOLOGY_MISMATCH")
    need(all(e["original"]==e["delivered"] and e["altered"]==0
             for e in a["native_see_events"] if e["kind"]=="witness"),
         "P1_R2_T0_SEE_POLICY_MUST_REMAIN_PASSIVE")
    return a

def source_lines(x,source,kind,role):
    triple=role["physical"]
    out=[]
    for line in x["ordered_source_operator_trace"]:
        e=line["fields"]
        if line["source"]!=source or e.get("kind")!=kind:continue
        if e.get("key64")!=triple["key64"]:continue
        if e.get("root_call")!=role["root_calls"][0]:continue
        if source=="physical_TT" and (e.get("slot")!=triple["slot"] or
           e.get("epoch")!=triple["epoch"]):continue
        out.append(line)
    return out

def post_source_match(obs,V,role):
    used=source_lines(obs,"TT_value_used","used",role)
    used+=source_lines(obs,"TT_value_used","main_cutoff",role)
    used+=source_lines(obs,"TT_value_used","qsearch_cutoff",role)
    blocked=source_lines(V,"physical_TT","reader_block",role)
    if not used or not blocked:
        return {"status":"HOLD_NATIVE_TT_USE_OR_ACTUAL_SOURCE_BLOCK_MISSING",
                "observed_real_source_events":len(used),
                "blocked_real_source_events":len(blocked),"strict_post_source_matches":0}
    baseline_start=min(x["line_ordinal"] for x in used)
    treated_start=min(x["line_ordinal"] for x in blocked)
    corresponding=candidates(obs["native_see_events"],V["native_see_events"],True)
    def seen_trace(events):
        groups={}
        for e in events:
            if e["source"]!="native_SEE" or e["fields"]["kind"]!="witness":continue
            k=identity(e["fields"])
            groups.setdefault(k,[]).append(e["line_ordinal"])
        return groups
    original_events=seen_trace(obs["ordered_source_operator_trace"])
    counterfactual_events=seen_trace(V["ordered_source_operator_trace"])
    after=[]
    before=[]
    for record in corresponding["matched"]:
        key=tuple(record["exact_source_identity"][k] for k in
                   ("root_call","root_move","key64","parent_key64","path_hash",
                    "path_length","move","site","threshold"))
        first=original_events.get(key,[])
        second=counterfactual_events.get(key,[])
        need(len(first)==len(second)==1,"T0_NONUNIQUE_FULL_LIVE_EVENT")
        event={"site":record["exact_source_identity"]["site"],
               "post_native_TT_value_use_in_original":first[0]>baseline_start,
               "post_original_selected_TT_FIRST_block_in_treatment":second[0]>treated_start,
               "original_SEE_source_line_ordinal":first[0],
               "treated_SEE_source_line_ordinal":second[0],
               "relative_line_delta_after_source_original":first[0]-baseline_start,
               "relative_line_delta_after_source_treatment":second[0]-treated_start}
        (after if event["post_native_TT_value_use_in_original"] and
                   event["post_original_selected_TT_FIRST_block_in_treatment"]
         else before).append(event)
    censored=corresponding["observed_prefix_censored"]
    return {
       "status":("AFTER_NATIVE_TT_REAL_USE_COMMON_SOURCE_SEE_FOUND" if after
                 else "HOLD_CENSORED_NO_POST_TT_COMMON_SEE" if censored
                 else "NO_POST_TT_COMMON_SEE_IN_OBSERVED_SCOPE"),
       "source_original_native_use_first_line_ordinal":baseline_start,
       "source_treated_physical_block_first_line_ordinal":treated_start,
       "observed_real_source_events":len(used),
       "blocked_real_source_events":len(blocked),
       "source_path_identical_pre_or_post_total":len(corresponding["matched"]),
       "strict_post_source_matches":len(after),
       "post_event_sites":dict(sorted(Counter(x["site"] for x in after).items())),
       "preceding_or_unqualified_shared_events":len(before),
       "source_prefix_censored":censored,
       "first_post_tt_real_source_event":after[0] if after else None,
       "proves_same_search_alpha_beta_depth_state":False,
       "claimed_natural_mediation":False
    }

def run(source,stagea,engine):
    need(len(source["per_ecology"]["may2026_broadcast"]["selected"])==16,
         "P1_R2_T0_SOURCE_NOT_NEW_MAY16")
    results=[]
    for gid,order,role in SELECTED:
        row=source["per_ecology"]["may2026_broadcast"]["selected"][gid-1]
        earlier=stagea["ecologies"]["may2026_broadcast"]["cases"][gid-1]
        need(row["id"]==earlier["id"]==gid,"R2_T0_NOT_FROZEN_GAME")
        target=earlier["worlds"][order]["roles"][role]
        need(target["status"]=="FIRST_SOURCE_PAIR_PRE_OUTCOME",
             "R2_T0_PRE_REGISTERED_NONELIGIBLE_ROLE")
        w,clocks,_=native_world(row)
        target_key={"key64":target["physical"]["key64"],
                    "root_call":target["root_calls"][0]}
        original=cold(engine,w,clocks,order,"OBS",watch=target_key)
        need(original["UCI"]==earlier["worlds"][order]["baseline_UCI"],
             "R2_T0_ORIGINAL_SAME_SOURCE_UCI_CHANGED")
        pair={"physical":target["physical"],"root_calls":target["root_calls"],
              "root_candidate_native":target["root_candidate_native"]}
        first=cold(engine,w,clocks,order,"V",target["physical"],
                   filter=mask_filters(RULES[role],pair,"FIRST"),watch=target_key)
        blocks=[x for x in first["blocks"] if x["kind"]=="reader_block"]
        need(blocks and all(x["key64"]==target["physical"]["key64"] and
             x["slot"]==target["physical"]["slot"] and
             x["epoch"]==target["physical"]["epoch"] and
             x["root_call"]==target["root_calls"][0] and
             x["root_move"]==target["root_candidate_native"] for x in blocks),
             "R2_T0_MISMATCHED_PHYSICAL_TT_READER")
        lineage=verified_reader_lineage(first)
        need(lineage["all_valid"] and lineage["count"]>=len(blocks),
             "R2_T0_WRITER_LINEAGE_PROOF_FAIL")
        analysis=post_source_match(original,first,target)
        record={"game_id":gid,"order":order,"source_role":role,
                "TT_FIRST_actual_physical_contact":True,
                "first_see_chronological_result":analysis,
                "actual_move_change":original["UCI"]["bestmove"]!=first["UCI"]["bestmove"],
                "SEE_Boolean_interventions":0,
                "full_raw_source_key_and_original_TWIC_PGN_not_distributed":True}
        results.append(record)
        print("C3X023_P1_R2_T0_CHRONOLOGICAL_CAUSAL_ORDER",gid,order,role,
              "status",analysis["status"],"post_common",analysis["strict_post_source_matches"],
              "TT_move_changed",record["actual_move_change"],flush=True)
    out={"schema":SCHEMA,"study":STUDY,"source_sha256":SOURCE_SHA,
         "stageA_sha256":STAGEA_SHA,"cases":results}
    out["summary"]={
      "development_case_count":len(SELECTED),
      "post_source_common_SEE_positive_case_count":sum(
           v["first_see_chronological_result"]["strict_post_source_matches"]>0 for v in results),
      "post_source_common_SEE_distinct_native_event_prefix_count":sum(
           v["first_see_chronological_result"]["strict_post_source_matches"] for v in results),
      "observed_prefix_censored_count":sum(
           v["first_see_chronological_result"].get("source_prefix_censored",False) for v in results),
      "real_native_TT_FIRST_source_delivered_cases":sum(v["TT_FIRST_actual_physical_contact"] for v in results),
      "changed_bestmove_cases":sum(v["actual_move_change"] for v in results),
      "SEE_Boolean_interventions":0,
      "aligned_search_depth_and_alpha_beta":"NOT_YET_INSTRUMENTED",
      "source_temporal_match_not_sufficient_to_prove_natural_mediation":True}
    return out

def main():
    p=argparse.ArgumentParser()
    for k in ("source","stagea","engine","out"):p.add_argument("--"+k,required=True)
    q=p.parse_args()
    x=run(frozen(q.source,SOURCE_SHA),frozen(q.stagea,STAGEA_SHA),q.engine)
    path=Path(q.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(x,sort_keys=True,indent=2)+"\n")
    print("C3X023_P1_R2_T0_TRUE_NATIVE_POST_TT_SOURCE_SEE_CHRONOLOGY",
          x["summary"],hashlib.sha256(path.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
