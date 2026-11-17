"""Measure how a fixed-reply comparison relates to the full legal reply sets."""

import argparse
import json
from pathlib import Path

from c3x_030_s4l_r10_reply_transport import board_at, digest
from c3x_030_s4l_r12_explanation_score import sign


def gap(first, second):
    return None if first is None or second is None else first - second


def partition(first, second):
    shared = first.keys() & second.keys()
    deltas = {move: gap(first[move], second[move]) for move in sorted(shared)}
    counts = {str(direction): 0 for direction in (-1, 0, 1)}
    for delta in deltas.values():
        if delta is not None:
            counts[str(sign(delta))] += 1
    extrema = []
    for points, common in ((first, shared), (second, shared)):
        minimum = min(points.values()) if points and None not in points.values() else None
        reduced = [points[reply] for reply in common]
        common_min = min(reduced) if reduced and None not in reduced else None
        extrema.append({"minimum": minimum, "shared_minimum": common_min,
                        "minimizers": sorted(reply for reply, value in points.items()
                                             if minimum is not None and value == minimum),
                        "legal_replies": len(points), "exclusive_replies": len(points) - len(common)})
    left, right = extrema
    return {"full_gap": gap(left["minimum"], right["minimum"]),
            "shared_minima_gap": gap(left["shared_minimum"], right["shared_minimum"]),
            "reply_deltas": deltas, "directions": counts, "roots": extrema}


def read_points(after, replies, depth):
    if replies.keys() != {move.uci() for move in after.legal_moves}:
        raise ValueError("Judged replies differ from legal replies")
    values = {}
    for reply, record in replies.items():
        point = record["point"]
        if point is None or point["bound"]:
            values[reply] = None
            continue
        if point["depth"] == 0:
            leaf = after.copy()
            leaf.push_uci(reply)
            valid = (point["nodes"] == 0 and not point["pv"] and
                     leaf.is_game_over(claim_draw=False))
        else:
            valid = point["depth"] == depth
        values[reply] = point["ordered"] if valid else None
    return values


def audit(cohort, judgment):
    cases = {case["round"]: case for case in cohort["selection"]}
    judgments = {row["round"]: row["roots"] for row in judgment["rows"]}
    if (cases.keys() != judgments.keys() or len(cases) != len(cohort["selection"]) or
            len(judgments) != len(judgment["rows"])):
        raise ValueError("Cohort and judge round identities differ")
    depth = judgment["depth"]
    if type(depth) is not int or depth < 1:
        raise ValueError("Expected positive judge depth")
    rows = {}
    for round_id, case in cases.items():
        roots = case["roots"]
        root_replies = judgments[round_id]
        if len(roots) != 2 or set(roots) != root_replies.keys():
            raise ValueError("Candidate identities differ")
        if "0000" in (*case["history"], *roots):
            raise ValueError("Null moves are not legal game moves")
        board = board_at(case["history"])
        points = []
        for root in roots:
            after = board.copy()
            after.push_uci(root)
            points.append(read_points(after, root_replies[root], depth))
        rows[round_id] = {"ordered_candidates": roots, **partition(*points)}
    return {"depth": depth, "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cohort", type=Path)
    parser.add_argument("judge", type=Path)
    args = parser.parse_args()
    cohort, judgment = (json.loads(path.read_text()) for path in (args.cohort, args.judge))
    if judgment["cohort_sha256"] != digest(args.cohort):
        raise ValueError("Judge cohort hash mismatch")
    print(json.dumps(audit(cohort, judgment), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
