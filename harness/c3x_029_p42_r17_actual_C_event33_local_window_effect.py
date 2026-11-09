#!/usr/bin/env python3
"""R17: source-value transmission after R15's combined C + 33rd cycle change.

This is NOT attribution of original B event33 to C (R16 disproved the
full source-state identity). Audit C's own event33 against C+B33 and ask:
did its actual alpha assignment, immediate cutoff and subsequent source
cycle/root summary observables change? Root equality does not mean no
unmeasured search-state difference.
"""
import argparse
import json
import subprocess
from pathlib import Path
from c3x_029_p42_r14_original_guard_vs_event33_same_engine_court import cycle_rows
from c3x_029_p42_r12_native_single_cycle_event_court import split_two_physical_plays
from c3x_029_p42_r16_original_event33_crossworld_source_support import (
    first_difference,BOARD,WINDOW,SCORE)

SOURCE_FIELDS=SCORE

def test_dynamic_effect(c,modified):
    if len(c)<33 or len(modified)<33:
        return {"status":"HOLD_EVENT33_NOT_IN_BOTH_NATIVE_EXECUTIONS"}
    if len(c)!=len(modified):
        return {"status":"HOLD_NATIVE_EVENT_SUPPORT_LENGTH_CHANGED"}
    initial=first_difference(c,modified,SOURCE_FIELDS)
    if initial is not None:
        return {"status":"HOLD_PRE_SCORE_NATIVE_SOURCE_CONTEXT_DRIFT",
                "first_difference_ordinal":initial}
    diff=[i+1 for i,(a,b) in enumerate(zip(c,modified))
          if a["candidate"]!=b["candidate"] or a["cutoff"]!=b["cutoff"]]
    if diff!=[33]:
        return {"status":"HOLD_UNEXPECTED_NUMBER_OR_LOCATION_OF_DRAW_VALUE_CHANGES",
                "changed_event_count":len(diff)}
    a,b=c[32],modified[32]
    if a["candidate"] not in (-1,1) or b["candidate"]!=0:
        return {"status":"HOLD_ORIGINAL_OR_NEUTRALIZED_DRAW_VALUE_UNEXPECTED"}
    if a["cutoff"]!=int(a["candidate"]>=a["beta"]) or b["cutoff"]!=int(0>=b["beta"]):
        return {"status":"HOLD_NATIVE_IMMEDIATE_CUTOFF_INCONSISTENT"}
    return {"status":"PASS_ONE_ACTUAL_C_EVENT_VALUE_CHANGE_WITH_PRESERVED_SOURCE_CONTEXT",
            "original_C_event33_draw_return":a["candidate"],
            "combined_C_event33_draw_return":0,
            "actual_return_delta":-a["candidate"],
            "original_C_event33_cutoff":bool(a["cutoff"]),
            "combined_C_event33_cutoff":bool(b["cutoff"]),
            "immediate_cutoff_changed":a["cutoff"]!=b["cutoff"],
            "cycle_calls_after_event33":len(c)-33,
            "cycle_source_pre_score_contexts_all_identical":True,
            "only_cycle_return_or_cutoff_difference_at_event33":True,
            "unmeasured_search_state_equal":False,
            "natural_B33_source_mediation_identified":False}

def main():
    p=argparse.ArgumentParser()
    for key in ("source","stagea","forecast","engine","private","public-out"):
        p.add_argument("--"+key,required=True)
    a=p.parse_args()
    priv=Path(a.private);priv.mkdir(parents=True,exist_ok=True)
    r16private=priv/"native_R16_support_and_R15_worlds"
    r16out=priv/"native_R16_private_summary.json"
    subprocess.run(["python","-u",
       "harness/c3x_029_p42_r16_original_event33_crossworld_source_support.py",
       "--source",a.source,"--stagea",a.stagea,
       "--forecast",a.forecast,"--engine",a.engine,
       "--private",str(r16private),"--public-out",str(r16out)],check=True)
    cross=json.loads(r16out.read_text())
    if cross["status"]!="PASS_NATIVE_SOURCE_SUPPORT_AUDIT_ONLY":
        raise ValueError("R17_HOLD_ORIGINAL_R16_NATIVE_SOURCE_SUPPORT")
    r15=r16private/"native_R15_original_guard_and_combined"
    r14=r15/"original_R14_controls"
    all_original=cycle_rows((r14/"ABC_legacy_cycle_windows.txt").read_text())
    if len(all_original)<943:
        raise ValueError("R17_HOLD_ORIGINAL_A_B_C_NATIVE_EVENT_STREAM")
    c=split_two_physical_plays(all_original[942:])
    outcomes=[]
    for trial in range(2):
        joint=split_two_physical_plays(cycle_rows(
          (r15/f"joint_cold_{trial}"/"cycle.txt").read_text()))
        outcomes.append(test_dynamic_effect(c,joint))
    if outcomes[0]!=outcomes[1]:
        raise ValueError("R17_HOLD_COLD_NATIVE_DYNAMIC_RETURN_DELTA_DISAGREES")
    result={
       "schema":"c3x042-r17-source-cycle-value-effect-after-guard-v1",
       **outcomes[0],
       "two_cold_native_repeats":2,
       "original_R16_native_support_reproduced":True,
       "C_and_combined_root_depths_all_12_identical":(
          cross["C_vs_combined_full_root_summary_matching_depths"]==list(range(1,13))),
       "original_B_event33_full_source_identity_in_C":cross[
          "original_B_event33_full_source_signature_in_C"],
       "crossworld_common_natural_mediator_certified":False,
       "root_choice_mediated_by_this_C_value_certified":False,
       "objective_chess_future_semantics_certified":False,
       "game14_postselected":True,"nnue_enabled":False,
       "private_key_or_full_native_trace_exposed":False
    }
    dest=Path(a.public_out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X042_R17_NATIVE_C_EVENT33_SCORE_CAUSAL_COURT",result["status"],
          "immediate_cutoff_changed",result.get("immediate_cutoff_changed"),
          "return_delta",result.get("actual_return_delta"))
    if not result["status"].startswith("PASS_"):raise SystemExit(2)

if __name__=="__main__":
    main()
