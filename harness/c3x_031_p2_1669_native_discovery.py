"""C3X 0.31/P2 B1: genuine physical source observation before ANY treatment.

Inputs are original TWIC1669 full legal game histories from the frozen
64-game/25 canonical-event-family source-only court, plus a P1-only fitted
M0/M1/M2 model. Runs 64 x (pristine R31 reference, R33-off, R33-observe)
actual fresh Stockfish16 32000-node searches and fixes the selected native
event signatures and forecast probabilities before any futility/null mask.

No skip_f/skip_n flags ever enabled, no observations of P2 treatment outcomes.
Output is source-only with an explicit all-case denominator and abstentions.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from c3x_030_r33_gate_panel import trial, select
from c3x_031_p1_extract import last_public
from c3x_031_p2_lock import infer, PUBLIC, SOURCE

SAMPLE_SHA = "8b7f5da799cc9610c7e4cb8347baa8b3b8bd74eb383939eac9fa91b527a8116d"
MODEL_SHA = "ae6f7add6838dc3b4cbe679bd728625593c4e3f9817ea1101e4a7fb550da8c53"
PUBLISHER_SHA = "0d5e76cff28bc18faea0f03987586cceee419471fd7bee963c43b1f7cf6569c1"
PRE_NATIVE_SOURCE_SEAL_SHA = "191dc382dd90869d0e59a900db3a97df996a6298e80b9c7c67fef2521cdbe973"
UPSTREAM_COMMIT = "68e1e9b3811e16cad014b590d7443b9063b3eb52"
REFERENCE_BINARY_SHA = "78cae269c73eb080c8a508e839dcde15ce48888b3fc4317fa3311de49e5ee7bb"
PATCHED_BINARY_SHA = "ce13b5899ab6862a621ee6033ac661f7ded0abf3f2b4ea073a163b0c3154afa1"
NNUE_SHA = "5af11540bbfefcb54e38c5dd000cab4b469dfa7599a1d55be5d2722c20a8929b"
NODES = 32000


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def validate_sources(args):
    for name, expected in (("sample", SAMPLE_SHA), ("model", MODEL_SHA),
                           ("old", REFERENCE_BINARY_SHA), ("patch", PATCHED_BINARY_SHA),
                           ("net", NNUE_SHA)):
        require(digest(getattr(args, name)) == expected,
                "P2 original pre-treatment identity changed: " + name)
    sample = json.loads(args.sample.read_text())
    model = json.loads(args.model.read_text())
    receipt = json.loads(args.build_receipt.read_text())
    require(sample["publisher_issue"] == 1669
            and sample["source_zip_sha256"] == PUBLISHER_SHA
            and sample["source_native_discovery_seen"] == 0
            and sample["source_native_treatments_seen"] == 0,
            "source sampling had native exposure or wrong publisher archive")
    rows = sample["positions"]
    require(len(rows) == 64 and
            len({x["id"] for x in rows}) == 64 and
            len({x["game_sha256"] for x in rows}) == 64 and
            len({x["family"] for x in rows}) == 25,
            "the entire pre-native 64 game /25 family denominator changed")
    require([x["id"] for x in rows] ==
            [f"P2-{i:03}" for i in range(1,65)],
            "original source sampling order changed")
    require(all(x["moves"] and len(x["moves"]) == x["ply"]
                for x in rows),
            "original full-history checkpoint truncated or empty")
    require(model["training_new_p2_outcomes_seen"] is False
            and model["source_native_p2_searches_seen"] == 0
            and model["training_physical_events"] == 128
            and model["training_positives"] == 11,
            "P1 model was not sealed before new native outcomes")
    require(model["m2"]["features"] == list(PUBLIC + SOURCE),
            "post-selection feature schema changed")
    require(receipt["stage"] == "P2_NATIVE_BUILD_SOURCE_ONLY_NO_TREATMENTS"
            and receipt["original_stockfish_commit"] == UPSTREAM_COMMIT
            and receipt["binary_sha256"] == PATCHED_BINARY_SHA
            and receipt["pre_R33_reference_binary_sha256"] == REFERENCE_BINARY_SHA
            and receipt["nnue_sha256"] == NNUE_SHA
            and receipt["source_event_treatments_executed"] == 0,
            "the SF16 source build is different from original pinned version")
    return sample, model, receipt


def native_features(public, event, original_best, group):
    depth, cp, pvlen, upper, lower = public
    feature = {
        "public_depth": depth,
        "public_score_cp": cp,
        "public_pv_len": pvlen,
        "public_upper_bound": upper,
        "public_lower_bound": lower,
        "source_depth": int(event["depth"]),
        "source_ply": int(event["ply"]),
        "futility_slack": int(event["floor"]) - int(event["beta"]),
        "source_progress_nodes": int(event["nodes"]),
        "source_attempt": int(event["attempt"]),
        "source_root_is_public_best": int(event["root"] == original_best),
        "stratum": int(group),
    }
    require(feature["futility_slack"] >= 0
            and event["null_eligible"] == group
            and set(feature) == set(PUBLIC + SOURCE),
            "selected physical native event or features do not match the fixed model")
    return feature


def execute(args):
    source, model, receipt = validate_sources(args)
    args.out.mkdir(parents=True, exist_ok=True)
    observed = []
    for pos in source["positions"]:
        stem = pos["id"]
        reference = trial(args, pos, stem + "/reference", binary=args.old,
                          observer=False)
        disabled = trial(args, pos, stem + "/patch-off", binary=args.patch,
                         observer=False)
        enabled = trial(args, pos, stem + "/source-observe", binary=args.patch,
                        observer=True)
        require(reference["uci"] == disabled["uci"] == enabled["uci"],
                "P2 native observational parity failed (UCI) " + stem)
        require(reference["proof"] == disabled["proof"] == enabled["proof"],
                "P2 native observational parity failed (root source) " + stem)
        require(reference["events"] == disabled["events"] == [],
                "untouched source logged an event in a disabled channel " + stem)
        best = enabled["proof"]["best"]["move"]
        require(isinstance(best,str) and len(best) in (4,5)
                and best[:2][0] in "abcdefgh" and best[2:4][0] in "abcdefgh",
                "missing/invalid original native final chosen move")
        pub = None
        public_reason = None
        try:
            pub, public_best = last_public(
                (args.out/stem/"source-observe"/"stdout.txt").read_bytes())
            require(public_best == best,
                    "public UCI disagrees with original native root " + stem)
        except ValueError as ex:
            if "non-cp terminal evaluation" in str(ex):
                public_reason = "MATE_OR_NON_CP_PUBLIC_FINAL_ABSTAIN"
            else:
                raise
        events = enabled["events"]
        nominations = select(events)
        case = {
            "id": stem,
            "family": pos["family"],
            "published_event_family": pos["published_event_family"],
            "game_sha256": pos["game_sha256"],
            "original_game_history_ply": pos["ply"],
            "source_legal_move_count": pos["legal_moves"],
            "original_untreated_bestmove": best,
            "physical_original_event_count": len(events),
            "original_public": pub,
            "public_abstention": public_reason,
            "original_reference_uci_sha256": hashlib.sha256(
                ("\n".join(enabled["uci"])+"\n").encode()).hexdigest(),
            "source_observe_stderr_sha256": enabled["trace"],
            "targets": {},
        }
        for group in ("0", "1"):
            if group not in nominations:
                case["targets"][group] = {
                    "status": "NO_ELIGIBLE_NATIVE_SOURCE_CONTACT",
                    "predictive_status": "ABSTAIN",
                }
                continue
            event = nominations[group]
            if pub is None:
                case["targets"][group] = {
                    "status": "PHYSICAL_TARGET_EXISTED_PUBLIC_ABSTAIN",
                    "predictive_status": "ABSTAIN",
                    "native_open_close": event,
                }
                continue
            features = native_features(pub, event["open"], best, group)
            predictions = infer(model, features)
            case["targets"][group] = {
                "status": "PHYSICAL_TARGET_PREDICTED_BEFORE_TREATMENT",
                "predictive_status": "FROZEN",
                "native_open_close": event,
                "pre_treatment_features": features,
                "frozen_m0_m1_m2_forecasts": predictions,
            }
        observed.append(case)
        cnt = Counter(x["status"] for x in case["targets"].values())
        print("P2_1669_PREOUTCOME", stem, "family", pos["family"],
              "events", len(events), "statuses", dict(cnt), flush=True)
    counts = Counter(row["targets"][g]["status"]
                     for row in observed for g in ("0","1"))
    require(len(observed) == 64
            and len({row["family"] for row in observed}) == 25,
            "pre-native cohort lost games or families during source observation")
    require(sum(counts.values()) == 128, "physical targets were dropped")
    private = {
        "schema": "C3X_031_P2_TWIC1669_PHYSICAL_OBSERVE_FORECAST_PREOUTCOME_V1",
        "status": "NATIVE_UNTREATED_PHYSICAL_TARGETS_AND_PREDICTIONS_FROZEN",
        "research_claim": "SOURCE_ONLY_ZERO_INTERVENTION_OUTCOMES",
        "source_publisher_issue": 1669,
        "original_publisher_zip_sha256": PUBLISHER_SHA,
        "frozen_candidate_sha256": SAMPLE_SHA,
        "pre_outcome_model_sha256": MODEL_SHA,
        "original_stockfish_commit": UPSTREAM_COMMIT,
        "original_source_build_receipt": receipt,
        "source_game_count": 64,
        "source_event_family_count": 25,
        "actual_untreated_stockfish_searches": 192,
        "actual_source_treatment_searches": 0,
        "physical_source_event_slots": 128,
        "target_contact_and_prediction_status": dict(counts),
        "native_source_records": observed,
        "scientific_holds": [
            "No P2 intervention bestmove labels have been observed.",
            "Exact-family and explicit-series exclusions cannot prove absence of all historic aliases.",
            "Family-level dependence means 64 games are not 64 independent sources.",
            "Pre-event prediction is not TT/history/budget mediation or chess strategy value.",
            "P2 statistical comparison awaits real physical interventions plus matched shams.",
        ],
    }
    public = {k:v for k,v in private.items()
              if k not in ("native_source_records","original_source_build_receipt")}
    public["per_case"] = [
        {"id":r["id"],"family":r["family"],
         "statuses":{g:r["targets"][g]["status"] for g in ("0","1")}}
        for r in observed
    ]
    return private, public


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for a in ("sample","model","old","patch","net","build_receipt",
              "out","private","public"):
        p.add_argument(a,type=Path)
    args=p.parse_args()
    private, public = execute(args)
    for path,data in ((args.private,private),(args.public,public)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
        print("P2_PREOUTCOME_SEALED",str(path),digest(path),flush=True)


if __name__ == "__main__":
    main()
