"""Separate missing replies from leaf ranking errors in scored R10 cases."""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("score", type=Path)
    parser.add_argument("forecast", type=Path)
    parser.add_argument("judge", type=Path)
    args = parser.parse_args()
    forecasts = {r["round"]: r["roots"]
                 for r in json.loads(args.forecast.read_text())["rows"]}
    judgments = {r["round"]: r["roots"]
                 for r in json.loads(args.judge.read_text())["rows"]}
    output = []
    for row in json.loads(args.score.read_text()):
        if not all(row["judge"]):
            continue
        arms = row["predictions"]["secondary"]
        for index, root in enumerate(row["roots"]):
            target = set(row["judge"][index][1])
            forecast = forecasts[row["round"]][root]
            discovered = {entry["pv"][0] for entry in forecast["discovery"]}
            prediction = arms["tree"]["scores"][index]
            judge = judgments[row["round"]][root]
            restricted_min = min(judge[move]["cp"] for move in discovered)
            output.append({"round": row["round"], "root": root,
                           "restricted_judge_min_cp": restricted_min,
                           "full_judge_min_cp": row["judge"][index][0],
                           "discovery_contains_target": bool(target & discovered),
                           "leaf_selects_target": None if prediction is None else bool(target & set(prediction[1]))})
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
