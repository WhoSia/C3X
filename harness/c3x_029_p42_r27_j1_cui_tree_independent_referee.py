#!/usr/bin/env python3
"""C3X P42/R27-J1: independent Berserk court for PRE-FROZEN recursive k=3 tree.

Source tree is raw-byte SHA locked from distinct previously successful native
R27 source-only run. Berserk is NEVER allowed to choose source branches.
Evaluate the 36 genuine 4-ply-after-root leaves at fixed depths 12 and 16,
scored from original root mover perspective. Compare same-horizon k1 path
to the worst across source-preselected k3^2 paths (not chess truth).
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
from c3x_029_p42_r22_berserk_fixed_depth_value_pilot import (
    quality, DEPTHS, NET_SHA, FAMILY_COMMIT)

TREE_SHA = "f41e96bbf598aa824e65467cd1f1c782674aa275460211ce02b68f6eff1d4d5e"
TREE_SCHEMA = "c3x042-r27-cui-actual-recursive-k3-two-opponent-layer-v1"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def reconstruct(originals, tree):
    if (tree.get("schema") != TREE_SCHEMA
        or tree.get("status") != "SOURCE_ONLY_ACTUAL_RECURSIVE_TWO_OPPONENT_LAYER_NO_JUDGE"
        or tree.get("independent_judge_consulted_to_build_tree") is not False
        or tree.get("opponent_k") != 3
        or tree.get("total_leaf_paths") != 36
        or tree.get("total_engine_queries") != 64):
        raise ValueError("R27_J1_HOLD_SOURCE_TREE_CUSTODY")
    worlds = source_positions(originals, FROZEN_EXPLORATORY_CASES)
    if len(worlds) != 2 or len(tree.get("cases", [])) != 2:
        raise ValueError("R27_J1_HOLD_CASE_COUNT")
    reconstructed = []
    for (source, board, pairs), case in zip(worlds, tree["cases"]):
        if (source["case_id"] != case["case_id"]
            or source["event_family"] != case["event_family"]
            or len(pairs) != len(case["roots"])):
            raise ValueError("R27_J1_HOLD_CASE_IDENTITY")
        roots = []
        for pair, candidate in zip(pairs, case["roots"]):
            if (pair["root"] != candidate["root_uci"]
                or len(candidate["first_layer"]) != 3
                or candidate["leaf_paths"] != 9
                or candidate["continuation_plies_after_root"] != 4):
                raise ValueError("R27_J1_HOLD_ROOT_IDENTITY")
            after_root = board.copy(stack=True)
            after_root.push_uci(pair["root"])
            if len({x["opponent_move_uci"] for x in candidate["first_layer"]}) != 3:
                raise ValueError("R27_J1_HOLD_DUPLICATE_FIRST_REPLY")
            paths = []
            for i, row in enumerate(candidate["first_layer"], 1):
                if row["opponent_engine_rank"] != i:
                    raise ValueError("R27_J1_HOLD_FIRST_ENGINE_RANK")
                first_reply = row["opponent_move_uci"]
                if first_reply not in pair["replies"]:
                    raise ValueError("R27_J1_HOLD_ORIGINAL_REPLY_UNIVERSE")
                first = after_root.copy(stack=True)
                for u in (first_reply, row["player_response_uci"]):
                    move = chess.Move.from_uci(u)
                    if move not in first.legal_moves:
                        raise ValueError("R27_J1_HOLD_FIRST_PATH_ILLEGAL")
                    first.push(move)
                subs = row["next_opponent_branches"]
                if (len(subs) != 3
                    or len({x["opponent_move_uci"] for x in subs}) != 3):
                    raise ValueError("R27_J1_HOLD_SECOND_BRANCH_UNIVERSE")
                for j, branch in enumerate(subs, 1):
                    if branch["opponent_engine_rank"] != j:
                        raise ValueError("R27_J1_HOLD_SECOND_ENGINE_RANK")
                    leaf = first.copy(stack=True)
                    for u in (branch["opponent_move_uci"], branch["player_response_uci"]):
                        move = chess.Move.from_uci(u)
                        if move not in leaf.legal_moves:
                            raise ValueError("R27_J1_HOLD_SECOND_PATH_ILLEGAL")
                        leaf.push(move)
                    if leaf.is_game_over(claim_draw=False):
                        raise ValueError("R27_J1_HOLD_TERMINAL_LEAF_REQUIRES_RULE_EXACT")
                    paths.append({"rank1": i, "rank2": j,
                                  "first_opponent_reply": first_reply,
                                  "own_first": row["player_response_uci"],
                                  "second_opponent_reply": branch["opponent_move_uci"],
                                  "own_second": branch["player_response_uci"],
                                  "board": leaf})
            if len(paths) != 9:
                raise ValueError("R27_J1_HOLD_NINE_PATHS")
            roots.append((pair["root"], paths))
        reconstructed.append((source, board.turn, roots))
    return reconstructed


def evaluate(cases, eng):
    result = []
    for source, original_turn, roots in cases:
        out_roots = []
        for root_uci, paths in roots:
            judged = []
            for x in paths:
                scores = {}
                for depth in DEPTHS:
                    info = eng.analyse(x["board"], chess.engine.Limit(depth=depth),
                                       game=object(), info=chess.engine.INFO_ALL)
                    quality_row = quality(x["board"], info, depth, original_turn)
                    if quality_row["status"] != "DEPTH_CONTROLLED_FINITE_SEARCH_ONLY":
                        raise ValueError("R27_J1_HOLD_NONFINITE_LEAF_SCORE")
                    scores[str(depth)] = quality_row
                judged.append({k: v for k, v in x.items() if k != "board"}
                              | {"depths": scores})
            per_depth = {}
            for d in DEPTHS:
                key = str(d)
                all_values = [(x["depths"][key]["root_mover_cp"], x) for x in judged]
                best1 = next(x for x in judged if x["rank1"] == 1 and x["rank2"] == 1)
                minimum = min(v for v, _ in all_values)
                worst = [x for v, x in all_values if v == minimum]
                per_depth[key] = {
                    "single_principal_rank1_rank1_cp": best1["depths"][key]["root_mover_cp"],
                    "worst_over_nine_source_ranked_paths_cp": minimum,
                    "single_line_minus_all_nine_worst_cp":
                        best1["depths"][key]["root_mover_cp"] - minimum,
                    "at_least_one_worst_path_off_principal": any(
                        x["rank1"] != 1 or x["rank2"] != 1 for x in worst),
                    "worst_rank_pairs": [[x["rank1"], x["rank2"]] for x in worst],
                    "actual_judge_nodes_total": sum(
                        x["depths"][key]["actual_nodes"] for x in judged)}
            out_roots.append({"root_uci": root_uci,
                              "source_tree_leaf_paths": 9,
                              "independently_judged_paths": judged,
                              "depth_summaries": per_depth})
            print("R27_J1_REFEREE_ROOT", source["event_family"], root_uci,
                  "d16_k1_minus_worst", per_depth["16"]["single_line_minus_all_nine_worst_cp"],
                  flush=True)
        result.append({"case_id": source["case_id"],
                       "event_family": source["event_family"],
                       "roots": out_roots})
    return {
        "schema": "c3x042-r27-j1-cui-two-layer-independent-9-path-referee-v1",
        "status": "SOURCE_PREJUDGE_TREE_INDEPENDENTLY_JUDGED_FINITE_DEPTH",
        "source_tree_sha256": TREE_SHA,
        "berserk_commit": FAMILY_COMMIT, "berserk_nnue_sha256": NET_SHA,
        "independent_referee_selected_source_branches": False,
        "source_tree_historical_postselected": True,
        "complete_puzzle_study_reproduced": False,
        "node_equalized_or_exact_minimax": False,
        "same_world_causal_computation_identified": False,
        "new_native_search_count": sum(len(r["independently_judged_paths"]) * len(DEPTHS)
                                       for c in result for r in c["roots"]),
        "cases": result
    }


def main():
    p = argparse.ArgumentParser()
    for a in ("source", "predictions", "frozen-tree", "engine", "network", "out"):
        p.add_argument("--" + a, required=True)
    args = p.parse_args()
    if sha(args.frozen_tree) != TREE_SHA or sha(args.network) != NET_SHA:
        raise ValueError("R27_J1_HOLD_FROZEN_TREE_OR_JUDGE_NET_SHA")
    original = authentic_cases(
        authentic_archive(Path(args.predictions), PRED_ZIP_SHA, PRED_MEMBER, PRED_JSON_SHA),
        authentic_archive(Path(args.source), SOURCE_ZIP_SHA, SOURCE_MEMBER, SOURCE_JSON_SHA))
    tree = json.loads(Path(args.frozen_tree).read_text(encoding="utf-8"))
    cases = reconstruct(original, tree)
    with chess.engine.SimpleEngine.popen_uci(args.engine, timeout=180) as eng:
        if ("berserk" not in eng.id.get("name", "").lower()
            or not {"Threads", "Hash"}.issubset(eng.options)):
            raise ValueError("R27_J1_HOLD_REFEREE_ENGINE_FAMILY")
        eng.configure({"Threads": 1, "Hash": 16})
        result = evaluate(cases, eng)
    if result["new_native_search_count"] != 72:
        raise ValueError("R27_J1_HOLD_EXPECTED_72_NATIVE_SEARCHES")
    result["berserk_binary_sha256"] = sha(args.engine)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("R27_J1_INDEPENDENT_CUI_TREE_9_BRANCH_COURT",
          result["new_native_search_count"], "NATIVE", flush=True)


if __name__ == "__main__":
    main()
