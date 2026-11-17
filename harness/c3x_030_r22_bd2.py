"""Quantify candidate-gap dependence on the legal c1–d2 bishop move."""

import argparse
import json
from pathlib import Path

import chess
import chess.engine

from c3x_030_r20_p40_value import BINARY
from c3x_030_s4l_r10_reply_transport import board_at, digest
from c3x_030_s4l_r11_allocation import NET, receipt

SELECTION = "f573f137f37904e6a3c5ea14ff931a2a250af7016474d4a2f778d6e82e30d89a"
REPLIES = ("d6b4", "a5c7", "g6e7")
BD2 = chess.Move.from_uci("c1d2")


def run(engine, board, depth, moves=None):
    info = engine.analyse(board, chess.engine.Limit(depth=depth), root_moves=moves, game=object())
    result = receipt(info, board.turn, board)
    if result is None or result["bound"] or result["depth"] != depth:
        return None
    if moves is not None and chess.Move.from_uci(result["pv"][0]) not in moves:
        raise ValueError("Judge escaped constrained move set")
    return result


def path_if_legal(board):
    copy = board.copy()
    output = []
    for uci in ("c1d2", "b4c3", "d2c3", "a5c3", "b2c3"):
        move = chess.Move.from_uci(uci)
        if move not in copy.legal_moves:
            break
        output.append(copy.san(move))
        copy.push(move)
    return output


def evaluate(engine, selection):
    rows = {}
    case = next(row for row in selection["selection"] if row["round"] == "1.2")
    for root in case["roots"]:
        for reply in REPLIES:
            board = board_at(case["history"])
            board.push_uci(root)
            board.push_uci(reply)
            legal = sorted(board.legal_moves, key=chess.Move.uci)
            possible = BD2 in legal
            result = {}
            for depth in (12, 14):
                result[str(depth)] = {
                    "open": run(engine, board, depth),
                    "without_bd2": run(engine, board, depth, [m for m in legal if m != BD2]) if possible else None,
                    "bd2_only": run(engine, board, depth, [BD2]) if possible else None,
                }
            rows[f"{root}/{reply}"] = {"bd2_legal": possible, "fen": board.fen(),
                                     "exchange_prefix": path_if_legal(board), "values": result}
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("net", type=Path)
    parser.add_argument("selection", type=Path)
    args = parser.parse_args()
    if tuple(map(digest, (args.binary, args.net, args.selection))) != (BINARY, NET, SELECTION):
        raise ValueError("Unexpected judge or R21 receipt")
    with chess.engine.SimpleEngine.popen_uci(str(args.binary.resolve()), timeout=90) as engine:
        engine.configure({"Threads": 1, "Hash": 16, "EvalFile": str(args.net.resolve())})
        output = evaluate(engine, json.loads(args.selection.read_text()))
    print(json.dumps(output, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
