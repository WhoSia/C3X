#!/usr/bin/env python3
"""C3X P42/R28-M1: PREDEFINED chess concept audit using nearby negative leaves.

Prior-art donor: Press & Golubev 2026 BinProp, ORIGINAL DRIVE PDF
https://drive.google.com/file/d/1gfmfug6814iYSEN3CkSF1xcsiG9uGTx6/view

This is NOT full BinProp: no LLM proposal, no 200k contrastive corpus,
no trained/discovered predicate claims. We use fixed human-readable chess
predicates and evaluate them on the immutable R27 source-selected 36 leaves,
whose judge scores are SHA-frozen. Group three leaf paths sharing the exact
first opponent reply and first own response; select higher and lower cp judge
leaf as matched positive/nearby negative ONLY when score separation >= 10cp.
No source move, rank, or judge score enters the chess predicate itself.
Historical cases 2 / roots 4 are adaptation-exposed and clustered.
"""
import argparse
import hashlib
import json
from pathlib import Path

import chess
from c3x_029_p42_r27_j1_cui_tree_independent_referee import reconstruct, TREE_SHA
from c3x_029_p38_r1_ethereal_independent_referee import (
    authentic_archive, authentic_cases, SOURCE_ZIP_SHA, SOURCE_MEMBER,
    SOURCE_JSON_SHA, PRED_ZIP_SHA, PRED_MEMBER, PRED_JSON_SHA)

JUDGE_SHA = "9844ebb1cae67d1af82c19696c8037ab53ca46b602ea44cdd66fc02d32ee27b7"
GAP_CP = 10
PIECE_VALUE = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
               chess.ROOK: 5, chess.QUEEN: 9}
FEATURES = (
    "material_ahead", "material_not_behind", "bishop_pair",
    "rook_on_open_file", "rook_on_semi_open_file",
    "passed_pawn", "opponent_king_in_check", "has_queen",
)
SCHEMA = "c3x042-r28-m1-fixed-concept-nearby-negatives-v1"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def feature_vector(board, mover):
    """Pure, predefined perspective-aware board predicates, no referee read."""
    if not isinstance(board, chess.Board) or mover not in (chess.WHITE, chess.BLACK):
        raise ValueError("R28_HOLD_BAD_BOARD_OR_ROOT_PERSPECTIVE")
    def points(color):
        return sum(len(board.pieces(p, color)) * v for p, v in PIECE_VALUE.items())
    advantage = points(mover) - points(not mover)
    my_rooks = board.pieces(chess.ROOK, mover)
    our_pawns = board.pieces(chess.PAWN, mover)
    opp_pawns = board.pieces(chess.PAWN, not mover)
    def own_file_pawn_exists(file):
        return any(chess.square_file(sq) == file for sq in our_pawns)
    def enemy_file_pawn_exists(file):
        return any(chess.square_file(sq) == file for sq in opp_pawns)
    def passed(pawn_sq):
        file, rank = chess.square_file(pawn_sq), chess.square_rank(pawn_sq)
        for enemy in opp_pawns:
            ef, er = chess.square_file(enemy), chess.square_rank(enemy)
            ahead = er > rank if mover == chess.WHITE else er < rank
            if abs(file - ef) <= 1 and ahead:
                return False
        return True
    values = {
        "material_ahead": advantage > 0,
        "material_not_behind": advantage >= 0,
        "bishop_pair": len(board.pieces(chess.BISHOP, mover)) >= 2,
        "rook_on_open_file": any(
            not own_file_pawn_exists(chess.square_file(sq))
            and not enemy_file_pawn_exists(chess.square_file(sq))
            for sq in my_rooks),
        "rook_on_semi_open_file": any(
            not own_file_pawn_exists(chess.square_file(sq))
            and enemy_file_pawn_exists(chess.square_file(sq))
            for sq in my_rooks),
        "passed_pawn": any(passed(sq) for sq in our_pawns),
        "opponent_king_in_check": board.is_check() and board.turn != mover,
        "has_queen": len(board.pieces(chess.QUEEN, mover)) > 0,
    }
    if set(values) != set(FEATURES):
        raise ValueError("R28_HOLD_PREDICATE_SCHEMA")
    return values


