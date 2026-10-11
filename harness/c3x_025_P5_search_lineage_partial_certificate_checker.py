#!/usr/bin/env python3
"""C3X0.25-P5 proof-obligation checker for SOURCE-NATIVE event traces.

A well-typed synthetic event history is only structural admissibility, NEVER
evidence of natural TT->SEE mediation, node equivalence or native execution.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

SCHEMA="c3x025-P5-source-native-event-chain-partial-certificate-v1"
COMMON=("SEE_CALL","BRANCH_DECISION","CHILD_RETURN","ROOT_CANDIDATE","FINAL_UCI")
OBS=("TT_PHYSICAL_READ","TT_SEMANTIC_USE")+COMMON
TREAT=("TT_PHYSICAL_BLOCK",)+COMMON
# Full native search-state identity beyond same board or parent path hash.
STATE_FIELDS=("chess_position","ancestor_vector","root_iteration","retry",
    "root_candidate","native_move","ply","depth","alpha","beta","pv",
    "cut_node","rule50","see_site","see_threshold","see_occupied")
STATE_EQUAL="COMPLETE_STATED_COMPUTATIONAL_FIELDS_EQUAL_NOT_ALL_HIDDEN_STOCKFISH_STATE"

def validate_arm(events:list[dict],arm:str)->dict:
    if arm not in ("OBS","TREAT"):raise ValueError("unknown arm")
    if not events:return {"status":"HOLD_CENSORED_EMPTY_TRACE","events":0}
    seen={}
    prevserial=-1
    kinds=[]
    for i,e in enumerate(events):
        for k in ("id","serial","parent","kind","state"):
            if k not in e:raise ValueError("MISSING_NATIVE_TRACE_FIELD_"+k)
        if not isinstance(e["serial"],int) or e["serial"]<=prevserial:
            raise ValueError("NATIVE_EVENT_SERIAL_NOT_STRICTLY_INCREASING")
        if not isinstance(e["id"],str) or not e["id"] or e["id"] in seen:
            raise ValueError("DUPLICATED_OR_INVALID_SOURCE_EVENT_ID")
        if i and e["parent"]!=events[i-1]["id"]:
            raise ValueError("SOURCE_ANCESTOR_EVENT_POINTER_NOT_EXECUTED_CHAIN")
        if i==0 and e["parent"] is not None:
            raise ValueError("INITIAL_SOURCE_EVENT_NONROOT")
        if e["kind"] not in OBS+("TT_PHYSICAL_BLOCK",):
            raise ValueError("UNKNOWN_SOURCE_OPERATOR")
        if not isinstance(e["state"],dict):
            raise ValueError("NATIVE_STATE_INVALID_TYPE")
        missing=[k for k in STATE_FIELDS if k not in e["state"]]
        if missing:raise ValueError("FULL_COMPUTATIONAL_STATE_FIELDS_MISSING_"+",".join(missing))
        if not e["state"]["ancestor_vector"]:
            raise ValueError("EMPTY_OR_CENSORED_SOURCE_ANCESTOR_VECTOR")
        if not isinstance(e["state"]["alpha"],int) or not isinstance(e["state"]["beta"],int) or e["state"]["alpha"]>=e["state"]["beta"]:
            raise ValueError("UNSOUND_ALPHA_BETA_WINDOW")
        if e["state"]["ply"]<0 or e["state"]["depth"]<0:
            raise ValueError("INVALID_SOURCE_PLY_OR_DEPTH")
        if not isinstance(e["state"]["chess_position"],str) or not e["state"]["chess_position"]:
            raise ValueError("NATIVE_CHESS_POSITION_ID_REQUIRED")
        if e.get("censored",False):
            return {"status":"HOLD_CENSORED_TRACE_WITH_FINITE_PREFIX",
                    "events":i+1,"first_censored_serial":e["serial"]}
        seen[e["id"]]=e
        kinds.append(e["kind"])
        prevserial=e["serial"]
    expected=OBS if arm=="OBS" else TREAT
    if tuple(kinds)!=expected:
        return {"status":"HOLD_MISSING_ORDERED_SOURCE_E0_TO_E6_EVENTS",
                "actual_kinds":kinds,"required_kinds":list(expected)}
    if arm=="OBS" and not events[1].get("tt_value_actually_consumed",False):
        return {"status":"HOLD_TT_PROBE_HIT_BUT_NO_ACTUAL_SEMANTIC_USE_CERTIFICATE",
                "events":len(events)}
    if arm=="TREAT" and not events[0].get("physically_blocked_and_writer_verified",False):
        return {"status":"HOLD_NO_NATIVE_PHYSICAL_FIRST_SOURCE_BLOCK",
                "events":len(events)}
    if events[2 if arm=="OBS" else 1].get("see_native_original_equals_delivered") is not True:
        return {"status":"HOLD_SEE_CALL_NOT_PROVED_PASSIVE",
                "events":len(events)}
    if not events[-1].get("legal_terminal_UCI",False):
        return {"status":"HOLD_NO_LEGAL_EXACT_FINAL_UCI_CERTIFICATE",
                "events":len(events)}
    return {"status":"STRUCTURALLY_COMPLETE_NONCAUSAL_SOURCE_CHAIN",
            "events":len(events),
            "first_native_serial":events[0]["serial"],
            "last_native_serial":events[-1]["serial"],
            "all_necessary_kinds_seen":True,
            "actual_native_execution_proved_by_this_synthetic_checker":False}

def compare(obs:list[dict],treated:list[dict])->dict:
    a=validate_arm(obs,"OBS")
    b=validate_arm(treated,"TREAT")
    if a["status"]!="STRUCTURALLY_COMPLETE_NONCAUSAL_SOURCE_CHAIN" or b["status"]!="STRUCTURALLY_COMPLETE_NONCAUSAL_SOURCE_CHAIN":
        return {"schema":SCHEMA,"status":"HOLD_OR_INSUFFICIENT_SOURCE_EVIDENCE",
                "OBS":a,"TREAT":b,"natural_TT_SEE_mediation_proven":False}
    orig=next(x for x in obs if x["kind"]=="SEE_CALL")
    after=next(x for x in treated if x["kind"]=="SEE_CALL")
    astate=orig["state"];bstate=after["state"]
    same_chess_path=(astate["chess_position"]==bstate["chess_position"]
        and astate["ancestor_vector"]==bstate["ancestor_vector"])
    full=all(astate[k]==bstate[k] for k in STATE_FIELDS)
    diff=[k for k in STATE_FIELDS if astate[k]!=bstate[k]]
    return {
        "schema":SCHEMA,
        "status":"TRACE_CHAIN_COMPLETE_NONCAUSAL",
        "observable_chess_position_and_ancestor_same":same_chess_path,
        "stated_computational_state_equal":full,
        "full_state_label":STATE_EQUAL if full else
            "SAME_CHESS_PATH_DIFFERENT_COMPUTATIONAL_STATE" if same_chess_path
            else "DIFFERENT_CHESS_PATH",
        "differing_state_fields":diff,
        "source_temporal_order_proved_within_arm":True,
        "source_same_native_event_crossarm_proved":False,
        "original_tt_semantic_use_source":a,
        "treatment_physical_first_source":b,
        "SEE_Boolean_natural_effect_proven":False,
        "branch_operator_intervention_and_value_mediation_proven":False,
        "root_ancestry_uniqueness_proven":False,
        "natural_TT_SEE_mediation_proven":False,
        "holds_even_if_both_original_and_treated_bestmove_UCI_differ":True
    }

def synthetic_fixture()->dict:
    # Deliberately synthetic static state; no real FEN, private native keys.
    state={"chess_position":"SYNTHETIC_BOARD_1","ancestor_vector":["SYNTHETIC_ROOT","SYNTHETIC_CHILD"],
        "root_iteration":12,"retry":0,"root_candidate":"c2c4",
        "native_move":"a7a6","ply":2,"depth":5,
        "alpha":-30,"beta":40,"pv":False,"cut_node":False,
        "rule50":0,"see_site":"qsearch_prune","see_threshold":-95,
        "see_occupied":"SYNTHETIC_OCCUPIED"}
    def arm(kinds,prefix):
        seq=[]
        for i,kind in enumerate(kinds):
            e={"id":prefix+str(i),"serial":10+10*i,"parent":None if i==0 else prefix+str(i-1),
                "kind":kind,"state":dict(state)}
            if kind=="TT_SEMANTIC_USE":e["tt_value_actually_consumed"]=True
            if kind=="TT_PHYSICAL_BLOCK":e["physically_blocked_and_writer_verified"]=True
            if kind=="SEE_CALL":e["see_native_original_equals_delivered"]=True
            if kind=="FINAL_UCI":e["legal_terminal_UCI"]=True
            seq.append(e)
        return seq
    obs=arm(OBS,"O")
    treated=arm(TREAT,"T")
    return {"OBS":obs,"TREAT":treated}
def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    a=p.parse_args()
    fixture=synthetic_fixture()
    cert=compare(fixture["OBS"],fixture["TREAT"])
    if cert["status"]!="TRACE_CHAIN_COMPLETE_NONCAUSAL" or cert["natural_TT_SEE_mediation_proven"]:
        raise AssertionError("synthesized checker improperly certified natural mediation")
    result={"schema":SCHEMA,"source":"SYNTHETIC_NO_ORIGINAL_CHESS_DATA",
        "certificate":cert,
        "science":"STRUCTURAL NECESSITY ONLY: no causal identification or true native oracle",
        "not_a_real_chess_or_M5_trial":True}
    out=Path(a.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("C3X025_P5_STRUCTURAL_NONCAUSAL_TRACE_VERDICT",
          {"status":cert["status"],"state":cert["full_state_label"],
           "natural_TT_SEE_mediation_proven":False},flush=True)
    print("C3X025_P5_SCAFFOLD_JSON_SHA256",
          hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
