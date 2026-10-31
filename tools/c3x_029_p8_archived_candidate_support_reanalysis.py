"""C3X 0.29 P8 — original pre-treatment forecast / native-outcome join.

Read-only. Treats 64 TWIC role cells as nested in 16 original games.
It does not construct a new engine run or refit a predictor.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORECAST = ROOT / "c3x/forecasts/c3x-022-P2-TWIC-puzzle32-exact-UCI-preregistered-stageA-20261010.json"
RECEIPT = ROOT / "c3x/receipts/c3x-022-P2-TWIC-puzzle32-stageB-literal-UCI-falsification-and-depth-20261010.json"

def analyze():
    f = json.loads(FORECAST.read_text(encoding="utf-8"))
    r = json.loads(RECEIPT.read_text(encoding="utf-8"))
    worlds = f["forecasts"]["twic"]
    observed = r["per_ecology"]["twic"]
    assert len(worlds) == 16
    assert f["sealed_before_any_first_TT_reader_intervention"] is True
    assert f["summary"]["cells"] == 128
    actual_flip_games = set(observed["actual_flip_distinct_games"])
    agreed, disagreed, cells = [], [], []
    for g in worlds:
        gid = g["game_id"]
        o, ff = g["baseline_O_bestmove"], g["baseline_F_bestmove"]
        disagrees = o != ff
        (disagreed if disagrees else agreed).append(gid)
        count = 0
        for world, roles in g["source_pair_role_forecasts"].items():
            for role, forecast in roles.items():
                assert world in ("O", "F") and role in ("STRICT", "BROAD")
                assert forecast["status"] == "PREDICTED_EXACT_UCI_BEFORE_TT_INTERVENTION"
                assert forecast["predicted_flip"] is disagrees
                assert forecast["predicted_UCI"] == ((ff if world == "O" else o) if disagrees else o)
                cells.append((gid, world, role, disagrees))
                count += 1
        assert count == 4
    assert len(cells) == 64
    assert len(agreed) == len(disagreed) == 8
    assert actual_flip_games <= set(disagreed)

    confusion = observed["flip_confusion"]
    tp, fp, fn, tn = (confusion[k] for k in ("TP", "FP", "FN", "TN"))
    assert (tp, fp, fn, tn) == (10, 22, 0, 32)
    assert len(disagreed)*4 == tp + fp
    assert len(agreed)*4 == tn + fn
    n = len(cells)
    flipped = observed["actual_flip_role_cells"]
    other_baseline_flip = observed["specific_move_exact_when_actual_flip"]
    third_candidates = flipped - other_baseline_flip
    assert flipped == 10 and other_baseline_flip == 6 and third_candidates == 4
    assert observed["literal_post_intervention_UCI_exact_matches"] == tn + other_baseline_flip
    assert observed["no_flip_majority_exact_matches"] == tn + fp
    assert set(observed["actual_flip_distinct_games"]) == {1,4,7,10}
    assert observed["eligible_and_delivered_physical_first_reader_role_cells"] == n
    # The puzzle stratum is a separate zero-flip comparison, not positive validation.
    puz = r["per_ecology"]["lichess_puzzles"]
    assert puz["actual_flip_role_cells"] == 0 and puz["eligible_and_delivered_physical_first_reader_role_cells"] == 28
    assert all(g["baseline_O_bestmove"] == g["baseline_F_bestmove"] for g in f["forecasts"]["lichess_puzzles"])
    assert {x["twic_game"] for x in r["distinct_mechanisms"] if "Third" in x.get("interpretation","") or "third" in x.get("interpretation","")} >= {4,10}

    return {
        "status": "ARCHIVED_PRETREATMENT_FORECAST_JOIN_WITH_AGGREGATE_NATIVE_RECEIPT",
        "twic": {
            "source_games": len(worlds), "eligible_role_cells": n,
            "baseline_agreed_games": agreed, "baseline_disagreed_games": disagreed,
            "actually_flipped_game_ids": sorted(actual_flip_games),
            "disagreed_but_not_flipped_games": sorted(set(disagreed)-actual_flip_games),
            "game_level_risk_positive_precision": len(actual_flip_games)/len(disagreed),
            "game_level_risk_recall": len(actual_flip_games)/len(actual_flip_games),
            "class_distribution": {"unchanged": tn+fp,
                                   "changed_to_other_baseline_move":other_baseline_flip,
                                   "changed_to_third_move":third_candidates},
            "binary_flip_accuracy": (tp+tn)/n,
            "exact_old_forecast_accuracy": observed["literal_post_intervention_UCI_exact_matches"]/n,
            "always_nochange_accuracy": observed["no_flip_majority_exact_matches"]/n,
            "two_baseline_output_oracle_accuracy_ceiling_in_this_sample": (n-third_candidates)/n,
            "risk_marker_agreement_only_coverage": len(agreed)*4/n,
            "agreement_only_observed_exact_accuracy": tn/(len(agreed)*4),
            "prediction_labels_raw_stageB_available": False
        },
        "puzzles": {"eligible_role_cells":28, "actual_flips":0,
                    "positive_flip_prediction_validated":False},
        "limits": [
            "Old 16 games post-outcome diagnostic, not a prospective new cohort",
            "Role cells nested in games; no iid sample-size-64 inference",
            "Third-move class count inferred from original aggregate exact-UCI results",
            "Selective no-change coverage excludes all observed true flips, not an explanation",
            "No new native engine run or source-path mediation evidence"
        ]
    }
if __name__ == "__main__":
    print(json.dumps(analyze(),ensure_ascii=False,indent=2,sort_keys=True))
