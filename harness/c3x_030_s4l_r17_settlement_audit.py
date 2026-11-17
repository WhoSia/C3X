"""Check horizon nesting and independently replay final legal defenses."""

import argparse
import json
from pathlib import Path

import chess

from c3x_030_s4l_r16_plan_oracle import attained, balance, target_after
from c3x_030_s4l_r16_plan_source import post_reply, root_boards


def reference(board, target, mover, baseline, plies):
    if plies == 0 or board.is_game_over(claim_draw=False):
        return attained(board, target, mover, baseline)
    for move in list(board.legal_moves):
        victim = target_after(board, move, target)
        ours = board.turn == mover
        board.push(move)
        result = reference(board, victim, mover, baseline, plies - 1)
        board.pop()
        if result == ours:
            return ours
    return board.turn != mover


def verify(plans, original, settled):
    checked = lost = leaves = 0
    for plan in plans:
        rid = plan["round"]
        branches = root_boards(plan)
        origin = chess.parse_square(plan["target"])
        for reply in plan["replies"]:
            side_results = zip(branches, original[rid][reply], settled[rid][reply], strict=True)
            for branch, early, late in side_results:
                if early["status"] != late["status"]:
                    raise ValueError("Horizon changed leaf coverage")
                if early["status"] != "judged":
                    continue
                leaves += 1
                shorter = set(early["truth"])
                longer = set(late["truth"])
                if not longer <= shorter or early["menus"] != late["menus"]:
                    raise ValueError("Horizon changed menus or violated witness nesting")
                board, target = post_reply(branch, reply, origin)
                mover = board.turn
                baseline = balance(board, mover)
                for uci in sorted(shorter):
                    move = board.parse_uci(uci)
                    victim = target_after(board, move, target)
                    board.push(move)
                    holds = reference(board, victim, mover, baseline, 3)
                    board.pop()
                    if holds != (uci in longer):
                        raise ValueError(f"Literal defense replay differs at {rid} {reply} {uci}")
                    checked += 1
                    lost += not holds
    return {"judged_leaves": leaves, "literal_four_ply_replays": checked,
            "initial_move_witnesses_lost": lost}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("goals", "original", "settled"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    goals, original, settled = (json.loads(file.read_text())
                                for file in (args.goals, args.original, args.settled))
    print(json.dumps(verify(goals["plans"], original["cases"], settled["cases"]),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
