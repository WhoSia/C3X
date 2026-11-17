"""Score frozen PV and reply-tree forecasts against exhaustive judges."""

import argparse
import hashlib
import json
from pathlib import Path

from c3x_030_s4l_r10_reply_transport import board_at, eligible


def sign(value):
    return (value > 0) - (value < 0)


def score_arm(root, arm, secondary):
    if arm == "pv":
        row = root["pv"]
        row = row["last_unbounded"] if secondary else (row if eligible(row) else None)
        return None if row is None else (row["cp"], [row["pv"][0]])
    if len(root["leaves"]) != 3:
        return None
    points = {}
    for move, row in root["leaves"].items():
        point = row["last_unbounded"] if secondary else (row if eligible(row) else None)
        if point is None:
            return None
        points[move] = point["cp"]
    lowest = min(points.values())
    return lowest, sorted(move for move, value in points.items() if value == lowest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cohort", "forecast", "judge"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    cohort, forecast, judges = (json.loads(p.read_bytes()) for p in
                                (args.cohort, args.forecast, args.judge))
    digest = hashlib.sha256(args.cohort.read_bytes()).hexdigest()
    if digest != forecast["cohort_sha256"] or digest != judges["cohort_sha256"]:
        raise ValueError("Cohort changed between analysis stages")
    forecasts = {r["round"]: r["roots"] for r in forecast["rows"]}
    judgments = {r["round"]: r["roots"] for r in judges["rows"]}
    if forecasts.keys() != judgments.keys() or forecasts.keys() != {r["round"] for r in cohort["selection"]}:
        raise ValueError("Cohort rows mismatch")
    rows = []
    for case in cohort["selection"]:
        ident = case["round"]
        roots = case["roots"]
        targets = []
        costs = {"pv": 0, "tree": 0, "judge": 0, "judge_searches": 0}
        for move in roots:
            after = board_at(case["history"])
            after.push_uci(move)
            judge = judgments[ident][move]
            if judge.keys() != {m.uci() for m in after.legal_moves}:
                raise ValueError(f"Judge reply coverage differs for {ident}/{move}")
            costs["judge"] += sum(r["nodes"] for r in judge.values())
            costs["judge_searches"] += sum(r["nodes"] > 0 for r in judge.values())
            target = None
            if judge and all(map(eligible, judge.values())):
                worst = min(r["cp"] for r in judge.values())
                target = (worst, sorted(m for m, r in judge.items() if r["cp"] == worst))
            targets.append(target)
            pred = forecasts[ident][move]
            costs["pv"] += pred["pv"]["nodes"]
            costs["tree"] += (max(r["nodes"] for r in pred["discovery"])
                              + sum(r["nodes"] for r in pred["leaves"].values()))
        row = {"round": ident, "roots": roots, "cost": costs, "judge": targets, "predictions": {}}
        for secondary in (False, True):
            layer = row["predictions"]["secondary" if secondary else "primary"] = {}
            for arm in ("pv", "tree"):
                scores = [score_arm(forecasts[ident][move], arm, secondary) for move in roots]
                entry = layer[arm] = {"scores": scores}
                if all(targets):
                    entry["reply_hits"] = [
                        None if score is None else bool(set(score[1]) & set(target[1]))
                        for score, target in zip(scores, targets)]
                    if all(scores):
                        gap = scores[0][0] - scores[1][0]
                        truth = targets[0][0] - targets[1][0]
                        entry["gap"] = gap
                        entry["sign_match"] = sign(gap) == sign(truth)
                        entry["absolute_gap_error"] = abs(gap - truth)
        rows.append(row)
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
