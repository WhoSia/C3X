"""C3X 0.31 P2: outcome-blind native source observation and frozen predictions.

Run only after immutable 64-game legal sample, source binary pair, and P1-only
final model are sealed. This stage NEVER sets R33 skip flags on any real event.
The post-selected physical target signatures and model forecasts are frozen
BEFORE the later physically intervening P2 experiment.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from c3x_030_r33_gate_panel import select,trial
from c3x_031_p1_extract import last_public
from c3x_031_p2_lockcheck import MODEL_SHA, verify, predict

GAME_SAMPLE_SHA = "2a174dcf56a333408693785eb0a844a419f7f8ba090c0a00187f3dab483d57e4"
NET_SHA = "5af11540bbfefcb54e38c5dd000cab4b469dfa7599a1d55be5d2722c20a8929b"


def require(ok,reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def transform(public,target,best,group):
    depth,cp,pv,upper,lower=public
    return {
        "public_depth":depth,
        "public_score_cp":cp,
        "public_pv_len":pv,
        "public_upper_bound":upper,
        "public_lower_bound":lower,
        "source_depth":int(target["depth"]),
        "source_ply":int(target["ply"]),
        "futility_slack":int(target["floor"])-int(target["beta"]),
        "source_progress_nodes":int(target["nodes"]),
        "source_attempt":int(target["attempt"]),
        "source_root_is_public_best":int(target["root"]==best),
        "stratum":int(group),
    }


def freeze(args):
    require(sha(args.sample.read_bytes())==GAME_SAMPLE_SHA,
            "invalid original pre-treatment P2 full history sample")
    original=json.loads(args.sample.read_text())
    require(original["stage"]=="GAME_HISTORY_SAMPLE_FROZEN_NO_NATIVE_TREATMENTS"
            and original["source_treatments_observed"]==0
            and len(original["sample"])==64,
            "P2 full game sample was unsealed or already treated")
    require(sha(args.net.read_bytes())==NET_SHA, "wrong pinned SF16 original NNUE")
    check=verify(args.model,args.p1_training)
    require(check["model_sha256"]==MODEL_SHA,"P1 final coefficients not frozen")
    build=json.loads(args.build_receipt.read_text())
    require(build.get("stage")=="P2_NATIVE_BUILD_SOURCE_ONLY_NO_TREATMENTS"
            and build["original_stockfish_commit"]==
                "68e1e9b3811e16cad014b590d7443b9063b3eb52",
            "not source-pinned official SF16")
    require("pre_R33_reference_binary_sha256" in build,
            "missing pre-R33 passive reference executable")
    require(build["binary_sha256"]==sha(args.patch.read_bytes())
            and build["pre_R33_reference_binary_sha256"]==sha(args.old.read_bytes()),
            "source binary identity drifted after prefreeze")
    model=json.loads(args.model.read_text())
    rows,failures=[],[]
    for pos in original["sample"]:
        id=pos["id"]
        old=trial(args,pos,id+"/r31",binary=args.old,observer=False)
        off=trial(args,pos,id+"/r33-off",binary=args.patch,observer=False)
        seen=trial(args,pos,id+"/r33-observed",binary=args.patch,observer=True)
        require(old["uci"]==off["uci"]==seen["uci"],
                "observer or R33 patch changed actual untouched UCI: "+id)
        require(old["proof"]==off["proof"]==seen["proof"],
                "observer or R33 patch changed full native root producer: "+id)
        require(old["events"]==off["events"]==[],
                "observer-only controls emitted actual R33 reads: "+id)
        public,best=last_public(
            (args.out/id/"r33-observed"/"stdout.txt").read_bytes())
        require(best==seen["proof"]["best"]["move"],
                "root public best and source producer disagree: "+id)
        selection=select(seen["events"])
        per_case={"id":id,"game_sha256":pos["game_sha256"],
                  "family":pos["family"],"source_legal_history_ply":pos["ply"],
                  "baseline_bestmove":best,
                  "untouched_public":list(public),
                  "untouched_uci_sha256":sha(("\n".join(seen["uci"])+"\n").encode()),
                  "event_census":len(seen["events"]),
                  "targets":{}}
        for group in ("0","1"):
            if group not in selection:
                per_case["targets"][group]={"status":"NOT_CONTACTED_NO_ELIGIBLE_EVENT"}
                continue
            target=selection[group]["open"]
            feature=transform(public,target,best,group)
            require(feature["futility_slack"]>=0
                    and feature["stratum"]==int(target["null_eligible"]),
                    "incorrect physical event eligible signature")
            forecasts={m:predict(model,feature,m) for m in ("m0","m1","m2")}
            per_case["targets"][group]={
                "status":"UNTREATED_NATIVELY_OBSERVED_FORECAST_FROZEN",
                "target":target,
                "before_treatment_features":feature,
                "predicted_bestmove_flip_probabilities":forecasts,
                "direct_open_close_pair":selection[group],
            }
        rows.append(per_case)
        counts=Counter(x["status"] for x in per_case["targets"].values())
        print("P2_PREOUTCOME",id,"source_events",len(seen["events"]),
              "predicted_targets",counts.get(
                "UNTREATED_NATIVELY_OBSERVED_FORECAST_FROZEN",0),flush=True)
    require(len(rows)==64 and len({r["game_sha256"] for r in rows})==64,
            "game denominator or history identity changed")
    counts=Counter(row["targets"][g]["status"] for row in rows for g in ("0","1"))
    frozen={
        "stage":"P2_PHYSICAL_EVENT_SELECTED_WITHOUT_TREATMENT",
        "original_publisher_zip_sha256":
            "6e6866cfe57ea0db7849f9b686fded1c1fe9d1fcab783359030b97ace377eccf",
        "game_freeze_sha256":GAME_SAMPLE_SHA,
        "source_binary_sha256":build["binary_sha256"],
        "pre_R33_reference_binary_sha256":
            build["pre_R33_reference_binary_sha256"],
        "network_sha256":NET_SHA,
        "frozen_model_sha256":MODEL_SHA,
        "source_game_count":len(rows),
        "source_control_searches":len(rows)*3,
        "real_treatment_searches":0,
        "potential_target_slots":128,
        "source_event_statuses":dict(counts),
        "original_event_family_count":len({r["family"] for r in rows}),
        "source_events":rows,
        "scientific_limits":[
            "No changed-final-move label has been observed under P2 intervention.",
            "An observable physical source-event pre-treatment projection is not a causal mediator.",
            "Predictive probability is not objective chess move value.",
            "No P2 native treatment result is permitted before this exact receipt is sealed."
        ]
    }
    public={
        k:v for k,v in frozen.items() if k!="source_events"
    }
    public["per_game_contact"]=[
        {"id":r["id"],"family":r["family"],"game_sha256":r["game_sha256"],
         "targets":{k:v["status"] for k,v in r["targets"].items()}}
        for r in rows]
    return frozen,public


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for x in ("sample","old","patch","net","build_receipt","model",
              "p1_training","out","private","public"):
        p.add_argument(x,type=Path)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    frozen,public=freeze(args)
    for path,what in ((args.private,frozen),(args.public,public)):
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(what,indent=2,sort_keys=True)+"\n")
    print("P2_DISCOVERY_DONE",frozen["source_game_count"],"physical_contacts",
          frozen["source_event_statuses"],"source_observer_control_searches",
          frozen["source_control_searches"],
          "preoutcome_sha256",sha(args.private.read_bytes()),
          "treatment_searches",frozen["real_treatment_searches"])


if __name__=="__main__":
    main()
