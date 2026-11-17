"""Measure bounded reply-menu architectures on new opening-disjoint games."""

import argparse
import json
import logging
from pathlib import Path

import chess
import chess.engine

from c3x_030_r20_p40_value import BINARY
from c3x_030_r21_root_screen import (
    SOURCE as R21_SOURCE, excluded_prefixes, games, moves_of, select,
)
from c3x_030_s4l_r10_reply_transport import analysis, board_at, digest
from c3x_030_s4l_r11_allocation import NET, SF, single
from c3x_030_s4l_r14_matched_trace import OPTIONS

SOURCE = "b0f04b20bef85542e6c84852669a0c8e4763bf8fea86284a0f2eafc54e036cff"
R21_SCREEN = "f89dbccdfafccf0a8a4e43b8fc2842c8bdfdb66301ca43f4a7802804653a2eec"
POLICIES = ("lead_pv", "opponent_pv", "mixed")


def unique(iterable):
    return list(dict.fromkeys(iterable))


def branches(case):
    root = board_at(case["history"])
    result = [root.copy(), root.copy()]
    for board, move in zip(result, case["roots"], strict=True):
        board.push_uci(move)
    return result


def legal_leaves(boards):
    shared = set(boards[0].legal_moves) & set(boards[1].legal_moves)
    result = {}
    for move in sorted(shared, key=chess.Move.uci):
        pair = [board.copy() for board in boards]
        for board in pair:
            board.push(move)
        if not any(board.is_game_over(claim_draw=False) for board in pair):
            result[move.uci()] = pair
    return result


def signature(board, move):
    captured = chess.PAWN if board.is_en_passant(move) else (
        board.piece_type_at(move.to_square)
        if board.is_capture(move) and not board.is_castling(move) else None)
    return board.gives_check(move), captured


def make_menus(boards, common, ranked):
    lead, other = [[move for move in row if move in common] for row in ranked]
    max_length = max(map(len, (lead, other)))
    pooled = unique(move for index in range(max_length) for row in (lead, other) for move in row[index:index + 1])
    fallback = unique([*pooled, *sorted(common)])
    mixed = unique([*lead[:1], *other[:1]])
    tactics = {}
    for uci in common:
        move = chess.Move.from_uci(uci)
        a, b = (signature(board, move) for board in boards)
        if a != b:
            tactics[uci] = [a, b]
    forcing = [move for move in fallback if move in tactics and move not in mixed]
    if forcing:
        mixed.append(forcing[0])
    return {"lead_pv": unique([*lead, *fallback])[:3],
            "opponent_pv": unique([*other, *fallback])[:3],
            "mixed": unique([*mixed, *fallback])[:3]}, tactics


def nominate_replies(engine, case):
    pair = branches(case)
    common = legal_leaves(pair)
    ranked = []
    for board in pair:
        count = min(8, board.legal_moves.count())
        ranked.append(analysis(engine, board, not board.turn, nodes=12000, count=count) if count else [])
    menus, tactics = make_menus(pair, common, [[row["pv"][0] for row in reports] for reports in ranked])
    return [], {"source_nomination": ranked, "menus": menus, "forcing": tactics,
                "common": list(common), "admitted": len(common) >= 3}


def nominate(engine, source, old_pgn, old_screen, prior, initial, initial_sha):
    if digest(old_pgn) != R21_SOURCE or digest(old_screen) != R21_SCREEN:
        raise ValueError("Unexpected R21 record")
    excluded = excluded_prefixes(prior)
    old = json.loads(old_screen.read_text())
    rounds = {row["round"] for row in old["audit"]}
    excluded.update(tuple(moves_of(game)[:12]) for game in games(old_pgn)
                    if game.headers["Round"] in rounds)
    if initial is not None:
        if digest(initial) != initial_sha:
            raise ValueError("The initial R22 pilot was not sealed")
        previous = json.loads(initial.read_text())
        if previous["source_sha256"] != SOURCE or previous["cohort"] != "pilot":
            raise ValueError("Unexpected R22 pilot")
        screened = {row["round"] for row in previous["audit"]}
        excluded.update(tuple(moves_of(game)[:12]) for game in games(source)
                        if game.headers["Round"] in screened)
    result = select(engine, source, excluded, expected_sha=SOURCE, pair_cap=6,
                    reply_selector=nominate_replies, allow_bound_nomination=initial is not None)
    return {**result, "cohort": "expansion" if initial is not None else "pilot"}


