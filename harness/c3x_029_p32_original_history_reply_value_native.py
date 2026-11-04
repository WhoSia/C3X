#!/usr/bin/env python3
"""P32: archival, full-game-history Stockfish16 adversarial continuation values.

An ORIGINAL SOURCE-EXPOSED developmental cohort, not a new independent test.
Q values are bounded-depth engine estimates and are NOT forced game-theoretic
minimax or observational explanations of an agent's causal intentions.

Retains chess.Board move_stack so the UCI engine receives the *original*
position startpos moves ... history instead of a four-field standalone FEN.
"""
import argparse
import hashlib
import json
from pathlib import Path

import chess
import chess.engine

FROZEN_SOURCE_SHA256 = "6520672aabab7f525872169085f19bdd81e27a4473f0c58ba9c9aa428937104c"
ORIGINAL_STOCKFISH16_COMMIT = "68e1e9b3811e16cad014b590d7443b9063b3eb52"
MATERIAL_CP = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
               chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 0}


def need(condition, label):
    if not condition:
        raise ValueError("P32_" + label)


def material_cp(board, color):
    return sum(MATERIAL_CP[p.piece_type] * (1 if p.color == color else -1)
               for p in board.piece_map().values())


def replay_original(row):
    board = chess.Board()
    moves = row["full_original_mainline_uci"]
    ply = row["source_ply_before_original_move"]
    need(isinstance(ply, int) and 0 <= ply < len(moves), "INVALID_SOURCE_PLY")
    for value in moves[:ply]:
        move = chess.Move.from_uci(value)
        need(move in board.legal_moves, "ILLEGAL_ORIGINAL_MOVE")
        board.push(move)
    fen4 = " ".join(board.fen(en_passant="fen").split()[:4])
    need(fen4 == row["fen4"], "FROZEN_FEN_MISMATCH")
    next_move = chess.Move.from_uci(moves[ply])
    need(next_move in board.legal_moves, "ORIGINAL_NEXT_MOVE_ILLEGAL")
    need(next_move.uci() == row["played_legal_move_uci"], "SOURCE_MOVE_DRIFT")
    need(len(board.move_stack) == ply, "LOST_GAME_HISTORY")
    return board


def perspective(info, color):
    score = info["score"].pov(color)
    cp = score.score(mate_score=100000)
    need(cp is not None, "SCORE_NOT_NUMERIC")
    return int(cp), str(score)


def analyze(engine, board, depth, name, multipv=None, root_moves=None):
    kwargs = {"game": name, "info": chess.engine.INFO_ALL}
    if multipv is not None:
        kwargs["multipv"] = multipv
    if root_moves is not None:
        kwargs["root_moves"] = root_moves
    return engine.analyse(board, chess.engine.Limit(depth=depth), **kwargs)


def clean_pv(info):
    return [m.uci() for m in info.get("pv", [])[:14]]


