#!/usr/bin/env python3
"""C3X P42/R27-CUI-T1: actual TWO-OPPONENT-LAYER engine-ranked partial strategy tree.

Faithful to the *tree construction rule* of Cui, Ling & Ng (Findings EMNLP
2026, sec.4.1): at solver/player nodes, play engine best; at opponent nodes,
retain top k engine-ranked opponent moves. We construct a 4-ply continuation
AFTER each previously frozen alternative root (O,S,O,S), with k_strat=3.
This is NOT a reproduction of their LLM verbalizer, human/LLM evaluation, or
full puzzle benchmark. Historical R22-postselected two games, four roots.

No independent referee, new labels, or R25/R26 outcome is imported to choose
branches. All 147 first replies from R24 are only used for a source-universe
identity gate; R27 constructs its own additional source-contingent strategy.
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
from c3x_029_p42_r25_e1_engine_ranked_first_layer import (
    rank_opponent, SF_COMMIT)

SCHEMA = "c3x042-r27-cui-actual-recursive-k3-two-opponent-layer-v1"
K = 3
DEPTH = 12
AFTER_ROOT_PLIES = 4
EXPECTED_ROOTS = 4


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def best_player(board, eng, depth=DEPTH):
    """Return exact legal own best, actual nodes, or fail closed."""
    if board.is_game_over(claim_draw=False):
        raise ValueError("R27_HOLD_TERMINAL_PLAYER_NODE")
    info = eng.analyse(board, chess.engine.Limit(depth=depth),
                       game=object(), info=chess.engine.INFO_ALL)
    pv = info.get("pv")
    d, nodes = info.get("depth"), info.get("nodes")
    if (type(d) is not int or d < depth or type(nodes) is not int or nodes <= 0
        or not isinstance(pv, list) or not pv
        or not isinstance(pv[0], chess.Move) or pv[0] not in board.legal_moves):
        raise ValueError("R27_HOLD_PLAYER_BEST_DEPTH_NODES_PV")
    return {"own_move": pv[0].uci(), "own_nodes": nodes, "own_depth": d}


def build_two_layer(board_after_root, eng, k=K, depth=DEPTH):
    """Two opponent nodes along every response branch, then player response.

    Avoid fake complete-tree claims. Explicitly reject early terminal
    positions rather than silently dropping potentially important branches.
    Opponent MultiPV info may expose cumulative nodes: use last/max entry
    as query instrumentation, never sum over all MultiPV ranks.
    """
    if not 1 <= k <= 3:
        raise ValueError("R27_HOLD_UNSUPPORTED_K")
    if board_after_root.is_game_over(claim_draw=False):
        raise ValueError("R27_HOLD_TERMINAL_ROOT_CHILD")
    counters = {"opponent_engine_queries": 0, "player_engine_queries": 0,
                "opponent_multipv_nodes_reported": 0,
                "player_nodes_reported": 0}
    first = rank_opponent(board_after_root, eng, k=k, depth=depth)
    counters["opponent_engine_queries"] += 1
    counters["opponent_multipv_nodes_reported"] += max(
        r["ranking_nodes"] for r in first)
    branches = []
    for x in first:
        board1 = board_after_root.copy(stack=True)
        board1.push_uci(x["opponent_reply"])
        own1 = best_player(board1, eng, depth)
        counters["player_engine_queries"] += 1
        counters["player_nodes_reported"] += own1["own_nodes"]
        board1.push_uci(own1["own_move"])
        second = rank_opponent(board1, eng, k=k, depth=depth)
        counters["opponent_engine_queries"] += 1
        counters["opponent_multipv_nodes_reported"] += max(
            r["ranking_nodes"] for r in second)
        subbranches = []
        for y in second:
            board2 = board1.copy(stack=True)
            board2.push_uci(y["opponent_reply"])
            own2 = best_player(board2, eng, depth)
            counters["player_engine_queries"] += 1
            counters["player_nodes_reported"] += own2["own_nodes"]
            board2.push_uci(own2["own_move"])
            subbranches.append({
                "opponent_move_uci": y["opponent_reply"],
                "opponent_engine_rank": y["engine_rank"],
                "player_response_uci": own2["own_move"],
                "player_search_nodes": own2["own_nodes"],
                "leaf_full_history_ply_count": len(board2.move_stack)})
        branches.append({
            "opponent_move_uci": x["opponent_reply"],
            "opponent_engine_rank": x["engine_rank"],
            "player_response_uci": own1["own_move"],
            "player_search_nodes": own1["own_nodes"],
            "next_opponent_branches": subbranches})
    nleaves = sum(len(b["next_opponent_branches"]) for b in branches)
    if not branches or not nleaves:
        raise ValueError("R27_HOLD_TREE_EMPTY")
    return {"opponent_k": k, "continuation_plies_after_root": AFTER_ROOT_PLIES,
            "first_layer": branches, "leaf_paths": nleaves,
            "physical_search_accounting": counters,
            "multipv_accounting_caveat": "MultiPV node reports may be cumulative; per-query maximum is an estimate, not independently verified engine-internal node total."}


def build_cases(worlds, frozen, eng):
    verified = source_policy(worlds, frozen)
    cases = []
    for source, board, roots in verified:
        built = []
        for pair, old_prejudge in roots:
            root_child = board.copy(stack=True)
            root_child.push_uci(pair["root"])
            tree = build_two_layer(root_child, eng)
            old_action = {x["opponent_reply"]: x["own_uci"] for x in old_prejudge}
            if set(old_action) != set(pair["replies"]):
                raise ValueError("R27_HOLD_R24_SOURCE_UNIVERSE")
            for branch in tree["first_layer"]:
                reply = branch["opponent_move_uci"]
                if reply not in old_action:
                    raise ValueError("R27_HOLD_FIRST_LAYER_UNIVERSE")
                branch["R24_frozen_first_own_move"] = old_action[reply]
                branch["same_first_own_as_R24"] = (
                    branch["player_response_uci"] == old_action[reply])
            built.append({"root_uci": pair["root"],
                          "all_legal_first_opponent_replies": len(pair["replies"]),
                          **tree})
            print("R27_CUI_TWO_LAYER_BUILT", source["event_family"],
                  pair["root"], "leaves", tree["leaf_paths"], flush=True)
        cases.append({"case_id": source["case_id"],
                      "event_family": source["event_family"], "roots": built})
    return {
        "schema": SCHEMA,
        "status": "SOURCE_ONLY_ACTUAL_RECURSIVE_TWO_OPPONENT_LAYER_NO_JUDGE",
        "source_commit": SF_COMMIT, "use_nnue": False,
        "source_depth": DEPTH, "opponent_k": K,
        "after_root_ply_horizon": AFTER_ROOT_PLIES,
        "R24_prejudge_sha256": FROZEN_PLAN_SHA,
        "prior_Cui_method_section": "Cui et al 2026 sec 4.1, opponent ranked top k, player engine best",
        "Cui_tree_selection_rule_reproduced": True,
        "Cui_full_puzzle_verbalization_and_human_evaluation_reproduced": False,
        "preexisting_historical_roots_postselected": True,
        "independent_judge_consulted_to_build_tree": False,
        "causal_source_root_explanation": False,
        "cases": cases
    }


def main():
    p = argparse.ArgumentParser()
    for name in ("source", "predictions", "frozen-plan", "engine", "out"):
        p.add_argument("--" + name, required=True)
    args = p.parse_args()
    if digest(args.frozen_plan) != FROZEN_PLAN_SHA:
        raise ValueError("R27_HOLD_PREJUDGE_SHA")
    originals = authentic_cases(
        authentic_archive(Path(args.predictions), PRED_ZIP_SHA, PRED_MEMBER, PRED_JSON_SHA),
        authentic_archive(Path(args.source), SOURCE_ZIP_SHA, SOURCE_MEMBER, SOURCE_JSON_SHA))
    worlds = source_positions(originals, FROZEN_EXPLORATORY_CASES)
    frozen = json.loads(Path(args.frozen_plan).read_text(encoding="utf-8"))
    with chess.engine.SimpleEngine.popen_uci(args.engine, timeout=180) as eng:
        if ("stockfish" not in eng.id.get("name", "").lower()
            or not {"Threads", "Hash", "Use NNUE"}.issubset(eng.options)):
            raise ValueError("R27_HOLD_PINNED_SOURCE_ID")
        eng.configure({"Threads": 1, "Hash": 16, "Use NNUE": False})
        result = build_cases(worlds, frozen, eng)
    roots = [r for c in result["cases"] for r in c["roots"]]
    if len(roots) != EXPECTED_ROOTS:
        raise ValueError("R27_HOLD_FOUR_ORIGINAL_ROOTS")
    if any(r["leaf_paths"] != 9 for r in roots):
        raise ValueError("R27_HOLD_NONFULL_TWO_LAYER_K3")
    if any(r["physical_search_accounting"]["opponent_engine_queries"] != 4
           or r["physical_search_accounting"]["player_engine_queries"] != 12
           for r in roots):
        raise ValueError("R27_HOLD_PER_ROOT_ENGINE_QUERY_CONTRACT")
    result["source_binary_sha256"] = digest(args.engine)
    result["total_leaf_paths"] = sum(r["leaf_paths"] for r in roots)
    result["total_engine_queries"] = sum(
        r["physical_search_accounting"]["opponent_engine_queries"]
        + r["physical_search_accounting"]["player_engine_queries"]
        for r in roots)
    result["total_first_own_matches_R24"] = sum(
        b["same_first_own_as_R24"]
        for r in roots for b in r["first_layer"])
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("R27_CUI_STRATEGY_TREE_COMPLETE_SOURCE_ONLY",
          "roots", len(roots), "leaves", result["total_leaf_paths"],
          "native_queries", result["total_engine_queries"],
          "R24_own_matches", result["total_first_own_matches_R24"], "/12", flush=True)


if __name__ == "__main__":
    main()
