"""Find unchanged recommendations and exact UCI scores with different opponent replies."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import itertools
import json
from pathlib import Path

import chess.engine

from c3x_030_r26_tt_panel import board_from_case, search
from c3x_030_r28_freeze import digest

DEPTHS = (10, 12, 14)
STOCKFISH_SHA = "fc2f6b069a775a463c6d17cce30f0bd24339ec446ab621e29c4933719026e8b5"


def score_kind(row):
    if row["upperbound"]:
        return "upperbound"
    if row["lowerbound"]:
        return "lowerbound"
    return "point"


def fork_pairs(rows):
    return [
        {"first_depth": left["depth"], "second_depth": right["depth"],
         "score_cp": left["cp"], "score_kinds": [score_kind(left), score_kind(right)],
         "lines": [left["pv_san"], right["pv_san"]]}
        for left, right in itertools.combinations(rows, 2)
        if left["move"] == right["move"]
        and left["cp"] is not None and left["cp"] == right["cp"]
        and all(len(row["pv"]) > 1 and row["pv"][0] == row["move"] for row in (left, right))
        and left["pv"][1] != right["pv"][1]
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cohort", "stockfish", "output"):
        parser.add_argument(name, type=Path)
    parser.add_argument("--cohort-sha256", required=True)
    parser.add_argument("--depths", type=int, nargs="+", default=DEPTHS)
    args = parser.parse_args()
    depths = tuple(sorted(set(args.depths)))
    if len(depths) < 2 or depths[0] < 1:
        parser.error("Provide at least two distinct positive depths")
    raw = args.cohort.read_bytes()
    engine = args.stockfish.resolve()
    if digest(raw) != args.cohort_sha256 or digest(engine.read_bytes()) != STOCKFISH_SHA:
        raise ValueError("Frozen cohort or Stockfish SHA mismatch")
    cases = json.loads(raw)["positions"]

    def measure(case):
        board = board_from_case(case)
        rows = [search(board, "upstream", chess.engine.Limit(depth=depth), engine, engine)
                for depth in depths]
        if tuple(row["depth"] for row in rows) != depths:
            raise ValueError(f"Missing completed depth for {case['id']}")
        return {"id": case["id"], "fen": case["fen"], "searches": rows, "forks": fork_pairs(rows)}

    with ThreadPoolExecutor(max_workers=4) as pool:
        positions = list(pool.map(measure, cases))
    with args.output.open("x") as stream:
        json.dump({"cohort_sha256": digest(raw), "stockfish_sha256": STOCKFISH_SHA,
                   "depths": depths, "positions": positions}, stream, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
