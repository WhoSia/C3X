"""Score matched reply predictions and disclose referee and game-level dependence."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from c3x_030_r20_p40_value import BINARY
from c3x_030_r21_matched_forecast import ARMS, DEPTHS
from c3x_030_s4l_r10_reply_transport import digest
from c3x_030_s4l_r11_allocation import NET, SF
from c3x_030_s4l_r14_trace_score import judge_sign


def count(rows, label):
    judged = [row for row in rows if row["targets"][label] is not None]
    outcome = {}
    for arm in ARMS:
        coverage = sum(row["forecasts"][arm] is not None for row in judged)
        hits = sum(row["forecasts"][arm] == row["targets"][label] for row in judged)
        outcome[arm] = {"coverage": coverage, "hits": hits}
    changed = [row for row in judged if row["forecasts"]["tree"] is not None
               and row["forecasts"]["trace"] is not None
               and row["forecasts"]["tree"] != row["forecasts"]["trace"]]
    return {"judge_coverage": len(judged), "games": len({row["round"] for row in judged}),
            "arms": outcome, "trace_changes": len(changed),
            "trace_gains": sum(row["forecasts"]["trace"] == row["targets"][label] for row in changed),
            "trace_losses": sum(row["forecasts"]["tree"] == row["targets"][label] for row in changed)}


def score(forecast, judged):
    if forecast["rows"].keys() != judged["rows"].keys():
        raise ValueError("Question sets differ")
    if forecast["cohort_sha256"] != judged["cohort_sha256"]:
        raise ValueError("Cohort digests differ")
    statuses = Counter()
    by_game = defaultdict(list)
    rows = {}
    for key, item in forecast["rows"].items():
        depths = judged["rows"][key]
        signs = item["signs"]
        if signs.keys() != set(ARMS) or any(
            label is not None and (type(label) is not int or label not in (-1, 0, 1))
            for label in signs.values()
        ):
            raise ValueError("Unexpected forecast")
        targets = {str(depth): judge_sign(depths[str(depth)], depth) for depth in DEPTHS}
        low, high = (targets[str(depth)] for depth in DEPTHS)
        targets["stable"] = low if low is not None and low == high else None
        statuses.update(leaf["trace_status"] for leaf in item["leaves"])
        row = {"round": item["round"], "reply": item["reply"], "forecasts": signs, "targets": targets}
        rows[key] = row
        by_game[item["round"]].append(row)
    values = list(rows.values())
    return {"questions": len(rows), "trace_leaf_statuses": dict(statuses),
            "scores": {label: count(values, label) for label in ("14", "16", "stable")},
            "by_game": {game: count(group, "stable") for game, group in sorted(by_game.items())},
            "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("forecast", type=Path)
    parser.add_argument("judged", type=Path)
    args = parser.parse_args()
    predicted = json.loads(args.forecast.read_text())
    judged = json.loads(args.judged.read_text())
    if (predicted["binary_sha256"] != SF or judged["binary_sha256"] != BINARY
            or judged["net_sha256"] != NET or judged["forecast_sha256"] != digest(args.forecast)):
        raise ValueError("The reference and sealed prediction provenance differ")
    print(json.dumps(score(predicted, judged), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
