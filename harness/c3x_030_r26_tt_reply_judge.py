"""Use the R11 all-reply judge on the frozen R26 named contrast and plan fork."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

import chess.engine

from c3x_030_r26_tt_cohort import digest
from c3x_030_r26_tt_panel import board_from_case
from c3x_030_s4l_r11_allocation import NET, judge, single

DEPTHS = (13, 15)
ROOT_CASE = "twic1670-08-61"
FORK_CASE = "twic1670-13-96"
ROOTS = ("f6d7", "a5a4")
FORKS = [(before, *tail) for before in ("f5f4", "d5f6") for tail in ((), ("h5h6",))]


def compare(case, fork, engine_path, net, depth):
    board = board_from_case(case)
    mover = board.turn
    with chess.engine.SimpleEngine.popen_uci(str(engine_path), timeout=60) as engine:
        if "berserk" not in engine.id.get("name", "").lower():
            raise ValueError(f"Unexpected judge engine {engine.id}")
        engine.configure({"Threads": 1, "Hash": 16, "EvalFile": str(net)})
        if fork:
            board.push_uci("h4h5")
            branches = {}
            for path in FORKS:
                child = board.copy()
                for move in path:
                    child.push_uci(move)
                branches[" ".join(path)] = single(engine, child, mover, depth=depth)
            return branches

        roots = {}
        for root in ROOTS:
            child = board.copy()
            child.push_uci(root)
            replies = judge(engine, child, mover, depth)
            points = {reply: row["point"]["ordered"] for reply, row in replies.items() if row["point"] is not None}
            worst = min(points.values()) if len(points) == len(replies) else None
            roots[root] = {
                "replies": replies, "point_count": len(points), "minimum_ordered_score": worst,
                "minimizers": [reply for reply, val in points.items() if val == worst],
            }
        return roots


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cohort", "berserk", "net", "output"):
        parser.add_argument(name, type=Path)
    parser.add_argument("--cohort-sha256", required=True)
    args = parser.parse_args()
    raw = args.cohort.read_bytes()
    if digest(raw) != args.cohort_sha256 or digest(args.net.read_bytes()) != NET:
        raise ValueError("Frozen history or judge network SHA mismatch")
    cases = {case["id"]: case for case in json.loads(raw)["positions"]}
    engine, net = args.berserk.resolve(), args.net.resolve()
    jobs = [(key, depth) for key in (ROOT_CASE, FORK_CASE) for depth in DEPTHS]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = [pool.submit(compare, cases[key], key == FORK_CASE, engine, net, depth) for key, depth in jobs]
        rows = {f"{key}/{depth}": future.result() for (key, depth), future in zip(jobs, results)}
    output = {"cohort_sha256": digest(raw), "nnue_sha256": NET,
              "engine_sha256": digest(engine.read_bytes()), "rows": rows}
    with args.output.open("x") as stream:
        json.dump(output, stream, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
