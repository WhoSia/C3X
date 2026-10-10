#!/usr/bin/env python3
"""T1 six prespecified post-R1 development arms: read-only full source-state audit.

No SEE flip and no change to frozen old M0/M1. The native callsite overlay
provides ply/depth/alpha/beta/rule50 and optional occupied bitboard.
"""
import argparse,hashlib,json
from pathlib import Path
from collections import Counter
from c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev import (
    SELECTED,cold,source_lines)
from c3x_023_P1_R1_licensed32_TT_FIRST_native_common_SEE_node_court import (
    SOURCE_SHA,STAGEA_SHA,frozen)
from c3x_022_P2_two_stage_exact_move_scout import native_world
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_023_P1_same_descendant_SEE_node_matcher import identity,candidates

FULL_STATE=("state_ply","state_depth","state_alpha","state_beta","state_rule50",
            "state_occupied_given","state_occupied64")
SCHEMA="c3x023-P1-R2-T1-same-path-native-SEE-full-window-state-observer-v1"

def match_full_state(obs,V,role):
    used=[]
    for kind in ("used","main_cutoff","qsearch_cutoff"):
        used+=source_lines(obs,"TT_value_used",kind,role)
    blocked=source_lines(V,"physical_TT","reader_block",role)
    if not used or not blocked:
        return {"status":"HOLD_NO_REAL_SCORE_USE_OR_SOURCE_READER",
                "path_after_TT":0,"full_window_state_matches":0,
                "different_state_after_TT":0}
    start_o=min(x["line_ordinal"] for x in used)
    start_v=min(x["line_ordinal"] for x in blocked)
    seen=candidates(obs["native_see_events"],V["native_see_events"],True)
    def get_events(x):
        d={}
        for e in x["ordered_source_operator_trace"]:
            if e["source"]!="native_SEE" or e["fields"]["kind"]!="witness":continue
            k=identity(e["fields"])
            d.setdefault(k,[]).append(e)
        return d
    left=get_events(obs);right=get_events(V)
    full=[];different=[]
    for pair in seen["matched"]:
        key=tuple(pair["exact_source_identity"][k] for k in (
             "root_call","root_move","key64","parent_key64","path_hash",
             "path_length","move","site","threshold"))
        a=left.get(key,[]);b=right.get(key,[])
        if len(a)!=1 or len(b)!=1:continue
        if a[0]["line_ordinal"]<=start_o or b[0]["line_ordinal"]<=start_v:continue
        aa=a[0]["fields"];bb=b[0]["fields"]
        for field in FULL_STATE:
            if field not in aa or field not in bb:
                raise ValueError("T1_NATIVE_SEE_SOURCE_FULL_STATE_MISSING_"+field)
        if any(aa[k]!=bb[k] for k in ("original","delivered")):
            raise ValueError("T1_NATIVE_SEE_DETERMINISM_VIOLATION")
        record={"site":aa["site"],"state_equal":all(aa[k]==bb[k] for k in FULL_STATE),
                "differing_state_fields":[k for k in FULL_STATE if aa[k]!=bb[k]],
                "original_see_Boolean_same":aa["original"]==bb["original"],
                "native_full64_chess_ancestry_equal":True,
                "source_search_window_equal":all(aa[k]==bb[k] for k in FULL_STATE),
                "full_original_ancestor_key_vector_bytes_compared":False}
        (full if record["state_equal"] else different).append(record)
    n=len(full)+len(different)
    censored=seen["observed_prefix_censored"]
    return {"status":"FULL_OBSERVED_SEARCH_WINDOW_EQUAL" if full else
            "POST_TT_SAME_CHESS_PATH_DIFFERENT_SEARCH_STATE" if different else
            "HOLD_CENSORED_NO_POST_TT_COMMON_EVENT" if censored else
            "NO_POST_TT_COMMON_EVENT_IN_LOGGED_SCOPE",
            "path_after_TT":n,
            "full_window_state_matches":len(full),
            "different_state_after_TT":len(different),
            "mismatch_fields":dict(sorted(Counter(field for x in different
                                               for field in x["differing_state_fields"]).items())),
            "source_sites_with_full_window_matches":dict(sorted(Counter(x["site"] for x in full).items())),
            "first_full_match":full[0] if full else None,
            "observed_source_prefix_censored":censored,
            "PV_node_and_consuming_branch_not_yet_instrumented":True,
            "equal_chess_source_and_window_is_not_natural_mediation_proof":True}

