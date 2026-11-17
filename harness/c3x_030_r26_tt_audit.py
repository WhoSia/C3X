"""Compute paired R26 outcomes without reading display text or aggregating bounds."""
import argparse
from collections import Counter, defaultdict
import itertools
import json
from pathlib import Path

from c3x_030_r26_tt_panel import ARMS, BUDGETS

TREATMENTS = ARMS[2:]


def score(row):
    if not row["pv"] or row["move"] != row["pv"][0] or row["upperbound"] or row["lowerbound"]:
        return None
    if row["cp"] is not None:
        return ("cp", row["cp"])
    if row["mate"] is not None:
        return ("mate", row["mate"])
    return None


def reply(row):
    if len(row["pv"]) >= 2 and row["move"] == row["pv"][0]:
        return row["pv"][1]
    return None


def pair_outcome(base, other):
    same_move = base["move"] == other["move"]
    known_replies = same_move and reply(base) is not None and reply(other) is not None
    same_score = same_move and score(base) is not None and score(base) == score(other)
    return {
        "cells": 1, "root_changed": int(not same_move),
        "same_root_both_replies": int(known_replies),
        "same_root_reply_changed": int(known_replies and reply(base) != reply(other)),
        "same_root_equal_score_both_replies": int(known_replies and same_score),
        "same_root_equal_score_reply_changed": int(known_replies and same_score and reply(base) != reply(other)),
    }


def reference_gap(rows):
    if len(rows) < 2:
        return None
    first, second = rows[:2]
    a, b = score(first), score(second)
    if first["depth"] != second["depth"] or a is None or b is None:
        return None
    if first["move"] == second["move"] or a[0] != "cp" or b[0] != "cp" or a[1] < b[1]:
        return None
    return a[1] - b[1]


def gap_band(gap):
    if gap is None:
        return "unavailable"
    if gap < 15:
        return "0-14cp"
    if gap < 50:
        return "15-49cp"
    return "50+cp"


def index_rows(rows, cases):
    cells = {}
    for row in rows:
        case = cases[row["case"]]
        if (case["game_id"], case["ply"]) != (row["game"], row["ply"]):
            raise ValueError(f"Wrong case metadata: {row['case']}")
        key = row["case"], row["arm"], row["requested_nodes"]
        if key in cells:
            raise ValueError(f"Duplicate cell: {key}")
        cells[key] = row["result"]
    planned = set(itertools.product(cases, ARMS, BUDGETS))
    planned.update((case, "reference", 120000) for case in cases)
    if cells.keys() != planned:
        raise ValueError(f"Panel mismatch: missing={planned - cells.keys()} extra={cells.keys() - planned}")
    return cells


def audit(rows, positions):
    cases = {case["id"]: case for case in positions}
    cells = index_rows(rows, cases)
    groups = defaultdict(Counter)
    changed_games = defaultdict(set)
    interactions = defaultdict(Counter)
    examples = defaultdict(list)
    references = Counter()
    baseline_depth_moves = Counter()
    baseline_mismatches = []
    for case_id, case in cases.items():
        game = case["game_id"]
        source = game.rsplit("-", 1)[0]
        reference = cells[case_id, "reference", 120000]
        gap = reference_gap(reference)
        band = gap_band(gap)
        references[band] += 1
        r8 = cells[case_id, "upstream", 8000]
        r32 = cells[case_id, "upstream", 32000]
        baseline_depth_moves.update(pair_outcome(r8, r32))
        for budget in BUDGETS:
            base = cells[case_id, "passive", budget]
            upstream = cells[case_id, "upstream", budget]
            if base != upstream:
                baseline_mismatches.append([case_id, budget])
            changed = {}
            for arm in TREATMENTS:
                other = cells[case_id, arm, budget]
                flags = pair_outcome(base, other)
                changed[arm] = bool(flags["root_changed"])
                for group in ("all", source, f"ply-{case['ply']}", f"{source}/ply-{case['ply']}", band):
                    groups[budget, arm, group].update(flags)
                if changed[arm]:
                    changed_games[budget, arm].add(game)
                    if band == "50+cp":
                        examples["large_reference_gap_root_changed"].append([case_id, budget, arm, gap])
                if flags["same_root_equal_score_reply_changed"]:
                    examples["equal_score_reply_fork"].append([case_id, budget, arm, gap])
            picker, value, both = (changed[arm] for arm in TREATMENTS[:3])
            any_mask = picker or value or both
            interactions[budget].update({
                "any_mask_changes_root": int(any_mask),
                "joint_only_switch": int(both and not (picker or value)),
                "combined_restores_default": int((picker or value) and not both),
                "root_count_3plus": int(len({cells[case_id, arm, budget]["move"] for arm in ARMS[1:5]}) >= 3),
            })
            if any_mask:
                for group in ("any_mask", f"any_mask/{source}"):
                    changed_games[budget, group].add(game)
    if baseline_mismatches:
        raise ValueError(f"Passive patched and original engines differ: {baseline_mismatches}")
    reported_nodes = sum((result[0] if arm == "reference" else result)["actual_nodes"] or 0
                         for (_, arm, _), result in cells.items())
    return {
        "positions": len(cases), "games": len({case["game_id"] for case in positions}),
        "searches": len(cells), "reported_nodes_sum": reported_nodes,
        "passive_exact_matches": len(cases) * len(BUDGETS),
        "reference_margins": dict(references), "baseline_across_budgets": dict(baseline_depth_moves),
        "paired": {f"{budget}/{arm}/{group}": dict(outcomes)
                   for (budget, arm, group), outcomes in sorted(groups.items())},
        "affected_games": {f"{budget}/{arm}": len(games) for (budget, arm), games in sorted(changed_games.items())},
        "factorial": {budget: dict(outcomes) for budget, outcomes in interactions.items()},
        "example_index": dict(examples),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cohort", type=Path)
    parser.add_argument("panel", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    positions = json.loads(args.cohort.read_bytes())["positions"]
    with args.panel.open() as stream:
        result = audit([json.loads(line) for line in stream], positions)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
