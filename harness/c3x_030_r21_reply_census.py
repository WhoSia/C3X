"""Enumerate and independently judge the complete common-reply set of round 1.2."""

import argparse
from collections import Counter
import json
from pathlib import Path

import chess.engine

from c3x_030_r20_p40_value import BINARY
from c3x_030_s4l_r10_reply_transport import board_at, digest
from c3x_030_s4l_r11_allocation import NET, single
from c3x_030_s4l_r14_trace_score import judge_sign

DEPTHS = (12, 14)


def legal_overlap(selection):
    case = next(row for row in selection["selection"] if row["round"] == "1.2")
    board = board_at(case["history"])
    branches = [board.copy(), board.copy()]
    for branch, move in zip(branches, case["roots"], strict=True):
        branch.push_uci(move)
    menus = [{move.uci() for move in branch.legal_moves} for branch in branches]
    omitted, active = [], {}
    for reply in sorted(menus[0] & menus[1]):
        leaves = [branch.copy() for branch in branches]
        for leaf in leaves:
            leaf.push_uci(reply)
        if any(leaf.is_game_over(claim_draw=False) for leaf in leaves):
            omitted.append(reply)
        else:
            active[reply] = leaves
    return {"roots": case["roots"], "root_fen": board.fen(), "selected": case["replies"],
            "legal_counts": [len(menu) for menu in menus], "omitted_terminal": omitted,
            "common_nonterminal": list(active)}, active


def evaluate(engine, active):
    output = {}
    for reply, leaves in active.items():
        output[reply] = {str(depth): [single(engine, leaf, leaf.turn, depth=depth) for leaf in leaves]
                         for depth in DEPTHS}
    return output


def summarize(rows):
    labels = {}
    minima = {}
    for depth in DEPTHS:
        values = [result[str(depth)] for result in rows.values()]
        labels[str(depth)] = {reply: judge_sign(row[str(depth)], depth) for reply, row in rows.items()}
        complete = all(label is not None for label in labels[str(depth)].values())
        minima[str(depth)] = ([min(row[side]["point"]["cp"] for row in values) for side in range(2)]
                               if complete and values else None)
    counts = Counter()
    for reply in rows:
        a, b = (labels[str(depth)][reply] for depth in DEPTHS)
        counts["missing" if a is None or b is None else "disagree" if a != b
               else "first" if a == 1 else "second" if a == -1 else "tie"] += 1
    return {"labels": labels, "counts": dict(counts), "minimum_cp": minima}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("selection", type=Path)
    parser.add_argument("selection_sha256")
    parser.add_argument("--binary", type=Path)
    parser.add_argument("--net", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    if digest(args.selection) != args.selection_sha256:
        raise ValueError("Selection did not match freeze")
    specification, active = legal_overlap(json.loads(args.selection.read_text()))
    specification["selection_sha256"] = args.selection_sha256
    if args.binary is None:
        result = specification
    else:
        if (not args.net or digest(args.net) != NET or digest(args.binary) != BINARY
                or not args.receipt or json.loads(args.receipt.read_text()) != specification):
            raise ValueError("Judge or census freeze differs")
        with chess.engine.SimpleEngine.popen_uci(str(args.binary.resolve()), timeout=120) as engine:
            engine.configure({"Threads": 1, "Hash": 16, "EvalFile": str(args.net.resolve())})
            rows = evaluate(engine, active)
        result = {**specification, **summarize(rows), "rows": rows, "judge_binary_sha256": BINARY}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
