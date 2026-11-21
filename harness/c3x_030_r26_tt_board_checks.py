"""Verify the board-level contrasts used in the R26 case report."""
import argparse
import json
from pathlib import Path

import chess

from c3x_030_r26_tt_panel import board_from_case
from c3x_030_r26_tt_reply_judge import DEPTHS, FORK_CASE, ROOT_CASE, ROOTS


def after(board, moves):
    child = board.copy()
    for move in moves:
        child.push_san(move)
    return child


def claim_checks(cohort, referee):
    rows = {case["id"]: case for case in cohort["positions"]}
    root = board_from_case(rows[ROOT_CASE])
    nd7, a4 = (after(root, [san]) for san in ("Nd7", "a4"))
    a4_b4 = after(a4, ["b4"])
    if nd7.piece_at(chess.D7) != chess.Piece(chess.KNIGHT, chess.BLACK):
        raise ValueError("Missing Black knight on d7")
    if (nd7.piece_at(chess.C5) != chess.Piece(chess.BISHOP, chess.WHITE)
            or chess.C5 not in nd7.attacks(chess.D7)
            or a4_b4.piece_at(chess.B4) != chess.Piece(chess.PAWN, chess.WHITE)
            or chess.C5 not in a4_b4.attacks(chess.B4)):
        raise ValueError("c5 attack or support failed to replay")
    reply_removal = {}
    for depth in DEPTHS:
        verdict = referee["rows"][f"{ROOT_CASE}/{depth}"]
        nd7_row, a4_row = (verdict[move] for move in ROOTS)
        if any(row["point_count"] != len(row["replies"]) for row in (nd7_row, a4_row)):
            raise ValueError("Incomplete reply universe")
        scores = [row["point"]["cp"] for mv, row in a4_row["replies"].items() if mv != "b3b4"]
        full_gap = nd7_row["minimum_ordered_score"] - a4_row["minimum_ordered_score"]
        remaining_gap = nd7_row["minimum_ordered_score"] - min(scores)
        reply_removal[depth] = {"full_gap_cp": full_gap, "gap_without_b4_cp": remaining_gap}
    fork = board_from_case(rows[FORK_CASE])
    paths = (("h5", "f4", "h6", "Nf6"), ("h5", "Nf6", "h6", "f4"))
    leaves = [after(fork, path) for path in paths]
    if leaves[0].fen().split()[:4] != leaves[1].fen().split()[:4]:
        raise ValueError("The legal lines do not converge in board geometry")
    for leaf in leaves:
        if not leaf.gives_check(leaf.parse_san("Ne2+")):
            raise ValueError("The shared knight check did not replay")
    return {
        "nd7_c5_geometry": "Black knight d7 attacks White bishop c5",
        "a4_b4_geometry": "White pawn b4 protects White bishop c5",
        "gap_after_excluding_reply_from_cached_scores": reply_removal,
        "fork_reply_orders": paths,
        "fork_leaf_fen": [leaf.fen() for leaf in leaves],
        "fork_shared_check": "Ne2+",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cohort", type=Path)
    parser.add_argument("referee", type=Path)
    args = parser.parse_args()
    result = claim_checks(json.loads(args.cohort.read_bytes()), json.loads(args.referee.read_bytes()))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
