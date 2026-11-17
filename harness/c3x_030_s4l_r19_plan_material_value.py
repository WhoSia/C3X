"""Compare bounded material value, first-move support and forced plan value."""

import argparse
import json
from pathlib import Path

import chess

from c3x_030_s4l_r10_reply_transport import digest
from c3x_030_s4l_r16_plan_oracle import VALUES, balance, target_after
from c3x_030_s4l_r16_plan_source import post_reply, root_boards


GOALS = "745645505b89849b54ace84a30491b3f0af0ef632801a436990ca230d6632da0"


def terminal_value(board, target, mover, baseline):
    value = balance(board, mover) - baseline
    return value, value if target is None and value >= 0 else None


def last_defense_value(board, mover):
    """Exact material after one adverse reply or the current terminal board."""
    starting = balance(board, mover)
    losses = [0]
    for move in board.generate_legal_captures():
        taken = chess.PAWN if board.is_en_passant(move) else board.piece_type_at(move.to_square)
        promotion = VALUES[move.promotion] - 1 if move.promotion else 0
        losses.append(VALUES[taken] + promotion)
    pawns = board.pieces_mask(chess.PAWN, board.turn)
    promotion_sources = chess.BB_RANK_7 if board.turn == chess.WHITE else chess.BB_RANK_2
    if any(move.promotion == chess.QUEEN for move in
           board.generate_legal_moves(from_mask=pawns & promotion_sources)):
        losses.append(VALUES[chess.QUEEN] - 1)
    loss = max(losses)
    if loss and board.is_game_over(claim_draw=False):
        return starting
    return starting - loss


def own_continuation(board, target, mover, baseline):
    if board.is_game_over(claim_draw=False):
        return terminal_value(board, target, mover, baseline)
    values, plan = [], []
    for move in list(board.legal_moves):
        landed = target_after(board, move, target)
        board.push(move)
        result = last_defense_value(board, mover) - baseline
        board.pop()
        values.append(result)
        if landed is None and result >= 0:
            plan.append(result)
    return max(values), max(plan) if plan else None


def defense_frontier(board, target, mover, baseline):
    if board.is_game_over(claim_draw=False):
        return terminal_value(board, target, mover, baseline)
    values, plan = [], []
    for reply in list(board.legal_moves):
        surviving = target_after(board, reply, target)
        board.push(reply)
        unrestricted, constrained = own_continuation(board, surviving, mover, baseline)
        board.pop()
        values.append(unrestricted)
        plan.append(constrained)
    return min(values), min(plan) if all(value is not None for value in plan) else None


def values_for_first_moves(board, target):
    mover = board.turn
    baseline = balance(board, mover)
    values = {}
    for first in sorted(board.legal_moves, key=chess.Move.uci):
        victim = target_after(board, first, target)
        board.push(first)
        open_value, plan_value = defense_frontier(board, victim, mover, baseline)
        board.pop()
        values[first.uci()] = {"open": open_value, "constrained": plan_value}
    return values


def compare(values, expected):
    viable = {move for move, value in values.items() if value["constrained"] is not None}
    if viable != set(expected):
        raise ValueError("Value recursion and R17 witness support disagree")
    top = max(v["open"] for v in values.values())
    best = [m for m, v in values.items() if v["open"] == top]
    if not viable:
        return {"V": top, "F": None, "G": None, "best": best}
    first_only = max(values[m]["open"] for m in viable)
    plan = max(values[m]["constrained"] for m in viable)
    if not top >= first_only >= plan:
        raise ValueError("Restricting continuations cannot increase value")
    return {"V": top, "F": first_only, "G": plan, "best": best,
            "every_best_admits": set(best) <= viable}


def run(goals, old):
    rows, unavailable = [], 0
    for g in goals["plans"]:
        boards = root_boards(g)
        victim = chess.parse_square(g["target"])
        for reply in g["replies"]:
            settled = old["cases"][g["round"]][reply]
            for root, branch, outcome in zip(g["roots"], boards, settled, strict=True):
                if outcome["status"] != "judged":
                    raise ValueError("Expected the 64 judged R17 leaves")
                if not outcome["truth"]:
                    unavailable += 1
                    continue
                board, target = post_reply(branch, reply, victim)
                values = values_for_first_moves(board, target)
                rows.append({"round": g["round"], "reply": reply, "root": root,
                             "target": g["target"], "values": values,
                             **compare(values, outcome["truth"])})
    return {"unavailable": unavailable, "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("goals", type=Path)
    parser.add_argument("settled", type=Path)
    parser.add_argument("settled_sha256")
    args = parser.parse_args()
    if digest(args.goals) != GOALS or digest(args.settled) != args.settled_sha256:
        parser.error("Expected sealed R17 goal and outcome files")
    goals, settled = (json.loads(p.read_text()) for p in (args.goals, args.settled))
    print(json.dumps(run(goals, settled), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
