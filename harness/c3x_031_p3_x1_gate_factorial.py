"""C3X 0.31/P3-X1: complete physical F/N 2x2 causal gate experiment.

New genuine search arm: leave futility active but disable the downstream
null gate only for all 128 frozen source events. Because the original
futility return is hit first, null must not be reached. Uses 256 fresh
independent SF16 processes; zero new source targets or fitted models.

The existing other 3 cells came from original, already-exposed P2.
"""
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path

from c3x_030_r33_gate_panel import trial
from c3x_030_r33_replay import focus
from c3x_031_p2_1669_native_discovery import (
    SAMPLE_SHA, PATCHED_BINARY_SHA, NNUE_SHA, require, digest
)
from c3x_031_p2_1669_native_treatment import B1_SHA

B2_SHA = "be66a985016b4ceaae1379c64ee0f6347c3a2e8c4fd3660ceb394227ac237df1"
OBSERVED_ORIGINAL_CASES = 128
N_ONLY_REPEATS = 2


def verify_originals(sample_path,b1_path,b2_path,patch_path,net_path):
    for path,sha in ((sample_path,SAMPLE_SHA),(b1_path,B1_SHA),
                     (b2_path,B2_SHA),(patch_path,PATCHED_BINARY_SHA),
                     (net_path,NNUE_SHA)):
        require(digest(path)==sha,"P3-X1 input SHA mismatches frozen P2 original")
    source=json.loads(sample_path.read_text())
    b1=json.loads(b1_path.read_text())
    b2=json.loads(b2_path.read_text())
    cases={r["id"]:r for r in source["positions"]}
    original={r["id"]:r for r in b1["native_source_records"]}
    rows=b2["source_event_results"]
    require(len(cases)==len(original)==64 and
            len(rows)==128 and len({r["id"] for r in rows})==128,
            "original 64-game 128-event cohort changed")
    for row in rows:
        old=original[row["case_id"]]
        signed=old["targets"][row["group"]]["native_open_close"]["open"]
        require(row["valid_primary"] and
                row["original_target"]==signed and
                row["game_sha256"]==cases[row["case_id"]]["game_sha256"],
                "B2 original source event or its validity changed")
    return cases,rows


def prior_factorial(rows):
    """Source result contrast only; counts are NOT new independent samples."""
    outcome=Counter()
    detail=[]
    for r in rows:
        arms=r["arms"]
        old=r["original_untreated_bestmove"]
        sham=arms["sham0"]["bestmove"]
        f_only=arms["futility_only"]["bestmove"]
        both=arms["both_off0"]["bestmove"]
        close=arms["futility_only"]["target_event"]["close"]
        require(sham==old and arms["sham1"]["bestmove"]==old,
                "old sham is no longer original")
        require(arms["both_off1"]["bestmove"]==both,
                "old treatment cold repeat disappeared")
        require(close["skip_f"]=="1" and close["skip_n"]=="0",
                "old F-only source flag mismatch")
        outcome["original_target_events"]+=1
        outcome["original_F_only_final_flips"]+=int(f_only!=sham)
        outcome["original_F_and_N_off_final_flips"]+=int(both!=sham)
        outcome["conditional_null_flip_given_F_off"]+=int(both!=f_only)
        outcome["original_F_only_null_tried"]+=int(close["null_tried"]=="1")
        outcome["original_F_only_null_cut"]+=int(close["null_cut"]=="1")
        if r["group"]=="0":
            require(close["null_tried"]=="0" and both==f_only,
                    "pre-existing null-ineligible mismatch")
            outcome["null_ineligible_cases"]+=1
        else:
            require(close["null_tried"]=="1",
                    "pre-existing B2 null-eligible contact changed")
            outcome["null_eligible_cases"]+=1
        if both!=f_only:
            require(r["group"]=="1" and close["null_cut"]=="1"
                    and f_only==old and both!=old,
                    "conditional null interaction was not source-confirmed")
            detail.append(r["id"])
    require(outcome=={
        "original_target_events":128,
        "original_F_only_final_flips":8,
        "original_F_and_N_off_final_flips":14,
        "conditional_null_flip_given_F_off":6,
        "original_F_only_null_tried":64,
        "original_F_only_null_cut":50,
        "null_ineligible_cases":64,"null_eligible_cases":64
    },"original P2 factorial counts changed")
    return dict(outcome),detail


