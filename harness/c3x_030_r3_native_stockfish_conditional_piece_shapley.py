#!/usr/bin/env python3
"""C3X 0.30 R3 — original Stockfish + exact 3-piece conditional SHAP pilot.

Primary original held in Google Drive:
https://drive.google.com/file/d/1xDaJ9bBxNYtxVU7YsNOqHvHuLMtQ149o/view
Spinnato (2025), piece-by-piece explanations using SHAP, section 3.

Build on *the same authentic historical chess boards* as 0.29 R30-D,
but score entire positions (not forced root actions), using original
Stockfish 16 classical and a fixed depth. Find the lexicographically first
3 nonking pieces such that all 2^3 removals produce python-chess-valid,
nonterminal boards. Remove unused original history from all variants,
preserve side and metadata, and run actual source engine on ALL masks.

Conditional value function v(S) = logistic(beta * white_cp_of_board_with
only_selected_pieces_in_S_and_all_other_original_pieces_held_fixed).
The resulting Shapley values are exact for those 3 CONDITIONAL features,
but NOT the original Spinnato full-piece game (king-only baseline),
original Stockfish 17.1 or SamplingExplainer 10000 benchmark.

These removed-piece states need not be reachable by real chess moves.
Search depth is held fixed, native node/time counts are NOT equalized.
Mate is represented by an explicit, arbitrary ±10000 cp surrogate, count
each such occurrence and never claim a true chess win probability.
No original engine source-level decision intervention or prospective cohort.
"""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

import chess
import chess.engine

from c3x_029_p38_r1_ethereal_independent_referee import (
    authentic_archive, authentic_cases, SOURCE_ZIP_SHA, SOURCE_MEMBER,
    SOURCE_JSON_SHA, PRED_ZIP_SHA, PRED_MEMBER, PRED_JSON_SHA)
from c3x_029_p42_r23_independent_all_opponent_reply_value_court import (
    FROZEN_EXPLORATORY_CASES, source_positions)
from c3x_029_p42_r25_e1_engine_ranked_first_layer import SF_COMMIT
from c3x_030_r2_exact_piece_shapley_kernel import shapley_exact

SCHEMA = "c3x030-r3-native-stockfish-conditional-3piece-shapley-v1"
N_FEATURES = 3
DEPTH = 10
BETA_PER_CP = 0.00368
MATE_SURROGATE_CP = 10000


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def static_board(board):
    result = board.copy(stack=True)
    result.clear_stack()
    if not result.is_valid() or result.is_game_over(claim_draw=False):
        raise ValueError("R030_R3_HOLD_ORIGINAL_BOARD_INVALID_OR_TERMINAL")
    return result


def coalition_board(original, squares, mask):
    """Preserve every nonchosen piece + chosen pieces present in the mask."""
    if not 0 <= mask < 1 << len(squares):
        raise ValueError("R030_R3_HOLD_COALITION_MASK_RANGE")
    board = original.copy(stack=False)
    for i, sq in enumerate(squares):
        if not mask & (1 << i):
            board.remove_piece_at(sq)
    if not board.is_valid() or board.is_game_over(claim_draw=False):
        raise ValueError("R030_R3_HOLD_COALITION_NOT_VALID_OR_TERMINAL")
    return board


def choose_complete_three(original):
    """Selection strictly based on legality, never engine values or outcomes."""
    base = static_board(original)
    nonking = [sq for sq in chess.SQUARES if
               (p := base.piece_at(sq)) is not None
               and p.piece_type != chess.KING]
    for triple in itertools.combinations(nonking, N_FEATURES):
        try:
            boards = [coalition_board(base, triple, mask)
                      for mask in range(1 << N_FEATURES)]
        except ValueError:
            continue
        if len({b.fen(en_passant="fen") for b in boards}) != 8:
            raise ValueError("R030_R3_HOLD_NONUNIQUE_SUBSET_POSITION")
        return triple, boards
    raise ValueError("R030_R3_HOLD_NO_THREE_PIECE_COMPLETE_VALID_LATTICE")


def white_win_probability(cp):
    if type(cp) is not int:
        raise ValueError("R030_R3_HOLD_NOT_INTEGER_WHITE_CP")
    x = BETA_PER_CP * cp
    return (1.0 / (1.0 + math.exp(-x)) if x >= 0
            else math.exp(x) / (1.0 + math.exp(x)))


def native_evaluate(board, engine):
    info = engine.analyse(board, chess.engine.Limit(depth=DEPTH),
                          game=object(), info=chess.engine.INFO_ALL)
    score = info.get("score")
    if (type(info.get("depth")) is not int or info["depth"] < DEPTH
        or type(info.get("nodes")) is not int or info["nodes"] <= 0
        or score is None):
        raise ValueError("R030_R3_HOLD_INCOMPLETE_NATIVE_SCORE")
    white = score.white()
    mate = white.is_mate()
    cp = white.score(mate_score=MATE_SURROGATE_CP)
    if type(cp) is not int:
        raise ValueError("R030_R3_HOLD_UNSCORABLE_MATE_PROXY")
    return {
        "white_score_cp_or_arbitrary_mate_surrogate": cp,
        "is_mate_score": mate,
        "mate_plies": white.mate() if mate else None,
        "white_win_logistic_proxy": white_win_probability(cp),
        "actual_search_depth": info["depth"],
        "actual_search_nodes": info["nodes"],
    }


