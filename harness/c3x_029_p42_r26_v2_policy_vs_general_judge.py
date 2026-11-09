#!/usr/bin/env python3
"""C3X P42/R26-V2: source-only vulnerability top3 versus R25 generic top3.

R26-V1 source-only selection is SHA-locked before any R26 Berserk search.
R25-E2 has 12 individual pre-judged free/forced Berserk reply results; reuse
their immutable scores for overlap. Physically search ONLY previously
unjudged selected replies. No artificial 147-row artifact reconstruction.
Historic postselected hypothesis and unequal compute cost are visible.
"""
import argparse
import hashlib
import json
from pathlib import Path

import chess
import chess.engine

from c3x_029_p38_r1_ethereal_independent_referee import (
    authentic_archive, authentic_cases, SOURCE_ZIP_SHA, SOURCE_MEMBER,
    SOURCE_JSON_SHA, PRED_ZIP_SHA, PRED_MEMBER, PRED_JSON_SHA)
from c3x_029_p42_r23_independent_all_opponent_reply_value_court import (
    FROZEN_EXPLORATORY_CASES, source_positions)
from c3x_029_p42_r24_independent_frozen_own_plan_judge import (
    FROZEN_PLAN_SHA, source_policy)
from c3x_029_p42_r22_berserk_fixed_depth_value_pilot import (
    quality, DEPTHS, NET_SHA, FAMILY_COMMIT)
from c3x_029_p42_r25_e2_k3_full_reply_coverage import B2_SHA, compare_minima

V1_SHA = "32db0d0dd880ba9ea9684ae039679cc610c1a204e0caae5f4ea52f53df18eec8"
R25_E2_SHA = "b18c7488edc66454a9cd79f54e7f072b2bbb9dddb56a0f1a87349bde4ec4440b"
V1_SCHEMA = "c3x042-r26-v1-source-policy-conditioned-stress-top3-v1"
R25_SCHEMA = "c3x042-r25-e2-source-ranked-k3-native-berserk-v2"
R26_SCHEMA = "c3x042-r26-v2-policy-aware-vs-general-k3-judge-v1"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate(v1, r25, b2, worlds, frozen):
    if (v1.get("schema") != V1_SCHEMA
        or v1.get("status") != "SOURCE_ONLY_V1_BEFORE_ANY_R26_BERSERK"
        or v1.get("reference_judge_ever_consulted_for_selection") is not False
        or v1.get("original_R24_prejudge_policy_sha256") != FROZEN_PLAN_SHA
        or r25.get("schema") != R25_SCHEMA
        or r25.get("R24_B2_aggregate_sha256") != B2_SHA
        or b2.get("prejudge_plan_sha256") != FROZEN_PLAN_SHA):
        raise ValueError("R26_V2_HOLD_SOURCE_JUDGE_CUSTODY")
    prepared = source_policy(worlds, frozen)
    if not (len(prepared) == len(v1.get("cases", []))
            == len(r25.get("cases", [])) == len(b2.get("cases", [])) == 2):
        raise ValueError("R26_V2_HOLD_CASE_SUPPORT")
    batches = []
    for (source, board, pairs), a, b, full in zip(
        prepared, v1["cases"], r25["cases"], b2["cases"]
    ):
        if not (source["case_id"] == a["case_id"] == b["case_id"] == full["case_id"]
                and source["event_family"] == a["event_family"] ==
                b["event_family"] == full["event_family"]
                and len(pairs) == len(a["roots"]) == len(b["roots"]) == len(full["roots"])):
            raise ValueError("R26_V2_HOLD_CASE_IDENTITY")
        roots = []
        for (pair, source_rows), candidate, old, full_root in zip(
            pairs, a["roots"], b["roots"], full["roots"]
        ):
            if not (pair["root"] == candidate["root_uci"] == old["root_uci"]
                    == full_root["root_uci"]
                    and candidate["legal_first_opponent_replies"] == len(pair["replies"])
                    == full_root["source_legal_reply_count"]):
                raise ValueError("R26_V2_HOLD_ROOT_IDENTITY")
            own = {x["opponent_reply"]: x["own_uci"] for x in source_rows}
            if len(own) != len(source_rows) or set(own) != set(pair["replies"]):
                raise ValueError("R26_V2_HOLD_SOURCE_UNIVERSE")
            old_rows = old["ranked_k3_replies"]
            cached = {x["opponent_reply"]: x for x in old_rows}
            if len(cached) != 3 or len(old_rows) != 3 or not set(cached).issubset(own):
                raise ValueError("R26_V2_HOLD_R25_CACHE_UNIVERSE")
            for x in old_rows:
                if own[x["opponent_reply"]] != x["frozen_own_move"]:
                    raise ValueError("R26_V2_HOLD_R25_CACHED_POLICY_ACTION")
            selection = candidate["ranked_policy_stress_top3"]
            chosen = [x["opponent_reply"] for x in selection]
            if (len(selection) != 3 or len(set(chosen)) != 3
                or not set(chosen).issubset(own)
                or [x["stress_rank"] for x in selection] != [1, 2, 3]
                or [x["source_policy_stress_cp"] for x in selection] != sorted(
                    x["source_policy_stress_cp"] for x in selection)):
                raise ValueError("R26_V2_HOLD_SOURCE_RANKING")
            child = board.copy(stack=True)
            child.push_uci(pair["root"])
            for x in selection:
                after = child.copy(stack=True)
                after.push_uci(x["opponent_reply"])
                frozen_own = chess.Move.from_uci(x["frozen_own_move"])
                if x["frozen_own_move"] != own[x["opponent_reply"]] or frozen_own not in after.legal_moves:
                    raise ValueError("R26_V2_HOLD_SOURCE_POLICY_DRIFT_OR_ILLEGAL")
            roots.append((pair, candidate, old, full_root, cached))
        batches.append((source, board, roots))
    return batches


