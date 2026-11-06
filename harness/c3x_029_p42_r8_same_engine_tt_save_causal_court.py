#!/usr/bin/env python3
"""C3X P42/R8: blinded-to-root within-descendant TTEntry::save perturbation.

Runs historical ABC twice in exact same compiled source, one normal and
one with only the originally reached guard descendant's TT writes disabled.
The source event is postselected development; no new cohort claim.
"""
from __future__ import annotations
import argparse,json,os,re,subprocess,hashlib
from pathlib import Path

STAGEA_SHA="b0eb51ab779609db346c75d65a6a65fd31efc9a648111d042cfec5199a4afde1"
SOURCE_SHA="9372e0fdce2c8499e8d12f6bef5d1bfaef40a2d5b7160cc48513085567c9098d"
FORECAST_SHA="4572edd4c0761c3875aed421b08880ff142c21f691fe940c7c6d760dbb397be5"
RECORD="EXACT_ONE_EVENT_REENABLED"
COUNT_RE=re.compile(r"^c3x042_r8 attempts=(\d+) suppressed=(\d+)$",re.M)

def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def judge(control, intervention, off_counts, on_counts):
    common=("baseline_bestmove","TT_FIRST_bestmove")
    if any(control[k]!=intervention[k] for k in common):
        return {"status":"HOLD_ROOT_CONTROL_DRIFT"}
    if control["baseline_bestmove"]!="b3a4" or control["TT_FIRST_bestmove"]!="f3f4":
        return {"status":"HOLD_HISTORICAL_ROOT_NOT_REPRODUCED"}
    if control["counterfactual_bestmove"]!="b3a4" or control["one_event_reenable_status"]!="ORIGINAL_ROOT_RESTORED":
        return {"status":"HOLD_NORMAL_GUARD_RESTORATION_FAILED"}
    if any(x["suppressed"]!=0 for x in off_counts) or len(off_counts)!=2 or len(on_counts)!=2:
        return {"status":"HOLD_SOURCE_ATTEMPT_COUNT_INVALID"}
    if any(x["suppressed"]==0 or x["suppressed"]!=x["attempts"] for x in on_counts):
        return {"status":"HOLD_TARGET_TT_WRITES_NOT_PHYSICALLY_SUPPRESSED"}
    if any(x["attempts"]==0 for x in off_counts):
        return {"status":"HOLD_UNTREATED_TARGET_TT_WRITES_ABSENT"}
    for record in (control,intervention):
        if record["counterfactual_branch_action_counts"].get(RECORD)!=2:
            return {"status":"HOLD_COUNTERFACTUAL_GUARD_CONTACT_DRIFT"}
        if not record["actual_branch_proof"] or not record["native_guard_one_event_contact"]:
            return {"status":"HOLD_SOURCE_GUARD_NOT_PHYSICALLY_REACHED"}
    outcome=intervention["counterfactual_bestmove"]
    if outcome=="b3a4":
        tag="TT_WRITES_NOT_NECESSARY_FOR_THIS_RESTORATION_UNDER_TESTED_INTERVENTION"
    elif outcome=="f3f4":
        tag="TT_WRITES_FUNCTIONALLY_NECESSARY_UNDER_TESTED_INTERVENTION"
    else:
        tag="TT_WRITES_CHANGE_ROOT_TO_THIRD_CANDIDATE_UNDER_TESTED_INTERVENTION"
    return {
      "status":"PASS_SOURCE_EXACT_TARGET_TT_SAVE_INTERVENTION_"+tag,
      "control_three_arm_choices":{"A":"b3a4","B":"f3f4","C":"b3a4"},
      "intervention_D_choice":outcome,
      "cold_replays":2,
      "off_descendant_tt_save_attempts":[x["attempts"] for x in off_counts],
      "D_suppressed_descendant_tt_save_attempts":[x["suppressed"] for x in on_counts],
      "direct_parent_bestvalue_mediation_previously_negative":True,
      "natural_mediation_certified":False,
      "only_one_side_effect_family_perturbed":True,
      "chess_strategy_meaning_certified":False,
      "postselected_game14_development_only":True,
      "private_source_keys_exposed":False
    }

def main():
    p=argparse.ArgumentParser()
    for name in ("source","stagea","forecast","engine","private","public"):
        p.add_argument("--"+name,required=True)
    a=p.parse_args()
    for file,want in ((a.source,SOURCE_SHA),(a.stagea,STAGEA_SHA),(a.forecast,FORECAST_SHA)):
        if file_sha(file)!=want:raise ValueError("R8_HOLD_FROZEN_SOURCE_OR_STAGEA_SHA")
    private=Path(a.private);private.mkdir(parents=True,exist_ok=True)
    public=Path(a.public);public.mkdir(parents=True,exist_ok=True)
    normal=[]
    for mode in ("control_C","drop_TT_D"):
        path=private/(mode+"_tt_events.txt")
        path.write_text("")
        env=os.environ.copy()
        env["C3X042_R5_LOCAL_TRACE"]=str(path.resolve())
        if mode=="drop_TT_D":env["C3X042_R8_DROP_DESCENDANT_TT_SAVE"]="1"
        else:env.pop("C3X042_R8_DROP_DESCENDANT_TT_SAVE",None)
        out=public/(mode+"_GAME14_ABC_SOURCE.json")
        subprocess.run([
            "python","-u","harness/c3x_027_sept_game14_direct_capture_guard.py",
            "--source",a.source,"--stagea",a.stagea,"--forecast",a.forecast,
            "--engine",a.engine,"--private",str(private/mode),
            "--out",str(out)
        ],env=env,check=True)
        raw=path.read_text()
        pairs=[{"attempts":int(x),"suppressed":int(y)} for x,y in COUNT_RE.findall(raw)]
        normal.append((json.loads(out.read_text()),pairs))
    report=judge(normal[0][0],normal[1][0],normal[0][1],normal[1][1])
    (public/"C3X042_R8_CAUSAL_TT_SIDE_EFFECT_COURT.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("C3X042_R8_NATIVE_CAUSAL_COURT",report["status"],
          "target_tt_attempts_count_only",len(normal[1][1]))
    if not report["status"].startswith("PASS_"):raise SystemExit(2)

if __name__=="__main__":
    main()
