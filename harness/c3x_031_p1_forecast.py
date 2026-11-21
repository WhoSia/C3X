"""0.31/P1: retrospective event-family-heldout native sensitivity benchmark.

Inputs: compact table extracted from original SHA-locked R33 source ZIP.
No Stockfish work is performed; this is not causal mediation or prospective
state sufficiency. Hyperparameters and folds are frozen by the P1 protocol.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import re

SOURCE_SHA = "6e5cd1215ab13ac3dba3c93447b577f305c06fad1fd00c2b4a5338c71e7a63ba"
SOURCE_JSON_SHA = "e96aff554f6cc90c4e7426df2ad8c2237737c2016115ea8608485ba9a1449e95"
PUBLIC = ("public_depth", "public_score_cp", "public_pv_len",
          "public_upper_bound", "public_lower_bound")
SOURCE = ("source_depth", "source_ply", "futility_slack",
          "source_progress_nodes", "source_attempt",
          "source_root_is_public_best", "stratum")
COLUMNS = ("id", "family_code") + PUBLIC + SOURCE + ("y",)
# The actual frozen TSV is in the order below, not in model design order.
SOURCE_COLUMNS = ("id", "family_code", "stratum", "public_depth",
                  "public_score_cp", "public_pv_len", "public_upper_bound",
                  "public_lower_bound", "source_depth", "source_ply",
                  "futility_slack", "source_progress_nodes", "source_attempt",
                  "source_root_is_public_best", "y")
SEED = 310121
RIDGE = .02
ITER = 900
STEP = .10
BOOT = 2000


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_rows(path):
    data = Path(path).read_bytes()
    require(sha(data) == SOURCE_SHA, "R33 pre-treatment source table SHA mismatch")
    reader = csv.DictReader(data.decode("utf8").splitlines(), delimiter="\t")
    require(tuple(reader.fieldnames or ()) == SOURCE_COLUMNS,
            "unexpected feature table schema")
    result = []
    for row in reader:
        require(set(row) == set(SOURCE_COLUMNS), "missing feature or added label")
        require(re.fullmatch(r"R33-\d{3}-[01]", row["id"]) is not None,
                "invalid source physical event id")
        try:
            rec = {k: (v if k == "id" else int(v))
                   for k, v in row.items()}
        except (ValueError, TypeError) as err:
            raise ValueError("noninteger original source feature") from err
        rec["family"] = rec.pop("family_code")
        rec["game"] = rec["id"].rsplit("-", 1)[0]
        result.append(rec)
    return validate(result)


def validate(rows):
    require(len(rows) == 128 and len({x["id"] for x in rows}) == 128,
            "expected 128 distinct source physical interventions")
    require(len({x["family"] for x in rows}) == 16
            and set(x["family"] for x in rows) == set(range(1, 17)),
            "event-family census mismatch")
    require(len({x["game"] for x in rows}) == 64,
            "source game denominator mismatch")
    require(all(set(x) == set(COLUMNS) - {"family_code"} | {"family", "game"}
                for x in rows), "feature leakage or missing input")
    games = defaultdict(list)
    for row in rows:
        require(type(row["y"]) is int and row["y"] in (0, 1),
                "nonbinary final bestmove change")
        require(row["stratum"] in (0, 1)
                and row["public_upper_bound"] in (0, 1)
                and row["public_lower_bound"] in (0, 1)
                and row["public_upper_bound"] + row["public_lower_bound"] <= 1,
                "illegal gate/bound source")
        for k in PUBLIC + SOURCE:
            require(type(row[k]) in (float, int)
                    and math.isfinite(row[k]), "nonfinite feature " + k)
        require(row["futility_slack"] >= 0 and row["source_progress_nodes"] >= 0,
                "negative pre-treatment source event")
        games[row["game"]].append(row)
    for pair in games.values():
        require(len(pair) == 2 and {r["stratum"] for r in pair} == {0, 1}
                and pair[0]["family"] == pair[1]["family"],
                "game-correlated targets split or duplicated")
        require(all(pair[0][k] == pair[1][k] for k in PUBLIC),
                "one original game has two different untreated public observations")
    require(sum(r["y"] for r in rows) == 11, "historical positive denominator")
    require({i: sum(r["y"] for r in rows if r["stratum"] == i)
             for i in (0, 1)} == {0: 4, 1: 7}, "effect-stratum mismatch")
    bounds = Counter("upper" if r["public_upper_bound"] else
                     "lower" if r["public_lower_bound"] else "exact"
                     for r in rows)
    require(bounds == {"exact": 68, "upper": 46, "lower": 14},
            "published upper/lower bounds lost")
    return sorted(rows, key=lambda row: row["id"])


def value(row, key):
    if key == "futility_slack":
        return math.log1p(row[key])
    if key == "source_progress_nodes":
        return row[key] / 32000
    return float(row[key])


def matrices(train, test, keys):
    avg = [sum(value(row, k) for row in train) / len(train) for k in keys]
    scales = []
    for j, k in enumerate(keys):
        v = sum((value(row, k) - avg[j]) ** 2 for row in train) / len(train)
        scales.append(math.sqrt(v) if v > 1e-12 else 1.0)

    def convert(data):
        return [[1.0] + [(value(row, k) - avg[j]) / scales[j]
                         for j, k in enumerate(keys)] for row in data]
    return convert(train), convert(test)


def sigmoid(z):
    if z >= 0:
        return 1 / (1 + math.exp(-min(700, z)))
    t = math.exp(max(-700, z))
    return t / (1 + t)


def fit_predict(train, test, keys):
    design, targets = matrices(train, test, keys)
    w = [0.0] * len(design[0])
    n = len(design)
    positives = sum(row["y"] for row in train)
    w[0] = math.log((positives + 0.5) / (n - positives + 0.5))
    for _ in range(ITER):
        grad = [0.0] * len(w)
        for row, x in zip(train, design):
            error = sigmoid(sum(a * b for a, b in zip(w, x))) - row["y"]
            for j in range(len(w)):
                grad[j] += error * x[j] / n
        for j in range(1, len(w)):
            grad[j] += RIDGE * w[j]
        w = [a - STEP * g for a, g in zip(w, grad)]
    return [sigmoid(sum(a * b for a, b in zip(w, x))) for x in targets]


def average_precision(y, scores):
    positives = sum(y)
    if not positives:
        return None
    tied = defaultdict(lambda: [0, 0])
    for score, label in zip(scores, y):
        tied[score][0] += 1
        tied[score][1] += label
    evaluated = true_positives = 0
    ap = 0.0
    for score in sorted(tied, reverse=True):
        size, found = tied[score]
        evaluated += size
        true_positives += found
        if found:
            ap += (found / positives) * (true_positives / evaluated)
    return ap


def metrics(rows, key):
    ys = [row["y"] for row in rows]
    ps = [row[key] for row in rows]
    eps = 1e-12
    return {
        "brier": sum((p - y) ** 2 for p, y in zip(ps, ys)) / len(rows),
        "log_loss": -sum(y * math.log(max(eps, min(1 - eps, p))) +
                         (1 - y) * math.log(max(eps, min(1 - eps, 1 - p)))
                         for y, p in zip(ys, ps)) / len(rows),
        "average_precision": average_precision(ys, ps),
        "positive_count": sum(ys),
        "predicted_positive_at_0_5": sum(p >= .5 for p in ps),
        "recall_at_0_5": sum(y and p >= .5 for y, p in zip(ys, ps)) /
                         max(1, sum(ys)),
    }


def evaluate(data):
    rows = validate(data)
    families = sorted({row["family"] for row in rows})
    predictions = []
    for family in families:
        train = [row for row in rows if row["family"] != family]
        held = [row for row in rows if row["family"] == family]
        require({r["game"] for r in train}.isdisjoint({r["game"] for r in held}),
                "same source game leaked across holdout")
        prior = (sum(r["y"] for r in train) + .5) / (len(train) + 1)
        public = fit_predict(train, held, PUBLIC)
        native = fit_predict(train, held, PUBLIC + SOURCE)
        for row, p1, p2 in zip(held, public, native):
            predictions.append({
                "id": row["id"], "family": family,
                "game": row["game"], "stratum": row["stratum"],
                "y": row["y"], "m0": prior, "m1": p1, "m2": p2,
            })
    require(len(predictions) == 128, "incomplete family-heldout predictions")
    summary = {model: metrics(predictions, model) for model in ("m0", "m1", "m2")}
    by_family = {
        family: {model: metrics([r for r in predictions if r["family"] == family], model)
                 for model in ("m0", "m1", "m2")}
        for family in families
    }
    randomizer = random.Random(SEED)
    groups = {family: [r for r in predictions if r["family"] == family]
              for family in families}
    differences = {"m0_minus_m2": [], "m1_minus_m2": []}
    for _ in range(BOOT):
        sample = [r for fam in (randomizer.choice(families) for _ in families)
                  for r in groups[fam]]
        for name, comparator in (("m0_minus_m2", "m0"), ("m1_minus_m2", "m1")):
            differences[name].append(metrics(sample, comparator)["brier"] -
                                     metrics(sample, "m2")["brier"])
    intervals = {
        name: {
            "observed": summary[name[:2]]["brier"] - summary["m2"]["brier"],
            "bootstrap_95": [sorted(samples)[int(.025 * BOOT)],
                             sorted(samples)[int(.975 * BOOT) - 1]],
        } for name, samples in differences.items()
    }
    licensed_signal = (
        all(row["observed"] >= .01 and row["bootstrap_95"][0] > 0
            for row in intervals.values()) and
        summary["m2"]["average_precision"] >= max(
            summary["m0"]["average_precision"], summary["m1"]["average_precision"])
    )
    return {
        "schema": "c3x-031-p1-family-heldout-source-forecast-v1",
        "evidence_class": "RETROSPECTIVE_DEVELOPMENT_NOT_PROSPECTIVE",
        "source_feature_receipt_sha256": SOURCE_SHA,
        "source_original_full_feature_json_sha256": SOURCE_JSON_SHA,
        "new_native_searches": 0,
        "source_games": 64, "source_treatments": 128, "event_families": 16,
        "positive_final_move_changes": 11,
        "public_terminal_bounds_game_counts": {"exact": 34, "upper": 23, "lower": 7},
        "model_contract": {
            "m0": "Jeffreys train prior", "m1": list(PUBLIC),
            "m2": list(PUBLIC + SOURCE),
            "ridge": RIDGE, "steps": ITER, "step_size": STEP,
            "seed": SEED, "bootstrap": BOOT,
            "heldout_group": "complete tournament event family",
        },
        "score": summary, "difference_95ci": intervals, "by_family": by_family,
        "verdict": ("P1_RETROSPECTIVE_PREDICTIVE_SIGNAL_ONLY" if licensed_signal
                    else "HOLD_NO_PRETREATMENT_SOURCE_STATE_GAIN"),
        "identified_mediator": False,
        "minimal_state_sufficiency_proved": False,
        "prospective_game_transfer_proved": False,
        "human_value_proved": False,
        "out_of_family_predictions": sorted(predictions, key=lambda row: row["id"]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("frozen_tsv", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    result = evaluate(load_rows(args.frozen_tsv))
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print("P1_BENCHMARK", result["verdict"], "Brier",
          {name: result["score"][name]["brier"] for name in ("m0", "m1", "m2")},
          "JSON_SHA256", sha(args.out.read_bytes()))


if __name__ == "__main__":
    main()
