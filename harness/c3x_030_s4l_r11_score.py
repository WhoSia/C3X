"""Score equal-budget arms on the same judge-complete game histories."""

import argparse
import json
from pathlib import Path

from c3x_030_s4l_r10_reply_transport import board_at, digest
from c3x_030_s4l_r11_allocation import ARMS

METHODS = ("pv", *ARMS)


def minimum(rows):
    if not rows or any(row is None for row in rows.values()):
        return None
    value = min(row["ordered"] for row in rows.values())
    moves = sorted(move for move, row in rows.items() if row["ordered"] == value)
    return {"ordered": value, "cp": rows[moves[0]]["cp"], "replies": moves}


def choose(forecast, arm, endpoint):
    if arm == "pv":
        row = forecast[endpoint]
        return ({**row, "replies": row["pv"][:1]} if row and not row["bound"] else None)
    return minimum({move: row[endpoint] if row[endpoint] and not row[endpoint]["bound"] else None
                    for move, row in forecast["leaves"].items()})


def direction(rows):
    x, y = (row["ordered"] for row in rows)
    return (x > y) - (x < y)


def score_case(case, forecasts, judges):
    board = board_at(case["history"])
    roots = case["roots"]
    if len(roots) != 2 or set(roots) != forecasts.keys() or set(roots) != judges.keys():
        raise ValueError("Candidate identities differ")
    judge_points = []
    for move in roots:
        after = board.copy()
        after.push_uci(move)
        replies = judges[move]
        if replies.keys() != {m.uci() for m in after.legal_moves}:
            raise ValueError("Judge's legal replies differ")
        judge_points.append(minimum({k: v["point"] for k, v in replies.items()}))
    arms = {arm: {} for arm in METHODS}
    for arm, result in arms.items():
        result["actual_nodes"] = sum(forecasts[move][arm]["actual_nodes"] for move in roots)
        for endpoint in ("point", "terminal"):
            result[endpoint] = [choose(forecasts[move][arm], arm, endpoint) for move in roots]
    scored = {"round": case["round"], "roots": roots, "judge": judge_points, "arms": arms,
              "judge_searches": sum(row["actual_nodes"] > 0 for replies in judges.values() for row in replies.values()),
              "judge_nodes": sum(row["actual_nodes"] for replies in judges.values() for row in replies.values())}
    if not all(judge_points) or not all(all(row["point"]) for row in arms.values()):
        return scored

    cp_ready = all(row["cp"] is not None for row in judge_points)
    cp_ready &= all(row["cp"] is not None for r in arms.values() for row in r["point"])
    for arm, result in arms.items():
        points = result["point"]
        result["sign_match"] = direction(points) == direction(judge_points)
        result["reply_hits"] = [bool(set(row["replies"]) & set(target["replies"]))
                                for row, target in zip(points, judge_points)]
        if cp_ready:
            result["gap_error"] = abs((points[0]["cp"] - points[1]["cp"])
                                      - (judge_points[0]["cp"] - judge_points[1]["cp"]))
        if arm in ARMS:
            discovered = [set(forecasts[move][arm]["leaves"]) for move in roots]
            result["discovery_hits"] = [bool(moves & set(target["replies"]))
                                        for moves, target in zip(discovered, judge_points)]
            restricted = [minimum({m: judges[root][m]["point"] for m in replies})
                          for root, replies in zip(roots, discovered)]
            result["restricted_judge_sign_match"] = direction(restricted) == direction(judge_points)
    return scored


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cohort", "forecast", "judge"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    cohort, predictions, judgments = (json.loads(p.read_text())
                                      for p in (args.cohort, args.forecast, args.judge))
    cohort_hash = digest(args.cohort)
    if predictions["cohort_sha256"] != cohort_hash or judgments["cohort_sha256"] != cohort_hash:
        raise ValueError("Cohort hashes differ")
    forecasts = {r["round"]: r["roots"] for r in predictions["rows"]}
    judges = {r["round"]: r["roots"] for r in judgments["rows"]}
    cases = cohort["selection"]
    if forecasts.keys() != judges.keys() or forecasts.keys() != {case["round"] for case in cases}:
        raise ValueError("Cohort round identities differ")
    rows = [score_case(case, forecasts[case["round"]], judges[case["round"]]) for case in cases]
    print(json.dumps({"depth": judgments["depth"], "rows": rows}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