def ref_search(board, own, root_mover, engine):
    result = {}
    for d in DEPTHS:
        free = engine.analyse(board, chess.engine.Limit(depth=d),
                              game=object(), info=chess.engine.INFO_ALL)
        forced = engine.analyse(board, chess.engine.Limit(depth=d),
                                root_moves=[own], game=object(),
                                info=chess.engine.INFO_ALL)
        first = quality(board, free, d, root_mover)
        second = quality(board, forced, d, root_mover)
        if (first["status"] != "DEPTH_CONTROLLED_FINITE_SEARCH_ONLY"
            or second["status"] != "DEPTH_CONTROLLED_FINITE_SEARCH_ONLY"):
            raise ValueError("R26_V2_HOLD_NEW_BERSERK_JUDGE")
        result[str(d)] = {"unrestricted": first, "frozen_policy": second}
    return result


def main():
    p = argparse.ArgumentParser()
    for name in ("source", "predictions", "frozen-plan", "v1", "r25-e2", "r24-b2",
                 "engine", "network", "out"):
        p.add_argument("--" + name, required=True)
    a = p.parse_args()
    for file, expected in ((a.frozen_plan, FROZEN_PLAN_SHA),
                           (a.v1, V1_SHA), (a.r25_e2, R25_E2_SHA),
                           (a.r24_b2, B2_SHA), (a.network, NET_SHA)):
        if sha(file) != expected:
            raise ValueError("R26_V2_HOLD_PINNED_FILE_SHA:" + str(file))
    v1 = json.loads(Path(a.v1).read_text(encoding="utf-8"))
    r25 = json.loads(Path(a.r25_e2).read_text(encoding="utf-8"))
    b2 = json.loads(Path(a.r24_b2).read_text(encoding="utf-8"))
    frozen = json.loads(Path(a.frozen_plan).read_text(encoding="utf-8"))
    original = authentic_cases(
        authentic_archive(Path(a.predictions), PRED_ZIP_SHA, PRED_MEMBER, PRED_JSON_SHA),
        authentic_archive(Path(a.source), SOURCE_ZIP_SHA, SOURCE_MEMBER, SOURCE_JSON_SHA))
    batches = validate(v1, r25, b2, source_positions(original, FROZEN_EXPLORATORY_CASES), frozen)
    if len(batches) != 2 or sum(len(x[2]) for x in batches) != 4:
        raise ValueError("R26_V2_HOLD_ACTUAL_TWO_CASE_FOUR_ROOT_SUPPORT")
    cases = []
    new_searches, cached_searches = 0, 0
    with chess.engine.SimpleEngine.popen_uci(a.engine, timeout=180) as eng:
        if ("berserk" not in eng.id.get("name", "").lower()
            or not {"Threads", "Hash"}.issubset(eng.options)):
            raise ValueError("R26_V2_HOLD_BERSERK_ENGINE_FAMILY")
        eng.configure({"Threads": 1, "Hash": 16})
        for source, board, roots in batches:
            judged_roots = []
            for pair, rank, old, full, cached in roots:
                child = board.copy(stack=True)
                child.push_uci(pair["root"])
                items = []
                for selection in rank["ranked_policy_stress_top3"]:
                    u = selection["opponent_reply"]
                    if u in cached:
                        row = cached[u]
                        depths = row["depths"]
                        cached_searches += 4
                        origin = "REUSE_R25_E2_SHA_FROZEN"
                    else:
                        after = child.copy(stack=True)
                        after.push_uci(u)
                        own = chess.Move.from_uci(selection["frozen_own_move"])
                        depths = ref_search(after, own, board.turn, eng)
                        new_searches += 4
                        origin = "NEW_R26_V2_BERSERK"
                    items.append({"opponent_reply": u,
                                  "frozen_own_move": selection["frozen_own_move"],
                                  "source_stress_rank": selection["stress_rank"],
                                  "independent_judge_provenance": origin,
                                  "depths": depths})
                modes = {}
                for d in DEPTHS:
                    depth = str(d)
                    original_values = full["depth_evaluations"][depth]
                    if original_values["all_legal_reply_plan_scores_finite"] is not True:
                        raise ValueError("R26_V2_HOLD_ORIGINAL_R24_FULL_SUPPORT")
                    comparisons = {}
                    for mode, fullkey in (
                        ("unrestricted", "worst_unrestricted_judge_response_value_cp"),
                        ("frozen_policy", "worst_frozen_plan_value_cp")):
                        candidate_min = min(x["depths"][depth][mode]["root_mover_cp"]
                                            for x in items)
                        full_min = original_values[fullkey]
                        generic_min = old["depth_aggregates"][depth][mode]["ranked_k3_worst_cp_new_rejudge"]
                        compare = compare_minima(candidate_min, full_min)
                        compare["R25_generic_ranked_k3_worst_cp"] = generic_min
                        compare["R26_policy_stress_minus_generic_cp"] = candidate_min - generic_min
                        compare["policy_stress_strictly_better_worst_capture"] = (
                            candidate_min < generic_min)
                        comparisons[mode] = compare
                    modes[depth] = comparisons
                judged_roots.append({"root_uci": pair["root"],
                                     "legal_first_opponent_replies": len(pair["replies"]),
                                     "ranked_policy_stress_top3": items,
                                     "depth_comparisons": modes,
                                     "source_stress_nodes_total": rank["stress_search_nodes_total"],
                                     "cached_overlap_reply_count": sum(
                                         x["opponent_reply"] in cached for x in items)})
            cases.append({"case_id": source["case_id"],
                          "event_family": source["event_family"], "roots": judged_roots})
    if new_searches + cached_searches != 48:
        raise ValueError("R26_V2_HOLD_NEW_PLUS_REUSED_EXPECTED_48")
    result = {"schema": R26_SCHEMA,
              "status": "EXPLORATORY_HISTORIC_SOURCE_STRESS_VS_GENERAL_TOP3",
              "R26_V1_source_only_sha256": V1_SHA,
              "R25_E2_cached_native_sha256": R25_E2_SHA,
              "R24_B2_all_reply_aggregate_sha256": B2_SHA,
              "new_native_search_count": new_searches,
              "reused_native_search_count": cached_searches,
              "cost_controlled_same_source_budget": False,
              "full_Cui_partial_tree": False,
              "source_root_causal_semantic_mediation": False,
              "prospective_validation": False,
              "R25_observed_failures_informed_R26_hypothesis": True,
              "cases": cases,
              "Berserk_binary_sha256": sha(a.engine)}
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("R26_V2_NATIVE_NEW", new_searches, "REUSED", cached_searches, flush=True)
    for case in cases:
        for root in case["roots"]:
            for d in ("12", "16"):
                for mode in ("frozen_policy", "unrestricted"):
                    v = root["depth_comparisons"][d][mode]
                    print("R26_V2_RESULT", case["event_family"], root["root_uci"],
                          d, mode, "full", v["full_147_reply_worst_cp_R24"],
                          "generic", v["R25_generic_ranked_k3_worst_cp"],
                          "policy", v["ranked_k3_worst_cp_new_rejudge"],
                          "new_minus_generic", v["R26_policy_stress_minus_generic_cp"],
                          flush=True)


if __name__ == "__main__":
    main()
