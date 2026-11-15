"""Summarize complete London reply sweeps without imputing missing scores."""
import argparse
import json
from pathlib import Path


def unbounded_cp(row):
    score = row.get("root_mover_cp")
    if type(score) is not int or row.get("lowerbound") or row.get("upperbound"):
        raise ValueError("Expected an eligible unbounded centipawn report")
    return score


def summarize(data):
    nd2 = data["candidates"]["b1d2"]
    ne5 = data["candidates"]["f3e5"]
    if not data["fixed_depth"] or not nd2 or nd2.keys() != ne5.keys():
        raise ValueError("Expected matched fixed-depth sweeps")
    result = {}
    for depth in nd2:
        cells = {}
        scores = []
        for label, trial, count in (("Nd2", nd2[depth], 35), ("Ne5", ne5[depth], 32)):
            replies = trial["replies"]
            if len(replies) != count:
                raise ValueError(f"Expected {count} London replies after {label}")
            if any(row["depth"] != int(depth) for row in (trial["free"], *replies.values())):
                raise ValueError(f"Expected completed depth {depth}")
            observed = {move: unbounded_cp(row) for move, row in replies.items()}
            minimum = min(observed.values())
            cells[label] = {"free_cp": unbounded_cp(trial["free"]), "minimum_cp": minimum,
                            "minimizing_replies": sorted(m for m, v in observed.items() if v == minimum),
                            "nodes": sum(r["actual_nodes"] for r in (trial["free"], *replies.values()))}
            scores.append(observed)
        left, right = scores
        common = left.keys() & right.keys()
        cells["shared_reply_counts"] = {
            "Nd2_higher": sum(left[m] > right[m] for m in common),
            "equal": sum(left[m] == right[m] for m in common),
            "Ne5_higher": sum(left[m] < right[m] for m in common),
        }
        result[depth] = cells
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sweep", type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(json.loads(args.sweep.read_text())), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
