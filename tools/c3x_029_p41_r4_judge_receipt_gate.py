"""P41/R4 exact source-context acceptance gate for an external chess-value judge.

A passing receipt is TECHNICALLY ADMISSIBLE ONLY: declared family/source IDs
are not independently proved by the JSON itself, and finite search is not truth.
"""
from __future__ import annotations
import re
import chess

SHA256=re.compile(r"^[a-f0-9]{64}$")
SOURCE_COMMIT=re.compile(r"^[a-f0-9]{40}$")

def require(ok,why):
    if not ok:
        raise ValueError("P41_JUDGE_HOLD_"+why)

def validate_judge_receipt(receipt):
    # Never infer independent model provenance from UCI engine name alone.
    need=("engine_family","verified_source_commit","binary_sha256",
          "source_audit_verified","original_chess_history_uci",
          "original_root_fen","candidate_root_uci","opponent_reply_uci",
          "own_continuation_uci","evaluated_fen","requested_nodes",
          "actual_nodes","depth","root_side_cp","lowerbound","upperbound",
          "root_mover_is_white","pv_uci")
    for key in need:require(key in receipt,"MISSING_"+key)
    family=receipt["engine_family"].strip().lower()
    require(family and family not in ("stockfish","stockfish16","stockfish 16"),
            "NOT_INDEPENDENT_FAMILY")
    require(receipt["source_audit_verified"] is True,"SOURCE_NOT_AUDITED")
    require(bool(SOURCE_COMMIT.fullmatch(receipt["verified_source_commit"])),
            "INVALID_SOURCE_COMMIT")
    require(bool(SHA256.fullmatch(receipt["binary_sha256"])),
            "INVALID_BINARY_SHA")
    if receipt.get("uses_neural_net"):
        require(bool(SHA256.fullmatch(receipt.get("network_sha256",""))),
                "INVALID_NETWORK_SHA")
    budget=receipt["requested_nodes"]
    observed=receipt["actual_nodes"]
    depth=receipt["depth"]
    require(type(budget) is int and budget>0,"REQUESTED_NODES")
    require(type(observed) is int and observed>=0.9*budget,"INSUFFICIENT_NODES")
    require(type(depth) is int and depth>=3,"INSUFFICIENT_DEPTH")
    require(type(receipt["root_side_cp"]) is int,"ROOT_CP_NOT_INTEGER")
    lo=receipt["lowerbound"];hi=receipt["upperbound"]
    require(type(lo) is bool and type(hi) is bool and not(lo and hi),
            "CONFLICTING_SCORE_BOUNDS")
    require(receipt.get("root_side_mate") is None,"MATE_AS_CP")
    board=chess.Board()
    history=receipt["original_chess_history_uci"]
    require(isinstance(history,list) and len(history)>=30,"ORIGINAL_HISTORY_MISSING")
    for u in history:
        try: move=chess.Move.from_uci(u)
        except (ValueError,TypeError): raise ValueError("P41_JUDGE_HOLD_MALFORMED_HISTORY")
        require(move in board.legal_moves,"ILLEGAL_HISTORY")
        board.push(move)
    require(board.fen()==receipt["original_root_fen"],"ROOT_FEN_MISMATCH")
    require(not board.is_game_over(claim_draw=False),"TERMINAL_ROOT")
    require((board.turn==chess.WHITE)==receipt["root_mover_is_white"],
            "SCORE_VIEWPOINT")
    for key in ("candidate_root_uci","opponent_reply_uci","own_continuation_uci"):
        try: move=chess.Move.from_uci(receipt[key])
        except (ValueError,TypeError): raise ValueError("P41_JUDGE_HOLD_MALFORMED_BRANCH")
        require(move in board.legal_moves,"ILLEGAL_BRANCH_"+key)
        board.push(move)
    require(board.fen()==receipt["evaluated_fen"],"JUDGE_FEN_MISMATCH")
    require(not board.is_game_over(claim_draw=False),"TERMINAL_SCORE_CONTEXT")
    for u in receipt["pv_uci"]:
        try: move=chess.Move.from_uci(u)
        except (ValueError,TypeError): raise ValueError("P41_JUDGE_HOLD_MALFORMED_PV")
        require(move in board.legal_moves,"ILLEGAL_PV")
        board.push(move)
        if board.is_game_over(claim_draw=False):
            break
    cp=receipt["root_side_cp"]
    return {"status":"TECHNICAL_JUDGE_RECEIPT_ELIGIBLE_NOT_INDEPENDENT_VALUE_TRUTH",
            "score_interval_root_mover_cp":{
                "lower":None if hi else cp,
                "upper":None if lo else cp},
            "requested_nodes":budget,"actual_nodes":observed,"depth":depth,
            "source_family_declared":family,
            "source_commit":receipt["verified_source_commit"],
            "claim_ceiling":"Receipt alone cannot independently certify engine provenance or chess truth."}
