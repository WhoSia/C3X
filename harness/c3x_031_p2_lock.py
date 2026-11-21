"""C3X 0.31/P2: train frozen P1 logistic models before accessing new-case labels.

All 128 known R33 native effects are training-only history. The resulting
three model parameter sets must be frozen as a read-only source artifact before
independent P2 treatment. No new-case training, fitting, or adaptive threshold.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from c3x_031_p1_forecast import (
    PUBLIC, SOURCE, RIDGE, ITER, STEP, SOURCE_SHA,
    fit_predict, load_rows, sigmoid, value,
)


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def estimator(rows, keys):
    require(len(rows) == 128, "expected all original P1 target rows")
    avg = [sum(value(row, k) for row in rows) / len(rows) for k in keys]
    scale = []
    for j, k in enumerate(keys):
        var = sum((value(row, k) - avg[j]) ** 2 for row in rows) / len(rows)
        scale.append(math.sqrt(var) if var > 1e-12 else 1.0)
    X = [[1] + [(value(row, k) - avg[j]) / scale[j]
                for j, k in enumerate(keys)] for row in rows]
    n = len(rows)
    positives = sum(row["y"] for row in rows)
    weights = [0.0] * (len(keys) + 1)
    weights[0] = math.log((positives + .5) / (n - positives + .5))
    for _ in range(ITER):
        grad = [0.0] * len(weights)
        for row, x in zip(rows, X):
            error = sigmoid(sum(a*b for a, b in zip(weights, x))) - row["y"]
            for j in range(len(weights)):
                grad[j] += error * x[j] / n
        for j in range(1, len(weights)):
            grad[j] += RIDGE * weights[j]
        weights = [w - STEP*g for w, g in zip(weights, grad)]
    package = {"features": list(keys), "mean": avg,
               "scale": scale, "weights": weights}
    # Independent computation path from P1 cross-validation helper:
    result = [predict(package, {k: row[k] for k in keys}) for row in rows]
    reference = fit_predict(rows, rows, keys)
    require(all(abs(a-b) < 1e-12 for a,b in zip(result, reference)),
            "serialized P2 model and P1 learner disagree")
    return package


def predict(model, row):
    # Explicit allowlist: no source family or outcome enters inference.
    require(set(row) == set(model["features"]), "label/post-treatment/ID in inference row")
    def transform(key, raw):
        require(type(raw) in (int, float) and math.isfinite(raw),
                "nonfinite predictor")
        if key == "futility_slack":
            require(raw >= 0, "negative futility slack")
            return math.log1p(raw)
        if key == "source_progress_nodes":
            require(raw >= 0, "negative progressed nodes")
            return raw/32000
        return float(raw)
    require(row["public_upper_bound"] in (0,1)
            and row["public_lower_bound"] in (0,1)
            and row["public_upper_bound"]+row["public_lower_bound"]<=1,
            "invalid published bound")
    x = [1.0] + [(transform(k, row[k]) - model["mean"][j]) / model["scale"][j]
                  for j,k in enumerate(model["features"])]
    return sigmoid(sum(a*b for a,b in zip(model["weights"],x)))


def seal(source_tsv):
    rows = load_rows(source_tsv)
    positive = sum(row["y"] for row in rows)
    prior = (positive + .5) / (len(rows)+1)
    result = {
        "schema": "c3x-031-p2-pre-outcome-fixed-learner-v1",
        "evidence_class": "FULL_R33_DEVELOPMENT_TRAINING_ONLY",
        "training_games": 64,
        "training_event_families": 16,
        "training_physical_events": 128,
        "training_positives": positive,
        "training_feature_source_sha256": SOURCE_SHA,
        "training_new_p2_outcomes_seen": False,
        "source_native_p2_searches_seen": 0,
        "frozen_brier_success_threshold": .01,
        "training_algorithm": {
            "name": "full-batch-ridge-logistic-900-iterations",
            "ridge": RIDGE, "step": STEP, "iterations": ITER,
            "scale": "training-only-population-standard-deviation",
            "futility_slack": "natural-log1p",
            "source_progress_nodes": "divided by 32000",
        },
        "m0": {"probability":prior, "features":[]},
        "m1": estimator(rows, PUBLIC),
        "m2": estimator(rows, PUBLIC + SOURCE),
    }
    require(result["m2"]["features"] == list(PUBLIC + SOURCE),
            "changed original P1 source feature list")
    return result


def infer(bundle, row):
    require(bundle["training_new_p2_outcomes_seen"] is False,
            "label-knowledge isolation lost")
    require(set(row) == set(bundle["m2"]["features"]),
            "unexpected P2 scoring input")
    return {
        "m0": bundle["m0"]["probability"],
        "m1": predict(bundle["m1"],
                      {k:row[k] for k in bundle["m1"]["features"]}),
        "m2": predict(bundle["m2"], row),
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("p1_tsv", type=Path)
    parser.add_argument("model_lock", type=Path)
    args=parser.parse_args()
    bundle=seal(args.p1_tsv)
    args.model_lock.write_text(json.dumps(bundle,sort_keys=True,indent=2)+"\n")
    print("P2_SOURCE_MODEL_LOCK",len(bundle["m2"]["features"]),"features",
          "source",SOURCE_SHA,"locked_json_sha256",
          hashlib.sha256(args.model_lock.read_bytes()).hexdigest())


if __name__=="__main__":
    main()
