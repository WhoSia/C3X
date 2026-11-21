"""P2-B2 independent prospective outcome court: no model fit on TWIC1669.

Reads frozen B1 pre-outcome probabilities from signed B2 native results.
Computes family-cluster uncertainty using original locked P1 criteria.
B2 physical source results and Brier/ap calculations are distinct objects.
"""
from collections import Counter, defaultdict
import argparse
import hashlib
import json
import random
from pathlib import Path

from c3x_031_p1_forecast import metrics
from c3x_031_p2_1669_native_treatment import B1_SHA, MODEL_SHA, SAMPLE_SHA

SEED=310121
BOOTSTRAPS=2000
REQUIRED_BRIER_GAIN=.01


def require(test, reason):
    if not test:
        raise ValueError(reason)


def audit_and_score(source):
    require(source["stage"]=="ACTUAL_NEW_SOURCE_INTERVENTIONS_UNSCORED",
            "not a new physical intervention result")
    require(source["pre_outcome_signed_source_event_sha256"]==B1_SHA
            and source["pre_outcome_model_sha256"]==MODEL_SHA
            and source["original_source_cohort_sha256"]==SAMPLE_SHA,
            "original source/prediction seal mismatch")
    rows=source["source_event_results"]
    require(len(rows)==128 and len({r["id"] for r in rows})==128
            and len({r["case_id"] for r in rows})==64
            and len({r["family"] for r in rows})==25,
            "case, source event or event-family denominator incomplete")
    require(source["actual_native_intervention_processes"]==640
            and source["native_treatment_processes_per_event"]==5,
            "not all original physical intervention arms executed")
    complete=[]
    all_prediction=[]
    phys_invalid=[]
    for row in rows:
        if row["predictions"] is not None:
            require(set(row["predictions"])=={"m0","m1","m2"} and
                    all(type(p) in (float,int) and 0<p<1
                        for p in row["predictions"].values()),
                    "P2-B1 forecasts missing or changed")
            all_prediction.append(row)
        if row["valid_primary"]:
            require(row["y"] in (0,1) and row["invalid_reason"] is None,
                    "invalid physical y represented as a result")
            require(set(row["arms"])=={
                    "sham0","sham1","both_off0","both_off1","futility_only"},
                    "source treatment lacks a physical arm")
            require(row["y"]==int(row["original_untreated_bestmove"]!=
                                   row["arms"]["both_off0"]["bestmove"]),
                    "final-root-move effect does not match original source arm")
            if row["predictions"] is not None:
                complete.append({"id":row["id"],"family":row["family"],"y":row["y"],
                                 **row["predictions"]})
        else:
            require(row["y"] is None and row["invalid_reason"],
                    "invalid physical case has an alleged real outcome")
            phys_invalid.append(row["id"])
    require(len(all_prediction)==126,
            "predeclared two public non-cp abstentions were erased")
    families=sorted({r["family"] for r in rows})
    require(set(r["family"] for r in complete).issubset(set(families)),
            "family duplication or unknown source group")
    if not complete:
        return {
            "verdict":"HOLD_NO_PHYSICALLY_VALID_FORECAST_ROWS",
            "original_event_slots":128,"measured_with_preforecast":0,
            "invalid_source_target_ids":phys_invalid,
        }
    metric={name:metrics(complete,name) for name in ("m0","m1","m2")}
    grouped=defaultdict(list)
    for row in complete:
        grouped[row["family"]].append(row)
    rng=random.Random(SEED)
    gains={"m0_minus_m2":[],"m1_minus_m2":[]}
    for _ in range(BOOTSTRAPS):
        draws=[rng.choice(families) for _ in families]
        sampled=[r for fam in draws for r in grouped[fam]]
        if not sampled:
            continue
        m2=metrics(sampled,"m2")["brier"]
        for k,model in (("m0_minus_m2","m0"),("m1_minus_m2","m1")):
            gains[k].append(metrics(sampled,model)["brier"]-m2)
    intervals={}
    for k,samples in gains.items():
        require(len(samples)==BOOTSTRAPS,"cluster bootstrap lost an entire replicate")
        x=sorted(samples)
        model=k[:2]
        intervals[k]={
            "observed_gain":metric[model]["brier"]-metric["m2"]["brier"],
            "family_cluster_bootstrap95":[x[int(.025*BOOTSTRAPS)],
                                          x[int(.975*BOOTSTRAPS)-1]],
        }
    sufficient_statistical_signal=(
        all(v["observed_gain"]>=REQUIRED_BRIER_GAIN
            and v["family_cluster_bootstrap95"][0]>0
            for v in intervals.values())
        and metric["m2"]["average_precision"] is not None
        and all(metric[x]["average_precision"] is not None
                for x in ("m0","m1"))
        and metric["m2"]["average_precision"]>=max(
            metric["m0"]["average_precision"],
            metric["m1"]["average_precision"])
    )
    physical_valid=sum(row["valid_primary"] for row in rows)
    if physical_valid!=128:
        verdict="HOLD_INCOMPLETE_PHYSICAL_SOURCE_EFFECT_COVERAGE"
    elif len(complete)!=128:
        verdict=("HOLD_PREDECLARED_PUBLIC_NONCP_PREDICTION_ABSTENTION" if
                 sufficient_statistical_signal else
                 "NO_CONFIRMED_PROSPECTIVE_SOURCE_STATE_GAIN")
    elif sufficient_statistical_signal:
        verdict="P2_PROSPECTIVE_PREDICTIVE_SIGNAL_ONLY_NO_CAUSAL_SUFFICIENCY"
    else:
        verdict="NO_CONFIRMED_PROSPECTIVE_SOURCE_STATE_GAIN"
    results={
        "schema":"C3X_031_P2_B2_TWIC1669_FAMILY_CLUSTERED_OUTCOME_COURT_V1",
        "evidence_class":"ACTUAL_NEW_NATIVE_INTERVENTION_AFTER_FROZEN_MODEL",
        "source_physical_event_seal_sha256":B1_SHA,
        "source_pre_outcome_model_sha256":MODEL_SHA,
        "source_original_cohort_sha256":SAMPLE_SHA,
        "games":64,"canonical_tournament_families":25,
        "original_event_slots":128,
        "actual_native_treatment_searches":640,
        "valid_physical_event_contacts":physical_valid,
        "invalid_physical_target_ids":phys_invalid,
        "predeclared_noncpscore_abstentions":2,
        "actual_scored_forecasts":len(complete),
        "actual_final_move_flips":sum(r["y"]==1 for r in rows),
        "scored_actual_positive_flips":sum(r["y"] for r in complete),
        "required_brier_gain":REQUIRED_BRIER_GAIN,
        "metrics":metric,
        "family_cluster_gain_intervals":intervals,
        "passes_predictive_gain_only":sufficient_statistical_signal,
        "verdict":verdict,
        "scientific_sufficiency_causal_TT_history_mechanism_proved":False,
        "human_chess_strategy_value_proved":False,
        "note":"Complete outcomes required for all 128; 2 original P2 public-mate predictions abstained by design. No post-result retraining.",
        "all_pre_outcome_predictions_and_genuine_y":sorted(complete,key=lambda r:r["id"]),
    }
    return results


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("real_native_result",type=Path)
    p.add_argument("analysis_json",type=Path)
    args=p.parse_args()
    result=audit_and_score(json.loads(args.real_native_result.read_text()))
    args.analysis_json.parent.mkdir(parents=True,exist_ok=True)
    args.analysis_json.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("P2_NATIVE_OUTCOME_COURT",result["verdict"],
          "prediction_count",result.get("actual_scored_forecasts"),
          "source_flips",result.get("actual_final_move_flips"),
          "sha256",hashlib.sha256(args.analysis_json.read_bytes()).hexdigest())


if __name__=="__main__":
    main()