def root_case(engine, original, depth, reply_depth):
    board = replay_original(original)
    mover = board.turn
    case_id = original["id"]
    # MultiPV is the high-information reference baseline; no treatment applied.
    top = analyze(engine, board, depth, f"p32:{case_id}:baseline",
                  multipv=2)
    need(len(top) == 2 and all(t.get("pv") for t in top), "MISSING_TOP_TWO")
    source_played = original["played_legal_move_uci"]
    candidates = list(dict.fromkeys([top[0]["pv"][0].uci(),
                                    top[1]["pv"][0].uci(), source_played]))
    baseline = [{
        "root_uci": info["pv"][0].uci(),
        "value_for_mover_cp_or_mate_scaled": perspective(info, mover)[0],
        "uci_score": perspective(info, mover)[1],
        "pv_uci": clean_pv(info)
    } for info in top]

    entries = []
    for root_uci in candidates:
        move = chess.Move.from_uci(root_uci)
        need(move in board.legal_moves, "CANDIDATE_NOT_LEGAL")
        root_result = analyze(engine, board, depth, f"p32:{case_id}:forced:{root_uci}",
                              root_moves=[move])
        need(root_result.get("pv") and root_result["pv"][0] == move,
             "FORCED_ROOT_PV_MISMATCH")
        root_value, root_score = perspective(root_result, mover)
        after_root = board.copy(stack=True)
        capture = board.is_capture(move)
        before_material = material_cp(board, mover)
        after_root.push(move)
        n_reply = min(3, after_root.legal_moves.count())
        need(n_reply > 0 or after_root.is_game_over(claim_draw=True), "EMPTY_NONTERMINAL")
        reply_entries = []
        if n_reply:
            variations = analyze(engine, after_root, reply_depth,
                                 f"p32:{case_id}:reply:{root_uci}",
                                 multipv=n_reply)
            need(len(variations) == n_reply, "REPLY_MULTIPV_MISMATCH")
            for variation in variations:
                need(variation.get("pv"), "REPLY_WITHOUT_PV")
                response = variation["pv"][0]
                need(response in after_root.legal_moves, "ILLEGAL_REPLY")
                after_reply = after_root.copy(stack=True)
                after_reply.push(response)
                value, label = perspective(variation, mover)
                pv_after_reply = list(variation["pv"][1:])
                after_response_material_cp = material_cp(after_reply, mover) - before_material
                if pv_after_reply:
                    next_mover_response = pv_after_reply[0]
                    need(next_mover_response in after_reply.legal_moves, "ILLEGAL_NEXT_PV_MOVE")
                    after_mover_next = after_reply.copy(stack=True)
                    after_mover_next.push(next_mover_response)
                    material_after_next = material_cp(after_mover_next, mover) - before_material
                else:
                    material_after_next = None
                reply_entries.append({
                    "reply_uci": response.uci(),
                    "mover_followup_uci": pv_after_reply[0].uci() if pv_after_reply else None,
                    "material_after_opponent_reply_cp": after_response_material_cp,
                    "material_after_mover_followup_cp": material_after_next,
                    "root_pov_cp_or_mate_scaled": value,
                    "uci_score": label,
                    "next_pv_uci": clean_pv(variation)[1:],
                    "material_change_from_root_cp": material_cp(after_reply, mover) - before_material
                })
        else:
            reply_entries = []
        # Opponent's best response is the top ranked first element of a
        # fixed-depth MultiPV analysis, NOT the most frequent legal move.
        entries.append({
            "root_uci": root_uci,
            "is_source_played": root_uci == source_played,
            "root_makes_capture": capture,
            "immediate_material_delta_cp": material_cp(after_root, mover) - before_material,
            "forced_root_value_cp_or_mate_scaled": root_value,
            "forced_root_uci_score": root_score,
            "forced_root_pv_uci": clean_pv(root_result),
            "legal_opponent_reply_count": after_root.legal_moves.count(),
            "opponent_reply_top3": reply_entries,
            "best_opponent_reply": reply_entries[0]["reply_uci"] if reply_entries else None,
            "best_opponent_reply_value_cp_or_mate_scaled": reply_entries[0]["root_pov_cp_or_mate_scaled"] if reply_entries else None,
        })
    return {
        "id": case_id,
        "game_sha256": original["source_game_sha256"],
        "source_ply": original["source_ply_before_original_move"],
        "root_fen4": original["fen4"],
        "root_legal_count": board.legal_moves.count(),
        "original_move_uci": source_played,
        "baseline_stockfish16_top2": baseline,
        "candidates": entries,
        "history_mode": "position_startpos_full_original_mainline_prefix",
        "source_exposed_development": True
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--engine", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--depth", type=int, default=12)
    p.add_argument("--reply-depth", type=int, default=12)
    p.add_argument("--focus-case", type=int, default=10)
    p.add_argument("--focus-depth", type=int, default=18)
    args = p.parse_args()
    need(6 <= args.depth <= 24 and 6 <= args.reply_depth <= 24, "DEPTH_RANGE")
    source_bytes = Path(args.source).read_bytes()
    need(hashlib.sha256(source_bytes).hexdigest() == FROZEN_SOURCE_SHA256,
         "SOURCE_SHA_MISMATCH")
    source = json.loads(source_bytes)
    need(len(source["selected"]) == 16, "SOURCE_DENOMINATOR")
    need(len({r["source_game_sha256"] for r in source["selected"]}) == 16,
         "GAME_DISJOINTNESS")
    cases = []
    focus = None
    engine = chess.engine.SimpleEngine.popen_uci(args.engine, timeout=120)
    try:
        engine.configure({"Threads": 1, "Hash": 16, "Use NNUE": False})
        for row in source["selected"]:
            result = root_case(engine, row, args.depth, args.reply_depth)
            cases.append(result)
            if row["id"] == args.focus_case:
                focus = root_case(engine, row, args.focus_depth, args.focus_depth)
                print("P32_FOCUS_DEEPER_CASE", row["id"], "depth", args.focus_depth,
                      [(z["root_uci"], z["forced_root_value_cp_or_mate_scaled"],
                        z["best_opponent_reply_value_cp_or_mate_scaled"])
                       for z in focus["candidates"]], flush=True)
            print("P32_ORIGINAL_HISTORY_CASE", row["id"],
                  "best", result["baseline_stockfish16_top2"][0]["root_uci"],
                  "played", row["played_legal_move_uci"],
                  "replies", [(x["root_uci"], x["best_opponent_reply"],
                               x["best_opponent_reply_value_cp_or_mate_scaled"])
                              for x in result["candidates"]], flush=True)
    finally:
        engine.quit()
    need(len(cases) == 16, "INCOMPLETE_COHORT")
    result = {
        "schema": "c3x029-p32-original-pgn-history-root-contingent-reply-values-v1",
        "source_sha256": FROZEN_SOURCE_SHA256,
        "official_stockfish16_git_commit": ORIGINAL_STOCKFISH16_COMMIT,
        "source_only_original_run_id": 37981820261,
        "source_exposed_development_not_new_heldout": True,
        "depth": args.depth, "reply_depth": args.reply_depth,
        "threads": 1, "hash_mb": 16, "use_nnue": False,
        "score_semantics": "root-player cp; mate scaled to +/-100000, not guaranteed minimax",
        "causal_status": "no search-internal intervention; no causal mediation evidence",
        "evaluation_scope": "engine-forced root and engine-ranked top3 opponent replies; output-score and PV baselines",
        "cases": cases,
        "focus_case_depth18": focus,
        "focus_depth": args.focus_depth,
        "complete_original_history_cases": len(cases)
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                              encoding="utf-8")
    print("P32_16_ORIGINAL_HISTORY_CANDIDATES_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
