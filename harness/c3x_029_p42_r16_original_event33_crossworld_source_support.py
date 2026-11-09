#!/usr/bin/env python3
"""P42/R16: actual source-state support across original B, guard C, joint C+B33.

Root choice agreement alone cannot identify a common cross-world mediator.
Reuse R15 physical native execution; compare source event33 signature against
EVERY observed cycle-alpha source call in C and combined worlds.  Source keys,
windows and FEN stay in PRIVATE files and are never published.
"""
import argparse
import json
import subprocess
from pathlib import Path

from c3x_029_p42_r14_original_guard_vs_event33_same_engine_court import (
    cycle_rows,parse_three_cold_root_worlds)
from c3x_029_p42_r12_native_single_cycle_event_court import (
    split_two_physical_plays)
from c3x_027_game14_root_boundary_court import parse_boundary_lines

BOARD=("key","ply","depth","root_move")
WINDOW=("key","ply","depth","root_move","old_alpha","beta")
SCORE=("key","ply","depth","root_move","old_alpha","beta","mod4")

def match_indices(target,events,fields):
    return [i+1 for i,e in enumerate(events)
            if all(e[k]==target[k] for k in fields)]

def first_difference(a,b,fields):
    for i,(x,y) in enumerate(zip(a,b),1):
        if any(x[k]!=y[k] for k in fields):
            return i
    return min(len(a),len(b))+1 if len(a)!=len(b) else None

def audit(b,c,joint,root_c,root_joint):
    """Pure in-memory private source comparison; public result exposes counts only."""
    target=b[32]
    signature_counts={}
    for name,events in (("original_B",b),("capture_guard_C",c),("combined_C_plus_B33",joint)):
        signature_counts[name]={
           "board_context":len(match_indices(target,events,BOARD)),
           "board_and_window":len(match_indices(target,events,WINDOW)),
           "exact_source_computation":len(match_indices(target,events,SCORE))
        }
    fields=BOARD+("old_alpha","beta","mod4")
    if len(root_c)!=len(root_joint):
        return {"status":"HOLD_DIFFERENT_ROOT_DEPTH_SUPPORT",
                "crossworld_source_support":signature_counts}
    root_leader_score=[x["depth"] for x,y in zip(root_c,root_joint)
                       if (x["leader"],x["score"])==(y["leader"],y["score"])]
    root_fully_equal=[x["depth"] for x,y in zip(root_c,root_joint) if x==y]
    return {
        "status":"PASS_NATIVE_SOURCE_SUPPORT_AUDIT_ONLY",
        "target_original_B_ordinal":33,
        "crossworld_source_support":signature_counts,
        "source_call_counts":{"B":len(b),"C":len(c),"C_plus_B33":len(joint)},
        "first_native_event_identity_difference":{
          "B_vs_C":first_difference(b,c,fields),
          "B_vs_combined":first_difference(b,joint,fields),
          "C_vs_combined":first_difference(c,joint,fields)
        },
        "root_depths_compared":len(root_c),
        "C_vs_combined_root_leader_score_matching_depths":root_leader_score,
        "C_vs_combined_full_root_summary_matching_depths":root_fully_equal,
        "original_B_event33_same_board_context_in_C":
            signature_counts["capture_guard_C"]["board_context"]>0,
        "original_B_event33_same_window_and_board_in_C":
            signature_counts["capture_guard_C"]["board_and_window"]>0,
        "original_B_event33_full_source_signature_in_C":
            signature_counts["capture_guard_C"]["exact_source_computation"]>0,
        "source_key_or_score_values_disclosed":False,
        "causal_reachability_of_B33_in_C_established":False,
        "natural_common_mediator_certified":False,
        "independent_chess_strategic_reason_certified":False,
        "prospective_transport_certified":False
    }

def main():
    p=argparse.ArgumentParser()
    for item in ("source","stagea","forecast","engine","private","public-out"):
        p.add_argument("--"+item,required=True)
    a=p.parse_args()
    private=Path(a.private);private.mkdir(parents=True,exist_ok=True)
    r15root=private/"native_R15_original_guard_and_combined"
    r15out=private/"R15_PRIVATE_AGGREGATE.json"
    # This reruns the original pinned historical source state under the same
    # physical combined guard + cycle intervention, not a synthetic trace.
    subprocess.run(["python","-u","harness/c3x_029_p42_r15_original_guard_plus_event33_interaction_court.py",
        "--source",a.source,"--stagea",a.stagea,
        "--forecast",a.forecast,"--engine",a.engine,
        "--private",str(r15root),"--public-out",str(r15out)],check=True)
    r15=json.loads(r15out.read_text())
    if r15["status"]!="PASS_COMBINED_PHYSICAL_SOURCE_INTERVENTIONS_ONLY":
        raise ValueError("R16_HOLD_R15_NATIVE_DOUBLE_INTERVENTION_NOT_PASS")
    original=r15root/"original_R14_controls"
    raw=cycle_rows((original/"ABC_legacy_cycle_windows.txt").read_text())
    if len(raw)<942:raise ValueError("R16_HOLD_ORIGINAL_R11_COUNTS_DRIFT")
    a_stream=split_two_physical_plays(raw[:380])
    b_stream=split_two_physical_plays(raw[380:942])
    c_stream=split_two_physical_plays(raw[942:])
    if (len(a_stream),len(b_stream))!=(190,281):
        raise ValueError("R16_HOLD_ORIGINAL_B_NATIVE_SOURCE_LENGTH_CHANGED")
    original_root=parse_three_cold_root_worlds(
       (original/"ABC_legacy_root_depths.txt").read_text())
    root_c=original_root["C"]
    observed=[]
    for i in range(2):
        path=r15root/f"joint_cold_{i}"
        native=cycle_rows((path/"cycle.txt").read_text())
        stream=split_two_physical_plays(native)
        boundaries=parse_boundary_lines((path/"root.txt").read_text().splitlines())
        if boundaries["status"]!="PASS_TWO_IDENTICAL_COLD_BOUNDARY_RUNS":
            raise ValueError("R16_HOLD_COMBINED_ROOT_TRACES_NOT_IDENTICAL")
        observed.append(audit(b_stream,c_stream,stream,root_c,boundaries["runs"][0]))
    if observed[0]!=observed[1]:
        raise ValueError("R16_HOLD_TWO_COLD_SUPPORT_AUDITS_DISAGREE")
    out=observed[0]
    out.update({
       "schema":"c3x042-r16-source-event-crossworld-support-audit-v1",
       "R15_cold_native_guard_and_cycle_contact_verified":True,
       "R14_original_A_B_C_and_B33_source_controls_verified":True,
       "game14_postselected":True,"nnue_enabled":False
    })
    dest=Path(a.public_out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("C3X042_R16_NATIVE_SOURCE_SUPPORT",out["status"],
          out["crossworld_source_support"],
          "first differences",out["first_native_event_identity_difference"])
    if not out["status"].startswith("PASS_"):raise SystemExit(2)

if __name__=="__main__":
    main()
