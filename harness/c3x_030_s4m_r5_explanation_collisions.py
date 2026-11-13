"""Measure how often promotion explanations merge outcome-changing legal alternatives."""
import argparse
from collections import Counter, defaultdict
import hashlib
from itertools import combinations
import json
from pathlib import Path
import random

import chess
import chess.syzygy

from c3x_030_s4m_r3_kpkp import CASES
from c3x_030_s4m_r4_reply_contrast import TABLES

SEED = 301305
STRESS_SEED = 301306
PARENT_COUNT = 256
FEATURE_SETS = {
    "check": ("check",),
    "check_capture": ("check", "queen_capturable"),
    "check_capture_tempo": ("check", "queen_capturable", "black_pawn_pushes"),
    "check_capture_tempo_geometry": (
        "check", "queen_capturable", "black_pawn_pushes",
        "black_king_to_pawn", "white_king_to_pawn",
    ),
}

FEATURE_SETS["check_capture_tempo_geometry_counterplay"] = (
    *FEATURE_SETS["check_capture_tempo_geometry"],
    "black_can_promote_now", "white_attacks_black_promotion_square",
)


def generate_parents(seed, pawn_ranks, excluded):
    """Select parents using board geometry and legality before probing any WDL."""
    rng = random.Random(seed)
    excluded = set(excluded)
    for fen, candidate in CASES.values():
        board = chess.Board(fen)
        board.push_san(candidate)
        for orientation in (board, board.mirror()):
            for variant in (orientation, orientation.transform(chess.flip_horizontal)):
                excluded.add(variant.epd())
    parents = {}
    for _ in range(30_000):
        wk, bk = rng.sample(range(64), 2)
        wp = chess.square(rng.randrange(8), 6)
        bp = chess.square(rng.randrange(8), rng.choice(pawn_ranks))
        if len({wk, bk, wp, bp}) < 4:
            continue
        board = chess.Board.empty()
        for square, piece in (
            (wk, chess.Piece(chess.KING, chess.WHITE)),
            (bk, chess.Piece(chess.KING, chess.BLACK)),
            (wp, chess.Piece(chess.PAWN, chess.WHITE)),
            (bp, chess.Piece(chess.PAWN, chess.BLACK)),
        ):
            board.set_piece_at(square, piece)
        board.turn = chess.BLACK
        if board.epd() in excluded or not board.is_valid() or board.is_check():
            continue
        promotion = chess.Move(wp, wp + 8, promotion=chess.QUEEN)
        eligible = []
        for reply in sorted(board.legal_moves, key=chess.Move.uci):
            board.push(reply)
            if board.pieces(chess.PAWN, chess.BLACK) and promotion in board.legal_moves:
                eligible.append(reply)
            board.pop()
        if len(eligible) < 2:
            continue
        parents[board.epd()] = (board.fen(), eligible, promotion)
        excluded.update((board.epd(), board.transform(chess.flip_horizontal).epd()))
        if len(parents) == PARENT_COUNT:
            return list(parents.values())
    raise RuntimeError("Could not generate the requested legal parent cohort")


def probe_replies(tablebase, fen, replies, promotion):
    board = chess.Board(fen)
    rows = []
    for reply in replies:
        reply_san = board.san(reply)
        board.push(reply)
        promotion_san = board.san(promotion)
        board.push(promotion)
        pawn, = board.pieces(chess.PAWN, chess.BLACK)
        defenses = list(board.legal_moves)
        black_promotion_square = chess.square(chess.square_file(pawn), 0)
        rows.append({
            "reply": reply_san,
            "promotion": promotion_san,
            "white_wdl": -tablebase.probe_wdl(board),
            "check": board.is_check(),
            "queen_capturable": any(
                move.to_square == promotion.to_square for move in defenses
            ),
            "black_can_promote_now": any(move.promotion for move in defenses),
            "white_attacks_black_promotion_square": board.is_attacked_by(chess.WHITE, black_promotion_square),
            "black_pawn_pushes": chess.square_rank(pawn),
            "black_king_to_pawn": chess.square_distance(board.king(chess.BLACK), pawn),
            "white_king_to_pawn": chess.square_distance(board.king(chess.WHITE), pawn),
        })
        board.pop()
        board.pop()
    return rows


