"""Evaluate legal defense ordering at a fixed tablebase query budget."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path

import chess
import chess.syzygy

from c3x_030_s4m_r5_explanation_collisions import (
    FEATURE_SETS, TABLES, generate_parents, probe_replies,
)

TABLE_HASHES = {
    **TABLES,
    "KBvK.rtbw": "bc0d8ab3560de9038460f0e8f61e3b7efd3e3d0327d19ae0387c0da7ddeb244d",
    "KNvK.rtbw": "9d3518b12df3d2006441df758bce31e961346e70a11920aaad75c647003bb6e7",
    "KQvKB.rtbw": "0c18bbcaec0e7c161d56392ff57a39258dd93acd0321e3bbb32f7c05636abeac",
    "KQvKN.rtbw": "ba07bd47c6eaa20904b595f43e171c6fc70fcc056cb33696fe12ed254c546100",
    "KQvKQ.rtbw": "571a85d86e635e48567997ea648fd1e90dde39c9b413b2fe968f5e7faeacfbb0",
    "KQvKR.rtbw": "8cdbe3c8e098037875de5854c656f8afeadb8327c85b5b7b1cac81719afd3e2c",
    "KRvK.rtbw": "37f8601644113dc83be9822913d6ecf75e5c8b7eeb11b7689c38a3ff986d2a48",
}

R5_SHA = "72412de28a0ecc89b08a846fb9575b0d1063b3efd4bcc3b7d5d8d707f0161282"
COHORTS = {
    "ranks_4_to_6": (301607, (3, 4, 5)),
    "ranks_2_to_3": (301608, (1, 2)),
    "recheck_ranks_4_to_6": (301617, (3, 4, 5)),
    "recheck_ranks_2_to_3": (301618, (1, 2)),
}
BUDGETS = (1, 2, 3)
METHODS = (
    "uniform", "pawn_first", "king_support_first",
    "pawn_first_queen_first", "pawn_then_king",
)


def read_r5(path):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != R5_SHA:
        raise ValueError("R5 archive SHA-256 mismatch")
    report = json.loads(raw)
    excluded = set()
    audit = {}
    for name, cohort in report["cohorts"].items():
        counts = Counter()
        for case in cohort["cases"]:
            board = chess.Board(case["fen"])
            excluded.update((board.epd(), board.transform(chess.flip_horizontal).epd()))
            for left, right in combinations(case["replies"], 2):
                if left["white_wdl"] != right["white_wdl"]:
                    counts["outcome_pairs"] += 1
                    counts["rich_feature_collisions"] += all(
                        left[key] == right[key]
                        for key in FEATURE_SETS["check_capture_tempo_geometry_counterplay"]
                    )
        archived = cohort["summary"]["check_capture_tempo_geometry_counterplay"]
        if (counts["outcome_pairs"], counts["rich_feature_collisions"]) != (
            archived["outcome_pairs"], archived["collision_pairs"]
        ):
            raise ValueError("R5 archived pair counts failed independent recount")
        audit[name] = dict(counts)
    return excluded, audit


def orders(board, moves):
    pawn, = board.pieces(chess.PAWN, chess.BLACK)
    king = board.king(chess.BLACK)
    promotion_square = chess.square(chess.square_file(pawn), 0)

    def priority(move, king_first):
        support = move.from_square == king and chess.square_distance(move.to_square, pawn) <= 1
        return (
            not board.is_capture(move),
            not support if king_first else move.from_square != pawn,
            chess.square_distance(move.to_square, promotion_square)
            if move.from_square == king else 8,
            move.uci(),
        )

    pawn_first = sorted(moves, key=lambda move: priority(move, False))
    queen_first = sorted(
        moves,
        key=lambda move: (*priority(move, False)[:-1],
                          move.promotion not in (None, chess.QUEEN), move.uci()),
    )
    diversified = queen_first.copy()
    if diversified[0].from_square == pawn:
        king_move = next((move for move in diversified if move.from_square == king), None)
        if king_move is not None:
            diversified.remove(king_move)
            diversified.insert(1, king_move)
    return {
        "pawn_first": pawn_first,
        "king_support_first": sorted(moves, key=lambda move: priority(move, True)),
        "pawn_first_queen_first": queen_first,
        "pawn_then_king": diversified,
    }


def probe_defenses(tablebase, board, root_wdl):
    moves = list(board.legal_moves)
    if not moves:
        if board.is_checkmate() and root_wdl == 2:
            terminal = "checkmate"
        elif board.is_stalemate() and root_wdl == 0:
            terminal = "stalemate"
        else:
            raise ValueError("Unexpected terminal after promotion")
        return {"terminal": terminal, "defenses": [], "orders": {}}
    ranked = orders(board, moves)
    if any(len(order) != len(moves) or set(order) != set(moves) for order in ranked.values()):
        raise ValueError("An ordering dropped or duplicated legal moves")
    defenses = []
    for move in sorted(moves, key=chess.Move.uci):
        san = board.san(move)
        board.push(move)
        wdl = tablebase.probe_wdl(board)
        board.pop()
        defenses.append({"uci": move.uci(), "san": san, "white_wdl": wdl})
    if min(row["white_wdl"] for row in defenses) != root_wdl:
        raise ValueError(f"Syzygy WDL mismatch across legal defenses: {board.fen()}")
    return {
        "terminal": None,
        "defenses": defenses,
        "orders": {name: [move.uci() for move in moves] for name, moves in ranked.items()},
    }


def evaluate(rows):
    """Expected hits for uniform draws, exact hits for the two fixed orderings."""
    hits = {method: {budget: Fraction() for budget in BUDGETS} for method in METHODS}
    for row in rows:
        n = len(row["defenses"])
        witnesses = {d["uci"] for d in row["defenses"] if d["white_wdl"] <= 0}
        if not witnesses:
            raise ValueError("A nonwinning White position must offer a defense")
        for budget in BUDGETS:
            k = min(budget, n)
            hits["uniform"][budget] += 1 - Fraction(comb(n - len(witnesses), k), comb(n, k))
            for method, order in row["orders"].items():
                hits[method][budget] += bool(witnesses.intersection(order[:k]))
    return {
        "positions": len(rows),
        "hits": {method: {budget: round(float(count), 6) for budget, count in counts.items()}
                 for method, counts in hits.items()},
    }


def ordering_diagnostic(targets):
    """Attribute first hits at budget three in the original pawn ordering."""
    hits_at_three = Counter()
    for row in targets:
        values = {move["uci"]: move["white_wdl"] for move in row["defenses"]}
        prefix = row["orders"]["pawn_first"][:3]
        if len(prefix) == 3 and all(values[m] > 0 for m in prefix[:2]) and values[prefix[2]] <= 0:
            hits_at_three[" / ".join(move[-1] for move in prefix)] += 1
    return dict(hits_at_three)


def audit_cohort(tablebase, parents, seed, ranks):
    cases = []
    for fen, replies, promotion in parents:
        rows = probe_replies(tablebase, fen, replies, promotion)
        board = chess.Board(fen)
        for move, row in zip(replies, rows, strict=True):
            board.push(move)
            board.push(promotion)
            row.update(probe_defenses(tablebase, board, row["white_wdl"]))
            board.pop()
            board.pop()
        cases.append({"fen": fen, "replies": rows})
    rows = [row for case in cases for row in case["replies"]]
    targets = [row for row in rows if row["defenses"] and row["white_wdl"] <= 0]
    unique = [row for row in targets if sum(d["white_wdl"] <= 0 for d in row["defenses"]) == 1]
    return {
        "seed": seed, "black_pawn_rank_indices": ranks, "parents": len(cases),
        "promotion_positions": len(rows), "terminals": dict(Counter(r["terminal"] for r in rows if r["terminal"])),
        "child_probes": sum(len(r["defenses"]) for r in rows),
        "outcome_counts": dict(Counter(r["white_wdl"] for r in rows)),
        "all_witness_targets": evaluate(targets),
        "unique_witness_targets": evaluate(unique),
        "first_pawn_order_hits_at_budget_3": ordering_diagnostic(targets),
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r5", required=True, type=Path)
    parser.add_argument("--tables", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    excluded, recount = read_r5(args.r5)
    with chess.syzygy.Tablebase() as tablebase:
        for name, digest in TABLE_HASHES.items():
            if hashlib.sha256((args.tables / name).read_bytes()).hexdigest() != digest:
                raise ValueError(f"Table SHA-256 mismatch: {name}")
            tablebase.add_file(str(args.tables / name))
        cohorts = {}
        for name, (seed, ranks) in COHORTS.items():
            parents = generate_parents(seed, ranks, excluded)
            for fen, _, _ in parents:
                board = chess.Board(fen)
                excluded.update((board.epd(), board.transform(chess.flip_horizontal).epd()))
            cohorts[name] = audit_cohort(tablebase, parents, seed, ranks)
    report = {"r5_sha256": R5_SHA, "r5_recount": recount,
              "tables_sha256": TABLE_HASHES, "cohorts": cohorts,
              "posthoc_policies": ["pawn_first_queen_first", "pawn_then_king"]}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for name, cohort in cohorts.items():
        print(name, {key: value for key, value in cohort.items() if key != "cases"})


if __name__ == "__main__":
    main()
