#!/usr/bin/env python3
"""C3X R25-E2: referee-blind k3 selection joined to immutable R24 B2 ALL replies.

Zero chess/engine dependencies. This is a *retrospective* coverage analysis of
post-selected historical positions: not an independent evaluation and not a full
Cui multi-ply strategy tree. Reference values never enter E1 ranking.
"""
import argparse
import hashlib
import json
from pathlib import Path

B2_SHA = "2fd30e135a1d4f4575b71cd263f01fdd363659fe3f05b6cafc653dc98646e365"
B2_SCHEMA = "c3x042-r24-independently-judged-full-reply-source-own-policy-v1"
E1_SCHEMA = "c3x042-r25-e1-source-ranked-first-layer-k3-v1"
DEPTHS = ("12", "16")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ordered_unique(values):
    return len(values) == len(set(values))


def joined_coverage(e1, b2):
    if (e1.get("schema") != E1_SCHEMA
        or e1.get("status") != "SOURCE_ONLY_BEFORE_ANY_R25_REFEREE_ADJUDICATION"
        or e1.get("independent_referee_consulted_for_ranking") is not False
        or e1.get("first_opponent_layer_only_not_full_Cui_tree") is not True
        or e1.get("original_R24_frozen_147_policy_sha256") != b2.get("prejudge_plan_sha256")
        or b2.get("schema") != B2_SCHEMA):
        raise ValueError("R25_E2_HOLD_JOIN_OR_PROVENANCE")
    if len(e1.get("cases", [])) != len(b2.get("cases", [])):
        raise ValueError("R25_E2_HOLD_CASE_SUPPORT")
    results = []
    for left_case, right_case in zip(e1["cases"], b2["cases"]):
        if (left_case["case_id"] != right_case["case_id"]
            or left_case["event_family"] != right_case["event_family"]
            or len(left_case["roots"]) != len(right_case["roots"])):
            raise ValueError("R25_E2_HOLD_CASE_IDENTITY")
        roots = []
        for lroot, rroot in zip(left_case["roots"], right_case["roots"]):
            if lroot["root_uci"] != rroot["root"]:
                raise ValueError("R25_E2_HOLD_ROOT_IDENTITY")
            all_rows = rroot["reply_results"]
            by_reply = {x["opponent_reply"]: x for x in all_rows}
            if len(all_rows) != len(by_reply) or len(all_rows) != lroot["legal_first_opponent_replies"]:
                raise ValueError("R25_E2_HOLD_FULL_REPLY_SUPPORT")
            selected = lroot["ranked_replies"]
            names = [x["opponent_reply"] for x in selected]
            if (len(selected) != min(3, len(all_rows))
                or not ordered_unique(names)
                or [x["engine_rank"] for x in selected] != list(range(1, len(selected) + 1))
                or not set(names).issubset(by_reply)):
                raise ValueError("R25_E2_HOLD_ENGINE_RANKED_SELECTION")
            for x in selected:
                if x["frozen_source_own_move"] != by_reply[x["opponent_reply"]]["frozen_own_move"]:
                    raise ValueError("R25_E2_HOLD_PREJUDGE_OWN_ACTION_DRIFT")
            estimates = {}
            for d in DEPTHS:
                modes = {}
                for mode in ("frozen_policy", "unrestricted"):
                    def value(row):
                        value_ = row.get(d, {}).get(mode, {}).get("root_mover_cp")
                        if type(value_) is not int:
                            raise ValueError("R25_E2_HOLD_UNADMITTED_FINITE_SCORE")
                        return value_
                    worst_full = min(value(row) for row in all_rows)
                    worst_k3 = min(value(by_reply[name]) for name in names)
                    if worst_k3 < worst_full:
                        raise ValueError("R25_E2_HOLD_SAMPLE_MINIMUM_INVARIANT")
                    modes[mode] = {
                        "full_reply_worst_cp": worst_full,
                        "source_ranked_k3_worst_cp": worst_k3,
                        "k3_optimism_cp": worst_k3 - worst_full,
                        "full_worst_in_k3": any(
                            value(by_reply[name]) == worst_full for name in names),
                    }
                estimates[d] = modes
            roots.append({
                "root_uci": lroot["root_uci"],
                "legal_reply_count": len(all_rows),
                "ranked_k3_reply_uci": names,
                "ranked_k3_count": len(names),
                "estimates": estimates,
            })
        results.append({"case_id": left_case["case_id"],
                        "event_family": left_case["event_family"],
                        "roots": roots})
    return {
        "schema": "c3x042-r25-e2-k3-vs-full-first-reply-coverage-v1",
        "status": "RETROSPECTIVE_FIRST_LAYER_COVERAGE_ONLY",
        "r24_b2_sha256": B2_SHA,
        "same_prejudge_policy_provenance_checked": True,
        "opponent_selection_used_judge": False,
        "no_new_judge_calls": True,
        "first_layer_only_not_full_Cui": True,
        "different_node_costs_not_controlled": True,
        "root_action_causal_explanation": False,
        "prospective_validation": False,
        "cases": results,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--e1", required=True)
    p.add_argument("--b2", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    if sha(a.b2) != B2_SHA:
        raise ValueError("R25_E2_HOLD_R24_B2_JUDGE_BYTES")
    e1 = json.loads(Path(a.e1).read_text(encoding="utf-8"))
    b2 = json.loads(Path(a.b2).read_text(encoding="utf-8"))
    result = joined_coverage(e1, b2)
    result["e1_sha256"] = sha(a.e1)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("R25_E2_RETROSPECTIVE_ENGINE_RANKED_K3_COVERAGE",
          sum(len(c["roots"]) for c in result["cases"]), "ROOTS")


if __name__ == "__main__":
    main()
