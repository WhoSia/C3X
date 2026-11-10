#!/usr/bin/env python3
"""P7: stdlib-only reanalysis of *existing* P4-B frozen Berserk judgments.

This module performs ZERO new searches. It validates source-selected k=2
leaf outcomes at depths 10/12; it cannot infer unsearched opponent replies.
"""
import argparse
import hashlib
import json
from pathlib import Path

SOURCE_SCHEMA = "c3x030-p4b-frozen-source-cui-independent-berserk-leaf-judge-v1"
AUDIT_SCHEMA = "c3x030-p7-p4b-conditional-depth-audit-v1"


def audit(data):
    if (data.get("schema") != SOURCE_SCHEMA
        or data.get("independent_engine_family") != "Berserk14"
        or data.get("source_selected_replies_unchanged_by_referee") is not True
        or data.get("full_opponent_universe_judged") is not False
        or data.get("source_engine_actual_causal_decision_proven") is not False
        or data.get("depths") != [10, 12]):
        raise ValueError("P7_HOLD_RECEIPT_SCOPE")
    roots = data.get("roots")
    if not isinstance(roots, list) or len(roots) != 2:
        raise ValueError("P7_HOLD_ROOT_COUNT")
    if len({r.get("root_uci") for r in roots}) != 2:
        raise ValueError("P7_HOLD_ROOT_DUPLICATE")
    result = []
    count = 0
    for root in roots:
        leaves = root.get("independent_leaf_scores")
        if not isinstance(leaves, list) or len(leaves) != 4:
            raise ValueError("P7_HOLD_K2_LEAF_COUNT")
        paths, scores = [], {"10": [], "12": []}
        for leaf in leaves:
            path = leaf.get("path_uci")
            if (not isinstance(path, list) or len(path) != 5
                or any(not isinstance(x, str) or len(x) not in (4, 5) for x in path)):
                raise ValueError("P7_HOLD_PATH_FORMAT")
            if path[0] != root["root_uci"]:
                raise ValueError("P7_HOLD_ROOT_PATH_DISAGREEMENT")
            paths.append(tuple(path))
            depths = leaf.get("scores", {})
            if set(depths) != {"10", "12"}:
                raise ValueError("P7_HOLD_DEPTH_MISSING")
            for depth in ("10", "12"):
                cp = depths[depth].get("root_mover_cp")
                nodes = depths[depth].get("actual_nodes")
                if type(cp) is not int or type(nodes) is not int or nodes <= 0:
                    raise ValueError("P7_HOLD_NUMERIC_PROVENANCE")
                scores[depth].append((tuple(path), cp, nodes))
                count += 1
        if len(set(paths)) != 4:
            raise ValueError("P7_HOLD_DUPLICATE_PATH")
        summaries = {}
        for depth, rows in scores.items():
            vals = [cp for _, cp, _ in rows]
            lo, hi = min(vals), max(vals)
            total_nodes = sum(nodes for _, _, nodes in rows)
            expected = {
                "min_over_only_four_source_selected_paths_cp": lo,
                "max_over_only_four_source_selected_paths_cp": hi,
                "span_across_only_four_paths_cp": hi - lo,
                "actual_independent_nodes": total_nodes}
            if root.get("depth_summaries", {}).get(depth) != expected:
                raise ValueError("P7_HOLD_SUMMARY_MISMATCH")
            summaries[depth] = {
                "min_cp": lo, "max_cp": hi, "span_cp": hi - lo,
                "actual_nodes": total_nodes,
                "minimum_paths": [list(p) for p, cp, _ in rows if cp == lo]}
        first = set(map(tuple, summaries["10"]["minimum_paths"]))
        second = set(map(tuple, summaries["12"]["minimum_paths"]))
        result.append({
            "root_uci": root["root_uci"],
            "selected_leaf_count": 4,
            "depth_conditional": summaries,
            "minimum_cp_depth12_minus_depth10": summaries["12"]["min_cp"] - summaries["10"]["min_cp"],
            "minimum_path_sets_disjoint_across_depths": first.isdisjoint(second)})
    if count != 16 or data.get("independent_search_count") != count:
        raise ValueError("P7_HOLD_SEARCH_COUNT")
    a, b = (r["depth_conditional"]["12"] for r in result)
    return {
        "schema": AUDIT_SCHEMA,
        "status": "REANALYSIS_OF_EXISTING_P4B_RECEIPT_ONLY",
        "roots": result,
        "depth12_selected_minimum_margin_a_minus_b_cp": a["min_cp"] - b["min_cp"],
        "depth12_selected_ranges_overlap": not (a["max_cp"] < b["min_cp"] or b["max_cp"] < a["min_cp"]),
        "new_native_engine_searches": 0,
        "source_selected_k": 2,
        "opponent_layers": 2,
        "full_opponent_universe_judged": False,
        "source_engine_causal_choice_proven": False,
        "user_learning_benefit_proven": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--judge-json", required=True)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    raw = Path(args.judge_json).read_bytes()
    if (len(args.expected_sha256) != 64
        or hashlib.sha256(raw).hexdigest() != args.expected_sha256):
        raise ValueError("P7_HOLD_INPUT_RAW_SHA")
    result = audit(json.loads(raw))
    result["verified_p4b_receipt_sha256"] = args.expected_sha256
    target = Path(args.out)
    target.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print("C3X_P7_EXISTING_RECEIPT_AUDIT_PASS", hashlib.sha256(target.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
