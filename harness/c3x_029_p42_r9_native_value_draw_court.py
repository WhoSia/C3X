#!/usr/bin/env python3
"""P42/R9 native source-contact court: two ABC+D suites, one executable.

Hypothesis: extra search changes future value_draw node-parity results.
Always report contact and full-root outcomes separately. A nonexistent source
contact rules out THIS particular value_draw call mechanism for observed
root restoration, but not other node-sensitive effects.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from c3x_029_p42_r8_same_engine_tt_save_causal_court import file_sha, STAGEA_SHA, SOURCE_SHA, FORECAST_SHA

ROW=re.compile(r"^c3x042_r9_draw call=1 node_mod4=(\d+) original=(-?\d+) neutral=([01]) return=(-?\d+)$",re.M)

def inspect(raw, neutral:bool):
    lines=[x for x in raw.splitlines() if x.startswith("c3x042_r9_draw")]
    parsed=ROW.findall(raw)
    if len(lines)!=len(parsed):
        raise ValueError("R9_HOLD_MALFORMED_NATIVE_DRAW_EVENTS")
    hist={str(n):0 for n in range(4)}
    for n,v,z,w in parsed:
        n,v,z,w=map(int,(n,v,z,w))
        if n>3 or z!=int(neutral):
            raise ValueError("R9_HOLD_DRAW_PARITY_OR_MODE_MISMATCH")
        hist[str(n)]+=1
        # Stockfish16's VALUE_DRAW=0, with -1/+1 dependent on node bit 0x2.
        if v!=(-1+(n&2)) or w!=(0 if neutral else v):
            raise ValueError("R9_HOLD_NATIVE_DRAW_RETURN_MISMATCH")
    return {"actual_value_draw_calls":len(parsed),"node_mod4_histogram":hist}

def decide(regular,neutral,base,changed,regular_exit,neutral_exit):
    result={
      "schema":"c3x042-r9-actual-value-draw-causal-court-v1",
      "scope":"historical postselected Game14; NNUE disabled",
      "normal":regular,"neutralized":neutral,
      "baseline_r8_exit":regular_exit,"draw_neutralized_r8_exit":neutral_exit,
      "natural_TT_mediation_certified":False,
      "independent_chess_strategic_meaning_certified":False,
      "prospective_heldout_chess_certified":False,
      "private_source_events_disclosed":False
    }
    if regular_exit!=0 or neutral_exit!=0 or not base or not changed:
        result["status"]="HOLD_NATIVE_FOUR_ARM_REPLAY_OR_CONTROL_DRIFT"
        return result
    a=base.get("control_three_arm_choices")
    b=changed.get("control_three_arm_choices")
    if (a!={"A":"b3a4","B":"f3f4","C":"b3a4"}
        or b!=a):
        result["status"]="HOLD_ORIGINAL_THREE_ARM_CHOICES_DRIFT"
        return result
    if not (base.get("status","").startswith("PASS_SOURCE_EXACT_TARGET_TT_SAVE_INTERVENTION")
            and changed.get("status","").startswith("PASS_SOURCE_EXACT_TARGET_TT_SAVE_INTERVENTION")):
        result["status"]="HOLD_R8_FOUR_ARM_COURT_NOT_PASS"
        return result
    result["normal_D_move"]=base.get("intervention_D_choice")
    result["neutralized_D_move"]=changed.get("intervention_D_choice")
    if regular["actual_value_draw_calls"]==0 and neutral["actual_value_draw_calls"]==0:
        result["status"]="PASS_ACTUAL_NO_VALUE_DRAW_CONTACT_IN_TESTED_SOURCE_EXECUTIONS"
        result["claim"]="No source value_draw calls executed in these original and neutralized four-arm suites; the specific node-parity draw-return path cannot be the cause of Game14 root restoration in these executions."
    elif (regular["actual_value_draw_calls"]==0)!=(neutral["actual_value_draw_calls"]==0):
        result["status"]="HOLD_ASYMMETRIC_DRAW_CONTACT"
    elif result["normal_D_move"]==result["neutralized_D_move"]:
        result["status"]="PASS_GLOBAL_DRAW_PARITY_NEUTRALIZATION_ROOT_UNCHANGED"
        result["claim"]="The D-arm root survived global value_draw parity neutralization; not a proof that all draw nodes or other node-sensitive effects are irrelevant."
    else:
        result["status"]="PASS_GLOBAL_DRAW_PARITY_NEUTRALIZATION_ROOT_CHANGED"
        result["claim"]="Root changed under broad draw-score neutralization, but source-path specificity and the A/B/C controls remain necessary before attributing cause."
    return result

def main():
    p=argparse.ArgumentParser()
    for key in ("source","stagea","forecast","engine","private","public"):
        p.add_argument("--"+key,required=True)
    a=p.parse_args()
    for f,expected in ((a.source,SOURCE_SHA),(a.stagea,STAGEA_SHA),(a.forecast,FORECAST_SHA)):
        if file_sha(f)!=expected:raise ValueError("R9_HOLD_ORIGINAL_SOURCE_BYTES")
    out=Path(a.public);out.mkdir(parents=True,exist_ok=True)
    private=Path(a.private);private.mkdir(parents=True,exist_ok=True)
    outcomes=[]
    for name,neutral in (("original_draw",False),("neutralized_draw",True)):
        destination=private/(name+"_draw_events.txt")
        destination.write_text("")
        env=os.environ.copy()
        env["C3X042_R9_DRAW_TRACE"]=str(destination.resolve())
        if neutral:env["C3X042_R9_DRAW_PARITY_NEUTRAL"]="1"
        else:env.pop("C3X042_R9_DRAW_PARITY_NEUTRAL",None)
        output=out/name
        cmd=["python","-u","harness/c3x_029_p42_r8_same_engine_tt_save_causal_court.py",
             "--source",a.source,"--stagea",a.stagea,
             "--forecast",a.forecast,"--engine",a.engine,
             "--private",str(private/name),"--public",str(output)]
        ran=subprocess.run(cmd,env=env,check=False)
        counts=inspect(destination.read_text(),neutral)
        resultfile=output/"C3X042_R8_CAUSAL_TT_SIDE_EFFECT_COURT.json"
        result=json.loads(resultfile.read_text()) if resultfile.exists() else {}
        outcomes.append((counts,result,ran.returncode))
    # Keep original ABC/D public interim reports out of the R9 artifact.
    # R8 already published those same historical labels in its own rights-gated
    # receipts; R9 releases only aggregate counts and conditional verdict.
    shutil.rmtree(out/"original_draw")
    shutil.rmtree(out/"neutralized_draw")
    result=decide(outcomes[0][0],outcomes[1][0],outcomes[0][1],
                  outcomes[1][1],outcomes[0][2],outcomes[1][2])
    (out/"C3X042_R9_DRAW_CAUSAL_COURT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X042_R9_SOURCE_DRAW_COURT",result["status"])
    if not result["status"].startswith("PASS_"):raise SystemExit(2)
if __name__=="__main__":
    main()
