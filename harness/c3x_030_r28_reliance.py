"""Adjudicate a frozen set of Stockfish recommendations against named alternatives."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

import chess.engine

from c3x_030_r26_tt_panel import board_from_case, search
from c3x_030_r28_freeze import digest
from c3x_030_s4l_r11_allocation import NET, judge, single

DEPTHS = (13, 15)
MARGIN = 25


def label(differences):
    if all(value is not None and value >= MARGIN for value in differences):
        return "agree"
    if all(value is not None and value <= -MARGIN for value in differences):
        return "reverse"
    return "unresolved"


def cp(receipt):
    point = receipt["point"]
    return None if point is None or point["bound"] else point["cp"]


def evaluate(board, moves, engine_path, net, enumerate_replies=False):
    mover = board.turn
    rows = []
    with chess.engine.SimpleEngine.popen_uci(str(engine_path), timeout=60) as engine:
        if "berserk" not in engine.id.get("name", "").lower():
            raise ValueError(f"Unexpected reference engine {engine.id}")
        engine.configure({"Threads": 1, "Hash": 16, "EvalFile": str(net)})
        for depth in DEPTHS:
            branches, scores = {}, {}
            for move in moves:
                child = board.copy()
                child.push_uci(move)
                if enumerate_replies:
                    replies = judge(engine, child, mover, depth - 1)
                    values = [cp(receipt) for receipt in replies.values()]
                    branches[move] = replies
                    scores[move] = min(values) if values and None not in values else None
                else:
                    branches[move] = single(engine, child, mover, depth=depth)
                    scores[move] = cp(branches[move])
            score, alternative = (scores[move] for move in moves)
            margin = None if score is None or alternative is None else score - alternative
            rows.append({"child_depth": depth, "measurements": branches,
                         "scores": scores, "margin_cp": margin})
    return {"label": label([row["margin_cp"] for row in rows]), "rows": rows}


def measure(case, stockfish, berserk, net):
    board = board_from_case(case)
    short, long = [
        search(board, "upstream", chess.engine.Limit(nodes=nodes), stockfish, stockfish)
        for nodes in (8000, 32000)
    ]
    alternatives = []
    if short["move"] != long["move"]:
        foil = short
    else:
        alternatives = search(board, "reference", chess.engine.Limit(depth=12), stockfish, stockfish)
        foil = next(row for row in alternatives if row["move"] != long["move"])
    moves = [long["move"], foil["move"]]
    return {
        "id": case["id"], "fen": case["fen"], "recommendation": long["move"],
        "alternative": foil["move"], "short": short, "long": long, "foil": foil,
        "discovery_multipv": alternatives, "judge": evaluate(board, moves, berserk, net),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cohort", "stockfish", "berserk", "net", "output"):
        parser.add_argument(name, type=Path)
    parser.add_argument("--cohort-sha256", required=True)
    args = parser.parse_args()
    cohort = args.cohort.read_bytes()
    assets = [p.resolve() for p in (args.stockfish, args.berserk, args.net)]
    if digest(cohort) != args.cohort_sha256 or digest(assets[2].read_bytes()) != NET:
        raise ValueError("Cohort or reference NNUE SHA mismatch")
    cases = json.loads(cohort)["positions"]
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(lambda case: measure(case, *assets), cases))
        checked = {"agree": 0, "reverse": 0}
        audit = {}
        for case, row in zip(cases, rows, strict=True):
            outcome = row["judge"]["label"]
            if outcome in checked and checked[outcome] < 2:
                checked[outcome] += 1
                moves = [row["recommendation"], row["alternative"]]
                audit[row["id"]] = pool.submit(
                    evaluate, board_from_case(case), moves, *assets[1:], enumerate_replies=True,
                )
        stress = {case_id: future.result() for case_id, future in audit.items()}
    output = {"cohort_sha256": digest(cohort), "assets_sha256": {
        name: digest(path.read_bytes())
        for name, path in zip(("stockfish", "berserk", "net"), assets, strict=True)
    }, "positions": rows, "all_replies": stress}
    with args.output.open("x") as stream:
        json.dump(output, stream, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
