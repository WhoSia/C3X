"""Compare limited menus, reply regret and robust preference on shared references."""

import argparse
from collections import Counter
import json
from pathlib import Path

from c3x_030_r20_p40_value import BINARY
from c3x_030_r22_reply_menus import POLICIES
from c3x_030_s4l_r10_reply_transport import digest
from c3x_030_s4l_r11_allocation import NET, SF
from c3x_030_s4l_r12_explanation_score import sign


def cp(run, depth=None):
    point = run["point"]
    if point is None or point["bound"] or (depth is not None and point["depth"] != depth):
        return None
    return point["cp"]


def minimum(rows, moves, side):
    relevant = [(move, rows[move][side]) for move in moves]
    if any(value is None for _, value in relevant):
        return None
    low = min(value for _, value in relevant)
    return {"cp": low, "moves": [move for move, value in relevant if value == low]}


def rank(pair):
    return sign(pair[0]["cp"] - pair[1]["cp"]) if all(pair) else None


def score(cohort, forecast, judged):
    result = {}
    for case in cohort["selection"]:
        detail, game = case["discovery"], case["round"]
        if not detail["admitted"]:
            continue
        if set(judged[game]) != set(detail["common"]):
            raise ValueError("Judge must cover exactly the legal common-reply set")
        source = {move: [cp(point) for point in sides] for move, sides in forecast[game].items()}
        rows = {}
        for depth in (12, 14):
            judge = {move: [cp(point, depth) for point in values[str(depth)]]
                     for move, values in judged[game].items()}
            exact = [minimum(judge, detail["common"], side) for side in range(2)]
            policies = {}
            for policy, moves in detail["menus"].items():
                if len(set(moves)) != 3:
                    raise ValueError("Expected exactly three replies per menu")
                observed = [minimum(judge, moves, side) for side in range(2)]
                predicted = [minimum(source, moves, side) for side in range(2)]
                regrets = [a["cp"] - b["cp"] if a and b else None
                           for a, b in zip(observed, exact, strict=True)]
                policies[policy] = {"regret_cp": regrets, "sample_minima": observed,
                                    "predicted_minima": predicted, "forecast_rank": rank(predicted),
                                    "menu_reference_rank": rank(observed)}
            rows[str(depth)] = {"reference_rank": rank(exact), "minima": exact, "policies": policies}
        result[game] = {"roots": case["roots"], "common_count": len(detail["common"]),
                        "menus": detail["menus"], "forcing_selected": any(
                            move in detail["forcing"] for move in detail["menus"]["mixed"]),
                        "depths": rows}
    return result


def summarize(rows):
    output = {}
    for depth in ("12", "14"):
        result = {}
        for name in POLICIES:
            regret = []
            counts = Counter()
            for row in rows.values():
                data = row["depths"][depth]
                result_row = data["policies"][name]
                regret.extend(value for value in result_row["regret_cp"] if value is not None)
                for kind in ("forecast_rank", "menu_reference_rank"):
                    if result_row[kind] is not None and data["reference_rank"] is not None:
                        counts[kind + "_covered"] += 1
                        counts[kind + "_correct"] += result_row[kind] == data["reference_rank"]
            result[name] = {**counts, "regret_n": len(regret), "worst_reply_hits": regret.count(0),
                            "mean_regret_cp": sum(regret) / len(regret) if regret else None,
                            "max_regret_cp": max(regret, default=None)}
        output[depth] = result
    stable = [row["depths"] for row in rows.values()
              if row["depths"]["12"]["reference_rank"] is not None
              and row["depths"]["12"]["reference_rank"] == row["depths"]["14"]["reference_rank"]]
    output["stable_reference_games"] = len(stable)
    output["stable_rank"] = {}
    for name in POLICIES:
        predictions = [(game["12"]["policies"][name]["forecast_rank"], game["12"]["reference_rank"])
                       for game in stable]
        output["stable_rank"][name] = {
            "public_correct": sum(p == r for p, r in predictions),
            "public_covered": sum(p is not None for p, _ in predictions),
            "menu_both_correct": sum(all(game[d]["policies"][name]["menu_reference_rank"] ==
                                         game[d]["reference_rank"] for d in ("12", "14"))
                                     for game in stable)}
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cohort", type=Path)
    parser.add_argument("forecast", type=Path)
    parser.add_argument("judgment", type=Path)
    args = parser.parse_args()
    cohort, forecast, judge = (json.loads(path.read_text())
                               for path in (args.cohort, args.forecast, args.judgment))
    if (judge["net_sha256"] != NET or judge["binary_sha256"] != BINARY
            or forecast["binary_sha256"] != SF or judge["forecast_sha256"] != digest(args.forecast)
            or forecast["cohort_sha256"] != judge["cohort_sha256"]
            or judge["cohort_sha256"] != digest(args.cohort)
            or forecast["rows"].keys() != judge["rows"].keys()):
        raise ValueError("Inconsistent evaluation provenance")
    rows = score(cohort, forecast["rows"], judge["rows"])
    print(json.dumps({"cohort": cohort["cohort"], "summary": summarize(rows), "rows": rows},
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
