#!/usr/bin/env python3
"""C3X R25-E2: actual 48-search Berserk rejudge of E1 source-ranked first-layer k3.

R24-B2 archived only per-root all-reply aggregates, NOT per-reply scores.
Never infer missing 147 detail. E1 source ranking was sealed in a separate
run BEFORE any R25 referee. This runner performs 4 roots * 3 replies *
2 depths * (unrestricted, forced source own action) = 48 new searches.
Historical exposed cases; finite depth, unequal nodes, no complete Cui tree.
"""
import argparse
import hashlib
import json
from pathlib import Path
import chess
import chess.engine
from c3x_029_p38_r1_ethereal_independent_referee import (
    authentic_archive, authentic_cases, SOURCE_ZIP_SHA, SOURCE_MEMBER,
    SOURCE_JSON_SHA, PRED_ZIP_SHA, PRED_MEMBER, PRED_JSON_SHA,
)
from c3x_029_p42_r23_independent_all_opponent_reply_value_court import (
    FROZEN_EXPLORATORY_CASES, source_positions,
)
from c3x_029_p42_r22_berserk_fixed_depth_value_pilot import (
    quality, DEPTHS, NET_SHA, FAMILY_COMMIT,
)

B2_SHA = "2fd30e135a1d4f4575b71cd263f01fdd363659fe3f05b6cafc653dc98646e365"
B2_SCHEMA = "c3x042-r24-independently-judged-full-reply-source-own-policy-v1"
E1_SCHEMA = "c3x042-r25-e1-source-ranked-first-layer-k3-v1"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_join(e1, b2, worlds):
    if (e1.get("schema") != E1_SCHEMA
        or e1.get("status") != "SOURCE_ONLY_BEFORE_ANY_R25_REFEREE_ADJUDICATION"
        or e1.get("independent_referee_consulted_for_ranking") is not False
        or e1.get("first_opponent_layer_only_not_full_Cui_tree") is not True
        or e1.get("original_R24_frozen_147_policy_sha256") != b2.get("prejudge_plan_sha256")
        or b2.get("schema") != B2_SCHEMA
        or len(e1.get("cases", [])) != len(b2.get("cases", []))
        or len(worlds) != len(e1["cases"])):
        raise ValueError("R25_E2_HOLD_JOIN_OR_PROVENANCE")
    tasks = []
    for lcase, rcase, (source, board, pairs) in zip(e1["cases"], b2["cases"], worlds):
        if (lcase["case_id"] != rcase["case_id"] or lcase["case_id"] != source["case_id"]
            or lcase["event_family"] != rcase["event_family"]
            or lcase["event_family"] != source["event_family"]
            or not (len(lcase["roots"]) == len(rcase["roots"]) == len(pairs))):
            raise ValueError("R25_E2_HOLD_CASE_IDENTITY")
        local_roots = []
        for lroot, rroot, pair in zip(lcase["roots"], rcase["roots"], pairs):
            if (lroot["root_uci"] != rroot["root_uci"]
                or lroot["root_uci"] != pair["root"]
                or lroot["legal_first_opponent_replies"] != len(pair["replies"])
                or rroot["source_legal_reply_count"] != len(pair["replies"])):
                raise ValueError("R25_E2_HOLD_ROOT_OR_FULL_REPLY_SUPPORT")
            selected = lroot["ranked_replies"]
            selected_uci = [x["opponent_reply"] for x in selected]
            if (len(selected) != min(3, len(pair["replies"]))
                or len(set(selected_uci)) != len(selected_uci)
                or [x["engine_rank"] for x in selected] != list(range(1, len(selected) + 1))
                or not set(selected_uci).issubset(pair["replies"])):
                raise ValueError("R25_E2_HOLD_ENGINE_RANKED_SELECTION")
            child = board.copy(stack=True)
            child.push_uci(pair["root"])
            for x in selected:
                after = child.copy(stack=True)
                after.push_uci(x["opponent_reply"])
                own = chess.Move.from_uci(x["frozen_source_own_move"])
                if after.is_game_over(claim_draw=False) or own not in after.legal_moves:
                    raise ValueError("R25_E2_HOLD_SOURCE_FROZEN_OWN_ILLEGAL")
            local_roots.append((pair, lroot, rroot))
        tasks.append((source, board, local_roots))
    return tasks


def compare_minima(k3, full):
    """Only call truncation optimism when independent replay preserves inclusion."""
    if type(full) is not int or type(k3) is not int:
        raise ValueError("R25_E2_HOLD_NONFINITE_MINIMUM")
    return {
        "full_147_reply_worst_cp_R24": full,
        "ranked_k3_worst_cp_new_rejudge": k3,
        "delta_k3_minus_full_cp": k3 - full,
        "valid_subset_minimum_if_replay_consistent": k3 >= full,
        "interpretation": "REPLAY_CONSISTENT_SAMPLED_OPTIMISM" if k3 >= full
                          else "HOLD_CROSS_RUN_FINITE_SEARCH_SCORE_INCONSISTENCY",
    }


