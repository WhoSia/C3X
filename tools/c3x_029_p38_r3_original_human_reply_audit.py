#!/usr/bin/env python3
"""P38/R3: posthoc *observed human-reply* audit of untouched P37 forecasts.

This is an archival observational secondary comparison, NOT a pre-registered
prospective human-outcome experiment. Each event supplies at most one actual
opponent response, and a foil absent from history has NO observable answer.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

SOURCE_ZIP = "3f16f69c6cb01029c519aeb24654913303916ce79537c1a86497bb9c84b79191"
PRED_ZIP = "721471da43d0bd973e2b084fc47070f5a5826d0add38cbc39a2ccfbca6a427f6"
SOURCE_MEMBER = "P37_R1_8_EVENT_8_GAME_SOURCE_ONLY_MANIFEST.json"
PRED_MEMBER = "P37_R2_THREE_RIVAL_PRE_REFERENCE_PREDICTIONS.json"
PREFIX_MEMBER = "P37_PREDICTOR_PREFIX_ONLY_INPUT.json"
SOURCE_SHA = "77ebaa409e7c2099cc6cce3419c2f55ded295d925ab441dc2d13c16b67c2c361"
PRED_SHA = "da395f0eb16e7b294af2056dadd92b579770aa8f1ae288d1d358132685807051"
PREFIX_SHA = "0f6a3c371e4154342f65167dfa9afa269705999c549eec53235d8763cb18ceb9"
METHODS = ("stockfish_pv", "simple_json", "c3x_legal_plan")


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError("P38_HUMAN_OBSERVATION_HOLD_" + reason)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def get_member(source: Path, expected_zip_sha: str,
               name: str, expected_member_sha: str) -> dict:
    if source.is_dir():
        member_path = source / name
        need(member_path.is_file(), "MEMBER_MISSING_" + name)
        body = member_path.read_bytes()
    else:
        need(sha(source.read_bytes()) == expected_zip_sha, "ZIP_SHA_" + name)
        with zipfile.ZipFile(source) as z:
            need(name in z.namelist(), "MEMBER_MISSING_" + name)
            body = z.read(name)
    need(sha(body) == expected_member_sha, "MEMBER_SHA_" + name)
    return json.loads(body)


def inspect_observed_case(pred: dict, game: dict, prefix: dict) -> dict:
    need(pred["case_id"] == game["case_id"] == prefix["case_id"], "CASE_ID")
    need(pred["source_id"] == game["source_id"] == prefix["source_id"], "EVENT_ID")
    moves = game["full_game_uci"]
    need(len(moves) >= 60, "ORIGINAL_GAME_TOO_SHORT")
    need(game["fixed_ply"] == prefix["fixed_ply"] == pred["fixed_ply"] == 30,
         "PLY_NOT_30")
    game_sha = sha(" ".join(moves).encode("ascii"))
    need(game_sha == game["full_game_uci_sha256"] ==
         pred["original_game_sha256"] == prefix["original_game_sha256"],
         "SOURCE_GAME_HISTORY_SHA")
    need(pred["original_prefix_uci"] == prefix["original_prefix_uci"] ==
         moves[:30], "FORECAST_PREFIX_LEAKAGE")
    need(pred["frozen_fen"] == prefix["frozen_fen"] ==
         game["frozen_fen"], "SOURCE_BOARD")
    need(len(pred["candidate_pairs"]) == 2, "PREDICTION_CARDINALITY")
    roots = {x["root_uci"]: x for x in pred["candidate_pairs"]}
    need(len(roots) == 2, "ROOT_DUPLICATE")
    played, reply = moves[30], moves[31]
    result = {
        "case_id": pred["case_id"], "event_family": pred["event_family"],
        "source_id": pred["source_id"], "historical_played_root_uci": played,
        "historical_opponent_reply_uci": reply,
        "two_frozen_engine_candidate_roots": list(roots),
        "prediction_coverage": played in roots,
        "status": "OBSERVED_OWN_CANDIDATE" if played in roots
                  else "NO_ACTUAL_COUNTERFACTUAL_FOR_FROZEN_CANDIDATES",
        "predictions": {}, "hits": {},
    }
    if played not in roots:
        return result
    predictions = roots[played]["predictions"]
    need(set(predictions) == set(METHODS), "FROZEN_PREDICTORS")
    for method in METHODS:
        value=predictions[method]["reply"]
        result["predictions"][method] = value
        result["hits"][method] = value == reply if value is not None else False
    return result


def audit(source: dict, prediction: dict, prefixes: dict) -> dict:
    need(prediction["status"] == "PRE_REFEREE_FROZEN_THREE_RIVAL_RESPONSE_FORECASTS",
         "PREDICTION_STATUS")
    need(prediction["source_manifest_sha256"] == SOURCE_SHA, "PRESEALED_SOURCE_LINK")
    need(prefixes["original_full_manifest_sha256"] == SOURCE_SHA,
         "PREFIX_SOURCE_LINK")
    need(prefixes["reference_oracle_available_in_this_file"] is False,
         "PREDICTOR_ALREADY_HAS_REFERENCE")
    need(len(source["sources"]) == len(prediction["cases"]) ==
         len(prefixes["cases"]) == 8, "CASE_COUNT")
    original = {s["source_id"]: s["selected"] for s in source["sources"]}
    pref = {p["source_id"]: p for p in prefixes["cases"]}
    need(len(original)==len(pref)==8, "EVENT_ID_DUPLICATED")
    seen = set()
    out = []
    for p in prediction["cases"]:
        sid=p["source_id"]
        need(sid in original and sid in pref, "SOURCE_ID_NOT_IN_MANIFEST")
        need(sid not in seen, "PREDICTION_EVENT_DUPLICATE")
        seen.add(sid)
        out.append(inspect_observed_case(p,original[sid],pref[sid]))
    evaluated = [x for x in out if x["prediction_coverage"]]
    unobserved = [x for x in out if not x["prediction_coverage"]]
    need(len(out)==8 and len(evaluated)+len(unobserved)==8,
         "DENOMINATOR_GONE")
    counts={m:sum(x["hits"][m] for x in evaluated) for m in METHODS}
    p_only=sum(x["hits"]["stockfish_pv"] and not x["hits"]["c3x_legal_plan"] for x in evaluated)
    c_only=sum(x["hits"]["c3x_legal_plan"] and not x["hits"]["stockfish_pv"] for x in evaluated)
    both=sum(x["hits"]["stockfish_pv"] and x["hits"]["c3x_legal_plan"] for x in evaluated)
    neither=len(evaluated)-p_only-c_only-both
    return {
        "status": "P38_POSTHOC_ACTUAL_HUMAN_REPLY_AUDIT_NOT_CONFIRMATORY",
        "original_source_zip_sha256": SOURCE_ZIP,
        "original_predicted_zip_sha256": PRED_ZIP,
        "source_event_families": len(out),
        "observed_played_move_is_in_frozen_two_candidate_roots":len(evaluated),
        "observed_human_reply_unavailable_for_foils":len(unobserved),
        "conditional_prediction_accuracy_on_observed_coverage":{
            m:{"correct":counts[m],"evaluable":len(evaluated),
               "accuracy":counts[m]/len(evaluated) if evaluated else None}
            for m in METHODS
        },
        "paired_pv_c3x":{"pv_only_correct":p_only,
                         "c3x_only_correct":c_only,
                         "both_correct":both,"both_wrong":neither},
        "events":out,
        "claims_not_licensed":["independent blind prospective validation",
            "human reply equals optimal chess reply",
            "foils have observed historical replies",
            "full C3X source-neural mechanism validation",
            "cost-equal predictor comparison",
            "explanation benefit for human chess understanding"],
    }


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--source-zip",type=Path,required=True)
    a.add_argument("--prediction-zip",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    v=a.parse_args()
    src=get_member(v.source_zip,SOURCE_ZIP,SOURCE_MEMBER,SOURCE_SHA)
    pre=get_member(v.prediction_zip,PRED_ZIP,PRED_MEMBER,PRED_SHA)
    prefix=get_member(v.prediction_zip,PRED_ZIP,PREFIX_MEMBER,PREFIX_SHA)
    result=audit(src,pre,prefix)
    v.out.parent.mkdir(parents=True,exist_ok=True)
    v.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("P38_HUMAN_OBSERVED_REPLY_AUDIT",result["source_event_families"],
          result["observed_played_move_is_in_frozen_two_candidate_roots"],
          result["conditional_prediction_accuracy_on_observed_coverage"],
          flush=True)


if __name__=="__main__":
    main()