def score(cases, features):
    pair_counts = Counter({"outcome_pairs": 0, "collision_pairs": 0})
    pure_rows = 0
    examples = []
    for case in cases:
        buckets = defaultdict(list)
        rows = case["replies"]
        for row in rows:
            buckets[tuple(row[key] for key in features)].append(row["white_wdl"])
        pure_rows += sum(len(values) for values in buckets.values() if len(set(values)) == 1)
        for first, second in combinations(rows, 2):
            if first["white_wdl"] == second["white_wdl"]:
                continue
            pair_counts["outcome_pairs"] += 1
            if all(first[key] == second[key] for key in features):
                pair_counts["collision_pairs"] += 1
                if len(examples) < 5:
                    examples.append({"fen": case["fen"], "pair": [first, second]})
    return {**pair_counts, "rows_in_pure_buckets": pure_rows, "examples": examples}


def audit_cohort(tablebase, parents, seed, pawn_ranks):
    cases = [
        {"fen": fen, "replies": probe_replies(tablebase, fen, replies, promotion)}
        for fen, replies, promotion in parents
    ]
    totals = {name: score(cases, features) for name, features in FEATURE_SETS.items()}
    collisions = [counts["collision_pairs"] for counts in totals.values()]
    if collisions != sorted(collisions, reverse=True):
        raise ValueError("Nested feature sets unexpectedly added collisions")
    return {
        "seed": seed, "parent_count": len(cases), "black_pawn_rank_indices": pawn_ranks,
        "summary": totals, "cases": cases,
        "reply_count": sum(len(case["replies"]) for case in cases),
        "mixed_parent_count": sum(len({row["white_wdl"] for row in case["replies"]}) > 1 for case in cases),
    }


def replay_geometry_counterexample(tablebase):
    fen = "8/P7/8/8/1k3K2/8/p7/8 b - - 0 1"
    branches = {}
    for reply in ("Kc3", "Kc4"):
        board = chess.Board(fen)
        board.push_san(reply)
        board.push_san("a8=Q")
        defenses = {}
        for move in sorted(board.legal_moves, key=chess.Move.uci):
            san = board.san(move)
            board.push(move)
            defenses[san] = tablebase.probe_wdl(board)
            board.pop()
        branches[reply] = defenses
    if {san for san, wdl in branches["Kc3"].items() if wdl != 2} != {"Kb2"}:
        raise ValueError("Unexpected defense after Kc3")
    if branches["Kc3"]["Kb2"] != 0 or set(branches["Kc4"].values()) != {2}:
        raise ValueError("Unexpected WDL in the matched counterexample")
    return {"fen": fen, "white_promotion": "a8=Q", "white_wdl_by_black_defense": branches}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tables", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    for name, expected in TABLES.items():
        if hashlib.sha256((args.tables / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Table SHA-256 mismatch: {name}")
    standard = generate_parents(SEED, (3, 4, 5), set())
    excluded = {chess.Board(fen).epd() for fen, _, _ in standard}
    excluded.update(chess.Board(fen).transform(chess.flip_horizontal).epd() for fen, _, _ in standard)
    stress = generate_parents(STRESS_SEED, (1, 2), excluded)
    with chess.syzygy.open_tablebase(str(args.tables)) as tablebase:
        report = {
            "tables_sha256": TABLES,
            "feature_sets": FEATURE_SETS,
            "posthoc_geometry_counterexample": replay_geometry_counterexample(tablebase),
            "cohorts": {
                name: audit_cohort(tablebase, parents, seed, ranks)
                for name, parents, seed, ranks in (
                    ("standard", standard, SEED, (3, 4, 5)),
                    ("advanced_black_pawn", stress, STRESS_SEED, (1, 2)),
                )
            },
        }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for name, cohort in report["cohorts"].items():
        print(name, cohort["parent_count"], cohort["reply_count"], cohort["mixed_parent_count"])
        for features, counts in cohort["summary"].items():
            print(features, {key: value for key, value in counts.items() if key != "examples"})


if __name__ == "__main__":
    main()
