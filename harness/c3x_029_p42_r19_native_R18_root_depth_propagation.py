#!/usr/bin/env python3
"""P42/R19 source-native R18 root-boundary propagation and compensation.

Rerun the original R18 EXACT source-state reversal; privately inspect the
original unchanged C and modified C root depth summaries from THAT execution.
Only aggregate depth-wise change flags and score deltas enter public output.

A changed interim root leader is NOT evidence that the final action changed,
nor proof of natural TT->capture->cycle mediation or chess strategic truth.
"""
import argparse
import json
import subprocess
from pathlib import Path
from c3x_027_game14_root_boundary_court import parse_boundary_lines
from c3x_029_p42_r14_original_guard_vs_event33_same_engine_court import parse_three_cold_root_worlds

FIELDS=("leader","score","average")

def classify(original, counterfactual):
    out={
      "status":"HOLD_ROOT_DEPTH_PROVENANCE",
      "source_state_exclusive_reverse_event_certified":False,
      "intermediate_choice_causal_sensitivity_certified":False,
      "natural_guard_cycle_mediation_certified":False,
      "true_chess_strategic_meaning_certified":False,
      "prospective_heldout_certified":False,
      "reveals_source_keys":False,
    }
    if len(original)!=12 or len(counterfactual)!=2 or any(len(x)!=12 for x in counterfactual):
        return out
    if counterfactual[0]!=counterfactual[1]:
        return dict(out,status="HOLD_COUNTERFACTUAL_COLD_BOUNDARY_DRIFT")
    if any(a["depth"]!=i+1 or b["depth"]!=i+1
           for i,(a,b) in enumerate(zip(original,counterfactual[0]))):
        return dict(out,status="HOLD_DEPTH_IDENTITY_DRIFT")
    rows=[]
    for a,b in zip(original,counterfactual[0]):
        rows.append({
          "depth":a["depth"],
          "leader_changed":a["leader"]!=b["leader"],
          "score_changed":a["score"]!=b["score"],
          "average_changed":a["average"]!=b["average"],
          "score_delta":b["score"]-a["score"],
          "average_delta":b["average"]-a["average"],
        })
    changed=[r["depth"] for r in rows if any(r[x+"_changed"] for x in FIELDS)]
    leaders=[r["depth"] for r in rows if r["leader_changed"]]
    if not changed:
        status="PASS_NO_OBSERVED_INTERMEDIATE_ROOT_DEPTH_DIFFERENCE"
    elif leaders:
        status="PASS_NATIVE_SOURCE_REVERSAL_CHANGED_INTERMEDIATE_ROOT_LEADER"
    else:
        status="PASS_NATIVE_SOURCE_REVERSAL_CHANGED_ROOT_SCORES_ONLY"
    return dict(out,status=status,
        root_depth_count=12, changed_depths=changed,leader_changed_depths=leaders,
        first_changed_depth=changed[0] if changed else None,
        last_changed_depth=changed[-1] if changed else None,
        final_depth_summary_equals_original=original[-1]==counterfactual[0][-1],
        depth_delta_aggregates=rows,
        intermediate_choice_causal_sensitivity_certified=bool(leaders),
        caveat="Only source-intervened depth-boundary summary, not path-specific natural mediation.")

def main():
    p=argparse.ArgumentParser()
    for key in ("source","stagea","forecast","engine","private","public-out"):
        p.add_argument("--"+key,required=True)
    a=p.parse_args()
    private=Path(a.private);private.mkdir(parents=True,exist_ok=True)
    r18=private/"R18_verified_native"
    r18out=private/"R18_original_verified_public_held_private.json"
    subprocess.run([
       "python","-u","harness/c3x_029_p42_r18_source_identity_reverse_B33_in_C_court.py",
       "--source",a.source,"--stagea",a.stagea,"--forecast",a.forecast,
       "--engine",a.engine,"--private",str(r18),"--public-out",str(r18out)
    ],check=True)
    prior=json.loads(r18out.read_text())
    if (prior.get("status")!="PASS_ACTUAL_ONE_REVERSED_DRAW_EVENT_DOES_NOT_REVERT_C_ROOT"
        or prior.get("native_identity_source_contacts_per_cold")!=[2,2]
        or prior.get("reverse_C_beta_cutoff")!=[False,False]
        or prior.get("original_C_guard_physically_reenabled") is not True):
        raise ValueError("R19_HOLD_R18_EXACT_NATIVE_REVERSE_PROVENANCE")
    r14=r18/"original_R16_and_R15_controls"/"native_R15_original_guard_and_combined"/"original_R14_controls"
    originals=parse_three_cold_root_worlds((r14/"ABC_legacy_root_depths.txt").read_text())
    original=originals["C"]
    runs=[]
    for i in range(2):
        root_file=r18/f"reverse_cold_{i}"/"root.txt"
        court=parse_boundary_lines(root_file.read_text().splitlines())
        if court["status"]!="PASS_TWO_IDENTICAL_COLD_BOUNDARY_RUNS":
            raise ValueError("R19_HOLD_NATIVE_REVERSE_ROOT_BOUNDARY_PROVENANCE")
        runs.append(court["runs"][0])
    result=classify(original,runs)
    result.update({
       "schema":"c3x042-r19-actual-source-root-depth-propagation-v1",
       "source_game_id":14,
       "original_C_move":"b3a4",
       "reverse_C_move":prior["C_reverse_root_move"],
       "reverse_target_source_ordinal":prior["actual_C_target_source_ordinal"],
       "exact_source_event_contacts_per_cold":prior["native_identity_source_contacts_per_cold"],
       "original_C_immediate_cutoff":True,
       "reversed_C_immediate_cutoff":prior["reverse_C_beta_cutoff"],
       "same_original_pinned_game14_source_and_stagea":True,
       "uses_original_R18_control_no_mutation":True,
       "source_state_exclusive_reverse_event_certified":True,
    })
    output=Path(a.public_out);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("C3X042_R19_ACTUAL_ROOT_BOUNDARY",result["status"],
          "changed",result.get("changed_depths"),
          "leader_changed",result.get("leader_changed_depths"),
          "final_move",result["reverse_C_move"])
    if not result["status"].startswith("PASS_"):
        raise SystemExit(2)

if __name__=="__main__":
    main()
