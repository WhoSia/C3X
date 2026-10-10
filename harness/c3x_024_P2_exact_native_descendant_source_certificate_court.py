#!/usr/bin/env python3
"""P2 C3 native exact SEE guard -> make move -> child entry -> return.
Runs development-only 2 source events x 4 arms x two cold repeats. No new M3.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_022_P2_two_stage_exact_move_scout import native_world,source_depth_ladder
from c3x_023_P1_R1_licensed32_TT_FIRST_native_common_SEE_node_court import SOURCE_SHA,STAGEA_SHA,frozen
from c3x_023_P1_R2_T3_strict_SEE_TT_two_by_two_source_court import prereg,T2_JSON_SHA,ELIGIBLE
from c3x_023_P1_R2_T4_native_pruning_guard_execution_court import ARMS,LEGACY_T3_RAW

SCHEMA="c3x024-P2-exact-guard-to-do-move-to-child-entry-to-parent-return-v1"
FULL=("GUARD_PASS","DO_MOVE_EXECUTED","CHILD_ENTERED","CHILD_RETURNED_TO_PARENT")
def arm(engine,world,clock,order,role,scope,t,use_tt,policy,historic):
    kwargs={"fen_clocks":clock,"allow_empty_lineage":True,
            "t3_target":t,"t3_policy":policy,"t4_branch_audit":True,
            "p2_descendant_audit":True,
            "see_watch":{"key64":scope["physical"]["key64"],
                         "root_call":scope["root_calls"][0],
                         "policy":"OBS","passive_ancestry":True},
            "native_use_watch":{"key64":scope["physical"]["key64"],
                                "root_call":scope["root_calls"][0]}}
    if use_tt:
        pair={k:scope[k] for k in ("physical","root_calls","root_candidate_native")}
        kwargs["tt_reader_filters"]=mask_filters(RULES[role],pair,"FIRST")
    first=play(engine,world,order,"V" if use_tt else "OBS",
               scope["physical"] if use_tt else None,**kwargs)
    second=play(engine,world,order,"V" if use_tt else "OBS",
                scope["physical"] if use_tt else None,**kwargs)
    need(first==second,"P2_COLD_NATIVE_REPLAY_CHANGED")
    need(first["UCI"]["bestmove"]==historic["bestmove"] and
         first["UCI"]["nodes"]==historic["nodes"] and
         first["UCI"]["score_kind"]=="cp" and
         first["UCI"]["score_value"]==historic["score_cp"],
         "P2_PASSIVE_OBSERVER_CHANGED_T3_UCI_NODES_SCORE")
    t3=first["native_T3_exact_source_contact_events"]
    t4=first["native_T4_actual_source_guard_events"]
    p2=first["native_C3_source_descendant_events"]
    need(len(t3)==len(t4)==1 and len(p2)>=1,"P2_MISSING_EXACT_GUARD")
    g=t4[0]
    need(t3[0]["kind"]=="contact" and
         t3[0]["site"]==g["site"]==t["site"] and
         t3[0]["key64"]==g["key64"]==int(t["key64"]) and
         g["exact_sequence"]==1 and
         t3[0]["root_call"]==g["root_call"]==t["root_call"],
         "P2_T3_T4_EXACT_JOIN_FAILED")
    delivered=int(t["original_SEE_Boolean"])^(policy=="FLIP")
    expected="ACTUAL_CONTINUE" if delivered==0 else "PASSED_SEE_GUARD"
    need(g["decision"]==expected and
         t3[0]["delivered"]==delivered,"P2_GUARD_BOOLEAN_MISMATCH")
    need(len(p2)<=4 and
         all(e["site"]==t["site"] and
             e["exact_sequence"]==1 and
             e["root_call"]==t["root_call"] and
             e["native_move"]==t["move"] for e in p2) and
         [e["event_ordinal"] for e in p2]==list(range(1,len(p2)+1)),
         "P2_UNTRUSTED_EXACT_SOURCE_SEQUENCE")
    events=tuple(e["event"] for e in p2)
    if delivered==0:
        need(events==("GUARD_CONTINUE",),"P2_CONTINUED_BRANCH_HAS_DESCENDANT")
        status="C2_ACTUAL_CONTINUE_NO_BRANCH"
    else:
        need(events[0]=="GUARD_PASS","P2_PASSED_GUARD_UNRECORDED")
        if events==FULL:
            a,b,c,d=p2
            need(a["key64"]==a["parent64"]==int(t["key64"]) and
                 b["key64"]==c["key64"]==d["key64"]==
                        a["expected_child64"] and
                 b["parent64"]==c["parent64"]==d["parent64"]==
                        a["parent64"] and
                 b["did_move"]==c["did_move"]==d["did_move"]==1 and
                 c["child_entered"]==d["child_entered"]==1,
                 "P2_C3_PARENT_CHILD_KEY_OR_STATE_INVALID")
            status="C3_ACTUAL_CHILD_SOURCE_ENTRY_AND_RETURN_CERTIFIED"
        else:
            need(all(e in FULL for e in events),"P2_UNSUPPORTED_EVENT")
            status="C3_HOLD_INCOMPLETE_SOURCE_CHAIN"
    blocks=[b for b in first["blocks"] if b["kind"]=="reader_block"]
    need(bool(blocks)==bool(use_tt),"P2_PHYSICAL_TT_FIRST_MISMATCH")
    if use_tt:
        need(all(b["key64"]==scope["physical"]["key64"] and
                 b["slot"]==scope["physical"]["slot"] and
                 b["epoch"]==scope["physical"]["epoch"] for b in blocks),
             "P2_PHYSICAL_TT_TARGET_MISMATCH")
        verified=verified_reader_lineage(first)
        need(verified["all_valid"] and verified["count"]>=len(blocks),
             "P2_SOURCE_PHYSICAL_WRITER_READER_INVALID")
    return {"certificate_status":status,"source_decision":g["decision"],
            "source_event_sequence":list(events),
            "source_events":p2,"real_TT_FIRST_contact":bool(blocks),
            "UCI":first["UCI"],"root_depth":source_depth_ladder(first["root_events"]),
            "cold_exact_replay":True}

def audit(source,stageA,presealed,source_target,engine,receipt):
    selected=prereg(source,stageA,presealed,source_target)
    need(len(selected)==2 and {key for key,_ in selected}==set(ELIGIBLE),
         "P2_CASE_LOCK_CHANGED")
    old={int(c["game_id"]):c for c in receipt["root_cases"]}
    cases=[]
    for (gid,order,role),t in selected:
        s=source["per_ecology"]["may2026_broadcast"]["selected"][gid-1]
        a=stageA["ecologies"]["may2026_broadcast"]["cases"][gid-1]
        need(s["id"]==a["id"]==gid,"P2_SOURCE_GAME_ID_CHANGED")
        scope=a["worlds"][order]["roles"][role]
        need(scope["status"]=="FIRST_SOURCE_PAIR_PRE_OUTCOME","P2_SCOPE_NOT_FROZEN")
        world,clock,_=native_world(s)
        cells={}
        for use_tt,policy,label in ARMS:
            cells[label]=arm(engine,world,clock,order,role,scope,t,use_tt,policy,
                             old[gid]["arms"][label])
        cases.append({"game_id":gid,"root_order":order,"role":role,
                      "source_site":t["site"],"arms":cells})
        print("C3X024_P2_NATIVE_C3_PATH",gid,
              {k:(v["certificate_status"],v["source_event_sequence"])
               for k,v in cells.items()},flush=True)
    statuses=[a["certificate_status"] for c in cases for a in c["arms"].values()]
    completed=sum(s=="C3_ACTUAL_CHILD_SOURCE_ENTRY_AND_RETURN_CERTIFIED" for s in statuses)
    holds=sum(s=="C3_HOLD_INCOMPLETE_SOURCE_CHAIN" for s in statuses)
    continue_n=sum(s=="C2_ACTUAL_CONTINUE_NO_BRANCH" for s in statuses)
    return {"schema":SCHEMA,"source_cases":2,"arm_worlds":8,
            "cold_native_runs":16,"source_guard_contacts":8,
            "C3_child_certificates":completed,"C2_continue_certificates":continue_n,
            "C3_incomplete_HOLD":holds,
            "scientific_claim":"conditional source-specific actual descendant traversal, not natural TT-to-SEE mediation",
            "prospective_forecast_M3_improved":False,
            "new_independent_games":0,"source_cases_development_only":True,
            "T3_disabled_exact_SHA_expected":LEGACY_T3_RAW,
            "cases":cases}
def main():
    p=argparse.ArgumentParser()
    for field in ("source","stagea","presealed","source-targets","engine","t3-receipt","out"):
        p.add_argument("--"+field,required=True)
    a=p.parse_args()
    old=json.loads(Path(a.t3_receipt).read_text())
    result=audit(frozen(a.source,SOURCE_SHA),frozen(a.stagea,STAGEA_SHA),
                 json.loads(Path(a.presealed).read_text()),
                 frozen(a.source_targets,T2_JSON_SHA),a.engine,old)
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("C3X024_P2_C3_NATIVE_SOURCE_JSON_SHA256",
          hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":
    main()
