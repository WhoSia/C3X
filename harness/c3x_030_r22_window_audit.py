"""Recover procedural finite bounds from complete nominal-depth root attempts."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

import chess

from c3x_030_s4l_r10_reply_transport import digest
from c3x_030_s4l_r14_matched_trace import positions
from c3x_030_s4l_r14_trace_projection import ORDINARY_LIMIT, complete_root_events, ordinary_cp

COHORT = "f89dbccdfafccf0a8a4e43b8fc2842c8bdfdb66301ca43f4a7802804653a2eec"
TRACE = "6e7a9441a9ac4120c30e0ccc0cb3f4129f6a1e80a46322866ade2cf316e332e6"


def encode(board, move):
    target = move.to_square
    flags = 0
    if board.is_castling(move):
        target = chess.square(7 if board.is_kingside_castling(move) else 0,
                              chess.square_rank(move.from_square))
        flags = 3 << 14
    elif board.is_en_passant(move):
        flags = 2 << 14
    elif move.promotion is not None:
        flags = (1 << 14) | ((move.promotion - chess.KNIGHT) << 12)
    return flags | (move.from_square << 6) | target


def attempt(rows, legal):
    depths = {r["iteration"] for r in rows}
    if len(depths) != 1 or any(r["depth"] != r["iteration"] for r in rows):
        return None, "effective_depth"
    alpha, beta = rows[0]["alpha"], rows[0]["beta"]
    if not -ORDINARY_LIMIT < alpha < beta < ORDINARY_LIMIT:
        return None, "nonordinary_window"
    if any((r["alpha"], r["beta"]) != (alpha, beta) for r in rows):
        return None, "mutable_window"
    moves = [r["root_move_raw"] for r in rows]
    if (len(moves) != len(set(moves)) or not set(moves) <= legal
            or [r["move_count"] for r in rows] != list(range(1, len(rows) + 1))):
        return None, "invalid_move_coverage"
    if any(r["value"] >= beta for r in rows[:-1]):
        return None, "continued_after_cutoff"
    if rows[-1]["value"] >= beta:
        return ("lower", ordinary_cp(beta)), "lower"
    if set(moves) == legal and all(r["value"] <= alpha for r in rows):
        return ("upper", ordinary_cp(alpha)), "upper"
    return None, "no_certifiable_threshold"


def public_interval(report):
    if report is None or report["cp"] is None:
        return None, None
    return (None if report["upper"] else report["cp"],
            None if report["lower"] else report["cp"])


def classify(bound, interval):
    direction, cp = bound
    lower, upper = interval
    if direction == "lower":
        if upper is not None and cp > upper:
            return "conflict"
        if lower is None:
            return "new_direction"
        return "stronger" if cp > lower else "weaker" if cp < lower else "equal"
    if lower is not None and cp < lower:
        return "conflict"
    if upper is None:
        return "new_direction"
    return "stronger" if cp < upper else "weaker" if cp > upper else "equal"


def inspect(board, leaf):
    events, status = complete_root_events(leaf["stderr"])
    if events is None:
        return {"status": status, "counts": {}, "source": [], "public": {}}
    legal = {encode(board, move) for move in board.legal_moves}
    by_call = defaultdict(list)
    for row in events:
        by_call[row["root_id"]].append(row)
    public = {row["depth"]: public_interval(row) for row in leaf["reports"]}
    source, counts = [], Counter()
    for call, rows in by_call.items():
        bound, reason = attempt(rows, legal)
        counts[reason] += 1
        if bound is not None:
            depth = rows[0]["iteration"]
            known = public.get(depth, (None, None))
            source.append({"attempt_id": call, "depth": depth, "threshold": bound,
                           "public_interval": known, "comparison": classify(bound, known)})
    return {"status": status, "counts": dict(counts), "source": source, "public": public}


def order(intervals):
    (la, ua), (lb, ub) = intervals
    if la is not None and ub is not None and la > ub:
        return 1
    if lb is not None and ua is not None and lb > ua:
        return -1
    return None


def pair_diagnostic(arms):
    depths = sorted({d for arm in arms for d in arm["public"]}
                    | {row["depth"] for arm in arms for row in arm["source"]})
    rows = []
    for depth in depths:
        public = [arm["public"].get(depth, (None, None)) for arm in arms]
        added = list(public)
        for side, arm in enumerate(arms):
            latest = next((r for r in reversed(arm["source"]) if r["depth"] == depth), None)
            if latest and latest["comparison"] in ("new_direction", "stronger"):
                direct, cp = latest["threshold"]
                lower, upper = added[side]
                added[side] = (cp, upper) if direct == "lower" else (lower, cp)
        rows.append({"depth": depth, "public_rank": order(public), "plus_source_rank": order(added)})
    return rows


def evaluate(cohort, forecast):
    rows = {}
    findings = Counter()
    for key, question in cohort["questions"].items():
        pair = list(positions(question))
        if not all(board.turn == mover for board, mover in pair):
            raise ValueError("Native/source score perspective mismatch")
        arms = [inspect(board, leaf) for (board, _), leaf in zip(pair, forecast["rows"][key]["leaves"], strict=True)]
        for arm in arms:
            findings.update(arm["counts"])
            findings.update("public_" + row["comparison"] for row in arm["source"])
        rank = pair_diagnostic(arms)
        findings["rank_depths"] += len(rank)
        findings["public_rank"] += sum(r["public_rank"] is not None for r in rank)
        findings["extra_ordered_rank"] += sum(r["public_rank"] is None and r["plus_source_rank"] is not None for r in rank)
        rows[key] = {"round": question["round"], "reply": question["reply"], "arms": arms, "rank": rank}
    return {"counts": dict(findings), "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cohort", type=Path)
    parser.add_argument("forecast", type=Path)
    args = parser.parse_args()
    if tuple(map(digest, (args.cohort, args.forecast))) != (COHORT, TRACE):
        raise ValueError("Unexpected archived source")
    result = evaluate(json.loads(args.cohort.read_text()), json.loads(args.forecast.read_text()))
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
