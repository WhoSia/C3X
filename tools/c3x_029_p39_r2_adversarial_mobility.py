#!/usr/bin/env python3
"""P39/R2 chess-law adversarial option-count diagnostic. No chess engine.

Exact W(s,m) = max_legal opponent r min_legal own u
              [number of opponent legal options after m,r,u].
A proxy for reply-robust tactical restriction, NOT winning value.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import chess

from c3x_029_p39_r1_exact_mate2_legal_certificate import (
    SOURCE_SHA, PRED_SHA, read_fixed, board_from_source, need
)

MAX_EXPANSIONS = 250000
DRAW_PENALTY = 256


def mobility_after_own_reply(state: chess.Board) -> tuple[int, str]:
    """Caller has pushed our reply; state.turn is opponent."""
    if state.is_checkmate():
        return 0, "CHECKMATE"
    if state.is_game_over(claim_draw=False):
        return DRAW_PENALTY, "DRAW_OR_TERMINAL"
    return state.legal_moves.count(), "CONTINUATION"


def compute_world(board: chess.Board, root_uci: str, cap: int = MAX_EXPANSIONS) -> dict:
    root = chess.Move.from_uci(root_uci)
    need(root in board.legal_moves, "ROOT_ILLEGAL")
    after_root = board.copy(stack=True)
    after_root.push(root)
    if after_root.is_checkmate():
        return {"root_uci": root_uci, "w": 0, "kind": "IMMEDIATE_MATE",
                "branches": [], "worst_opponent_reply": None,
                "expanded_legal_moves": 1}
    if after_root.is_game_over(claim_draw=False):
        return {"root_uci": root_uci, "w": DRAW_PENALTY,
                "kind": "TERMINAL_NOT_MATE", "branches": [],
                "worst_opponent_reply": None, "expanded_legal_moves": 1}
    opp_replies = sorted(move.uci() for move in after_root.legal_moves)
    need(bool(opp_replies), "NO_NONTERMINAL_OPP_MOVES")
    branches = []
    expanded = 1
    for reply in opp_replies:
        expanded += 1
        need(expanded <= cap, "EXPANSION_CAP")
        after_reply = after_root.copy(stack=True)
        after_reply.push_uci(reply)
        if after_reply.is_game_over(claim_draw=False):
            branches.append({"opponent_reply": reply, "b": DRAW_PENALTY,
                             "best_own_reply": None,
                             "best_leaf_kind": "TERMINAL_AFTER_OPPONENT",
                             "own_legal_reply_count": 0})
            continue
        legal_own = sorted(move.uci() for move in after_reply.legal_moves)
        need(bool(legal_own), "NO_NONTERMINAL_OWN_MOVES")
        best = None
        for response in legal_own:
            expanded += 1
            need(expanded <= cap, "EXPANSION_CAP")
            leaf = after_reply.copy(stack=True)
            leaf.push_uci(response)
            options, kind = mobility_after_own_reply(leaf)
            val = (options, response, kind)
            if best is None or (val[0], val[1]) < (best[0], best[1]):
                best = val
        branches.append({"opponent_reply": reply, "b": best[0],
                         "best_own_reply": best[1],
                         "best_leaf_kind": best[2],
                         "own_legal_reply_count": len(legal_own)})
    need(len(branches) == len(opp_replies), "OPPONENT_UNIVERSE")
    maximum = max(row["b"] for row in branches)
    worst = min(row["opponent_reply"] for row in branches if row["b"] == maximum)
    return {"root_uci": root_uci, "w": maximum,
            "kind": "COMPLETE_ADVERSARIAL_MOBILITY",
            "branches": branches, "worst_opponent_reply": worst,
            "expanded_legal_moves": expanded}


def verify_world(board: chess.Board, proof: dict, cap: int = MAX_EXPANSIONS) -> bool:
    """Re-derive every opponent/own branch independently, reject tampered receipts."""
    computed = compute_world(board, proof["root_uci"], cap)
    need(computed == proof, "MOBILITY_CERT_MISMATCH")
    return True


def court(source: dict, pred: dict) -> dict:
    need(source["status"] == "EIGHT_EVENT_SOURCE_ONLY_FROZEN_HISTORY_LEDGER_GATE_PENDING",
         "SOURCE_STATUS")
    need(pred["status"] == "PRE_REFEREE_FROZEN_THREE_RIVAL_RESPONSE_FORECASTS",
         "PRED_STATUS")
    need(len(source["sources"]) == len(pred["cases"]) == 8, "EIGHT_EVENTS")
    cases = []
    for row, prediction in zip(source["sources"], pred["cases"]):
        game = row["selected"]
        need(game["case_id"] == prediction["case_id"], "CASE_ID")
        need(row["source_id"] == prediction["source_id"] == game["source_id"], "SOURCE_ID")
        need(prediction["original_prefix_uci"] == game["full_game_uci"][:30],
             "PRED_PREFIX")
        need(prediction["frozen_fen"] == game["frozen_fen"], "PRED_FEN")
        board = board_from_source(game)
        pair = prediction["candidate_pairs"]
        need(len(pair) == 2 and len(set(c["root_uci"] for c in pair)) == 2,
             "CANDIDATE_PAIR")
        results = []
        for candidate in pair:
            proof = compute_world(board, candidate["root_uci"])
            verify_world(board, proof)
            results.append(proof)
        cases.append({"case_id": game["case_id"], "event_family": row["event_family"],
                      "source_id": row["source_id"],
                      "worlds": results,
                      "delta_w_first_minus_second": results[0]["w"] - results[1]["w"],
                      "w_discriminates_candidates": results[0]["w"] != results[1]["w"]})
    distinguish = sum(x["w_discriminates_candidates"] for x in cases)
    return {
        "status": "P39_R2_RULE_COMPLETE_COUNTERPLAY_MOBILITY_PILOT_NOT_VALUE_TRUTH",
        "game_events": 8, "candidate_worlds": 16,
        "distinct_pair_count": distinguish,
        "methodology_gate": "NO_PROMOTION" if distinguish < 2 else "NONTRIVIAL_VARIATION_ONLY",
        "source_sha256": SOURCE_SHA, "prediction_sha256": PRED_SHA,
        "draw_terminal_penalty": DRAW_PENALTY,
        "scientific_limit": "Exposed original games and candidate choices; tactical forcing proxy, not chess value, source NNUE mediation or C3X model victory.",
        "cases": cases
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-member", type=Path, required=True)
    p.add_argument("--prediction-member", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    result = court(read_fixed(a.source_member, SOURCE_SHA),
                   read_fixed(a.prediction_member, PRED_SHA))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print("P39_R2_COMPLETE", result["distinct_pair_count"], "of 8",
          result["methodology_gate"], flush=True)


if __name__ == "__main__":
    main()
