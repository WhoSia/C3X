"""C3X 0.31/P2: actual new-game physical futility/null intervention court.

Requires sealed P2 source-only, before-treatment selection and M0/M1/M2
predictions. Executes the original R33 arms exactly, never retunes outcomes.
All game/target, sham, null and censoring denominators are explicit.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import random

from c3x_030_r33_gate_panel import trial
from c3x_030_r33_replay import PRETREATMENT
from c3x_031_p1_forecast import metrics
from c3x_031_p2_lockcheck import MODEL_SHA, verify

ORIGIN_GAME_SHA="2a174dcf56a333408693785eb0a844a419f7f8ba090c0a00187f3dab483d57e4"
SOURCE_NET_SHA="5af11540bbfefcb54e38c5dd000cab4b469dfa7599a1d55be5d2722c20a8929b"
SOURCE_BINARY_SHA="ce13b5899ab6862a621ee6033ac661f7ded0abf3f2b4ea073a163b0c3154afa1"
FAMILY_BOOT=2000
RNG_SEED=310221


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def matched(events,original):
    candidates=[e for e in events if e["open"]["event"]==original["event"]]
    require(len(candidates)==1, "physical event not reached exactly once")
    row=candidates[0]
    require(all(row["open"][key]==original[key] for key in PRETREATMENT),
            "physical pre-contact event signature drift")
    return row


def assert_public_same(a,b,context):
    require(a["uci"]==b["uci"] and a["proof"]==b["proof"],
            "source sham diverged from original baseline: "+context)


def real_arm(args,case,context,target,arm,skip_f,skip_n):
    repeat=[]
    for count in (0,1):
        observed=trial(args,case,context+f"/{arm}-{count}",binary=args.patch,
                       observer=True,target=int(target["event"]),
                       skip_f=skip_f,skip_n=skip_n)
        event=matched(observed["events"],target)
        require(event["close"]["skip_f"]==str(int(skip_f))
                and event["close"]["skip_n"]==str(int(skip_n)),
                "source intervention gate not physically activated")
        repeat.append({
            "event":event,
            "public_uci":observed["uci"],
            "source_best":observed["proof"]["best"],
            "source_best_producer":observed["proof"]["best_source"],
            "source_root_counts":observed["proof"]["counts"],
            "stderr_sha256":observed["trace"],
        })
    for key in ("event","public_uci","source_best","source_best_producer","source_root_counts"):
        require(repeat[0][key]==repeat[1][key],
                "two native cold repeats disagreed: "+context+"/"+arm+"/"+key)
    return repeat


def source_case(args,baseline,case):
    pos=case["id"]
    untouched=baseline["baseline_bestmove"]
    status={}
    sham=trial(args,case,pos+"/untargeted-sham",binary=args.patch,
               observer=True,target=0,skip_f=True,skip_n=True)
    require(sham["proof"]["best"]["move"]==untouched,
            "no-contact sham unexpectedly changed move")
    # Compare source control to original baseline known from sealed experiment.
    require(sham["events"] is not None,
            "sham source trace unavailable")
    for group in ("0","1"):
        b=baseline["targets"][group]
        if b["status"]=="NOT_CONTACTED_NO_ELIGIBLE_EVENT":
            status[group]={"status":"NOT_CONTACTED_SOURCE_ONLY"}
            continue
        require(b["status"]=="UNTREATED_NATIVELY_OBSERVED_FORECAST_FROZEN",
                "unknown after-treatment source status")
        target=b["target"]
        context=pos+"/"+group
        arms={}
        for name,off_f,off_n in (
            ("futility_only",True,False),
            ("both_off",True,True),
        ):
            pair=real_arm(args,case,context,target,name,off_f,off_n)
            closed=pair[0]["event"]["close"]
            arms[name]={
                "source_contact":True,
                "stopped":closed["stopped"]=="1",
                "direct_child_return":closed["value"],
                "null_tried":closed["null_tried"]=="1",
                "null_cut":closed["null_cut"]=="1",
                "real_child_board_replies":int(closed["replies"]),
                "final_move":pair[0]["source_best"]["move"],
                "final_completed_depth":pair[0]["source_best"]["completed"],
                "final_bestmove_changed":pair[0]["source_best"]["move"]!=untouched,
                "original_untreated_move":untouched,
                "full_repeats":pair,
            }
        if group=="0":
            x,y=arms["futility_only"],arms["both_off"]
            require(all(x[key]==y[key] for key in (
                "direct_child_return","null_tried","null_cut",
                "real_child_board_replies","final_move","final_completed_depth")),
                "null-ineligible extra null mask was not inert")
        p=b["predicted_bestmove_flip_probabilities"]
        if arms["both_off"]["stopped"]:
            conclusion="HOLD_CHILD_RETURN_UNOBSERVABLE"
        else:
            conclusion="ACTUAL_SOURCE_TREATMENT_OBSERVED"
        status[group]={
            "status":conclusion,
            "treatment_bestmove_changed":arms["both_off"]["final_bestmove_changed"],
            "frozen_predictions":p,
            "frozen_pre_contact_features":b["before_treatment_features"],
            "original_target":target,
            "arms":arms,
        }
    return {"id":pos,"family":baseline["family"],"game_sha256":baseline["game_sha256"],
            "sham_result":sham["proof"]["best"]["move"],
            "sham_public_uci":sham["uci"],
            "targets":status}


def bootstrap(rows):
    if not rows:
        return None
    families=sorted({r["family"] for r in rows})
    byfamily={family:[r for r in rows if r["family"]==family]
              for family in families}
    rng=random.Random(RNG_SEED)
    scores={k:metrics(rows,k) for k in ("m0","m1","m2")}
    differentials={"m0_minus_m2":[],"m1_minus_m2":[]}
    for _ in range(FAMILY_BOOT):
        sample=[r for family in (rng.choice(families) for __ in families)
                for r in byfamily[family]]
        for key,comparator in (("m0_minus_m2","m0"),("m1_minus_m2","m1")):
            differentials[key].append(
                metrics(sample,comparator)["brier"]-metrics(sample,"m2")["brier"])
    CIs={}
    for key,draws in differentials.items():
        x=sorted(draws)
        CIs[key]={"observed":scores[key[:2]]["brier"]-scores["m2"]["brier"],
                  "family_cluster_bootstrap95":[
                      x[int(.025*FAMILY_BOOT)],x[int(.975*FAMILY_BOOT)-1]]}
    aps=[scores[k]["average_precision"] for k in ("m0","m1","m2")]
    eligibility=sum(r["y"] for r in rows)>0
    pass_gate=(eligibility and all(v["observed"]>=.01 and
               v["family_cluster_bootstrap95"][0]>0 for v in CIs.values())
               and aps[2]>=max(aps[:2]))
    return {
        "source_family_groups_with_physically_reached_targets":len(families),
        "physically_observed_target_count":len(rows),
        "observed_root_flips":sum(r["y"] for r in rows),
        "scores":scores,
        "Brier_effect_differences":CIs,
        "predeclared_min_gain":.01,
        "prospective_model_gain_gate":
            "P2_PROSPECTIVE_PREDICTIVE_GAIN" if pass_gate else
            "NEGATIVE_OR_UNRESOLVED_PROSPECTIVE_TRANSPORT",
        "no_physical_mediation_claim":True,
        "no_chess_move_superiority_claim":True,
    }


def examine(args):
    require(digest(args.sample.read_bytes())==ORIGIN_GAME_SHA,
            "full original game freeze changed")
    require(digest(args.net.read_bytes())==SOURCE_NET_SHA,
            "not the original network")
    require(digest(args.patch.read_bytes())==SOURCE_BINARY_SHA,
            "not the original source-gate binary")
    verify(args.model,args.p1_training)
    frozen_bytes=args.discovery.read_bytes()
    require(digest(frozen_bytes)==args.expected_discovery_sha256,
            "post-outcome modifications to pre-treatment source discovery")
    frozen=json.loads(frozen_bytes)
    require(frozen["stage"]=="P2_PHYSICAL_EVENT_SELECTED_WITHOUT_TREATMENT"
            and frozen["real_treatment_searches"]==0
            and frozen["source_game_count"]==64
            and frozen["frozen_model_sha256"]==MODEL_SHA
            and frozen["source_binary_sha256"]==SOURCE_BINARY_SHA,
            "invalid pre-treatment source nomination or model")
    game_data=json.loads(args.sample.read_text())
    original={x["id"]:x for x in game_data["sample"]}
    require(len(original)==64 and len(frozen["source_events"])==64,
            "sample size was opportunistically shortened")
    results=[]
    for b in frozen["source_events"]:
        case=original[b["id"]]
        require(case["game_sha256"]==b["game_sha256"],
                "physical game prefix changed since prefreeze")
        row=source_case(args,b,case)
        results.append(row)
        print("P2_TREATMENT_PROGRESS",len(results),"/64",row["id"],
              {k:v["status"] for k,v in row["targets"].items()},flush=True)
    require(len(results)==64,"incomplete actual P2 candidate-family cohort")
    all_targets=[(r,g,x) for r in results for g,x in r["targets"].items()]
    statuses=Counter(x["status"] for r,g,x in all_targets)
    metrics_rows=[]
    for r,g,x in all_targets:
        if x["status"]=="ACTUAL_SOURCE_TREATMENT_OBSERVED":
            metrics_rows.append({
                "game":r["game_sha256"],"family":r["family"],
                "id":r["id"]+"-"+g,
                "y":int(x["treatment_bestmove_changed"]),
                **x["frozen_predictions"]})
    require(len(metrics_rows)+sum(v for k,v in statuses.items()
                if k!="ACTUAL_SOURCE_TREATMENT_OBSERVED")==128,
            "unobservable and no-contact events excluded from denominator")
    report={
        "id":"C3X_031_P2_TWIC1670_PROSPECTIVE_NATIVE_EARLY_EXIT_CONTRAST",
        "source":frozen["original_publisher_zip_sha256"],
        "before_treatment_source_discovery_sha256":
            args.expected_discovery_sha256,
        "original_legal_game_sample_sha256":ORIGIN_GAME_SHA,
        "original_p1_train_model_sha256":MODEL_SHA,
        "stockfish16_source_patched_binary_sha256":SOURCE_BINARY_SHA,
        "source_game_count":64,
        "potential_source_event_slots":128,
        "physical_target_statuses":dict(statuses),
        "observed_effect_denominator":len(metrics_rows),
        "new_source_native_searches_attempted":
            64+sum(4 for r,g,x in all_targets
                   if x["status"]!="NOT_CONTACTED_SOURCE_ONLY"),
        "result_over_eligible_events":bootstrap(metrics_rows),
        "scope":"new game/source intervention study, conditioned on frozen eligible physical events",
        "true_mechanistic_intermediate_mediator_identified":False,
        "independently_evaluated_strategy":False,
        "human_learning_measured":False,
        "cases":results,
    }
    public={key:val for key,val in report.items() if key!="cases"}
    public["per_game"]= [{
        "id":x["id"],"family":x["family"],
        "status":{k:v["status"] for k,v in x["targets"].items()},
        "final_move_changed":{k:v.get("treatment_bestmove_changed")
                              for k,v in x["targets"].items()}}
        for x in results]
    return report,public


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("sample","discovery","patch","net","model",
                "p1_training","out","private","public"):
        p.add_argument(key,type=Path)
    p.add_argument("--expected-discovery-sha256",required=True)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    full,public=examine(args)
    for dest,obj in ((args.private,full),(args.public,public)):
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
    print("P2_NATIVE_TREATMENT_COURT",public["physical_target_statuses"],
          "searches",public["new_source_native_searches_attempted"],
          "derived_verdict",public["result_over_eligible_events"]["prospective_model_gain_gate"]
          if public["result_over_eligible_events"] else "NO_OBSERVABLE_EVENTS",
          "full_sha256",digest(args.private.read_bytes()))


if __name__=="__main__":
    main()
