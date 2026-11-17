"""Run the R26 paired native Stockfish search panel on SHA-frozen histories."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import itertools
import json
import os
from pathlib import Path

import chess
import chess.engine

BUDGETS = (8000, 32000)
ARMS = ("upstream", "passive", "picker_off", "value_off", "both_off", "hash_1m")


def board_from_case(case):
    board = chess.Board()
    for move in case["moves"]:
        board.push_uci(move)
    if board.fen() != case["fen"] or board.legal_moves.count() != case["legal_moves"]:
        raise ValueError(f"History mismatch for {case['id']}")
    return board


def info_row(board, info, bestmove):
    pv = info.get("pv", [])
    legal_board = board.copy()
    san = []
    for move in pv:
        if move not in legal_board.legal_moves:
            raise ValueError(f"Illegal PV move {move.uci()} in {legal_board.fen()}")
        san.append(legal_board.san(move))
        legal_board.push(move)
    if bestmove not in board.legal_moves:
        raise ValueError(f"Illegal engine recommendation {bestmove}")
    score = info.get("score")
    pov = score.pov(board.turn) if score is not None else None
    return {
        "move": bestmove.uci(),
        "san": board.san(bestmove),
        "depth": info.get("depth"),
        "seldepth": info.get("seldepth"),
        "actual_nodes": info.get("nodes"),
        "hashfull": info.get("hashfull"),
        "upperbound": bool(info.get("upperbound")),
        "lowerbound": bool(info.get("lowerbound")),
        "cp": pov.score() if pov is not None else None,
        "mate": pov.mate() if pov is not None else None,
        "pv": [move.uci() for move in pv],
        "pv_san": san,
    }


def search(board, arm, limit, baseline, patched, root_moves=None):
    env = dict(os.environ)
    env["C3X_NO_TT_PICKER"] = "1" if arm in ("picker_off", "both_off") else "0"
    env["C3X_NO_TT_VALUE"] = "1" if arm in ("value_off", "both_off") else "0"
    path = baseline if arm in ("upstream", "reference") else patched
    with chess.engine.SimpleEngine.popen_uci(str(path), env=env, timeout=30) as engine:
        engine.configure({"Threads": 1, "Hash": 1 if arm == "hash_1m" else 16})
        ranks = {}
        multipv = 3 if arm == "reference" else 1
        with engine.analysis(board, limit, multipv=multipv, root_moves=root_moves, info=chess.engine.INFO_ALL) as analysis:
            for update in analysis:
                if "pv" in update and "score" in update:
                    ranks[update.get("multipv", 1)] = update
            best = analysis.wait()
        if arm == "reference":
            return [info_row(board, row, row["pv"][0]) for _, row in sorted(ranks.items())]
        return info_row(board, ranks[1], best.move)


def compare(case, arm, nodes, baseline, patched):
    limit = chess.engine.Limit(nodes=nodes)
    return search(board_from_case(case), arm, limit, baseline, patched)


def one_job(job):
    case, arm, nodes, baseline, patched = job
    return {
        "case": case["id"], "game": case["game_id"], "ply": case["ply"],
        "arm": arm, "requested_nodes": nodes,
        "result": compare(case, arm, nodes, baseline, patched),
    }


def jobs(cases, baseline, patched):
    for case in cases:
        for arm, nodes in itertools.product(ARMS, BUDGETS):
            yield case, arm, nodes, baseline, patched
        yield case, "reference", 120000, baseline, patched


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cohort", type=Path)
    parser.add_argument("cohort_sha256")
    parser.add_argument("upstream", type=Path)
    parser.add_argument("patched", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    raw = args.cohort.read_bytes()
    if hashlib.sha256(raw).hexdigest() != args.cohort_sha256:
        raise ValueError("Frozen cohort SHA-256 mismatch")
    cases = json.loads(raw)["positions"]
    plan = list(jobs(cases, args.upstream.resolve(), args.patched.resolve()))
    output_temp = args.output.with_suffix(args.output.suffix + ".partial")
    if args.output.exists():
        raise FileExistsError(args.output)
    with output_temp.open("x") as stream, ThreadPoolExecutor(max_workers=args.workers) as pool:
        for index, row in enumerate(pool.map(one_job, plan), 1):
            stream.write(json.dumps(row, separators=(",", ":")) + "\n")
            if index % 100 == 0:
                print(f"{index}/{len(plan)} native searches", flush=True)
    output_temp.rename(args.output)
    print(f"{len(plan)} native searches", flush=True)


if __name__ == "__main__":
    main()
