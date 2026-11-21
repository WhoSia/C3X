"""Check whether equal-score PV forks reconverge on the board within their public lines."""
import argparse
import json
from pathlib import Path

from c3x_030_r26_tt_panel import board_from_case
from c3x_030_r28_freeze import digest


def replay(board, line):
    board = board.copy()
    states = []
    for san in line:
        move = board.parse_san(san)
        occupied = board.piece_at(move.to_square)
        states.append({"san": san, "uci": move.uci(),
                       "piece": board.piece_at(move.from_square).symbol(),
                       "captured": ("P" if not board.turn else "p") if board.is_en_passant(move)
                       else (occupied.symbol() if occupied else None)})
        board.push(move)
        states[-1]["fen"] = board.fen()
    return states


def audit(board, fork):
    left, right = [replay(board, line) for line in fork["lines"]]
    matching = [ply for ply, (a, b) in enumerate(zip(left, right), 1)
                if ply > 2 and a["fen"] == b["fen"]]
    return {**fork, "first_same_fen_after_reply": min(matching, default=None),
            "branches": [left, right]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cohort", "forks", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    cohort_bytes = args.cohort.read_bytes()
    fork_bytes = args.forks.read_bytes()
    forks = json.loads(fork_bytes)
    if digest(cohort_bytes) != forks["cohort_sha256"]:
        raise ValueError("Forks and cohort hashes differ")
    cases = {row["id"]: row for row in json.loads(cohort_bytes)["positions"]}
    output = {"fork_input_sha256": digest(fork_bytes), "pairs": [
        {"id": row["id"], **audit(board_from_case(cases[row["id"]]), fork)}
        for row in forks["positions"] for fork in row["forks"]
        if fork["score_kinds"] == ["point", "point"]
    ]}
    with args.output.open("x") as stream:
        json.dump(output, stream, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
