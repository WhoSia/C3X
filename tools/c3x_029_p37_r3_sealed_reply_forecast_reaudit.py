#!/usr/bin/env python3
"""P37/R3 independent re-adjudication of sealed original P37 prediction/referee ZIPs.

Do not alter either original file. A missing 96k reference opponent reply is
neither a model hit nor an error; retain it in denominator reporting separately.
"""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

PRED_ZIP_SHA = "721471da43d0bd973e2b084fc47070f5a5826d0add38cbc39a2ccfbca6a427f6"
REF_ZIP_SHA = "3bd8d76602b51f0bbb8b5892452444c27bad19532bc542e58565c726f2d6f93b"
PRED_JSON_SHA = "da395f0eb16e7b294af2056dadd92b579770aa8f1ae288d1d358132685807051"
REF_JSON_SHA = "d92c33d05fa506b1a84c222b57729f76a53a95970dd61ba38f67ea1ce3f700fa"
PRED_MEMBER = "P37_R2_THREE_RIVAL_PRE_REFERENCE_PREDICTIONS.json"
REF_MEMBER = "P37_R2_THREE_RIVAL_96K_REPLY_FORECAST_VERDICT.json"
METHODS = ("stockfish_pv", "simple_json", "c3x_legal_plan")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def require(ok, code):
    if not ok:
        raise ValueError("P37_R3_AUDIT_HOLD_" + code)


def sealed(zip_path, zip_sha, member, member_sha):
    raw = Path(zip_path).read_bytes()
    require(sha(raw) == zip_sha, "ZIP_HASH_" + member)
    with zipfile.ZipFile(zip_path) as z:
        b = z.read(member)
    require(sha(b) == member_sha, "MEMBER_HASH_" + member)
    return json.loads(b)


def recompute(pred, ref):
    require(pred["status"] == "PRE_REFEREE_FROZEN_THREE_RIVAL_RESPONSE_FORECASTS",
            "PRED_SCHEMA")
    require(ref["status"] == "EIGHT_EVENT_P37_EXPLORATORY_RESPONSE_FORECAST_SCORED_NOT_CONFIRMED_SUPERIORITY",
            "REF_SCHEMA")
    require(len(pred["cases"]) == len(ref["cases"]) == 8, "CASE_COUNT")
    counters = {m: {"correct": 0, "wrong": 0, "reference_missing": 0, "model_abstain_with_label": 0}
                for m in METHODS}
    pair_comparisons = {"pv_only_correct": 0, "c3x_only_correct": 0, "both_correct": 0,
                        "both_incorrect": 0, "undefined_reference": 0}
    event_results = []
    for p, r in zip(pred["cases"], ref["cases"]):
        require(p["case_id"] == r["case_id"] and p["source_id"] == r["source_id"],
                "CASE_IDENTITY")
        require(len(p["candidate_pairs"]) == len(r["scored_candidate_predictions"]) == 2,
                "TWO_SOURCE_FROZEN_CANDIDATES")
        per_event = {"event_family": r["event_family"],"source_id": r["source_id"],
                     "evaluable": 0,"undefined": 0,
                     "hits": {m:0 for m in METHODS}}
        for forecast, receipt in zip(p["candidate_pairs"],
                                     r["scored_candidate_predictions"]):
            require(forecast["root_uci"] == receipt["root_uci"], "ROOT_IDENTITY")
            answer=receipt["reference_96k"]["answer"]
            if answer is None:
                per_event["undefined"] += 1
                pair_comparisons["undefined_reference"] += 1
            else:
                per_event["evaluable"] += 1
            outcomes={}
            for method in METHODS:
                pre = forecast["predictions"][method]["reply"]
                original = receipt["method_verdicts"][method]
                require(pre == original["prediction"],"ORIGINAL_PREDICTION_WAS_CHANGED")
                require(answer == original["reference"],"REFERENCE_WAS_CHANGED")
                if answer is None:
                    counters[method]["reference_missing"] += 1
                    outcomes[method] = None
                    continue
                hit = pre is not None and pre == answer
                outcomes[method] = hit
                if hit:
                    counters[method]["correct"] += 1
                    per_event["hits"][method] += 1
                else:
                    counters[method]["wrong"] += 1
                    if pre is None:
                        counters[method]["model_abstain_with_label"] += 1
            if answer is not None:
                a,b = outcomes["stockfish_pv"],outcomes["c3x_legal_plan"]
                if a and b: pair_comparisons["both_correct"] += 1
                elif a: pair_comparisons["pv_only_correct"] += 1
                elif b: pair_comparisons["c3x_only_correct"] += 1
                else: pair_comparisons["both_incorrect"] += 1
        event_results.append(per_event)
    stable = sum(bool(x["stable_near_across_24_48_96k"]) for x in ref["cases"])
    near_24k = sum(x["initial_24k_margin"]["stratum"]=="near" for x in ref["cases"])
    labeled = sum(x["evaluable"] for x in event_results)
    undefined = sum(x["undefined"] for x in event_results)
    require(labeled + undefined == 16, "TRIAL_DENOMINATOR")
    return {
        "status":"P37_R3_READ_ONLY_REAUDIT_COMPLETE_C3X_LEGAL_PLAN_PV_COMPETITION_NEGATIVE",
        "original_archives_unchanged":True,
        "original_prediction_json_sha256":PRED_JSON_SHA,
        "original_referee_json_sha256":REF_JSON_SHA,
        "event_families":8,"candidate_trials_all":16,
        "evaluable_reference_labels":labeled,
        "unobserved_reference_labels":undefined,
        "raw_referee_summary_denominator_included_undefined":True,
        "corrected_denominator_inference_only":True,
        "per_method":{k:{**v,
                          "accuracy_on_evaluable":v["correct"]/labeled if labeled else None}
                      for k,v in counters.items()},
        "stockfish_pv_vs_c3x_plan_pairs":pair_comparisons,
        "near_24k_cases":near_24k,
        "stable_near_24_48_96k_cases":stable,
        "per_event":event_results,
        "model_limit":"C3X-inspired finite 3-ply material recovery heuristic, not full causal NNUE C3X system",
        "outcome_limit":"96k forced-root Stockfish PV opponent reply is an engine reference, not objective chess truth",
        "compute_limit":"Engine24k shared equally; C3X heuristic enumerates more legal states, so CPU is not equalized",
        "history_limit":"40 prior original games checked for full-UCI overlap; not all historical C3X event/family ledgers",
        "no_claims":["independent confirmed holdout","superior C3X explanation",
                     "NNUE feature->root mediation","human knowledge transfer"],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--predictions-zip",type=Path,required=True)
    p.add_argument("--referee-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    pred=sealed(a.predictions_zip,PRED_ZIP_SHA,PRED_MEMBER,PRED_JSON_SHA)
    ref=sealed(a.referee_zip,REF_ZIP_SHA,REF_MEMBER,REF_JSON_SHA)
    report=recompute(pred,ref)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("P37_R3_REAUDIT",report["candidate_trials_all"],
          report["evaluable_reference_labels"],report["per_method"],flush=True)


if __name__=="__main__":
    main()
