#!/usr/bin/env python3
"""P42/R15: real double intervention C(capture bypass)+B33(cycle call).

Runs the already verified R14 original C and B33 controls in one compiled
Stockfish16, then intervenes on BOTH in fresh engine processes. A target
ordinal remains an ordinal, not proof that it denotes the same native frame.
Different source support is a finding, never silently re-labelled mediation.
Private full chess state and raw events never enter public artifacts.
"""
import argparse
import json
import os
import subprocess
from collections import Counter
from pathlib import Path

from c3x_029_p42_r9_original_AB_neutralized_source_probe import verify_original_inputs
from c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev import cold
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_027_game14_root_boundary_court import parse_boundary_lines
from c3x_029_p42_r12_native_single_cycle_event_court import (
    split_two_physical_plays,match_single_event,selected_ordinals)
from c3x_029_p42_r14_original_guard_vs_event33_same_engine_court import (
    parsed_actions,parse_three_cold_root_worlds,cycle_rows,
    SOURCE_FIELDS,compare_native_worlds)

FORCE={
 "key64":"C3X027_FORCE_CAPTURE_KEY64",
 "root_call":"C3X027_FORCE_CAPTURE_ROOT_CALL",
 "move":"C3X027_FORCE_CAPTURE_MOVE",
 "threshold":"C3X027_FORCE_CAPTURE_THRESHOLD"
}

def adjudicate(control,combined_roots,forced_actions,cycle_events,baseline_B,readers):
    out={"schema":"c3x042-r15-native-double-source-intervention-v1",
         "historical_development_case":True,"nnue_enabled":False,
         "natural_causal_mediation_certified":False,
         "single_native_event_causal_necessity_certified":False,
         "independent_chess_future_certified":False,
         "prospective_transport_certified":False,
         "private_chess_keys_exposed":False}
    if control.get("status")!="PASS_ACTUAL_NATIVE_C_AND_B33_SOURCE_ROOT_COMPARISON_ONLY":
        return dict(out,status="HOLD_ORIGINAL_R14_CONTROL_NOT_ADMITTED")
    if control.get("C_guard_exact_reenable_native_source_attempts")!=2 or not control.get("C_and_B33_reproduce_b3a4"):
        return dict(out,status="HOLD_HISTORICAL_ORIGINAL_GUARD_OR_B33")
    if len(combined_roots)!=2 or len(forced_actions)!=2 or len(cycle_events)!=2 or readers!=[True,True]:
        return dict(out,status="HOLD_COLD_SOURCE_EVIDENCE_MISSING")
    if any(forced_actions[i]!=2 for i in range(2)):
        return dict(out,status="HOLD_COMBINED_GUARD_NOT_PHYSICALLY_REENABLED")
    if any(len(cycle_events[i])<33 for i in range(2)):
        return dict(out,status="HOLD_COMBINED_CYCLE_ORDINAL_NOT_REACHED")
    if any(cycle_events[i][32]["candidate"]!=0 for i in range(2)):
        return dict(out,status="HOLD_COMBINED_CYCLE_ORDINAL_NOT_NEUTRALIZED")
    moves=[x["move"] for x in combined_roots]
    if moves[0]!=moves[1]:
        return dict(out,status="HOLD_COMBINED_COLD_ROOT_INSTABILITY",combined_moves=moves)
    # This strict check may fail because forcing the guard changes the
    # visited search states BEFORE original B's 33rd cycle call.
    source_match=[match_single_event(baseline_B,cycle_events[i],33)
                  for i in range(2)]
    support=simple_support(source_match)
    return dict(out,status="PASS_COMBINED_PHYSICAL_SOURCE_INTERVENTIONS_ONLY",
                combined_moves=moves,
                original_C_move="b3a4",original_B33_move="b3a4",original_B_move="f3f4",
                cycle_event33_same_B_preintervention_source_identity=support,
                matched_prefix_courts=source_match,
                possible_interaction="combined result compared to two single-arm restorations; no unique natural mediator inference")

def simple_support(matches):
    return all(x=="PASS_ACTUAL_ONE_SOURCE_EVENT_WITH_MATCHED_PREFIX" for x in matches)

