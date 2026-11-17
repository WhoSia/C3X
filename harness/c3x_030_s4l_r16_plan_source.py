"""Freeze named goals, common replies and equal-slot public and trace menus."""

import argparse
import json
import logging
from pathlib import Path

import chess.engine

from c3x_030_s4l_r10_reply_transport import analysis, board_at, digest, selection
from c3x_030_s4l_r11_allocation import SF
from c3x_030_s4l_r14_matched_trace import OPTIONS, leaf_forecast
from c3x_030_s4l_r14_trace_projection import ORDINARY_LIMIT, complete_root_events
from c3x_030_s4l_r16_plan_oracle import TARGETS, target_after


PGN = "60524a292b71ee2b4711e01ce22623a86e58483cc096aaa4f5c6e7584179e853"
R14 = "59f4a9e2c4de583105a9d4051cb1e0b2d7d73a03bc69871cd3edd96a9c2fa38a"
SLOTS = 3


def root_boards(case):
    base = board_at(case["history"])
    boards = []
    for uci in case["roots"]:
        branch = base.copy()
        branch.push_uci(uci)
        boards.append(branch)
    return boards


def named_victim(first, second, line):
    tracked = {square: square for square, piece in first.piece_map().items()
               if piece.color == first.turn and piece.piece_type in TARGETS
               and second.piece_at(square) == piece}
    board = first.copy()
    for uci in line[:4]:
        move = board.parse_uci(uci)
        for origin, position in sorted(tracked.items()):
            updated = target_after(board, move, position)
            if updated is None:
                return origin
            tracked[origin] = updated
        board.push(move)
    return None


def nominate(engine_path, source, parent):
    if digest(source) != PGN or digest(parent) != R14:
        raise ValueError("Expected pinned Entrance League and R14 files")
    parent_cases = json.loads(parent.read_text())["cohort"]["selection"]
    excluded = [tuple(case["history"][:12]) for case in parent_cases]
    goals = []
    with chess.engine.SimpleEngine.popen_uci(str(engine_path.resolve()), timeout=45) as engine:
        engine.configure(OPTIONS)
        cohort = selection(engine, source, excluded_openings=excluded, expected_sha=PGN, count=24)
        for case in cohort["selection"]:
            first, second = root_boards(case)
            common = {m.uci() for m in first.legal_moves} & {m.uci() for m in second.legal_moves}
            if len(common) < 2:
                continue
            lines = analysis(engine, first, not first.turn, nodes=12000, count=3)
            shared = [row["pv"] for row in lines if row["pv"][0] in common]
            for line in shared:
                victim = named_victim(first, second, line)
                if victim is None:
                    continue
                replies = list(dict.fromkeys([line[0], *(pv[0] for pv in shared), *sorted(common)]))[:4]
                goals.append({**case, "target": chess.square_name(victim),
                              "target_piece": first.piece_at(victim).symbol(), "replies": replies,
                              "nominal_pv": line, "source_lines": lines})
                break
            if len(goals) == 8:
                break
    return {"cohort": cohort, "plans": goals}


def decode(board, raw):
    flag = raw >> 14
    move = chess.Move((raw >> 6) & 63, raw & 63, promotion=2 + ((raw >> 12) & 3) if flag == 1 else None)
    return board.parse_uci(move.uci()).uci()


def menus(board, target, observation):
    captures = sorted(move.uci() for move in board.generate_legal_captures(to_mask=chess.BB_SQUARES[target]))
    reports = list(reversed(observation["public_reports"]))
    leaders = [row["pv"][0] for row in reports]
    exact = [row["pv"][0] for row in reports if row["cp"] is not None and not row["bound"]]
    public = list(dict.fromkeys(captures + exact + sorted(m.uci() for m in board.legal_moves)))[:SLOTS]
    augmented = public.copy()
    events, status = complete_root_events(observation["stderr"])
    witness = None
    if events and public and public[-1] not in captures:
        for event in sorted(events, key=lambda e: (e["iteration"], e["ordinal"]), reverse=True):
            if (event["will_update_root_pv"] != 1 or event["move_count"] <= 1
                    or abs(event["value"]) >= ORDINARY_LIMIT or event["value"] <= event["alpha"]):
                continue
            move = decode(board, event["root_move_raw"])
            if move not in public and move not in leaders:
                augmented[-1] = move
                witness = {"move": move, "event": event}
                break
    return {"public": public, "augmented": augmented, "substitution": witness, "epoch_status": status}


def post_reply(branch, reply, target):
    board = branch.copy()
    move = board.parse_uci(reply)
    after = target_after(board, move, target)
    board.push(move)
    if after is None or board.piece_at(after) is None:
        raise ValueError("Enemy reply must retain its own named victim")
    return board, after


def freeze_menus(path, goals_file):
    goals = json.loads(goals_file.read_text())["plans"]
    receipts = {}
    for case in goals:
        boards = root_boards(case)
        origin = chess.parse_square(case["target"])
        rows = {}
        for reply in case["replies"]:
            sides = []
            for branch in boards:
                leaf, target = post_reply(branch, reply, origin)
                if leaf.is_game_over(claim_draw=False):
                    sides.append({"status": "terminal_leaf"})
                    continue
                try:
                    observation = leaf_forecast(path, leaf, leaf.turn)
                except ValueError as error:
                    if str(error) != "No legal leaf receipt":
                        raise
                    sides.append({"status": "missing_source_receipt"})
                    continue
                sides.append({"status": "ready", "target_after_reply": chess.square_name(target),
                              "menus": menus(leaf, target, observation), "source": observation})
            rows[reply] = sides
        receipts[case["round"]] = rows
    return {"engine_sha256": digest(path), "goals_sha256": digest(goals_file), "rows": receipts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="stage", required=True)
    nominate_parser = subparsers.add_parser("nominate")
    nominate_parser.add_argument("engine", type=Path)
    nominate_parser.add_argument("source", type=Path)
    nominate_parser.add_argument("parent", type=Path)
    freeze_parser = subparsers.add_parser("freeze")
    freeze_parser.add_argument("engine", type=Path)
    freeze_parser.add_argument("goals", type=Path)
    args = parser.parse_args()
    logging.getLogger("chess.engine").setLevel(logging.ERROR)
    if digest(args.engine) != SF:
        parser.error("Expected the pinned R4 Stockfish")
    result = (nominate(args.engine, args.source, args.parent) if args.stage == "nominate"
              else freeze_menus(args.engine, args.goals))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
