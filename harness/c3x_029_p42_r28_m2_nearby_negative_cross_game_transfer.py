#!/usr/bin/env python3
"""C3X P42/R28-M2: two-event leave-one-game-out concept-transport diagnostic.

Standard-library-only. Input is SHA-frozen R28-M1 analysis. This tests
whether a *single* simple board predicate selected by its pairwise separation
on Sahel survives transfer to Cerrado and vice versa. We do NOT claim
independent holdout: both historical games, the model family and labels were
already observed before this experiment. Selecting from eight concepts and
only six matched prefixes per event is a tiny diagnostic for hypothesis
pruning, NOT an estimator of generalization.

A signed feature direction +1 means positive=True and nearby negative=False,
-1 means positive=False and nearby negative=True. Ties are deterministic.
"""
import argparse
import hashlib
import json
from pathlib import Path

INPUT_SHA = "c8768b6ac02e62548a61e87f18bfa4d9406136316da9ae81ee296867aa2433e4"
SCHEMA = "c3x042-r28-m2-two-event-fixed-predicate-transport-diagnostic-v1"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def data_checks(rows, features):
    if len(rows) != 12 or len(features) != 8:
        raise ValueError("R28_M2_HOLD_12_PREFIX_8_FIXED_FEATURES")
    seen = set()
    groups = {}
    for row in rows:
        key = (row["event_family"], row["root_uci"], row["rank1"])
        if key in seen:
            raise ValueError("R28_M2_HOLD_DUPLICATE_PREFIX")
        seen.add(key)
        if not row["admitted_minimum_gap"] or row["gap_cp"] < 10:
            raise ValueError("R28_M2_HOLD_INADMISSIBLE_NEARBY_PAIR")
        if row["positive_cp"] <= row["nearby_negative_cp"]:
            raise ValueError("R28_M2_HOLD_INVERTED_SCORE_LABEL")
        if row["shared_first_opponent_reply"] == row["negative_second_opponent_reply"]:
            # Coincidental equality of move UCI across distinct turns is legal;
            # never infer identical chess histories from move strings alone.
            pass
        contrasts = row["predicate_contrasts"]
        if set(contrasts) != set(features):
            raise ValueError("R28_M2_HOLD_FEATURE_SCHEMA")
        for v in contrasts.values():
            if type(v["positive"]) is not bool or type(v["negative"]) is not bool:
                raise ValueError("R28_M2_HOLD_BOOLEAN_FEATURES_ONLY")
        groups.setdefault(row["event_family"], []).append(row)
    if len(groups) != 2 or sorted(len(x) for x in groups.values()) != [6, 6]:
        raise ValueError("R28_M2_HOLD_TWO_GAMES_SIX_PREFIXES_EACH")
    return groups


def classify(row, feature, orientation):
    z = row["predicate_contrasts"][feature]
    pos, neg = z["positive"], z["negative"]
    return (pos and not neg) if orientation == 1 else (not pos and neg)


def select_model(training, features):
    scoreboard = []
    for name in features:
        for direction in (1, -1):
            supports = sum(classify(row, name, direction) for row in training)
            scoreboard.append({"feature": name, "orientation": direction,
                               "train_separations": supports})
    # Explicit first-feature and +1 tie-breaking; both are not independent.
    best = max(scoreboard, key=lambda a: (a["train_separations"],
                                          -list(features).index(a["feature"]),
                                          a["orientation"]))
    return best, scoreboard


def transport(data):
    if (data.get("schema") != "c3x042-r28-m1-fixed-concept-nearby-negatives-v1"
        or data.get("status") != "EXPLORATORY_FIXED_PREDICATE_NEARBY_NEGATIVE_AUDIT"
        or data.get("n_matched_first_reply_prefixes") != 12
        or data.get("n_admitted_positive_nearby_negative_pairs") != 12):
        raise ValueError("R28_M2_HOLD_SHA_SOURCE_AND_METHOD_CONTRACT")
    features = tuple(data["feature_summaries"])
    groups = data_checks(data["nearby_groups"], features)
    folds = []
    for training_name, training in sorted(groups.items()):
        other = next(k for k in groups if k != training_name)
        holdout = groups[other]
        best, _ = select_model(training, features)
        n = sum(classify(row, best["feature"], best["orientation"]) for row in holdout)
        direct = {name: {
            "positive_true_negative_false": sum(
                classify(row, name, 1) for row in holdout),
            "positive_false_negative_true": sum(
                classify(row, name, -1) for row in holdout)}
            for name in features}
        folds.append({
            "train_event": training_name, "diagnostic_test_event": other,
            "selected_feature": best["feature"], "selected_direction": best["orientation"],
            "train_separation": best["train_separations"], "train_pairs": len(training),
            "other_event_separation": n, "other_event_pairs": len(holdout),
            "chance_oracle_comparison_not_provided": True,
            "all_feature_scores_on_test_for_diagnostics_only": direct,
        })
    return {
        "schema": SCHEMA, "status": "TINY_POSTHOC_HISTORIC_CROSS_GAME_DIAGNOSTIC",
        "R28_M1_source_json_sha256": INPUT_SHA,
        "two_games": 2, "matched_prefixes": 12, "fixed_features": list(features),
        "not_independent_prospective_transport": True,
        "outcome_labels_already_observed_before_R28": True,
        "selected_model_from_one_event_each_fold_only": True,
        "no_significance_or_causal_mediation_claim": True,
        "folds": folds,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    if sha(args.input) != INPUT_SHA:
        raise ValueError("R28_M2_HOLD_R28_M1_SHA_DRIFT")
    d = json.loads(Path(args.input).read_text(encoding="utf-8"))
    report = transport(d)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for fold in report["folds"]:
        print("R28_M2_TINY_GAME_TRANSFER", fold["train_event"], "->",
              fold["diagnostic_test_event"], "feature", fold["selected_feature"],
              "orientation", fold["selected_direction"],
              "train", fold["train_separation"], "/6",
              "other", fold["other_event_separation"], "/6", flush=True)


if __name__ == "__main__":
    main()