def audit(worlds, judged):
    """Join two SHA-frozen artifacts without using score labels to define predicates."""
    if (judged.get("schema") != "c3x042-r27-j1-cui-two-layer-independent-9-path-referee-v1"
        or judged.get("source_tree_sha256") != TREE_SHA
        or judged.get("new_native_search_count") != 72
        or len(worlds) != len(judged.get("cases", []))):
        raise ValueError("R28_HOLD_SOURCE_JUDGE_JOIN")
    observations = []
    records = []
    for (source, root_side, roots), case in zip(worlds, judged["cases"]):
        if source["case_id"] != case["case_id"] or source["event_family"] != case["event_family"]:
            raise ValueError("R28_HOLD_CASE_IDENTITY")
        if len(roots) != len(case["roots"]):
            raise ValueError("R28_HOLD_ROOT_SUPPORT")
        for (root_name, paths), row in zip(roots, case["roots"]):
            if root_name != row["root_uci"] or len(paths) != len(row["independently_judged_paths"]) != 9:
                raise ValueError("R28_HOLD_ROOT_OR_LEAF_COUNT")
            by_rank = {(x["rank1"], x["rank2"]): x for x in row["independently_judged_paths"]}
            if len(by_rank) != 9:
                raise ValueError("R28_HOLD_DUPLICATE_RANK_PAIR")
            groups = {}
            for x in paths:
                key = (x["rank1"], x["rank2"])
                judge = by_rank.get(key)
                if judge is None or any(x[field] != judge[field] for field in (
                    "first_opponent_reply", "own_first", "second_opponent_reply",
                    "own_second")):
                    raise ValueError("R28_HOLD_LEGAL_PATH_AND_SCORE_CUSTODY")
                if "16" not in judge["depths"]:
                    raise ValueError("R28_HOLD_MISSING_DEPTH16")
                value = judge["depths"]["16"]["root_mover_cp"]
                if type(value) is not int:
                    raise ValueError("R28_HOLD_NONFINITE_CP")
                observations.append({
                    "event_family": source["event_family"],
                    "root_uci": root_name, "rank1": x["rank1"], "rank2": x["rank2"],
                    "first_opponent_reply": x["first_opponent_reply"],
                    "own_first": x["own_first"],
                    "second_opponent_reply": x["second_opponent_reply"],
                    "own_second": x["own_second"],
                    "referee_depth16_root_mover_cp": value,
                    "features": feature_vector(x["board"], root_side),
                })
                groups.setdefault(x["rank1"], []).append(observations[-1])
            if len(groups) != 3 or any(len(v) != 3 for v in groups.values()):
                raise ValueError("R28_HOLD_NEARBY_GROUP_UNIVERSE")
            for rank1, group in sorted(groups.items()):
                if len({(x["first_opponent_reply"], x["own_first"]) for x in group}) != 1:
                    raise ValueError("R28_HOLD_NOT_NEARBY_SAME_FIRST_PREFIX")
                high = max(group, key=lambda x: (x["referee_depth16_root_mover_cp"], -x["rank2"]))
                low = min(group, key=lambda x: (x["referee_depth16_root_mover_cp"], x["rank2"]))
                gap = high["referee_depth16_root_mover_cp"] - low["referee_depth16_root_mover_cp"]
                records.append({
                    "event_family": source["event_family"], "root_uci": root_name,
                    "rank1": rank1, "shared_first_opponent_reply": high["first_opponent_reply"],
                    "shared_own_first": high["own_first"],
                    "positive_second_opponent_reply": high["second_opponent_reply"],
                    "negative_second_opponent_reply": low["second_opponent_reply"],
                    "positive_cp": high["referee_depth16_root_mover_cp"],
                    "nearby_negative_cp": low["referee_depth16_root_mover_cp"],
                    "gap_cp": gap, "admitted_minimum_gap": gap >= GAP_CP,
                    "predicate_contrasts": {
                        key: {"positive": high["features"][key],
                              "negative": low["features"][key],
                              "separates_positive_from_nearby_negative":
                                  high["features"][key] and not low["features"][key]}
                        for key in FEATURES}
                })
    if len(observations) != 36 or len(records) != 12:
        raise ValueError("R28_HOLD_FULL_36_LEAF_12_PREFIX_AUDIT")
    admitted = [row for row in records if row["admitted_minimum_gap"]]
    per_feature = {}
    for feature in FEATURES:
        eligible = [x for x in admitted if x["predicate_contrasts"][feature][
            "separates_positive_from_nearby_negative"]]
        false_positives = [x for x in admitted if x["predicate_contrasts"][feature]["negative"]]
        per_feature[feature] = {
            "eligible_nearby_groups": len(admitted),
            "positive_only_separation_count": len(eligible),
            "negative_firing_count": len(false_positives),
            "score_is_posthoc_on_same_historical_cases": True,
        }
    return {
        "schema": SCHEMA, "status": "EXPLORATORY_FIXED_PREDICATE_NEARBY_NEGATIVE_AUDIT",
        "source_tree_sha256": TREE_SHA, "judge_leaf_sha256": JUDGE_SHA,
        "prior_art_source_pdf_drive": "https://drive.google.com/file/d/1gfmfug6814iYSEN3CkSF1xcsiG9uGTx6/view",
        "not_reproduced_full_BinProp": True,
        "fixed_predicates_predefined_without_judge_labels": True,
        "positive_nearby_negative_selection_does_use_judge_labels": True,
        "two_historical_games_postselected": True,
        "identical_first_opponent_and_player_prefix": True,
        "source_tree_after_root_plies": 4,
        "positive_negative_threshold_cp": GAP_CP,
        "n_source_tree_leaves": len(observations),
        "n_matched_first_reply_prefixes": len(records),
        "n_admitted_positive_nearby_negative_pairs": len(admitted),
        "feature_summaries": per_feature, "nearby_groups": records,
        "no_train_test_claim": True, "no_causal_source_state_or_robust_motif_claim": True,
    }