def execute(source,stageA,engine):
    records=[]
    for gid,order,role in SELECTED:
        row=source["per_ecology"]["may2026_broadcast"]["selected"][gid-1]
        old=stageA["ecologies"]["may2026_broadcast"]["cases"][gid-1]
        target=old["worlds"][order]["roles"][role]
        if target["status"]!="FIRST_SOURCE_PAIR_PRE_OUTCOME":
            raise ValueError("T1_PRECOMMITTED_PAIR_CHANGED")
        w,clocks,_=native_world(row)
        watch={"key64":target["physical"]["key64"],"root_call":target["root_calls"][0]}
        obs=cold(engine,w,clocks,order,"OBS",watch=watch)
        if obs["UCI"]!=old["worlds"][order]["baseline_UCI"]:
            raise ValueError("T1_PASSIVE_SOURCE_CHANGED_NATIVE_UCI")
        pair={"physical":target["physical"],"root_calls":target["root_calls"],
              "root_candidate_native":target["root_candidate_native"]}
        V=cold(engine,w,clocks,order,"V",target["physical"],
               filter=mask_filters(RULES[role],pair,"FIRST"),watch=watch)
        blocks=[x for x in V["blocks"] if x["kind"]=="reader_block"]
        if not blocks or any(x["key64"]!=target["physical"]["key64"] or
             x["slot"]!=target["physical"]["slot"] or
             x["epoch"]!=target["physical"]["epoch"] or
             x["root_call"]!=target["root_calls"][0] or
             x["root_move"]!=target["root_candidate_native"] for x in blocks):
            raise ValueError("T1_REAL_PHYSICAL_TT_BLOCK_SOURCE_WRONG")
        proof=verified_reader_lineage(V)
        if not proof["all_valid"] or proof["count"]<len(blocks):
            raise ValueError("T1_NATIVE_WRITER_READER_LINEAGE_FAILURE")
        result=match_full_state(obs,V,target)
        records.append({"game_id":gid,"order":order,"role":role,
                        "TT_first_contact":True,
                        "bestmove_changed":obs["UCI"]["bestmove"]!=V["UCI"]["bestmove"],
                        "full_state_audit":result,"SEE_interventions":0})
        print("C3X023_P1_R2_T1_FULL_NATIVE_SEARCH_STATE",gid,order,role,
              result["status"],result["full_window_state_matches"],
              result["different_state_after_TT"],flush=True)
    return {"schema":SCHEMA,"study":"SIX_POST_R1_DEVELOPMENT_CASES_NOT_PROSPECTIVE",
        "original_licensed32_SHA256":SOURCE_SHA,"untreated_StageA_SHA256":STAGEA_SHA,
        "cases":records,
        "summary":{
          "development_cases":len(records),
          "real_TT_FIRST_contacts":sum(x["TT_first_contact"] for x in records),
          "cases_with_same_path_and_full_source_search_state":
              sum(x["full_state_audit"]["full_window_state_matches"]>0 for x in records),
          "same_path_same_full_native_logged_search_state_events":
              sum(x["full_state_audit"]["full_window_state_matches"] for x in records),
          "same_path_but_different_native_search_state_events":
              sum(x["full_state_audit"]["different_state_after_TT"] for x in records),
          "SEE_Boolean_interventions":0,
          "full_PV_and_exact_ancestor_vector_observed":False,
          "natural_mediation_identified":False}}

def main():
    p=argparse.ArgumentParser()
    for x in ("source","stagea","engine","out"):p.add_argument("--"+x,required=True)
    q=p.parse_args()
    d=execute(frozen(q.source,SOURCE_SHA),frozen(q.stagea,STAGEA_SHA),q.engine)
    out=Path(q.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print("C3X023_P1_R2_T1_SEARCH_STATE_AUDIT",d["summary"],
          hashlib.sha256(out.read_bytes()).hexdigest())
if __name__=="__main__":main()