def main():
    p=argparse.ArgumentParser()
    for key in ("source","stagea","forecast","engine","private","public-out"):
        p.add_argument("--"+key,required=True)
    a=p.parse_args()
    world,clock,physical,watch,filters=verify_original_inputs(a.source,a.stagea,a.forecast)
    priv=Path(a.private);priv.mkdir(parents=True,exist_ok=True)
    r14priv=priv/"original_R14_controls"
    r14priv.mkdir(exist_ok=True)
    r14out=priv/"original_R14_private_control_summary.json"
    subprocess.run(["python","-u","harness/c3x_029_p42_r14_original_guard_vs_event33_same_engine_court.py",
        "--source",a.source,"--stagea",a.stagea,"--forecast",a.forecast,
        "--engine",a.engine,"--private",str(r14priv),"--public-out",str(r14out)],check=True)
    reference=json.loads(r14out.read_text())
    legacy=parsed_actions((r14priv/"original_027_native"/"TT_FIRST_REENABLE_ONE.txt").read_text())
    forced=[x for x in legacy if x["action"]=="EXACT_ONE_EVENT_REENABLED"]
    if len(forced)!=2 or len({tuple(x[k] for k in SOURCE_FIELDS) for x in forced})!=1:
        raise ValueError("R15_HOLD_C_ORIGINAL_GUARD_PRIVATE_SOURCE_SIGNATURE")
    target=forced[0]
    original=cycle_rows((r14priv/"ABC_legacy_cycle_windows.txt").read_text())
    if len(original)<942:raise ValueError("R15_HOLD_ORIGINAL_ABC_NATIVE_WINDOW_LENGTH")
    baseline_B=split_two_physical_plays(original[380:942])
    if selected_ordinals(baseline_B)!=[30,31,32,33]:
        raise ValueError("R15_HOLD_EVENT33_ORIGINAL_PRESPECIFICATION_DRIFT")
    root_runs=[];actions=[];cycles=[];readers=[]
    for trial in range(2):
        tag=priv/f"joint_cold_{trial}"
        tag.mkdir(exist_ok=True)
        paths={n:tag/f"{n}.txt" for n in ("root","cycle","capture")}
        for value in paths.values():value.write_text("")
        env=os.environ.copy()
        os.environ.update({v:str(target[k]) for k,v in FORCE.items()})
        os.environ.update({
          "C3X027_GAME14_LINEAGE_LOG":str(paths["root"].resolve()),
          "C3X042_R11_CYCLE_WINDOW_TRACE":str(paths["cycle"].resolve()),
          "C3X027_CAPTURE_BRANCH_LOG":str(paths["capture"].resolve()),
          "C3X042_R12_TARGET_ORDINAL":"33","C3X042_R10_NEUTRAL_DRAW_SITE":"0"})
        os.environ.pop("C3X042_R9_DRAW_PARITY_NEUTRAL",None)
        os.environ.pop("C3X042_R8_DROP_DESCENDANT_TT_SAVE",None)
        try:
            result=cold(a.engine,world,clock,"O","V",physical,filter=filters,watch=watch)
        finally:
            os.environ.clear();os.environ.update(env)
        root_court=parse_boundary_lines(paths["root"].read_text().splitlines())
        if root_court["status"]!="PASS_TWO_IDENTICAL_COLD_BOUNDARY_RUNS":
            raise ValueError("R15_HOLD_COMBINED_PHYSICAL_ROOT_BOUNDARY")
        native=cycle_rows(paths["cycle"].read_text())
        # Two real engine subprocesses per cold(); fail if they disagree.
        events=split_two_physical_plays(native)
        found=parsed_actions(paths["capture"].read_text())
        physical_guard=sum(x["action"]=="EXACT_ONE_EVENT_REENABLED"
           and all(x.get(k)==str(target[k]) for k in SOURCE_FIELDS)
           for x in found)
        root_runs.append({"move":result["UCI"]["bestmove"],
                          "root_boundaries":root_court["runs"][0]})
        actions.append(physical_guard);cycles.append(events)
        readers.append(bool(verified_reader_lineage(result)["all_valid"]
                            and any(x.get("kind")=="reader_block" for x in result["blocks"])))
    report=adjudicate(reference,root_runs,actions,cycles,baseline_B,readers)
    if report["status"].startswith("PASS_"):
        # Aggregate root depth9 comparison may be inspected WITHOUT claiming
        # identical dynamic source states or private event identities.
        for i in range(2):
            if len(root_runs[i]["root_boundaries"])<9:
                raise ValueError("R15_HOLD_COMBINED_DEPTH9_ROOT_MISSING")
        report["combined_depth9_native_root_summary"]=root_runs[0]["root_boundaries"][8]
        report["combined_root_depths"]=len(root_runs[0]["root_boundaries"])
        report["combined_matches_original_C_depth9_leader_score"]=(
            root_runs[0]["root_boundaries"][8]["leader"]==
                reference["depth9_source_boundary"]["C_capture_guard_bypass"]["leader"]
            and root_runs[0]["root_boundaries"][8]["score"]==
                reference["depth9_source_boundary"]["C_capture_guard_bypass"]["score"])
    dest=Path(a.public_out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("C3X042_R15_NATIVE_GUARD_AND_CYCLE33",report["status"],
          report.get("combined_moves"),"B_source_prefix_same",
          report.get("cycle_event33_same_B_preintervention_source_identity"))
    if not report["status"].startswith("PASS_"):raise SystemExit(2)
if __name__=="__main__":
    main()