def predictions(engine, cohort, nodes=12000):
    result = {}
    for case in cohort["selection"]:
        details = case["discovery"]
        if not details["admitted"]:
            continue
        leaves = legal_leaves(branches(case))
        union = sorted({m for menu in details["menus"].values() for m in menu})
        result[case["round"]] = {}
        for move in union:
            result[case["round"]][move] = [single(engine, board, board.turn, nodes=nodes)
                                          for board in leaves[move]]
    return result


def reference(engine, cohort):
    rows = {}
    for case in cohort["selection"]:
        details = case["discovery"]
        if not details["admitted"]:
            continue
        leaves = legal_leaves(branches(case))
        if list(leaves) != details["common"]:
            raise ValueError("Frozen common replies differ")
        rows[case["round"]] = {
            move: {str(depth): [single(engine, board, board.turn, depth=depth) for board in pair]
                   for depth in (12, 14)}
            for move, pair in leaves.items()
        }
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("select", "predict", "judge"))
    parser.add_argument("engine", type=Path)
    parser.add_argument("input", type=Path)
    parser.add_argument("--old-pgn", type=Path)
    parser.add_argument("--old-screen", type=Path)
    parser.add_argument("--exclude", type=Path, nargs=4)
    parser.add_argument("--cohort-sha")
    parser.add_argument("--forecast", type=Path)
    parser.add_argument("--forecast-sha")
    parser.add_argument("--net", type=Path)
    parser.add_argument("--initial", type=Path)
    parser.add_argument("--initial-sha")
    parser.add_argument("--leaf-nodes", type=int, choices=(12000, 48000), default=12000)
    parser.add_argument("--round", help="Judge only this committed round as a parallel shard")
    args = parser.parse_args()
    logging.getLogger("chess.engine").setLevel(logging.ERROR)
    if args.leaf_nodes != 12000 and args.stage != "predict":
        parser.error("--leaf-nodes applies to predict only")
    if args.round is not None and args.stage != "judge":
        parser.error("--round applies to judge only")
    if args.stage == "judge":
        if (digest(args.engine) != BINARY or not args.net or digest(args.net) != NET
                or not args.forecast or digest(args.forecast) != args.forecast_sha):
            raise ValueError("Unrecognized independent judge or forecast seal")
        options = {"Threads": 1, "Hash": 16, "EvalFile": str(args.net.resolve())}
    else:
        if digest(args.engine) != SF:
            raise ValueError("Unrecognized Stockfish source")
        options = OPTIONS
    with chess.engine.SimpleEngine.popen_uci(str(args.engine.resolve()), timeout=120) as engine:
        engine.configure(options)
        if args.stage == "select":
            result = nominate(engine, args.input, args.old_pgn, args.old_screen, args.exclude,
                              args.initial, args.initial_sha)
        else:
            if digest(args.input) != args.cohort_sha:
                raise ValueError("Unrecognized selection seal")
            cohort = json.loads(args.input.read_text())
            if cohort["source_sha256"] != SOURCE:
                raise ValueError("Unrecognized archive")
            if args.stage == "judge":
                forecast = json.loads(args.forecast.read_text())
                if forecast["cohort_sha256"] != args.cohort_sha or forecast["binary_sha256"] != SF:
                    raise ValueError("Forecast source or cohort differs")
                if args.round is not None:
                    matching = [row for row in cohort["selection"] if row["round"] == args.round]
                    if len(matching) != 1 or args.round not in forecast["rows"]:
                        raise ValueError("Unknown judged round")
                    cohort["selection"] = matching
                    forecast["rows"] = {args.round: forecast["rows"][args.round]}
            rows = (reference(engine, cohort) if args.stage == "judge"
                    else predictions(engine, cohort, args.leaf_nodes))
            result = {"cohort_sha256": args.cohort_sha, "binary_sha256": digest(args.engine), "rows": rows}
            if args.stage == "judge":
                if forecast["rows"].keys() != rows.keys():
                    raise ValueError("Forecast cohort differs")
                result.update(forecast_sha256=args.forecast_sha, net_sha256=NET)
            elif args.leaf_nodes != 12000:
                result["leaf_nodes"] = args.leaf_nodes
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
