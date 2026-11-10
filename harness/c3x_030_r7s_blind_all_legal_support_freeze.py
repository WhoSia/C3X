#!/usr/bin/env python3
"""C3X 0.30/R7-S — freeze all-legal move support from R5 FEN-only BLIND arm.

This program NEVER sees the R5 truth audit with nominated root labels.
Its only input is original SHA-pinned FEN-only input for R6. Four legal
supports, with two distinct old positions repeated twice, are emitted
without target/chess case identifiers or any text explanations.

The explanation-only arm can use this support to score text likelihoods
but the *model prompt* still does NOT include any FEN. The hypothesis space
remains board-restricted by an experimenter, a limitation to disclose.
"""
import argparse
import hashlib
import json
from pathlib import Path

import chess
from c3x_030_r6a_actual_open_decoder_blind_arm import (
    read_legacy_r5_blind,input_arm
)

FEN_SHA="3709dd687f468170af80446f7ebe853b51328a866161c572597b96abf0504bbc"
SCHEMA="c3x030-r7-blind-complete-legal-support-v1"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def support(fen_only, source_sha):
    if source_sha!=FEN_SHA:
        raise ValueError("R030_R7_HOLD_FROZEN_FEN_ONLY_BYTES")
    entries=input_arm(fen_only,"fen_only")
    result=[]
    for ordinal,item in enumerate(entries):
        fen=item["fen"]
        board=chess.Board(fen)
        if not board.is_valid() or board.is_game_over(claim_draw=False):
            raise ValueError("R030_R7_HOLD_SOURCE_CHESS_BOARD")
        moves=sorted(m.uci() for m in board.legal_moves)
        if not 3<=len(moves)<=220 or len(set(moves))!=len(moves):
            raise ValueError("R030_R7_HOLD_LEGAL_MOVE_SUPPORT_SIZE")
        result.append({"ordinal":ordinal,"legal_move_ucis":moves})
    if len(result)!=4:
        raise ValueError("R030_R7_HOLD_EXACT_FOUR_ORIGINAL_INSTANCES")
    return {
        "schema":SCHEMA,"source_fen_only_blind_sha256":source_sha,
        "no_fen_or_reference_label_in_support_manifest":True,
        "source_not_generated_or_reference_move_labels":True,
        "same_board_can_appear_in_multiple_original_ordinal_rows":True,
        "requires_original_ordinal_alignment_across_isolated_arms":True,
        "entries":result
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fen-only",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    if sha(a.fen_only)!=FEN_SHA:
        raise ValueError("R030_R7_HOLD_FEN_FILE_SHA")
    manifest=support(read_legacy_r5_blind(a.fen_only), FEN_SHA)
    output=Path(a.out)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("R030_R7_SOURCE_BLIND_LEGAL_SUPPORT",
          [len(x["legal_move_ucis"]) for x in manifest["entries"]],
          sha(output))


if __name__=="__main__":
    main()
