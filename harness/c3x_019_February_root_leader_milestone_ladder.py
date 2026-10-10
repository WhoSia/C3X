#!/usr/bin/env python3
"""C3X019 February: separate first child divergence, score, and root leader.

Adaptive after February F19.5 fail. Uses only per-depth terminal
after_sort events in each arm, never aligns root_call IDs after path split.
"""
import argparse
import hashlib
import json
from pathlib import Path
from c3x_019_February_semantic_root_prefix_audit import (
    INPUT_SHA, EXPECTED, analyze, need,
)

WINNER_DEPTHS = {3: 4, 6: 11, 7: 11, 10: 6}
SCORE_DEPTHS = {3: 4, 6: 10, 7: 8, 10: 5}


def last_trial_each_depth(events):
    result = {}
    for depth in range(1, 13):
        candidates = [e for e in events if e["kind"] == "after_sort"
                      and e["depth"] == depth]
        need(bool(candidates), "MISSING_SOURCE_TRIAL_DEPTH_" + str(depth))
        need(all(e["trial"] == i + 1 for i, e in enumerate(candidates)),
             "NONCONSECUTIVE_TRIAL_DEPTH_" + str(depth))
        result[depth] = {"final": candidates[-1], "trial_count": len(candidates)}
    return result


def analyze_ladder(data):
    prefix = analyze(data)
    details = []
    for case, pref in zip(data["cases"], prefix["cases"]):
        game = case["game_id"]
        need(game == pref["game"], "SOURCE_CASE_ALIGNMENT")
        original = last_trial_each_depth(case["arms"]["F"]["all_root_search_events"])
        active = last_trial_each_depth(case["arms"]["FIRST"]["all_root_search_events"])
        rows = []
        for depth in range(1, 13):
            f = original[depth]
            v = active[depth]
            rows.append({
                "depth": depth,
                "F_final_root_leader": f["final"]["first_move"],
                "FIRST_final_root_leader": v["final"]["first_move"],
                "F_final_root_value": f["final"]["value"],
                "FIRST_final_root_value": v["final"]["value"],
                "F_aspiration_trial_count": f["trial_count"],
                "FIRST_aspiration_trial_count": v["trial_count"],
                "leader_changed": f["final"]["first_move"] != v["final"]["first_move"],
                "value_changed": f["final"]["value"] != v["final"]["value"],
                "trial_count_changed": f["trial_count"] != v["trial_count"]})
        winner = next((r["depth"] for r in rows if r["leader_changed"]), None)
        score = next((r["depth"] for r in rows if r["value_changed"]), None)
        first_child = pref["first_divergence"]["depth"]
        need(winner == WINNER_DEPTHS[game], "FIRST_LEADER_DEPTH_" + str(game))
        need(score == SCORE_DEPTHS[game], "FIRST_SCORE_DEPTH_" + str(game))
        need(winner >= first_child and score >= first_child,
             "EARLY_LEADER_OR_SCORE_DISCREPANCY")
        need(rows[-1]["leader_changed"], "FINAL_DEPTH_WINNER_UNCHANGED")
        details.append({
            "game": game, "selector": case["selector"],
            "first_semantic_child_return_change_depth": first_child,
            "first_terminal_trial_value_change_depth": score,
            "first_terminal_root_leader_change_depth": winner,
            "score_latency_in_depths": score - first_child,
            "leader_latency_in_depths": winner - first_child,
            "all_depths": rows})
    return {
        "schema": "c3x019-feb4-source-observed-depth-milestone-root-leader-lattice-v1",
        "source_sha256": INPUT_SHA,
        "status": "ADAPTIVE_DEVELOPMENT_NOT_INDEPENDENT",
        "cases": details,
        "summary": {
            "first_leader_change_depths": {str(c["game"]): c["first_terminal_root_leader_change_depth"] for c in details},
            "source_child_to_leader_depth_delays": {str(c["game"]): c["leader_latency_in_depths"] for c in details},
            "direct_same_depth_leader_change_cases": [c["game"] for c in details if c["leader_latency_in_depths"] == 0],
            "delayed_leader_change_cases": [c["game"] for c in details if c["leader_latency_in_depths"] > 0],
            "independent_F19_5": "FAIL_RETAINED"},
        "limits": [
            "Per-depth last after_sort records are an observed search-order outcome, not complete minimax value for all moves.",
            "Within-depth last aspiration trial can differ between arms; no cross-arm rootcall number identity assumed.",
            "Depth delay is an observed milestone gap, not proof the first child-return difference caused the later root winner change.",
            "Four known root flips selected after February outcomes, no independent predictive generalization."]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--native", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    raw = Path(args.native).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == INPUT_SHA, "FROZEN_SOURCE_SHA")
    result = analyze_ladder(json.loads(raw))
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print("C3X019_ROOT_LEADER_MILESTONE_LADDER_PASS",
          json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