def run(worlds, engine):
    cases = []
    for source, original, roots in worlds:
        squares, boards = choose_complete_three(original)
        names = [base for sq in squares
                 for base in [chess.square_name(sq) + ":" +
                              original.piece_at(sq).symbol()]]
        metrics = [native_evaluate(b, engine) for b in boards]
        values = {str(i): row["white_win_logistic_proxy"]
                  for i, row in enumerate(metrics)}
        shapley = shapley_exact(names, values)
        if len(metrics) != 8 or abs(shapley["efficiency_residual"]) > 1e-10:
            raise ValueError("R030_R3_HOLD_SHAPLEY_COMPLETE_EXACT_LATTICE")
        cases.append({
            "case_id": source["case_id"], "event_family": source["event_family"],
            "original_chess_turn": "white" if original.turn else "black",
            "inherited_two_candidate_roots": [p["root"] for p in roots],
            "selected_piece_names": names,
            "all_subset_positions_are_python_chess_valid": True,
            "baseline_is_conditional_not_two_kings": True,
            "masked_coalition_evaluations": [
                {"mask": i, "n_retained_selected_pieces": i.bit_count(),
                 "evaluation": metrics[i]} for i in range(8)],
            "conditional_shapley": shapley,
            "native_search_queries": 8,
            "native_search_nodes": sum(x["actual_search_nodes"] for x in metrics),
            "mate_score_surrogate_occurrences": sum(x["is_mate_score"] for x in metrics),
        })
        print("R030_R3_NATIVE_PIECE_SHAPLEY", source["event_family"],
              "features", names,
              "white_proxy_baseline", shapley["baseline_coalition_value"],
              "white_proxy_full", shapley["complete_coalition_value"],
              "nodes", cases[-1]["native_search_nodes"], flush=True)
    return {
        "schema": SCHEMA,
        "status": "REAL_NATIVE_SOURCE_EXACT_CONDITIONAL_3PIECE_SHAPLEY_PILOT",
        "primary_spinnato_drive_pdf": "https://drive.google.com/file/d/1xDaJ9bBxNYtxVU7YsNOqHvHuLMtQ149o/view",
        "inherited_R2_exact_kernel": "harness/c3x_030_r2_exact_piece_shapley_kernel.py",
        "inherited_R30_SARFA_pilot": "C3X_029_P42_R30_D",
        "original_source_commit": SF_COMMIT,
        "source_nnue_enabled": False,
        "fixed_depth": DEPTH,
        "logistic_beta_per_cp": BETA_PER_CP,
        "score_is_uncalibrated_win_proxy": True,
        "mate_surrogate_cp": MATE_SURROGATE_CP,
        "mate_surrogate_arbitrary": True,
        "two_historical_adaptively_selected_chess_games": True,
        "full_history_cleared_for_all_static_chess_subsets": True,
        "not_full_spinnato_piece_SHAP_benchmark": True,
        "not_original_king_only_coalition_baseline": True,
        "no_naturally_reachable_chess_counterfactual_guarantee": True,
        "not_source_mechanism_intervention_or_root_mediation": True,
        "not_prospective": True,
        "cases": cases,
        "total_actual_native_search_queries": sum(c["native_search_queries"] for c in cases),
        "total_actual_native_nodes": sum(c["native_search_nodes"] for c in cases),
        "total_mate_surrogate_occurrences": sum(c["mate_score_surrogate_occurrences"] for c in cases),
    }


def main():
    p = argparse.ArgumentParser()
    for name in ("source", "predictions", "engine", "out"):
        p.add_argument("--" + name, required=True)
    args = p.parse_args()
    originals = authentic_cases(
        authentic_archive(Path(args.predictions), PRED_ZIP_SHA, PRED_MEMBER, PRED_JSON_SHA),
        authentic_archive(Path(args.source), SOURCE_ZIP_SHA, SOURCE_MEMBER, SOURCE_JSON_SHA))
    worlds = source_positions(originals, FROZEN_EXPLORATORY_CASES)
    with chess.engine.SimpleEngine.popen_uci(args.engine, timeout=180) as engine:
        if ("stockfish" not in engine.id.get("name", "").lower()
            or not {"Threads", "Hash", "Use NNUE"}.issubset(engine.options)):
            raise ValueError("R030_R3_HOLD_PINNED_STOCKFISH_FAMILY")
        engine.configure({"Threads": 1, "Hash": 16, "Use NNUE": False})
        data = run(worlds, engine)
    if len(data["cases"]) != 2 or data["total_actual_native_search_queries"] != 16:
        raise ValueError("R030_R3_HOLD_EXACT_16_QUERIES_TWO_HISTORIC_WORLDS")
    data["original_engine_executable_sha256"] = sha(args.engine)
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False)+"\n",
                    encoding="utf-8")
    print("R030_R3_ACTUAL_STOCKFISH_COMPLETE_16_SEARCHES",
          data["total_actual_native_nodes"], "nodes", flush=True)


if __name__ == "__main__":
    main()
