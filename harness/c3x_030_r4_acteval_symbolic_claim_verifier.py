#!/usr/bin/env python3
"""C3X 0.30/R4: ACT-Eval-inspired deterministic atomic chess fact checker.

Original owned primary paper: Hebbar, Sheng, Oh & Viswanath (2026),
Hallucinations on the Board: Tool-Augmented Evaluation of LLM Chess Commentary.
https://drive.google.com/file/d/1BOHr8mZzY6vp14PBr2MrAiJH9vJDQStA/view

Only a *tool-checkable atomic claim verifier* is reproduced. No free-text
LLM decomposition, LLM tool routing, strategic gold atom matching,
human calibration, or original 325-position benchmark reproduction.

The demonstration uses original SHA-locked P37 full legal histories:
for each historically named candidate root, assert legal, capture, check;
and create deliberately false foils by flipping the EXPECTED boolean.
Thus observed true/false accuracy is an integrity/control check, NOT
performance on naturally generated chess explanations.
"""
import argparse
import hashlib
import json
from pathlib import Path

import chess

from c3x_029_p38_r1_ethereal_independent_referee import (
    authentic_archive, authentic_cases, SOURCE_ZIP_SHA, SOURCE_MEMBER,
    SOURCE_JSON_SHA, PRED_ZIP_SHA, PRED_MEMBER, PRED_JSON_SHA)
from c3x_029_p42_r23_independent_all_opponent_reply_value_court import (
    FROZEN_EXPLORATORY_CASES, source_positions)

SCHEMA = "c3x030-r4-act-eval-inspired-symbolic-atom-verifier-v1"
CLAIM_TYPES = ("legal_move", "move_is_capture", "move_gives_check",
               "piece_on_square", "square_attacked_by", "white_material_minus_black")
PIECE_CP = {chess.PAWN:1, chess.KNIGHT:3, chess.BISHOP:3,
            chess.ROOK:5, chess.QUEEN:9}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def evaluate_atom(board, atom):
    if (not isinstance(board,chess.Board) or not board.is_valid()
        or not isinstance(atom,dict) or type(atom.get("kind")) is not str
        or atom["kind"] not in CLAIM_TYPES):
        raise ValueError("R030_R4_HOLD_BOARD_OR_ATOM_SCHEMA")
    kind = atom["kind"]
    if kind in ("legal_move", "move_is_capture", "move_gives_check"):
        if set(atom) != {"kind","move_uci","expected"} or type(atom["expected"]) is not bool:
            raise ValueError("R030_R4_HOLD_MOVE_ATOM_FIELDS")
        try:
            move=chess.Move.from_uci(atom["move_uci"])
        except (ValueError, TypeError):
            raise ValueError("R030_R4_HOLD_INVALID_UCI_STRING")
        legal=move in board.legal_moves
        if kind=="legal_move":
            observed=legal
        else:
            if not legal:
                raise ValueError("R030_R4_HOLD_NONLEGAL_MOVE_FOR_TACTICAL_CLAIM")
            observed=(board.is_capture(move) if kind=="move_is_capture"
                      else board.gives_check(move))
    elif kind=="piece_on_square":
        if set(atom)!={"kind","square","expected"} or (atom["expected"] is not None
           and (type(atom["expected"]) is not str or atom["expected"] not in "PNBRQKpnbrqk")):
            raise ValueError("R030_R4_HOLD_PIECE_ATOM_FIELDS")
        try:
            sq=chess.parse_square(atom["square"])
        except (ValueError,TypeError):
            raise ValueError("R030_R4_HOLD_INVALID_PIECE_SQUARE")
        piece=board.piece_at(sq)
        observed=piece.symbol() if piece else None
    elif kind=="square_attacked_by":
        if set(atom)!={"kind","square","color","expected"} or type(atom["expected"]) is not bool or atom["color"] not in ("white","black"):
            raise ValueError("R030_R4_HOLD_ATTACK_ATOM_FIELDS")
        try:
            sq=chess.parse_square(atom["square"])
        except (ValueError,TypeError):
            raise ValueError("R030_R4_HOLD_INVALID_ATTACK_SQUARE")
        observed=board.is_attacked_by(atom["color"]=="white",sq)
    else:
        if set(atom)!={"kind","expected"} or type(atom["expected"]) is not int:
            raise ValueError("R030_R4_HOLD_MATERIAL_ATOM_FIELDS")
        observed=sum(
            value*(len(board.pieces(pt,chess.WHITE))-len(board.pieces(pt,chess.BLACK)))
            for pt,value in PIECE_CP.items())
    return {
        "kind":kind, "expected":atom["expected"], "actual":observed,
        "atom_factually_correct":atom["expected"]==observed,
        "verified_by_exact_chess_rules":True,
    }