def evaluate_negative_cell(b2_row,run):
    expected=b2_row["original_target"]
    event=focus(run["events"],expected)
    close=event["close"]
    old=b2_row["arms"]["sham0"]
    require(event["open"]==expected,"new original event OPEN drifted")
    require(close["skip_f"]=="0" and close["skip_n"]=="1" and
            close["stopped"]=="0", "null-only source flags/stop invalid")
    require(close["futility"]=="1" and close["null_tried"]=="0"
            and close["null_cut"]=="0" and close["replies"]=="0",
            "null-only control unexpectedly passed through futility")
    for key in ("value","nodes","futility","null_tried","null_cut","replies"):
        require(close[key]==old["target_event"]["close"][key],
                "source child return changed despite futility kept: "+key)
    require(run["proof"]==b2_row["arms"]["sham0"]["proof"] if
            "proof" in b2_row["arms"]["sham0"] else
            run["proof"]["best"]==b2_row["arms"]["sham0"]["proof"],
            "original root producer changed in unreachable downstream null-only intervention")
    require(run["uci"]==old["source_uci"],
            "normalized UCI differs despite no reachable null-only intervention")
    require(run["proof"]["best"]["move"]==old["bestmove"],
            "bestmove unexpectedly changed under null-only")
    return {
        "bestmove":old["bestmove"],
        "uci_sha256":hashlib.sha256(("\n".join(run["uci"])+"\n").encode()).hexdigest(),
        "source_event":{"open":event["open"],"close":close},
        "original_native_stderr_sha256":run["trace"],
        "original_untreated_producer":run["proof"]["best_source"],
    }


def execute(args):
    cases,rows=verify_originals(args.sample,args.b1,args.b2,args.patch,args.net)
    old_counts,incremental_ids=prior_factorial(rows)
    args.out.mkdir(parents=True,exist_ok=True)
    items=[]
    for row in rows:
        case=cases[row["case_id"]]
        record={"id":row["id"],"family":row["family"],
                "group":row["group"],
                "new_physical_null_only_controls":[],
                "complete":False,"failure":None}
        for repeat in range(N_ONLY_REPEATS):
            name=row["id"]+f"/null_only_{repeat}"
            try:
                run=trial(args,case,name,binary=args.patch,observer=True,
                          target=int(row["original_target"]["event"]),
                          skip_f=False,skip_n=True)
                audit=evaluate_negative_cell(row,run)
                record["new_physical_null_only_controls"].append(audit)
            except (ValueError,KeyError,IndexError,AssertionError) as err:
                record["failure"]=f"{type(err).__name__}: {err}"
                record["new_physical_null_only_controls"].append(
                    {"status":"PHYSICAL_SOURCE_FAILURE","reason":record["failure"]})
        pair=record["new_physical_null_only_controls"]
        if len(pair)==2 and pair[0]==pair[1] and record["failure"] is None:
            record["complete"]=True
        elif record["failure"] is None:
            record["failure"]="COLD_NATIVE_REPEAT_DIVERGENCE"
        items.append(record)
        print("P3_X1_NATIVE_N_ONLY",row["id"],
              "PASS" if record["complete"] else record["failure"],flush=True)
    require(len(items)==128,"P3-X1 lost original 128-event denominator")
    valid=sum(a["complete"] for a in items)
    return {
        "schema":"C3X_031_P3_X1_PHYSICAL_2x2_GATE_FACTORIAL_V1",
        "stage":"NEW_REAL_PHYSICAL_NULL_ONLY_ARM_NO_NEW_COHORT",
        "source_exposed_P2_sample_sha256":SAMPLE_SHA,
        "source_existing_P2_B1_event_signature_sha256":B1_SHA,
        "source_existing_P2_B2_physical_results_sha256":B2_SHA,
        "source_engine_binary_sha256":PATCHED_BINARY_SHA,
        "source_nnue_sha256":NNUE_SHA,
        "games":64,"conservative_series":25,"original_events":128,
        "new_native_null_only_searches":len(items)*N_ONLY_REPEATS,
        "prior_source_native_searches_reused_as_3_cells":640,
        "new_physical_null_only_pass":valid,
        "new_physical_null_only_fail":128-valid,
        "previously_observed_original_source_factorial":old_counts,
        "conditional_null_source_flip_event_ids":incremental_ids,
        "full_physical_2x2_factorial_pass":valid==128,
        "scientific_classification":(
            "OBSERVATIONAL_PLUS_FOUR_ARM_PHYSICAL_SOURCE_PATH_FACTORIAL"
            if valid==128 else
            "HOLD_NEGATIVE_CONTROL_PHYSICAL_PARITY_FAILURE"),
        "new_real_null_only_source_results":items,
        "scientific_limits":[
            "Original P2 F-only/Both outcomes were exposed before P3-X1 design.",
            "Null-only flag has no computational reach when futility return terminates same child.",
            "Six effects are conditional null-gate contributions after futility is suppressed.",
            "This is not a TT/history/search-budget mediator restoration.",
            "No fresh chess-future ranking or human test was performed.",
        ],
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ("sample","b1","b2","patch","net","out","result"):
        ap.add_argument(k,type=Path)
    a=ap.parse_args()
    data=execute(a)
    a.result.parent.mkdir(parents=True,exist_ok=True)
    a.result.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    print("P3_X1_GATE_FACTORIAL_VERDICT",data["scientific_classification"],
          "valid",data["new_physical_null_only_pass"],
          "new_searches",data["new_native_null_only_searches"],
          "result_sha256",digest(a.result))


if __name__=="__main__":
    main()
