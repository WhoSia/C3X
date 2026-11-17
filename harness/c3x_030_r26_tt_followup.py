"""Repeat all histories at depth 13 and replay the outcomes selected in R26."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from statistics import median

import chess
import chess.engine

from c3x_030_r26_tt_audit import gap_band, pair_outcome, reference_gap
from c3x_030_r26_tt_panel import ARMS, board_from_case, search

DEPTH = 13
DEEP_NODES = 500000
DEPTH_ARMS = (*ARMS[:5], "reference")


def fixed_depth(positions, baseline, patched, pool):
    def run(job):
        case, arm = job
        board = board_from_case(case)
        result = search(board, arm, chess.engine.Limit(depth=DEPTH), baseline, patched)
        return {"case": case["id"], "arm": arm, "result": result}

    rows = list(pool.map(run, ((case, arm) for case in positions for arm in DEPTH_ARMS)))
    return rows


def depth_audit(rows):
    cells = {(row["case"], row["arm"]): row["result"] for row in rows}
    cases = sorted({row["case"] for row in rows})
    groups = {arm: Counter() for arm in DEPTH_ARMS[2:-1]}
    refs = Counter()
    nodes_by_arm = {arm: [] for arm in DEPTH_ARMS}
    any_change = 0
    band_outcomes = {}
    for case in cases:
        upstream, passive, picker, value, both, reference = (cells[case, arm] for arm in DEPTH_ARMS)
        if upstream != passive:
            raise ValueError(f"Original/passive mismatch: {case}")
        band = gap_band(reference_gap(reference))
        refs[band] += 1
        any_change += len({row["move"] for row in (upstream, picker, value, both)}) > 1
        for arm, row in zip(DEPTH_ARMS[2:-1], (picker, value, both)):
            flags = pair_outcome(upstream, row)
            groups[arm].update(flags)
            band_outcomes.setdefault((arm, band), Counter()).update(flags)
        for arm in DEPTH_ARMS:
            row = cells[case, arm]
            if arm == "reference":
                row = row[0]
            nodes_by_arm[arm].append(row["actual_nodes"])
    return {
        "searches": len(rows), "passive_exact_matches": len(cases),
        "depth_requested": DEPTH, "any_mask_changes_root": any_change,
        "paired": groups, "reference_margins": refs,
        "by_reference_margin": {f"{arm}/{band}": outcomes for (arm, band), outcomes in band_outcomes.items()},
        "reported_node_median": {arm: median(nodes) for arm, nodes in nodes_by_arm.items()},
        "reported_node_sum": sum(map(sum, nodes_by_arm.values())),
    }


def replay_cases(positions, panel, discovery, baseline, patched, pool):
    cases = {case["id"]: case for case in positions}
    cells = {(row["case"], row["arm"], row["requested_nodes"]): row["result"] for row in panel}
    ids = sorted({row[0] for row in discovery["example_index"]["large_reference_gap_root_changed"]})
    tasks = []
    for case_id in ids:
        roots = {cells[case_id, arm, nodes]["move"]
                 for arm in ARMS[:5] for nodes in (8000, 32000)}
        roots.update(row["move"] for row in cells[case_id, "reference", 120000])
        tasks.extend((case_id, (), root) for root in (None, *sorted(roots)))
    for case_id in cases:
        low, high = (cells[case_id, "upstream", nodes] for nodes in (8000, 32000))
        flags = pair_outcome(low, high)
        if flags["same_root_equal_score_reply_changed"]:
            tasks.extend((case_id, tuple(row["pv"][:2]), None) for row in (low, high))

    def run(task):
        case_id, prefix, root = task
        board = board_from_case(cases[case_id])
        for move in prefix:
            board.push_uci(move)
        forced = [chess.Move.from_uci(root)] if root else None
        result = search(board, "upstream", chess.engine.Limit(nodes=DEEP_NODES), baseline, patched, forced)
        if root and result["move"] != root:
            raise ValueError(f"Restricted root changed: {task}")
        return {"case": case_id, "prefix": prefix, "required_root": root, "fen": board.fen(), "result": result}

    return list(pool.map(run, tasks))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cohort", "panel", "audit", "upstream", "patched", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    positions = json.loads(args.cohort.read_bytes())["positions"]
    panel = [json.loads(line) for line in args.panel.read_text().splitlines()]
    discovery = json.loads(args.audit.read_bytes())
    with ThreadPoolExecutor(max_workers=4) as pool:
        depth_rows = fixed_depth(positions, args.upstream.resolve(), args.patched.resolve(), pool)
        replays = replay_cases(positions, panel, discovery, args.upstream.resolve(), args.patched.resolve(), pool)
    result = {"depth_audit": depth_audit(depth_rows), "replays": replays, "depth_rows": depth_rows}
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