def demonstration(worlds):
    rows=[]
    for source, board, roots in worlds:
        if len(roots)!=2 or not board.is_valid():
            raise ValueError("R030_R4_HOLD_TWO_ORIGINAL_ROOTS")
        records=[]
        for root in roots:
            u=root["root"]
            move=chess.Move.from_uci(u)
            if move not in board.legal_moves:
                raise ValueError("R030_R4_HOLD_INHERITED_ROOT_NOT_LEGAL")
            for kind, fact in (
                ("legal_move",True),
                ("move_is_capture",board.is_capture(move)),
                ("move_gives_check",board.gives_check(move)),
            ):
                for expected, origin in ((fact,"source_derived_positive"),
                                         (not fact,"constructed_false_foil")):
                    atom={"kind":kind,"move_uci":u,"expected":expected}
                    result=evaluate_atom(board,atom)
                    if result["atom_factually_correct"]!=(origin=="source_derived_positive"):
                        raise ValueError("R030_R4_HOLD_DELIBERATE_CONTROL_FAILED")
                    records.append({"root_uci":u,"origin":origin,"result":result})
        if len(records)!=12:
            raise ValueError("R030_R4_HOLD_EXPECTED_TWELVE_ATOMS_PER_GAME")
        rows.append({"case_id":source["case_id"],
                     "event_family":source["event_family"],
                     "original_root_mover":"white" if board.turn else "black",
                     "atom_results":records})
    if len(rows)!=2:
        raise ValueError("R030_R4_HOLD_EXACT_TWO_HISTORICAL_GAMES")
    return {
        "schema":SCHEMA,
        "status":"REAL_ORIGINAL_CHESS_POSITION_SYMBOLIC_ATOM_CONTRACT_ONLY",
        "owned_primary_acteval_pdf":"https://drive.google.com/file/d/1BOHr8mZzY6vp14PBr2MrAiJH9vJDQStA/view",
        "n_original_source_games":len(rows),
        "n_historical_root_alternatives":4,
        "n_tool_checked_atoms":sum(len(r["atom_results"]) for r in rows),
        "true_source_derived_claims":sum(
            1 for r in rows for a in r["atom_results"] if a["result"]["atom_factually_correct"]),
        "intentionally_false_foils":sum(
            1 for r in rows for a in r["atom_results"] if not a["result"]["atom_factually_correct"]),
        "all_foils_constructed_from_checker_truth":True,
        "no_llm_commentary_or_original_gold_dataset":True,
        "not_original_full_ACT_Eval":True,
        "no_source_searches_or_judge_searches":True,
        "not_causal_chess_engine_explanation":True,
        "cases":rows,
    }


def main():
    ap=argparse.ArgumentParser()
    for item in ("source","predictions","out"):
        ap.add_argument("--"+item,required=True)
    a=ap.parse_args()
    originals=authentic_cases(
        authentic_archive(Path(a.predictions),PRED_ZIP_SHA,PRED_MEMBER,PRED_JSON_SHA),
        authentic_archive(Path(a.source),SOURCE_ZIP_SHA,SOURCE_MEMBER,SOURCE_JSON_SHA))
    worlds=source_positions(originals,FROZEN_EXPLORATORY_CASES)
    report=demonstration(worlds)
    out=Path(a.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n",
                   encoding="utf-8")
    print("R030_R4_REAL_HISTORY_ATOMIC_CLAIMS",
          report["n_tool_checked_atoms"],
          "TRUE",report["true_source_derived_claims"],
          "FALSE_FOILS",report["intentionally_false_foils"])


if __name__=="__main__":
    main()
