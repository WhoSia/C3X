#!/usr/bin/env python3
"""C3X P42/R29-T1: source-only temporal chess events in immutable nearby paths.

Owned primary-method donor: Press & Golubev, BinProp (2026), original Drive PDF
https://drive.google.com/file/d/1gfmfug6814iYSEN3CkSF1xcsiG9uGTx6/view

Focus on *within-branch events*, not tautological changes in endpoint-only
features. Two complete plies after an identical R27 first-reply/own prefix:
opponent action then source own action. The eight predeclared event features
are computed entirely from chess-legal moves, never from judge cp.
R28 M1's SHA-frozen judge-defined positive/nearby-negative labels are joined
ONLY AFTER independent event extraction; source paths never reselected.

This is neither the LLM-discovered BinProp algorithm nor causal C3X root
mediation. Only two exposed historic games, four clustered roots, 12 pairs.
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

M1_SHA = "c8768b6ac02e62548a61e87f18bfa4d9406136316da9ae81ee296867aa2433e4"
FEATURES = (
    "opponent_second_captured",
    "opponent_second_gave_check",
    "source_second_captured",
    "source_second_gave_check",
    "source_second_immediate_recapture",
    "source_second_recovered_material_deficit",
    "source_second_moved_pawn",
    "source_second_promoted",
)
SCHEMA = "c3x042-r29-t1-source-temporal-tactical-nearby-v1"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def material(board, player):
    values = (0, 1, 3, 3, 5, 9, 0)
    return sum((len(board.pieces(p, player)) -
                len(board.pieces(p, not player))) * values[p]
               for p in (chess.PAWN, chess.KNIGHT, chess.BISHOP,
                         chess.ROOK, chess.QUEEN))


def temporal_events(leaf, mover):
    """Eight *path* features, not static leaf-state predicates."""
    if not isinstance(leaf, chess.Board) or len(leaf.move_stack) < 2:
        raise ValueError("R29_HOLD_FULL_LEGAL_PATH_REQUIRED")
    if leaf.turn != mover:
        raise ValueError("R29_HOLD_FINAL_TURN_IS_NOT_ORIGINAL_ROOT_MOVER")
    path = leaf.copy(stack=True)
    own = path.pop()
    opponent = path.pop()
    prefix = path
    if prefix.turn != (not mover):
        raise ValueError("R29_HOLD_OPPONENT_OWN_ACTION_ALTERNATION")
    before = material(prefix, mover)
    if opponent not in prefix.legal_moves:
        raise ValueError("R29_HOLD_OPPONENT_ACTION_ILLEGAL")
    opponent_captured = prefix.is_capture(opponent)
    opponent_dest = opponent.to_square
    path.push(opponent)
    opponent_gave_check = path.is_check()
    intermediate = material(path, mover)
    if path.turn != mover or own not in path.legal_moves:
        raise ValueError("R29_HOLD_SOURCE_ACTION_ILLEGAL")
    source_captured = path.is_capture(own)
    moved = path.piece_at(own.from_square)
    if moved is None or moved.color != mover:
        raise ValueError("R29_HOLD_SOURCE_PIECE_MISMATCH")
    source_recaptured = opponent_captured and source_captured and own.to_square == opponent_dest
    path.push(own)
    source_gave_check = path.is_check()
    final_material = material(path, mover)
    if path.fen(en_passant="fen") != leaf.fen(en_passant="fen"):
        raise ValueError("R29_HOLD_RECONSTRUCTED_PATH_POSITION_DRIFT")
    return {
        "opponent_second_captured": opponent_captured,
        "opponent_second_gave_check": opponent_gave_check,
        "source_second_captured": source_captured,
        "source_second_gave_check": source_gave_check,
        "source_second_immediate_recapture": source_recaptured,
        "source_second_recovered_material_deficit":
            intermediate < before and final_material >= before,
        "source_second_moved_pawn": moved.piece_type == chess.PAWN,
        "source_second_promoted": own.promotion is not None,
    }


def analyze(worlds, m1):
    if (m1.get("schema") != "c3x042-r28-m1-fixed-concept-nearby-negatives-v1"
        or m1.get("status") != "EXPLORATORY_FIXED_PREDICATE_NEARBY_NEGATIVE_AUDIT"
        or m1.get("source_tree_sha256") != TREE_SHA
        or m1.get("n_matched_first_reply_prefixes") != 12
        or m1.get("n_admitted_positive_nearby_negative_pairs") != 12
        or len(worlds) != 2):
        raise ValueError("R29_HOLD_M1_FROZEN_LABEL_CUSTODY")
    labels = {(row["event_family"], row["root_uci"], row["rank1"]): row
              for row in m1["nearby_groups"]}
    if len(labels) != 12:
        raise ValueError("R29_HOLD_M1_DUPLICATE_LABEL_KEY")
    seen = set()
    pairs = []
    for source, mover, roots in worlds:
        for root_uci, paths in roots:
            groups = {}
            for x in paths:
                key = (source["event_family"], root_uci, x["rank1"])
                events = temporal_events(x["board"], mover)
                if set(events) != set(FEATURES) or any(type(v) is not bool for v in events.values()):
                    raise ValueError("R29_HOLD_PREDEFINED_EVENT_SCHEMA")
                groups.setdefault(key, []).append({**{field: x[field] for field in (
                    "rank1", "rank2", "first_opponent_reply", "own_first",
                    "second_opponent_reply", "own_second")}, "events": events})
            for key, group in groups.items():
                if key in seen or len(group) != 3:
                    raise ValueError("R29_HOLD_DUPLICATE_OR_INCOMPLETE_PREFIX")
                seen.add(key)
                if len({(x["first_opponent_reply"], x["own_first"]) for x in group}) != 1:
                    raise ValueError("R29_HOLD_PREFIX_NOT_IDENTICAL")
                label = labels.get(key)
                if label is None or not label["admitted_minimum_gap"]:
                    raise ValueError("R29_HOLD_UNKNOWN_OR_UNADMITTED_LABEL")
                first = group[0]
                if (first["first_opponent_reply"] != label["shared_first_opponent_reply"]
                    or first["own_first"] != label["shared_own_first"]):
                    raise ValueError("R29_HOLD_SHARED_PREFIX_DRIFT")
                positive = [x for x in group if x["second_opponent_reply"] ==
                            label["positive_second_opponent_reply"]]
                negative = [x for x in group if x["second_opponent_reply"] ==
                            label["negative_second_opponent_reply"]]
                if len(positive) != 1 or len(negative) != 1 or positive[0] is negative[0]:
                    raise ValueError("R29_HOLD_POSITIVE_NEGATIVE_SOURCE_PATH_DRIFT")
                pos, neg = positive[0]["events"], negative[0]["events"]
                pairs.append({
                    "event_family": key[0], "root_uci": root_uci,
                    "first_rank": key[2],
                    "gap_cp_existing_judge": label["gap_cp"],
                    "same_source_prefix_verified": True,
                    "event_contrast": {
                        f: {"positive": pos[f], "nearby_negative": neg[f],
                            "positive_only": pos[f] and not neg[f],
                            "negative_only": neg[f] and not pos[f]}
                        for f in FEATURES},
                })
    if len(seen) != 12 or set(labels) != seen:
        raise ValueError("R29_HOLD_LABEL_SOURCE_EXHAUSTIVENESS")
    summaries = {}
    for f in FEATURES:
        summaries[f] = {
            "positive_only": sum(x["event_contrast"][f]["positive_only"] for x in pairs),
            "negative_only": sum(x["event_contrast"][f]["negative_only"] for x in pairs),
            "pairs": 12,
            "interpretation_is_exploratory_not_generalizable": True,
        }
    return {
        "schema": SCHEMA, "status": "EXPLORATORY_PREDECLARED_TEMPORAL_PATH_EVENTS",
        "r27_source_tree_sha256": TREE_SHA,
        "r28_M1_nearby_labels_sha256": M1_SHA,
        "reference_drive_paper": "https://drive.google.com/file/d/1gfmfug6814iYSEN3CkSF1xcsiG9uGTx6/view",
        "method": "source legal path events then frozen independent judge label contrast",
        "event_feature_count": len(FEATURES),
        "source_path_count": 36, "matched_prefix_count": len(pairs),
        "same_chess_root_history_for_matching": True,
        "historical_outcomes_already_observed": True,
        "no_new_chess_searches_or_judge_calls": True,
        "not_full_BinProp_or_prospective_or_causal": True,
        "feature_summaries": summaries, "matched_pairs": pairs,
    }


def main():
    p = argparse.ArgumentParser()
    for name in ("source", "predictions", "frozen-tree", "m1", "out"):
        p.add_argument("--" + name, required=True)
    a = p.parse_args()
    if digest(a.frozen_tree) != TREE_SHA or digest(a.m1) != M1_SHA:
        raise ValueError("R29_HOLD_FROZEN_SOURCE_OR_LABEL_BYTES")
    originals = authentic_cases(
        authentic_archive(Path(a.predictions), PRED_ZIP_SHA, PRED_MEMBER, PRED_JSON_SHA),
        authentic_archive(Path(a.source), SOURCE_ZIP_SHA, SOURCE_MEMBER, SOURCE_JSON_SHA))
    tree = json.loads(Path(a.frozen_tree).read_text(encoding="utf-8"))
    m1 = json.loads(Path(a.m1).read_text(encoding="utf-8"))
    cases = reconstruct(originals, tree)
    result = analyze(cases, m1)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("R29_T1_TEMPORAL_36_LEAVES_12_MATCHED_PREFIXES", flush=True)
    for feature, data in result["feature_summaries"].items():
        print("R29_T1_FEATURE", feature, "positive_only", data["positive_only"],
              "negative_only", data["negative_only"], flush=True)


if __name__ == "__main__":
    main()
