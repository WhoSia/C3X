#!/usr/bin/env python3
"""R18 actual native reverse mediation challenge:
hold C guard bypass fixed, restore B's -1 draw return at exact B event33
board/window source identity instead of unstable ordinal33.

Original B/C source/game hashes, 2 independent cold()s, two physical plays
per cold, forced C guard and exact TT reader required. A favorable root
result is NOT automatically natural-mediation or chess strategic proof.
"""
import argparse,json,os,re,subprocess
from pathlib import Path
from collections import Counter
from c3x_029_p42_r9_original_AB_neutralized_source_probe import verify_original_inputs
from c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev import cold
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_027_game14_root_boundary_court import parse_boundary_lines
from c3x_029_p42_r14_original_guard_vs_event33_same_engine_court import (
    cycle_rows,parsed_actions,SOURCE_FIELDS,parse_three_cold_root_worlds)
from c3x_029_p42_r12_native_single_cycle_event_court import split_two_physical_plays
from c3x_029_p42_r16_original_event33_crossworld_source_support import WINDOW

FORCE_CAPTURE={
 "key64":"C3X027_FORCE_CAPTURE_KEY64",
 "root_call":"C3X027_FORCE_CAPTURE_ROOT_CALL",
 "move":"C3X027_FORCE_CAPTURE_MOVE",
 "threshold":"C3X027_FORCE_CAPTURE_THRESHOLD"
}
FORCE_SOURCE={
 "key":"C3X042_R18_TARGET_KEY",
 "ply":"C3X042_R18_TARGET_PLY",
 "depth":"C3X042_R18_TARGET_DEPTH",
 "root_move":"C3X042_R18_TARGET_ROOT_MOVE",
 "old_alpha":"C3X042_R18_TARGET_ALPHA",
 "beta":"C3X042_R18_TARGET_BETA"
}
HIT=re.compile(r"^c3x042_r18 candidate_contact=1 ordinal_match=(\d+) applied=([01]) native=(-?\d+) forced=-1$",re.M)

def summarize(actual_moves,contacts,cutoffs,readers,root_c,root_new):
    x={"schema":"c3x042-r18-source-identity-reverse-C-cycle-court-v1",
       "actual_combined_reverse_root_moves":actual_moves,
       "native_identity_source_contacts_per_cold":contacts,
       "original_C_return":1,"reversed_return":-1,
       "target_alpha_beta_window_beta":0,
       "old_C_beta_cutoff":True,
       "reverse_C_beta_cutoff":cutoffs,
       "same_native_chess_source_and_legal_history":True,
       "natural_guard_cycle_mediation_certified":False,
       "shared_crossworld_event_causation_certified":False,
       "independent_chess_strategy_certified":False,
       "prospective_heldout_certified":False,
       "nnue_enabled":False,"postselected_game14":True,
       "private_position_hash_or_windows_exposed":False}
    if len(actual_moves)!=2 or len(contacts)!=2 or len(cutoffs)!=2 or readers!=[True,True]:
        return dict(x,status="HOLD_NATIVE_REPLAY_OR_TT_READER")
    if contacts!=[2,2]:
        return dict(x,status="HOLD_TARGET_EXACT_SOURCE_CONTACT_PER_PROCESS")
    if actual_moves[0]!=actual_moves[1] or cutoffs[0]!=cutoffs[1]:
        return dict(x,status="HOLD_NATIVE_COLD_OUTCOME_DRIFT")
    if len(root_c)!=12 or len(root_new)!=2 or any(len(z)!=12 for z in root_new):
        return dict(x,status="HOLD_SOURCE_ROOT_BOUNDARY_MISSING")
    if root_new[0]!=root_new[1]:
        return dict(x,status="HOLD_SOURCE_ROOT_BOUNDARY_COLD_DRIFT")
    x["original_C_root_move"]="b3a4"
    x["original_B_root_move"]="f3f4"
    x["C_reverse_root_move"]=actual_moves[0]
    x["first_C_vs_C_reverse_changed_root_depth"]=next(
       (i+1 for i,(a,b) in enumerate(zip(root_c,root_new[0])) if a!=b),None)
    if actual_moves[0]=="f3f4":
        x["status"]="PASS_ACTUAL_ONE_REVERSED_DRAW_EVENT_REVERTS_C_ROOT_TO_B"
    elif actual_moves[0]=="b3a4":
        x["status"]="PASS_ACTUAL_ONE_REVERSED_DRAW_EVENT_DOES_NOT_REVERT_C_ROOT"
    else:
        x["status"]="PASS_ACTUAL_ONE_REVERSED_DRAW_EVENT_CREATES_THIRD_ROOT"
    return x

