"""C3X 0.31/P2-B2: genuine source-gate native interventions, after B1 seal.

Frozen experimental worlds: TWIC1669 64 legal complete histories in 25
conservative tournament-series clusters; 128 original eligible source events;
126 prior probabilities + two non-cp abstentions. Performs each ORIGINAL
source-chosen target with sham x2, both_off x2 and futility_only x1.
Never retargets by observing the bestmove flip. Preserves all null/failed arms.
No causal state mediation or independent chess-strength inference.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from c3x_030_r33_gate_panel import trial
from c3x_030_r33_replay import PRETREATMENT, focus
from c3x_031_p2_1669_native_discovery import (
    SAMPLE_SHA, MODEL_SHA, PUBLISHER_SHA, UPSTREAM_COMMIT,
    REFERENCE_BINARY_SHA, PATCHED_BINARY_SHA, NNUE_SHA, require, digest
)

B1_SHA = "d364e6ca24599110fa19ac41e19164069a164c15aa396aac6b2833482e3818b1"
B1_ORIGINAL_CONTROL_SEARCHES = 192
NODES = 32000
ARMS = (
    ("sham0", False, False),
    ("sham1", False, False),
    ("both_off0", True, True),
    ("both_off1", True, True),
    ("futility_only", True, False),
)


def validate_inputs(args):
    for name,sha in (("sample",SAMPLE_SHA),("b1",B1_SHA),
                     ("model",MODEL_SHA),("patch",PATCHED_BINARY_SHA),
                     ("net",NNUE_SHA)):
        require(digest(getattr(args,name))==sha,
                "physical intervention source identity changed: "+name)
    sample=json.loads(args.sample.read_text())
    b1=json.loads(args.b1.read_text())
    require(b1["status"]=="NATIVE_UNTREATED_PHYSICAL_TARGETS_AND_PREDICTIONS_FROZEN"
            and b1["actual_untreated_stockfish_searches"]==B1_ORIGINAL_CONTROL_SEARCHES
            and b1["actual_source_treatment_searches"]==0
            and b1["source_game_count"]==64 and b1["source_event_family_count"]==25
            and b1["frozen_candidate_sha256"]==SAMPLE_SHA
            and b1["pre_outcome_model_sha256"]==MODEL_SHA,
            "B1 is not an untouched original source forecast seal")
    require(len(b1["native_source_records"])==len(sample["positions"])==64,
            "B1 case set changed")
    require(b1["target_contact_and_prediction_status"]=={
            "PHYSICAL_TARGET_PREDICTED_BEFORE_TREATMENT":126,
            "PHYSICAL_TARGET_EXISTED_PUBLIC_ABSTAIN":2
        }, "frozen source opportunity/abstention denominator changed")
    for case,before in zip(sample["positions"],b1["native_source_records"]):
        require(case["id"]==before["id"]
                and case["family"]==before["family"]
                and case["game_sha256"]==before["game_sha256"]
                and set(before["targets"])=={"0","1"}
                and all(t["status"] in (
                    "PHYSICAL_TARGET_PREDICTED_BEFORE_TREATMENT",
                    "PHYSICAL_TARGET_EXISTED_PUBLIC_ABSTAIN",
                ) for t in before["targets"].values()),
                "B1 source targets missing or reselected")
        for grp in ("0","1"):
            signed=before["targets"][grp]["native_open_close"]
            require(signed["open"]["null_eligible"]==grp
                    and signed["close"]["event"]==signed["open"]["event"]
                    and signed["close"]["skip_f"]=="0"
                    and signed["close"]["skip_n"]=="0",
                    "the signed source event was not an untreated physical early return")
    return sample,b1


def validate_arm(original, target, receipt, f, n, log_path):
    """Fully contacted physical source event, not just a reported move."""
    match=focus(receipt["events"],target)
    require(match["open"]==target,
            "native target pre-treatment OPEN differs")
    close=match["close"]
    require(close["skip_f"]==str(int(f))
            and close["skip_n"]==str(int(n))
            and close["stopped"]=="0"
            and match["open"]["event"]==close["event"],
            "contact missing, wrong flags or source event interrupted")
    best=receipt["proof"]["best"]["move"]
    require(best and len(best) in (4,5), "bad source bestmove")
    emitted=receipt["uci"]
    log=Path(log_path).read_bytes()
    return {
        "bestmove":best,
        "proof":receipt["proof"]["best"],
        "root_producer":receipt["proof"]["best_source"],
        "target_event":{"open":match["open"],"close":close},
        "original_unchanged_target_signature":True,
        "uci_public_sha256":hashlib.sha256(("\n".join(emitted)+"\n").encode()).hexdigest(),
        "stderr_sha256":hashlib.sha256(log).hexdigest(),
        "first_pub":emitted[0] if emitted else "",
        "last_pub":emitted[-1] if emitted else "",
        "changes_untouched_choice":int(best!=original),
        "source_uci":emitted,
    }


def verified_equal(x,y):
    # Preserve exact raw logs, root provenance and UCI; no runtime time/nps
    # trusted as a control (run() normalizes UCI).
    return x==y


def execute(args):
    sample,b1=validate_inputs(args)
    source_by_id={p["id"]:p for p in sample["positions"]}
    output=[]
    for before in b1["native_source_records"]:
        pos=source_by_id[before["id"]]
        for grp in ("0","1"):
            target_item=before["targets"][grp]
            origin=before["original_untreated_bestmove"]
            signed=target_item["native_open_close"]["open"]
            contact_id=int(signed["event"])
            key=before["id"]+"-"+grp
            result={
                "id":key,"case_id":before["id"],"group":grp,
                "family":before["family"],"game_sha256":before["game_sha256"],
                "original_untreated_bestmove":origin,
                "b1_treatment_before_model_status":target_item["status"],
                "original_target":signed,
                "predictions":target_item.get("frozen_m0_m1_m2_forecasts"),
                "arms":{},
                "valid_primary":False,
                "y":None,"invalid_reason":None,
                "null_ineligible_extra_null_no_op":None,
            }
            # Genuine full source + prior fixed target, no re-selection.
            for name,off_f,off_n in ARMS:
                folder=args.out/key/name
                try:
                    receipt=trial(args,pos,key+"/"+name,binary=args.patch,
                                  observer=True,target=contact_id,
                                  skip_f=off_f,skip_n=off_n)
                    arm=validate_arm(origin,signed,receipt,off_f,off_n,
                                     folder/"stderr.txt")
                    result["arms"][name]=arm
                except (ValueError,AssertionError,KeyError,IndexError) as e:
                    result["arms"][name]={"status":"INVALID_PHYSICAL_ARM",
                                         "reason":str(e)}
                    if result["invalid_reason"] is None:
                        result["invalid_reason"]="ARM_"+name+"_"+type(e).__name__
            if all(name in result["arms"] and
                   result["arms"][name].get("original_unchanged_target_signature")
                   for name,_,_ in ARMS):
                a=result["arms"]
                # Need both checks across independently reset source processes.
                if (not verified_equal(a["sham0"],a["sham1"]) or
                    a["sham0"]["bestmove"]!=origin or
                    a["sham0"]["uci_public_sha256"]!=before["original_reference_uci_sha256"]):
                    result["invalid_reason"]="SHAM_OR_COLD_PARITY_FAIL"
                elif not verified_equal(a["both_off0"],a["both_off1"]):
                    result["invalid_reason"]="TREATMENT_COLD_REPEAT_DISAGREE"
                else:
                    result["valid_primary"]=True
                    result["y"]=int(a["both_off0"]["bestmove"]!=origin)
                    result["invalid_reason"]=None
                    if grp=="0":
                        result["null_ineligible_extra_null_no_op"]=(
                            a["futility_only"]["bestmove"]==a["both_off0"]["bestmove"]
                            and a["futility_only"]["uci_public_sha256"]==
                                a["both_off0"]["uci_public_sha256"]
                        )
            output.append(result)
            print("P2_NATIVE_TREATMENT",key,"original",origin,
                  "primary_y",result["y"],"valid",result["valid_primary"],
                  "failure",result["invalid_reason"],flush=True)
    require(len(output)==128 and
            len({r["id"] for r in output})==128 and
            len({r["game_sha256"] for r in output})==64,
            "the 128 frozen target denominator changed under treatment")
    counts=Counter(
        "VALID_"+str(row["y"]) if row["valid_primary"] else
        (row["invalid_reason"] or "INVALID_UNCLASSIFIED")
        for row in output)
    positive=sum(r["y"]==1 for r in output if r["valid_primary"])
    result={
        "schema":"C3X_031_P2_TWIC1669_NATIVE_PHYSICAL_B2_RESULTS_V1",
        "stage":"ACTUAL_NEW_SOURCE_INTERVENTIONS_UNSCORED",
        "research_version":"0.31",
        "source_issue":1669,
        "original_publisher_zip_sha256":PUBLISHER_SHA,
        "original_source_cohort_sha256":SAMPLE_SHA,
        "pre_outcome_signed_source_event_sha256":B1_SHA,
        "pre_outcome_model_sha256":MODEL_SHA,
        "native_original_stockfish_commit":UPSTREAM_COMMIT,
        "native_patched_sha256":PATCHED_BINARY_SHA,
        "native_reference_sha256":REFERENCE_BINARY_SHA,
        "native_nnue_sha256":NNUE_SHA,
        "source_game_count":64,
        "conservative_tournament_families":25,
        "intended_physical_event_slots":128,
        "actual_native_intervention_processes":len(output)*len(ARMS),
        "original_untreated_source_searches_before_arms":B1_ORIGINAL_CONTROL_SEARCHES,
        "native_treatment_processes_per_event":5,
        "physically_valid_primary_slots":sum(r["valid_primary"] for r in output),
        "physically_valid_primary_flip_count":positive,
        "physical_protocol_status_counts":dict(counts),
        "machine_derive_only_brier_AP_after_source_result_is_sealed":True,
        "source_event_results":output,
        "scientific_limitations":[
            "Source bestmove flip is a finite-budget native decision effect, not a superior chess strategy.",
            "Same event family/game correlations must be handled in uncertainty.",
            "Two original source events have predeclared public non-cp prediction abstentions.",
            "No source-state TT/history/budget mediator has been checkpoint-restored.",
            "The decision-state compression optimum and human learning remain unproved.",
        ],
    }
    public={k:v for k,v in result.items() if k!="source_event_results"}
    public["per_case"]=[{
        "id":row["id"],"family":row["family"],
        "has_original_forecast":row["predictions"] is not None,
        "physical_valid":row["valid_primary"],
        "final_choice_changed":row["y"],
        "invalid_reason":row["invalid_reason"],
        "null_ineligible_extra_null_no_op":row["null_ineligible_extra_null_no_op"],
    } for row in output]
    return result,public


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("sample","b1","model","patch","net","out","private","public"):
        p.add_argument(key,type=Path)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    private,public=execute(args)
    for path,value in ((args.private,private),(args.public,public)):
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")
        print("P2_B2_NATIVE_RESULTS",path,"sha256",digest(path),flush=True)


if __name__=="__main__":
    main()
