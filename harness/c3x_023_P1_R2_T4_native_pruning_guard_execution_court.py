#!/usr/bin/env python3
"""T4 exact C++ taken-continue vs passed-guard observer: two sealed T3 sites.

DEVELOPMENT follow-up, precommitted before first T4 native branch run.
Before any T4 interpretation, T3 with inactive observer must reproduce
its original private artifact byte-for-byte. This harness only observes.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_022_P2_two_stage_exact_move_scout import native_world,source_depth_ladder
from c3x_023_P1_R1_licensed32_TT_FIRST_native_common_SEE_node_court import SOURCE_SHA,STAGEA_SHA,frozen
from c3x_023_P1_R2_T3_strict_SEE_TT_two_by_two_source_court import prereg,T2_JSON_SHA,ELIGIBLE

ARMS=((0,"SHAM","TT0_SEE_SHAM"),(1,"SHAM","TT1_SEE_SHAM"),
      (0,"FLIP","TT0_SEE_FLIP"),(1,"FLIP","TT1_SEE_FLIP"))
LEGACY_T3_RAW="be2242388f50fc9e0d392a6bde20d624ed02ebc8a6149c13ecccd951ff312626"
SCHEMA="c3x023-P1-R2-T4-two-source-exact-native-branch-pruning-witness-v1"

def run_arm(engine,world,clock,order,role,scope,t,tt_first,policy):
    kwargs={"fen_clocks":clock,"allow_empty_lineage":True,
            "t3_target":t,"t3_policy":policy,"t4_branch_audit":True,
            "see_watch":{"key64":scope["physical"]["key64"],
                         "root_call":scope["root_calls"][0],
                         "policy":"OBS","passive_ancestry":True},
            "native_use_watch":{"key64":scope["physical"]["key64"],
                                "root_call":scope["root_calls"][0]}}
    if tt_first:
        pair={k:scope[k] for k in ("physical","root_calls","root_candidate_native")}
        kwargs["tt_reader_filters"]=mask_filters(RULES[role],pair,"FIRST")
    mode="V" if tt_first else "OBS"
    target=scope["physical"] if tt_first else None
    first=play(engine,world,order,mode,target,**kwargs)
    second=play(engine,world,order,mode,target,**kwargs)
    need(first==second,"T4_COLD_PAIR_NATIVE_NOT_REPRODUCIBLE")
    see=first["native_T3_exact_source_contact_events"]
    guards=first["native_T4_actual_source_guard_events"]
    need(len(see)==len(guards)==1,"T4_MISSING_OR_MULTIPLE_EXACT_SOURCE_GUARDS")
    event,guard=see[0],guards[0]
    need(event["kind"]=="contact" and
         event["key64"]==guard["key64"]==int(t["key64"]) and
         event["root_call"]==guard["root_call"]==t["root_call"] and
         event["site"]==guard["site"]==t["site"] and
         guard["exact_sequence"]==1,
         "T4_GUARD_NOT_SAME_SOURCE_AS_T3_CONTACT")
    original=t["original_SEE_Boolean"]
    delivered=(1-original if policy=="FLIP" else original)
    expected="ACTUAL_CONTINUE" if delivered==0 else "PASSED_SEE_GUARD"
    need(event["original"]==original and event["delivered"]==delivered and
         event["altered"]==(policy=="FLIP") and
         guard["decision"]==expected,"T4_ACTUAL_CPP_BRANCH_CONTRADICTS_BOOLEAN")
    blocks=[b for b in first["blocks"] if b["kind"]=="reader_block"]
    need(bool(blocks)==bool(tt_first),"T4_TT_FIRST_DELIVERY_MISMATCH")
    if tt_first:
        need(all(b["key64"]==scope["physical"]["key64"] and
                 b["slot"]==scope["physical"]["slot"] and
                 b["epoch"]==scope["physical"]["epoch"] for b in blocks),
             "T4_TT_PHYSICAL_SOURCE_MISMATCH")
        lineage=verified_reader_lineage(first)
        need(lineage["all_valid"] and lineage["count"]>=len(blocks),
             "T4_TT_WRITER_READER_NOT_VERIFIED")
    return {"status":"VALID_EXACT_T4_SOURCE_BRANCH_WITNESS",
            "actual_source_decision":guard["decision"],
            "original_SEE_boolean":original,"delivered_SEE_boolean":delivered,
            "actual_TT_FIRST_source_contact":bool(blocks),
            "final_UCI":first["UCI"],
            "root_depth_history":source_depth_ladder(first["root_events"]),
            "cold_exact":True}

def audit(source,stageA,presealed,source_target,engine,receipt):
    selected=prereg(source,stageA,presealed,source_target)
    need(len(selected)==2 and
         {k for k,_ in selected}==set(ELIGIBLE),"T4_CASES_CHANGED")
    need(receipt["schema"]=="c3x023-P1-R2-T3-two-preregistered-SEE-pruning-events-cross-real-physical-TT-first-v1",
         "T4_HISTORICAL_RECEIPT_WRONG")
    historic={int(c["game_id"]):c for c in receipt["root_cases"]}
    keys={"TT0_SEE_SHAM":"TT0_SEE_SHAM","TT1_SEE_SHAM":"TT1_SEE_SHAM",
          "TT0_SEE_FLIP":"TT0_SEE_FLIP","TT1_SEE_FLIP":"TT1_SEE_FLIP"}
    cases=[]
    for (gid,order,role),t in selected:
        src=source["per_ecology"]["may2026_broadcast"]["selected"][gid-1]
        old=stageA["ecologies"]["may2026_broadcast"]["cases"][gid-1]
        need(src["id"]==old["id"]==gid,"T4_SOURCE_SELECTION_CHANGED")
        scope=old["worlds"][order]["roles"][role]
        need(scope["status"]=="FIRST_SOURCE_PAIR_PRE_OUTCOME","T4_SOURCE_SCOPE_NOT_FIRST")
        world,clock,_=native_world(src)
        observed={}
        # Physical TT & SEE control shams MUST precede any T4-flip observation.
        for use_tt,policy,label in ARMS:
            o=run_arm(engine,world,clock,order,role,scope,t,use_tt,policy)
            h=historic[gid]["arms"][keys[label]]
            u=o["final_UCI"]
            need(u["bestmove"]==h["bestmove"] and
                 u["nodes"]==h["nodes"] and
                 u["score_kind"]=="cp" and u["score_value"]==h["score_cp"],
                 "T4_OBSERVER_CHANGED_ORIGINAL_T3_UCI_NODES_SCORE")
            observed[label]=o
        case={"game_id":gid,"root_order":order,"role":role,
              "source_site":t["site"],"arms":observed}
        expected=["PASSED_SEE_GUARD" if t["original_SEE_Boolean"]==1
                  else "ACTUAL_CONTINUE", "ACTUAL_CONTINUE" if
                  t["original_SEE_Boolean"]==1 else "PASSED_SEE_GUARD"]
        need(all(observed[z]["actual_source_decision"]==expected[0]
                 for z in ("TT0_SEE_SHAM","TT1_SEE_SHAM")) and
             all(observed[z]["actual_source_decision"]==expected[1]
                 for z in ("TT0_SEE_FLIP","TT1_SEE_FLIP")),
             "T4_SOURCE_BRANCH_PATH_WRONG")
        cases.append(case)
        print("C3X023_T4_CPP_ACTUAL_PRUNING_BRANCH",gid,order,role,
              {k:v["actual_source_decision"] for k,v in observed.items()},flush=True)
    return {"schema":SCHEMA,
            "status":"T4_NATIVE_ACTUAL_GUARD_OBSERVED_TWO_DEVELOPMENT_CASES",
            "case_count":len(cases),
            "arm_worlds":8,"cold_engine_runs":16,
            "pruning_branch_is_not_entire_descendant_survival":True,
            "natural_TT_SEE_mediation_proven":False,
            "prospective_independent_M3":False,"cases":cases}

def main():
    p=argparse.ArgumentParser()
    for k in ("source","stagea","presealed","source-targets","engine","t3-receipt","out"):
        p.add_argument("--"+k,required=True)
    a=p.parse_args()
    receipt=json.loads(Path(a.t3_receipt).read_text())
    out=audit(frozen(a.source,SOURCE_SHA),frozen(a.stagea,STAGEA_SHA),
              json.loads(Path(a.presealed).read_text()),
              frozen(a.source_targets,T2_JSON_SHA),a.engine,receipt)
    f=Path(a.out);f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("C3X023_T4_NATIVE_CPP_GUARD_WITNESS_SHA256",
          hashlib.sha256(f.read_bytes()).hexdigest(),flush=True)

if __name__=="__main__":
    main()