def main():
    p=argparse.ArgumentParser()
    for key in ("source","stagea","forecast","engine","private","public-out"):
        p.add_argument("--"+key,required=True)
    a=p.parse_args()
    world,clock,physical,watch,filters=verify_original_inputs(a.source,a.stagea,a.forecast)
    private=Path(a.private);private.mkdir(parents=True,exist_ok=True)
    r16priv=private/"original_R16_and_R15_controls"
    r16out=private/"original_R16_private_aggregate.json"
    subprocess.run(["python","-u","harness/c3x_029_p42_r16_original_event33_crossworld_source_support.py",
        "--source",a.source,"--stagea",a.stagea,"--forecast",a.forecast,
        "--engine",a.engine,"--private",str(r16priv),"--public-out",str(r16out)],check=True)
    support=json.loads(r16out.read_text())
    if (support["status"]!="PASS_NATIVE_SOURCE_SUPPORT_AUDIT_ONLY"
        or support["crossworld_source_support"]["capture_guard_C"]["board_and_window"]!=1
        or support["crossworld_source_support"]["capture_guard_C"]["exact_source_computation"]!=0):
        raise ValueError("R18_HOLD_FROZEN_B_SOURCE_ID_CROSSWORLD_SUPPORT_NOT_REPRODUCED")
    r15=r16priv/"native_R15_original_guard_and_combined"
    r14=r15/"original_R14_controls"
    events=cycle_rows((r14/"ABC_legacy_cycle_windows.txt").read_text())
    if len(events)<943:raise ValueError("R18_HOLD_ORIGINAL_B_C_SOURCE_EVENTS_MISSING")
    b=split_two_physical_plays(events[380:942])
    c=split_two_physical_plays(events[942:])
    target=b[32]
    if not (target["candidate"]==-1 and target["beta"]==0):
        raise ValueError("R18_HOLD_ORIGINAL_B33_CUTOFF_DIRECTION_NOT_MINUS_ONE")
    matched=[(i,e) for i,e in enumerate(c,1)
             if all(e[k]==target[k] for k in WINDOW)]
    if len(matched)!=1 or matched[0][1]["candidate"]!=1 or not matched[0][1]["cutoff"]:
        raise ValueError("R18_HOLD_C_SAME_BOARD_AND_WINDOW_NOT_PLUS_ONE_CUTOFF")
    forced=parsed_actions((r14/"original_027_native"/"TT_FIRST_REENABLE_ONE.txt").read_text())
    original_guard=[x for x in forced if x["action"]=="EXACT_ONE_EVENT_REENABLED"]
    if len(original_guard)!=2 or len({tuple(x[k] for k in SOURCE_FIELDS) for x in original_guard})!=1:
        raise ValueError("R18_HOLD_ORIGINAL_C_GUARD_UNSTABLE")
    original_C_depth=parse_three_cold_root_worlds(
       (r14/"ABC_legacy_root_depths.txt").read_text())["C"]
    contacts=[];moves=[];cutoffs=[];roots=[];readers=[]
    for trial in range(2):
        root_dir=private/f"reverse_cold_{trial}";root_dir.mkdir(exist_ok=True)
        paths={k:root_dir/(k+".txt") for k in ("cycle","capture","root","hits")}
        for f in paths.values():f.write_text("")
        previous=os.environ.copy()
        os.environ.update({v:str(original_guard[0][k]) for k,v in FORCE_CAPTURE.items()})
        os.environ.update({v:str(target[k]) for k,v in FORCE_SOURCE.items()})
        os.environ.update({
          "C3X042_R18_REVERSE_EVENT33":"1",
          "C3X042_R18_PRIVATE_HIT_LOG":str(paths["hits"].resolve()),
          "C3X042_R11_CYCLE_WINDOW_TRACE":str(paths["cycle"].resolve()),
          "C3X027_CAPTURE_BRANCH_LOG":str(paths["capture"].resolve()),
          "C3X027_GAME14_LINEAGE_LOG":str(paths["root"].resolve()),
          "C3X042_R10_NEUTRAL_DRAW_SITE":"0"})
        for k in ("C3X042_R12_TARGET_ORDINAL","C3X042_R9_DRAW_PARITY_NEUTRAL",
                  "C3X042_R8_DROP_DESCENDANT_TT_SAVE"):
            os.environ.pop(k,None)
        try:res=cold(a.engine,world,clock,"O","V",physical,filter=filters,watch=watch)
        finally:
            os.environ.clear();os.environ.update(previous)
        hitlines=[l for l in paths["hits"].read_text().splitlines() if l.startswith("c3x042_r18 ")]
        matches=HIT.findall(paths["hits"].read_text())
        if len(matches)!=len(hitlines) or len(matches)!=2 or any(
            tuple(map(int,m))!=(1,1,1) for m in matches):
            raise ValueError("R18_HOLD_EXACTLY_ONE_NATIVE_PLUS_ONE_TO_MINUS_ONE_PER_ENGINE")
        capture=parsed_actions(paths["capture"].read_text())
        n=sum(e["action"]=="EXACT_ONE_EVENT_REENABLED" and
              all(e.get(k)==original_guard[0][k] for k in SOURCE_FIELDS)
              for e in capture)
        if n!=2:raise ValueError("R18_HOLD_ACTUAL_ORIGINAL_C_CAPTURE_GUARD_BYPASS")
        cycle=split_two_physical_plays(cycle_rows(paths["cycle"].read_text()))
        selected=[(i,e) for i,e in enumerate(cycle,1)
                  if all(e[k]==target[k] for k in WINDOW)]
        if len(selected)!=1 or selected[0][1]["candidate"]!=-1:
            raise ValueError("R18_HOLD_SOURCE_IDENTITY_REVERSE_RETURN_NOT_NATIVE")
        # This intervention may change subsequent source event support;
        # validate the preintervention prefix before the selected event.
        original_idx=matched[0][0];modified_idx=selected[0][0]
        if original_idx!=modified_idx or any(
            any(c[i][k]!=cycle[i][k] or c[i]["candidate"]!=cycle[i]["candidate"]
                for k in WINDOW+("mod4",)) for i in range(original_idx-1)):
            raise ValueError("R18_HOLD_C_PREINTERVENTION_PHYSICAL_SOURCE_IDENTITY_DRIFT")
        boundary=parse_boundary_lines(paths["root"].read_text().splitlines())
        if boundary["status"]!="PASS_TWO_IDENTICAL_COLD_BOUNDARY_RUNS":
            raise ValueError("R18_HOLD_ORIGINAL_SOURCE_ROOT_REPLAY")
        readers.append(bool(verified_reader_lineage(res)["all_valid"]
                         and any(x.get("kind")=="reader_block" for x in res["blocks"])))
        contacts.append(len(matches));moves.append(res["UCI"]["bestmove"])
        cutoffs.append(bool(selected[0][1]["cutoff"]));roots.append(boundary["runs"][0])
    result=summarize(moves,contacts,cutoffs,readers,original_C_depth,roots)
    result["original_B_target_ordinal"]=33
    result["actual_C_target_source_ordinal"]=matched[0][0]
    result["original_C_guard_physically_reenabled"]=True
    result["original_source_B_event33_board_window_identity_matched"]=True
    output=Path(a.public_out);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("C3X042_R18_NATIVE_REVERSE_B33_IN_C",result["status"],
          "root",result.get("C_reverse_root_move"),
          "cutoff",result.get("reverse_C_beta_cutoff"))
    if not result["status"].startswith("PASS_"):raise SystemExit(2)
if __name__=="__main__":
    main()
