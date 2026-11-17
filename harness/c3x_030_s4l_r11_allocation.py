"""Execute the frozen R11 selection, forecasts, and all-reply judge."""

import argparse
import json
import logging
from pathlib import Path

import chess
import chess.engine

import c3x_030_s4l_r10_reply_transport as prior

SOURCE = "200e59cec6e5efb5133137c1758b97ab55cf92b4afb532690e80ee39461f539a"
OLD = "b81c2b31e733d4f151cbe068be3a98e79724a472c34ec14ce7f6f92e0a27983a"
SF = "3766b594a274e83bda1b2b1a8f67747b2f26724e6a64e388e659fb00c1fd12cb"
BERSERK = "64070336ecf4973bd704522198654f911d74b5b8ba290a57be695913cc4f9f63"
NET = "9b84c340af7e45f6e07f0046235ccb327f4ae0840c8ee2c4b97b99121e5c5084"
ARMS = {"tree_24_8": (24000, 8000), "tree_12_12": (12000, 12000)}


def select(engine, source, exclude):
    if prior.digest(source) != SOURCE or prior.digest(exclude) != OLD:
        raise ValueError("Input hash mismatch")
    blocked = {tuple(row["history"][:12]) for row in json.loads(exclude.read_text())["selection"]}
    return prior.selection(engine, source, excluded_openings=blocked, expected_sha=SOURCE)


def receipt(info, mover, board):
    if "score" not in info or not info.get("pv") or info.get("nodes", 0) <= 0:
        return None
    score = info["score"].pov(mover)
    probe = board.copy()
    for move in info["pv"]:
        if move not in probe.legal_moves:
            raise ValueError(f"Illegal PV move {move}")
        probe.push(move)
    return {"ordered": score.score(mate_score=100000), "cp": score.score(),
            "bound": bool(info.get("upperbound") or info.get("lowerbound")),
            "pv": [m.uci() for m in info["pv"]], "nodes": info["nodes"], "depth": info["depth"]}


def single(engine, board, mover, *, nodes=None, depth=None):
    if board.is_game_over(claim_draw=False):
        winner = board.outcome(claim_draw=False).winner
        order = 0 if winner is None else (100000 if winner == mover else -100000)
        endpoint = {"ordered": order, "cp": 0 if winner is None else None, "bound": False,
                    "pv": [], "nodes": 0, "depth": 0}
        return {"terminal": endpoint, "point": endpoint, "actual_nodes": 0}
    point = None
    with engine.analysis(board, chess.engine.Limit(nodes=nodes, depth=depth), game=object()) as stream:
        for info in stream:
            if depth is None:
                if info.get("upperbound") or info.get("lowerbound"):
                    continue
                complete = receipt(info, mover, board)
                if complete is not None:
                    point = complete
        final = receipt(stream.info, mover, board)
    if final is None:
        raise ValueError("Missing final engine output")
    if depth is not None and final["depth"] == depth and not final["bound"]:
        point = final
    return {"terminal": final, "point": point, "actual_nodes": final["nodes"]}


def predict(engine, after, mover):
    pv = single(engine, after, mover, nodes=48000)
    result = {"pv": pv}
    for arm, (discovery_nodes, leaf_nodes) in ARMS.items():
        if after.legal_moves.count() < 3:
            result[arm] = {"discovery": [], "leaves": {}, "actual_nodes": 0}
            continue
        discovery = prior.analysis(engine, after, mover, nodes=discovery_nodes, count=3)
        moves = [row["pv"][0] for row in discovery]
        if len(moves) != 3 or len(set(moves)) != 3:
            raise ValueError("Expected three distinct discovered replies")
        leaves = {}
        for reply in moves:
            leaf = after.copy()
            leaf.push_uci(reply)
            leaves[reply] = single(engine, leaf, mover, nodes=leaf_nodes)
        result[arm] = {"discovery": discovery, "leaves": leaves,
                       "actual_nodes": max(row["nodes"] for row in discovery)
                       + sum(row["actual_nodes"] for row in leaves.values())}
    return result


def judge(engine, after, mover, depth):
    result = {}
    for reply in sorted(after.legal_moves, key=lambda move: move.uci()):
        leaf = after.copy()
        leaf.push(reply)
        result[reply.uci()] = single(engine, leaf, mover, depth=depth)
    return result


def evaluate(engine, source, stage, depth):
    cohort = json.loads(source.read_text())
    if cohort["source_sha256"] != SOURCE or len(cohort["selection"]) != 8:
        raise ValueError("Expected eight sealed positions from League 2")
    rows = []
    for case in cohort["selection"]:
        board = prior.board_at(case["history"])
        roots = {}
        for candidate in case["roots"]:
            after = board.copy()
            after.push_uci(candidate)
            roots[candidate] = (predict(engine, after, board.turn) if stage == "predict"
                                else judge(engine, after, board.turn, depth))
        rows.append({"round": case["round"], "roots": roots})
    return {"cohort_sha256": prior.digest(source), "depth": depth, "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("select", "predict", "judge"))
    parser.add_argument("engine", type=Path)
    parser.add_argument("source", type=Path)
    parser.add_argument("--exclude", type=Path)
    parser.add_argument("--net", type=Path)
    parser.add_argument("--depth", type=int, choices=(12, 14, 16))
    args = parser.parse_args()
    logging.getLogger("chess.engine").setLevel(logging.ERROR)
    options = {"Threads": 1, "Hash": 16}
    binary = prior.digest(args.engine)
    if args.stage == "judge":
        if binary != BERSERK or args.depth is None or not args.net or prior.digest(args.net) != NET:
            parser.error("Expected pinned Berserk binary and network, and a judge depth")
        options["EvalFile"] = str(args.net.resolve())
    else:
        if binary != SF:
            parser.error("Expected pinned Stockfish binary")
        options["Use NNUE"] = False
    if args.stage == "select" and not args.exclude:
        parser.error("The frozen R10 cohort is required to exclude overlapping prefixes")
    with chess.engine.SimpleEngine.popen_uci(str(args.engine.resolve())) as engine:
        engine.configure(options)
        result = (select(engine, args.source, args.exclude) if args.stage == "select"
                  else evaluate(engine, args.source, args.stage, args.depth))
        result["binary_sha256"] = binary
        result["engine"] = engine.id
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
