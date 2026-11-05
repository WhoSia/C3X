"""P41 preflight for independently judged chess-plan experiments.

Structural input contract only: synthetic tests do NOT validate chess legality,
event-source custody, referee playing strength, or scientific performance.
"""
from __future__ import annotations
import hashlib
import json


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def verify_case(case, historical):
    failures = []

    def check(cond, code):
        if not cond:
            failures.append(code)

    source, freeze, judge = case["source"], case["freeze"], case["judge"]
    history = source["full_uci"]
    check(len(history) >= 60, "SHORT_GAME")
    check(source["original_sha256"] == hashlib.sha256(
        " ".join(history).encode()).hexdigest(), "GAME_SHA")
    check(source["game_sha256"] not in historical["game_sha256"], "GAME_LEAK")
    check(source["event_family"] not in historical["event_family"], "EVENT_LEAK")
    check(freeze["source_sha256"] == source["original_sha256"], "FROZEN_SOURCE_MISMATCH")
    check(freeze["plan_digest"] == digest(freeze["plan_spec"]), "PLAN_DIGEST")
    check(freeze["phase"] == "PRE_JUDGE", "POSTHOC_PLAN")
    check(freeze["candidate_uci"] == case["roots"]["24k"], "CANDIDATE_FREEZE")
    check(case["roots"]["24k"] == case["roots"]["48k"] ==
          case["roots"]["96k"], "CANDIDATE_DRIFT")
    check(judge["family"] not in case["predictor_families"], "SAME_FAMILY_JUDGE")
    check(judge["state"] == "NATIVE_VERIFIED", "JUDGE_NOT_VERIFIED")
    check(bool(judge["source_sha256"] and judge["binary_sha256"]), "JUDGE_PROVENANCE")
    check(judge["actual_nodes"] >= judge["required_nodes"] > 0, "UNDERBUDGET_JUDGE")

    required = ("pv", "partial_tree_k3", "foil_json", "c3x")
    for method in required:
        check(method in case["methods"], "MISSING_BASELINE_" + method)
    if all(method in case["methods"] for method in required):
        for method, record in case["methods"].items():
            check(all(record[m] >= 0 for m in
                      ("native_nodes", "legal_expansions", "cpu_ms")),
                  "NEGATIVE_COST_" + method)
            check(record["claim_slots"] == case["methods"]["c3x"]["claim_slots"],
                  "OUTPUT_BUDGET_" + method)
        for metric in ("native_nodes", "legal_expansions", "cpu_ms"):
            check(max(record[metric] for record in case["methods"].values()) <=
                  case["global_budget"][metric], "GLOBAL_BUDGET_" + metric)

    plan = freeze["plan_spec"]
    replies = plan["opponent_replies"]
    if plan["scope"] == "ALL_LEGAL":
        check(len(replies) == plan["opponent_total"], "FALSE_UNIVERSAL_COVERAGE")
    else:
        check(plan["scope"] == "SAMPLED", "INVALID_SCOPE")
    for reply, branch in replies.items():
        legal, chosen = branch["legal_own_count"], branch["plan_own_count"]
        check(0 <= chosen <= legal and legal > 0, "INVALID_PLAN_CARDINALITY_" + reply)
        check(chosen < legal, "TRIVIAL_ALL_LEGAL_" + reply)
        check(chosen * 2 <= legal, "NO_SELECTIVITY_" + reply)
    return {"status": ("PASS_STRUCTURAL_PREFLIGHT_ONLY" if not failures else "HOLD"),
            "failures": sorted(set(failures)),
            "claim_ceiling": ("Structural contract only; no actual chess legality,"
                             " no source-byte verification or chess-value outcome.")}
