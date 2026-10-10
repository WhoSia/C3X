#!/usr/bin/env python3
"""C3X019 source genealogy: compare semantic search events, not counters.

Fixed February four observed root flips. ADAPTIVE retrospective analysis:
first observed root difference != earliest underlying search cause.
"""
import argparse
import hashlib
import json
from pathlib import Path

INPUT_SHA = "6601dc3397ce939ce61a5bd85ec91190292e823a40230978569f5705e717d613"
EXPECTED = {3: ("STRICT", 4, "below_alpha", False),
            6: ("STRICT", 10, "at_or_above_beta", True),
            7: ("BROAD", 4, "below_alpha", False),
            10: ("STRICT", 4, "below_alpha", False)}
COUNTERS = {"seq", "root_nodes"}
CANDIDATE_ID = ("kind", "depth", "root_call", "trial", "index", "move",
                "alpha", "beta", "before")


def need(ok, label):
    if not ok:
        raise RuntimeError("C3X019_SEMANTIC_PREFIX_" + label)


def semantic(event):
    return {key: val for key, val in event.items() if key not in COUNTERS}


def candidate_identity(event):
    return tuple(event.get(key) for key in CANDIDATE_ID)


def window_class(value, alpha, beta):
    if value <= alpha:
        return "at_alpha" if value == alpha else "below_alpha"
    if value >= beta:
        return "at_or_above_beta"
    return "inside_window"


def first_semantic_divergence(left, right):
    for i, (x, y) in enumerate(zip(left, right)):
        if semantic(x) != semantic(y):
            return i, x, y
    return None


def matching_episode_event(events, kind, witness):
    matched = [event for event in events if event["kind"] == kind
               and all(event.get(k) == witness.get(k)
                       for k in ("depth", "root_call", "trial"))]
    need(len(matched) == 1, kind.upper() + "_NON_UNIQUE")
    return matched[0]


def analyze(data):
    need([c["game_id"] for c in data["cases"]] == [3, 6, 7, 10],
         "FIXED_FOUR_CASES")
    result = {"schema": "c3x019-feb4-semantic-root-prefix-alpha-beta-screen-v1",
              "source_sha256": INPUT_SHA,
              "study": "ADAPTIVE_AFTER_PROSPECTIVE_F19_5_FAIL",
              "cases": []}
    for case in data["cases"]:
        game = case["game_id"]
        role, depth, required_class, after_changed = EXPECTED[game]
        need(case["selector"] == role, "ROLE_" + str(game))
        left = case["arms"]["F"]["all_root_search_events"]
        right = case["arms"]["FIRST"]["all_root_search_events"]
        hit = first_semantic_divergence(left, right)
        need(hit is not None, "NO_SEMANTIC_DIFF_" + str(game))
        idx, prior, intervention = hit
        need(prior["kind"] == intervention["kind"] == "candidate",
             "FIRST_DIFF_NOT_CANDIDATE_" + str(game))
        need(candidate_identity(prior) == candidate_identity(intervention),
             "SOURCE_CANDIDATE_UNALIGNED_" + str(game))
        need(prior["child_return"] != intervention["child_return"],
             "CHILD_RETURN_EQUAL_" + str(game))
        need(prior["depth"] == depth, "DEPTH_" + str(game))
        need(all(semantic(x) == semantic(y)
                 for x, y in zip(left[:idx], right[:idx])),
             "SEMANTIC_PREFIX_NOT_IDENTICAL")
        alpha, beta = prior["alpha"], prior["beta"]
        from_status = window_class(prior["child_return"], alpha, beta)
        to_status = window_class(intervention["child_return"], alpha, beta)
        need(to_status == required_class, "WINDOW_CLASS_" + str(game))
        actual_after = prior["after"] != intervention["after"]
        need(actual_after == after_changed, "CANDIDATE_AFTER_" + str(game))
        ex_f = matching_episode_event(left, "window_exit", prior)
        ex_v = matching_episode_event(right, "window_exit", intervention)
        sort_f = matching_episode_event(left, "after_sort", prior)
        sort_v = matching_episode_event(right, "after_sort", intervention)
        need(case["root_bestmove_flipped_from_F"], "NO_FINAL_FLIP")
        result["cases"].append({
            "game": game, "role": role,
            "source_aligned_semantic_prefix": idx,
            "ignored_observer_fields": sorted(COUNTERS),
            "first_divergence": {
                "depth": depth, "root_call": prior["root_call"],
                "trial": prior["trial"], "candidate_move_native": prior["move"],
                "alpha": alpha, "beta": beta,
                "F_child_return": prior["child_return"],
                "FIRST_child_return": intervention["child_return"],
                "F_window_class": from_status, "FIRST_window_class": to_status,
                "F_candidate_after": prior["after"],
                "FIRST_candidate_after": intervention["after"],
                "candidate_after_changed": actual_after},
            "same_source_trial_outcome": {
                "F_window_exit_value": ex_f["value"],
                "FIRST_window_exit_value": ex_v["value"],
                "F_sorted_first_move": sort_f["first_move"],
                "FIRST_sorted_first_move": sort_v["first_move"],
                "F_sorted_first_score": sort_f["first_score"],
                "FIRST_sorted_first_score": sort_v["first_score"]}})
    result["summary"] = {
        "fixed_outcome_selected_cases": 4,
        "initial_value_diff_below_alpha_both_arms": 3,
        "initial_value_diff_crosses_beta": 1,
        "initial_candidate_after_score_changes": 1,
        "original_F19_5": "FAIL_RETAINED",
        "source_prefix_matched_before_first_value_divergence": True}
    result["limits"] = [
        "Observer counters and event IDs are not chess state identities.",
        "Earliest recorded root event difference is not earliest internal search cause.",
        "The three locally screened cases can diverge later within the same or a subsequent root trial.",
        "A beta crossing in one case does not prove a unique TT-to-root mediator.",
        "Cases were selected after known February root outcome changes."]
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    raw = Path(args.native).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == INPUT_SHA, "SOURCE_SHA")
    report = analyze(json.loads(raw))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("C3X019_SEMANTIC_ROOT_PREFIX_PASS",
          json.dumps(report["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