def judge(tasks, b2, eng):
    outcome = []
    for source, board, triples in tasks:
        roots = []
        for pair, lroot, rroot in triples:
            child = board.copy(stack=True)
            child.push_uci(pair["root"])
            rows = []
            for frozen in lroot["ranked_replies"]:
                after = child.copy(stack=True)
                after.push_uci(frozen["opponent_reply"])
                own = chess.Move.from_uci(frozen["frozen_source_own_move"])
                depth_rows = {}
                for depth in DEPTHS:
                    free_info = eng.analyse(after, chess.engine.Limit(depth=depth),
                                            game=object(), info=chess.engine.INFO_ALL)
                    forced_info = eng.analyse(after, chess.engine.Limit(depth=depth),
                                              root_moves=[own], game=object(),
                                              info=chess.engine.INFO_ALL)
                    free = quality(after, free_info, depth, board.turn)
                    forced = quality(after, forced_info, depth, board.turn)
                    if (free["status"] != "DEPTH_CONTROLLED_FINITE_SEARCH_ONLY"
                        or forced["status"] != "DEPTH_CONTROLLED_FINITE_SEARCH_ONLY"):
                        raise ValueError("R25_E2_HOLD_NEW_BERSERK_FINITE_JUDGE")
                    depth_rows[str(depth)] = {"unrestricted": free,
                                              "frozen_policy": forced}
                rows.append({"opponent_reply": frozen["opponent_reply"],
                             "source_engine_rank": frozen["engine_rank"],
                             "frozen_own_move": own.uci(), "depths": depth_rows})
            aggregates = {}
            for depth in DEPTHS:
                key = str(depth)
                original = rroot["depth_evaluations"][key]
                if not original["all_legal_reply_plan_scores_finite"]:
                    raise ValueError("R25_E2_HOLD_ORIGINAL_FULL_MINIMUM_NOT_FINITE")
                aggregates[key] = {
                    "unrestricted": compare_minima(
                        min(x["depths"][key]["unrestricted"]["root_mover_cp"] for x in rows),
                        original["worst_unrestricted_judge_response_value_cp"]),
                    "frozen_policy": compare_minima(
                        min(x["depths"][key]["frozen_policy"]["root_mover_cp"] for x in rows),
                        original["worst_frozen_plan_value_cp"]),
                    "new_k3_nodes_unrestricted": sum(
                        x["depths"][key]["unrestricted"]["actual_nodes"] for x in rows),
                    "new_k3_nodes_frozen_plan": sum(
                        x["depths"][key]["frozen_policy"]["actual_nodes"] for x in rows),
                }
            roots.append({"root_uci": pair["root"], "full_legal_replies": len(pair["replies"]),
                          "ranked_k3_replies": rows, "depth_aggregates": aggregates})
        outcome.append({"case_id": source["case_id"],
                        "event_family": source["event_family"], "roots": roots})
    return {"schema": "c3x042-r25-e2-source-ranked-k3-native-berserk-v2",
            "status": "48_NEW_NATIVE_INDEPENDENT_SEARCHES_FINITE_DEPTH",
            "R24_B2_aggregate_sha256": B2_SHA,
            "Berserk_commit": FAMILY_COMMIT, "Berserk_net_sha256": NET_SHA,
            "E1_selection_frozen_before_R25_judge": True,
            "retrospective_exposed_historical_cases": True,
            "no_full_Cui_tree": True, "new_search_count": sum(
                len(root["ranked_k3_replies"]) * len(DEPTHS) * 2
                for case in outcome for root in case["roots"]),
            "node_budget_equalized": False, "exact_oracle_or_regret": False,
            "natural_root_causal_explanation": False, "cases": outcome}


def main():
    p = argparse.ArgumentParser()
    for arg in ("source", "predictions", "e1", "b2", "engine", "network", "out"):
        p.add_argument("--" + arg, required=True)
    a = p.parse_args()
    if sha(a.b2) != B2_SHA or sha(a.network) != NET_SHA:
        raise ValueError("R25_E2_HOLD_R24_B2_OR_BERSERK_NETWORK_SHA")
    e1 = json.loads(Path(a.e1).read_text(encoding="utf-8"))
    b2 = json.loads(Path(a.b2).read_text(encoding="utf-8"))
    originals = authentic_cases(
        authentic_archive(Path(a.predictions), PRED_ZIP_SHA, PRED_MEMBER, PRED_JSON_SHA),
        authentic_archive(Path(a.source), SOURCE_ZIP_SHA, SOURCE_MEMBER, SOURCE_JSON_SHA))
    worlds = source_positions(originals, FROZEN_EXPLORATORY_CASES)
    tasks = validate_join(e1, b2, worlds)
    with chess.engine.SimpleEngine.popen_uci(a.engine, timeout=180) as eng:
        if "berserk" not in eng.id.get("name", "").lower() or not {"Threads", "Hash"}.issubset(eng.options):
            raise ValueError("R25_E2_HOLD_DIFFERENT_JUDGE_ENGINE")
        eng.configure({"Threads": 1, "Hash": 16})
        result = judge(tasks, b2, eng)
    if result["new_search_count"] != 48:
        raise ValueError("R25_E2_HOLD_INCOMPLETE_NEW_SEARCHES")
    result["e1_file_sha256"] = sha(a.e1)
    result["Berserk_binary_sha256"] = sha(a.engine)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("R25_E2_NEW_NATIVE_SEARCHES", result["new_search_count"])
    for case in result["cases"]:
        for root in case["roots"]:
            for d, modes in root["depth_aggregates"].items():
                print("R25_E2_RESULT", case["event_family"], root["root_uci"], d,
                      "frozen", modes["frozen_policy"]["delta_k3_minus_full_cp"],
                      "unrestricted", modes["unrestricted"]["delta_k3_minus_full_cp"])


if __name__ == "__main__":
    main()
