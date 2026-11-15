"""Compare London's two source candidates under every legal opponent reply."""
import argparse
import hashlib
import json
from pathlib import Path

import chess
import chess.engine

from c3x_029_p42_r21_independent_berserk_value_feasibility import NET_SHA, reference_info


def evaluate(engine, position, budget, fixed_depth):
    limit = chess.engine.Limit(depth=budget) if fixed_depth else chess.engine.Limit(nodes=budget)
    info = engine.analyse(position, limit, game=object())
    if fixed_depth and info.get("depth") != budget:
        raise ValueError(f"Expected completed depth {budget}")
    receipt = reference_info(position, info, 1 if fixed_depth else budget, chess.WHITE)
    if fixed_depth and not receipt.get("actual_nodes"):
        raise ValueError("Missing positive reported node count")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("engine", "network", "protocol"):
        parser.add_argument(name, type=Path)
    parser.add_argument("--fixed-depth", action="store_true")
    args = parser.parse_args()
    if hashlib.sha256(args.network.read_bytes()).hexdigest() != NET_SHA:
        raise ValueError("Expected pinned Berserk 14 network")
    spec, = [case for case in json.loads(args.protocol.read_text())["cases"]
             if case["case_id"] == "dev_london_ply8" and case["split"] == "development"]
    board = chess.Board()
    for move in spec["history_uci"]:
        board.push_uci(move)
    if board.fen() != spec["fen"] or board.turn != chess.WHITE:
        raise ValueError("Replayed history does not match London")
    result = {"fixed_depth": args.fixed_depth, "binary_sha256": hashlib.sha256(args.engine.read_bytes()).hexdigest(), "candidates": {}}
    with chess.engine.SimpleEngine.popen_uci(str(args.engine.resolve()), timeout=30) as engine:
        result["engine"] = engine.id
        engine.configure({"Threads": 1, "Hash": 16, "EvalFile": str(args.network.resolve())})
        for move in ("b1d2", "f3e5"):
            after = board.copy()
            after.push_uci(move)
            data = result["candidates"][move] = {}
            for budget in ((10, 12) if args.fixed_depth else (48000, 96000)):
                trial = data[str(budget)] = {"free": evaluate(engine, after, budget, args.fixed_depth), "replies": {}}
                for reply in sorted(after.legal_moves, key=lambda move: move.uci()):
                    leaf = after.copy()
                    leaf.push(reply)
                    trial["replies"][reply.uci()] = evaluate(engine, leaf, budget, args.fixed_depth)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
