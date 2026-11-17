"""Enumerate the immediate and delayed availability of b4 at the archived fork."""

import argparse
import json
from pathlib import Path

import chess

from c3x_030_r25_reply_provenance import CASES, FORK
from c3x_030_s4l_r10_reply_transport import board_at, digest

B4 = chess.Move.from_uci("b2b4")


def inspect(history, frozen_reports):
    first = frozen_reports[0]["pv"][0]
    if any(row["pv"][0] != first or B4.uci() not in row["pv"] for row in frozen_reports):
        raise ValueError("The expected resource is absent from an observed continuation")
    after_root = board_at([*history, first])
    result = {}
    for row in frozen_reports:
        reply = row["pv"][1]
        board = after_root.copy()
        reply_san = board.san(board.parse_uci(reply))
        board.push_uci(reply)
        legal = sorted(board.legal_moves, key=chess.Move.uci)
        responses = []
        if board.is_check():
            for white_move in legal:
                branch = board.copy()
                branch.push(white_move)
                choices = sorted(branch.legal_moves, key=chess.Move.uci)
                refuters = []
                for black_move in choices:
                    continuation = branch.copy()
                    continuation.push(black_move)
                    if B4 not in continuation.legal_moves:
                        refuters.append({"move": black_move.uci(), "san": branch.san(black_move),
                                         "next_is_check": continuation.is_check()})
                responses.append({"move": white_move.uci(), "san": board.san(white_move),
                                  "black_choices": len(choices),
                                  "b4_available": len(choices) - len(refuters), "refuters": refuters})
        result[reply] = {"san": reply_san, "check": board.is_check(),
                         "b4_now": B4 in legal, "legal_white_count": len(legal), "evasions": responses,
                         "black_attackers_h2": [
                             {"square": chess.square_name(square), "piece": board.piece_at(square).symbol()}
                             for square in board.attackers(chess.BLACK, chess.H2)
                         ]}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cases", type=Path)
    parser.add_argument("freeze", type=Path)
    args = parser.parse_args()
    if tuple(map(digest, (args.cases, args.freeze))) != (CASES, FORK):
        raise ValueError("Unexpected R24 evidence")
    freeze = json.loads(args.freeze.read_text())
    case = next(row for row in json.loads(args.cases.read_text())["cases"] if row["id"] == freeze["case"])
    print(json.dumps(inspect(case["history"], freeze["reports"]), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