def main():
    p = argparse.ArgumentParser()
    for name in ("source", "predictions", "frozen-tree", "frozen-judge", "out"):
        p.add_argument("--" + name, required=True)
    args = p.parse_args()
    if sha(args.frozen_tree) != TREE_SHA or sha(args.frozen_judge) != JUDGE_SHA:
        raise ValueError("R28_HOLD_FROZEN_SOURCE_OR_JUDGE_BYTES")
    original = authentic_cases(
        authentic_archive(Path(args.predictions), PRED_ZIP_SHA, PRED_MEMBER, PRED_JSON_SHA),
        authentic_archive(Path(args.source), SOURCE_ZIP_SHA, SOURCE_MEMBER, SOURCE_JSON_SHA))
    frozen_tree = json.loads(Path(args.frozen_tree).read_text(encoding="utf-8"))
    judge = json.loads(Path(args.frozen_judge).read_text(encoding="utf-8"))
    valid = reconstruct(original, frozen_tree)
    output = audit(valid, judge)
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("R28_BINPROP_INSPIRED_FIXED_FEATURES", output["n_source_tree_leaves"],
          "LEAVES", output["n_matched_first_reply_prefixes"], "MATCHED_PREFIXES",
          output["n_admitted_positive_nearby_negative_pairs"], "ADMITTED", flush=True)
    for key, item in output["feature_summaries"].items():
        print("R28_PREDECLARED_FEATURE", key,
              "separates", item["positive_only_separation_count"],
              "of", item["eligible_nearby_groups"], flush=True)


if __name__ == "__main__":
    main()
