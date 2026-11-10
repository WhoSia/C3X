#!/usr/bin/env python3
"""C3X P42/R30-D: genuine Stockfish SARFA *method pilot*, not root causation.

Original SARFA owned paper: ICLR2020 arXiv:1912.12191v4
https://drive.google.com/file/d/1C_c0AvNkEtzB2z6Nbji_NdRxlRpODgjs/view

Use two exposed R23/R27 historical chess positions, select R23's two
frozen alternative roots plus deterministic legal third UCI control.
From original source Stockfish16 classical, force each root action
individually at depth10, and repeat after removing three deterministically
eligible nonking pieces, requiring is_valid() and identical LEGAL candidate
support. This reproduces a *piece-removal saliency probe* as in SARFA,
not naturally reachable chess-game counterfactuals, no causal mechanism,
no human chess-saliency validation, no calibrated RL Q-values.

All engines run isolated in read-only CI. No python-chess in Chat runtime.
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
from c3x_029_p42_r30_sarfa_section2_kernel import sarfa
from c3x_029_p42_r25_e1_engine_ranked_first_layer import SF_COMMIT

SCHEMA = "c3x042-r30-d-source-native-sarfa-paper-piece-removal-v1"
DEPTH = 10
N_REMOVALS = 3
TEMPERATURE_CP = 100.0


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def support_three(board, roots):
    legal = sorted(m.uci() for m in board.legal_moves)
    nominated = [x["root"] for x in roots]
    if (len(nominated) != 2 or len(set(nominated)) != 2
        or not set(nominated).issubset(legal) or len(legal) < 3):
        raise ValueError("R30_D_HOLD_TWO_SOURCE_ROOTS_AND_THIRD_LEGAL")
    third = next((u for u in legal if u not in nominated), None)
    if third is None:
        raise ValueError("R30_D_HOLD_NO_THIRD_ACTION_CONTROL")
    return nominated + [third]


def supported_removals(board, support, count=N_REMOVALS):
    """Deterministic, original-position-only selection, no scores consulted."""
    candidates = []
    occupied_action_squares = set()
    for u in support:
        m = chess.Move.from_uci(u)
        occupied_action_squares.update((m.from_square, m.to_square))
    base = board.copy(stack=True)
    base.clear_stack()  # remove stale UCI game history for BOTH conditions
    if not base.is_valid():
        raise ValueError("R30_D_HOLD_ORIGINAL_STATIC_BOARD_INVALID")
    for sq in chess.SQUARES:
        piece = base.piece_at(sq)
        if piece is None or piece.piece_type == chess.KING or sq in occupied_action_squares:
            continue
        perturbed = base.copy(stack=False)
        perturbed.remove_piece_at(sq)
        if (not perturbed.is_valid() or perturbed.turn != base.turn
            or any(chess.Move.from_uci(u) not in perturbed.legal_moves for u in support)
            or perturbed.is_game_over(claim_draw=False)):
            continue
        candidates.append((sq, perturbed))
        if len(candidates) >= count:
            return base, candidates
    raise ValueError("R30_D_HOLD_NOT_ENOUGH_VALID_PAPER_ABLATIONS")


def forced_q(board, support, eng, depth=DEPTH):
    if not board.is_valid() or board.is_game_over(claim_draw=False):
        raise ValueError("R30_D_HOLD_Q_ON_INVALID_STATIC_BOARD")
    scores = {}
    nodes = 0
    for u in support:
        move = chess.Move.from_uci(u)
        if move not in board.legal_moves:
            raise ValueError("R30_D_HOLD_ROOT_ACTION_SUPPORT_CHANGED")
        info = eng.analyse(board, chess.engine.Limit(depth=depth), root_moves=[move],
                           game=object(), info=chess.engine.INFO_ALL)
        pv = info.get("pv")
        value = info.get("score")
        if (type(info.get("depth")) is not int or info["depth"] < depth
            or type(info.get("nodes")) is not int or info["nodes"] <= 0
            or not isinstance(pv, list) or not pv or pv[0] != move
            or value is None or value.pov(board.turn).is_mate()
            or type(value.pov(board.turn).score()) is not int):
            raise ValueError("R30_D_HOLD_FINITE_FORCED_SOURCE_Q")
        scores[u] = value.pov(board.turn).score()
        nodes += info["nodes"]
    return scores, nodes


def run(worlds, eng):
    cases = []
    for source, board, roots in worlds:
        support = support_three(board, roots)
        static, perturbations = supported_removals(board, support)
        original, original_nodes = forced_q(static, support, eng)
        trials = []
        for sq, changed in perturbations:
            changed_q, changed_nodes = forced_q(changed, support, eng)
            attrib = {u: sarfa(original, changed_q, u, TEMPERATURE_CP)
                      for u in support[:2]}
            trials.append({
                "removed_piece_square": chess.square_name(sq),
                "removed_piece": board.piece_at(sq).symbol(),
                "original_support_preserved": True,
                "changed_q_root_mover_cp": changed_q,
                "source_forced_nodes": changed_nodes,
                "sarfa_for_two_original_frozen_root_alternatives": attrib,
            })
        cases.append({
            "case_id": source["case_id"], "event_family": source["event_family"],
            "two_original_alternative_roots": support[:2],
            "third_control_root": support[2],
            "support_count": len(support),
            "original_forced_q_root_mover_cp": original,
            "original_forced_nodes": original_nodes,
            "perturbations": trials,
        })
        print("R30_D_REAL_SARFA_PILOT", source["event_family"],
              "three_root_Q", original, "removals", len(trials), flush=True)
    return {
        "schema": SCHEMA, "status": "REAL_SOURCE_CHESS_PIECE_ABLATION_METHOD_PILOT_ONLY",
        "source_commit": SF_COMMIT, "source_nnue": False,
        "source_forced_depth": DEPTH, "cp_to_softmax_temperature": TEMPERATURE_CP,
        "temperature_not_calibrated_to_RL_Q": True,
        "historically_postselected_root_worlds": True,
        "original_full_game_history_erased_for_static_probe": True,
        "piece_removal_is_not_a_reachable_chess_transition": True,
        "same_legality_of_three_supported_moves_verified": True,
        "not_actual_source_internal_computation_intervention": True,
        "not_natural_mediation_or_chess_truth": True,
        "new_actual_engine_calls": sum(
            (1 + len(c["perturbations"])) * c["support_count"] for c in cases),
        "new_actual_source_nodes": sum(
            c["original_forced_nodes"] +
            sum(x["source_forced_nodes"] for x in c["perturbations"]) for c in cases),
        "cases": cases,
    }


def main():
    p = argparse.ArgumentParser()
    for key in ("source", "predictions", "engine", "out"):
        p.add_argument("--" + key, required=True)
    a = p.parse_args()
    originals = authentic_cases(
        authentic_archive(Path(a.predictions), PRED_ZIP_SHA, PRED_MEMBER, PRED_JSON_SHA),
        authentic_archive(Path(a.source), SOURCE_ZIP_SHA, SOURCE_MEMBER, SOURCE_JSON_SHA))
    worlds = source_positions(originals, FROZEN_EXPLORATORY_CASES)
    with chess.engine.SimpleEngine.popen_uci(a.engine, timeout=180) as eng:
        if ("stockfish" not in eng.id.get("name", "").lower()
            or not {"Threads", "Hash", "Use NNUE"}.issubset(eng.options)):
            raise ValueError("R30_D_HOLD_ORIGINAL_STOCKFISH_ID")
        eng.configure({"Threads": 1, "Hash": 16, "Use NNUE": False})
        result = run(worlds, eng)
    if len(result["cases"]) != 2 or result["new_actual_engine_calls"] != 24:
        raise ValueError("R30_D_HOLD_EXACT_2_CASE_24_REAL_FORCED_SEARCHES")
    result["source_binary_sha256"] = sha(a.engine)
    path = Path(a.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("R30_D_SOURCE_SARFA_METHOD_N_24_NATIVE", result["new_actual_source_nodes"], flush=True)


if __name__ == "__main__":
    main()
