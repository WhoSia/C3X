#!/usr/bin/env python3
"""C3X024 P2-R2 fail-closed source C3b descendant-to-ancestor/root trace."""
import argparse,json,hashlib
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import need
from c3x_022_P2_two_stage_exact_move_scout import native_world
from c3x_023_P1_R1_licensed32_TT_FIRST_native_common_SEE_node_court import SOURCE_SHA,STAGEA_SHA,frozen
from c3x_023_P1_R2_T3_strict_SEE_TT_two_by_two_source_court import prereg,T2_JSON_SHA,ELIGIBLE
from c3x_023_P1_R2_T4_native_pruning_guard_execution_court import ARMS
from c3x_024_P2_exact_native_descendant_source_certificate_court import arm
SCHEMA="c3x024-P2-R2-exact-source-ancestor-return-root-path-v1"
def adjudicate(o):
    events=o["C3b_source_ancestor_events"]
    if o["source_decision"]=="ACTUAL_CONTINUE":
        need(not events,"C3B_GUARD_CONTINUE_MUST_NOT_ACTIVATE_ANCESTORS")
        return {"status":"C2_ACTUAL_CONTINUE","events":[],"candidate_edges":0,"root_reached":False}
    need(o["certificate_status"]=="C3_ACTUAL_CHILD_SOURCE_ENTRY_AND_RETURN_CERTIFIED",
         "C3B_REQUIRES_EXACT_SOURCE_C3A_CHILD_CHAIN")
    need(bool(events) and events[0]["event"]=="ANCESTOR_SNAPSHOT",
         "C3B_SOURCE_SNAPSHOT_NOT_OBSERVED")
    top=events[0]["ply"]
    need(0<=top<128 and events[0]["root_call"]>0,"C3B_INVALID_SOURCE_DEPTH")
    need(len(events)<=2*(top+1)+4,"C3B_BOUNDED_TRACE_EXCEEDED")
    need([e["sequence"] for e in events]==list(range(1,len(events)+1)),
         "C3B_SOURCE_LOG_SEQUENCE_NONMONOTONIC")
    rootcalls={e["root_call"] for e in events}
    need(len(rootcalls)==1,"C3B_ROOT_CALL_DIVERGED")
    expected=[("ANCESTOR_SNAPSHOT",top),("CHILD_VALUE_RETURNED",top)]
    for p in range(top,-1,-1):
        expected.extend((("PARENT_CANDIDATE_VALUE",p),
                         ("ROOT_FRAME_RETURN" if p==0 else "FRAME_RETURN",p)))
    observed=[(e["event"],e["ply"]) for e in events]
    full=(observed==expected)
    if full:
        for idx in range(2,len(events),2):
            candidate,returned=events[idx:idx+2]
            need(candidate["key64"]==returned["key64"] and
                 candidate["ply"]==returned["ply"] and
                 candidate["native_move"]==returned["native_move"],
                 "C3B_NATIVE_PARENT_RETURN_KEY_OR_MOVE_MISMATCH")
        need(events[1]["value"]==events[2]["value"],
             "C3B_CHILD_RETURN_NOT_MATCH_CANDIDATE_VALUE")
    elif any(e["event"]=="ANCESTOR_EDGE_AMBIGUOUS" for e in events):
        full=False
    status=("C3B_FULL_ANCESTOR_TO_ROOT_CANDIDATE_EXECUTED"
            if full else "C3B_PARTIAL_CENSORED_OR_PATH_DIVERGED")
    return {"status":status,"top_ply":top,"root_reached":full,
            "candidate_edges":sum(e["event"]=="PARENT_CANDIDATE_VALUE" for e in events),
            "frame_returns":sum(e["event"] in ("FRAME_RETURN","ROOT_FRAME_RETURN") for e in events),
            "root_candidate_updated":full,
            "source_events":events,
            "caused_final_bestmove":False,
            "natural_TT_SEE_mediation_proven":False}
def audit(source,stageA,presealed,source_target,engine,receipt):
    selected=prereg(source,stageA,presealed,source_target)
    need(len(selected)==2 and {x for x,_ in selected}==set(ELIGIBLE),
         "C3B_CASE_IDENTITIES_CHANGED")
    old={int(c["game_id"]):c for c in receipt["root_cases"]}
    cases=[]
    for (gid,order,role),t in selected:
        src=source["per_ecology"]["may2026_broadcast"]["selected"][gid-1]
        stage=stageA["ecologies"]["may2026_broadcast"]["cases"][gid-1]
        need(src["id"]==stage["id"]==gid,"C3B_FROZEN_GAME_ID_MISMATCH")
        scope=stage["worlds"][order]["roles"][role]
        world,clock,_=native_world(src)
        d={}
        for tt,policy,label in ARMS:
            result=arm(engine,world,clock,order,role,scope,t,tt,policy,
                       old[gid]["arms"][label],c3b=True)
            d[label]={"C3a":result["certificate_status"],
                      "C3b":adjudicate(result),
                      "final_UCI":result["UCI"],
                      "cold_replay_exact":result["cold_exact_replay"]}
        cases.append({"game_id":gid,"root_order":order,"role":role,
                      "source_site":t["site"],"arms":d})
        print("C3X024_P2_R2_SOURCE_ANCESTOR_CERTIFICATES",gid,
              {key:v["C3b"]["status"] for key,v in d.items()},flush=True)
    statuses=[v["C3b"]["status"] for c in cases for v in c["arms"].values()]
    return {"schema":SCHEMA,"source_games":2,"arm_worlds":8,"cold_native_runs":16,
            "actual_continue_arms":statuses.count("C2_ACTUAL_CONTINUE"),
            "full_ancestor_root_arms":statuses.count("C3B_FULL_ANCESTOR_TO_ROOT_CANDIDATE_EXECUTED"),
            "partial_or_diverged_arms":statuses.count("C3B_PARTIAL_CENSORED_OR_PATH_DIVERGED"),
            "old_2025aug_M3_scientific_result":"NEGATIVE_M3_IDENTICAL_M0_ALL_64",
            "natural_TT_SEE_mediation_proven":False,
            "prospective_games":0,
            "selected_examples_development_only":True,
            "cases":cases}
def main():
    p=argparse.ArgumentParser()
    for k in ("source","stagea","presealed","source-targets","engine","t3-receipt","out"):
        p.add_argument("--"+k,required=True)
    a=p.parse_args()
    result=audit(frozen(a.source,SOURCE_SHA),frozen(a.stagea,STAGEA_SHA),
                 json.loads(Path(a.presealed).read_text()),
                 frozen(a.source_targets,T2_JSON_SHA),
                 a.engine,json.loads(Path(a.t3_receipt).read_text()))
    o=Path(a.out);o.parent.mkdir(parents=True,exist_ok=True)
    o.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X024_P2_R2_SOURCE_C3B_FULL_SHA256",
          hashlib.sha256(o.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
