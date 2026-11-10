#!/usr/bin/env python3
"""C3X 0.30/R5: Parfenova-inspired explicit-move leakage controls.

Primary owned PDF: Angelina Parfenova (2026), arXiv 2609.22245v1
https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view

Implement conservative mechanical masking and five experimental *packets*.
This is NOT the author's generative decoder, 200 Lichess endgame puzzles,
all-legal token probability ranking, or demonstration of move recoverability.

A mechanically generated template includes explicit SAN+UCI so that
unmasked text provably leaks the chosen move, while masked text must not
contain UCI, SAN, coordinates or explicit origin-destination phrases.
Full natural-language semantic leakage cannot be certified by regex.
The actual original-game legality and gives-check/capture flags are
verified via the inherited ACT-Eval symbolic checker before packaging.

Synthetic human-written style templates about real boards are not
authentic explanations produced by any language model.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import chess

from c3x_029_p38_r1_ethereal_independent_referee import (
    authentic_archive, authentic_cases, SOURCE_ZIP_SHA, SOURCE_MEMBER,
    SOURCE_JSON_SHA, PRED_ZIP_SHA, PRED_MEMBER, PRED_JSON_SHA)
from c3x_029_p42_r23_independent_all_opponent_reply_value_court import (
    FROZEN_EXPLORATORY_CASES, source_positions)
from c3x_030_r4_acteval_symbolic_claim_verifier import evaluate_atom

SCHEMA = "c3x030-r5-parfenova-inspired-move-hint-mask-protocol-v1"
PRIMARY = "https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view"
CONTROL_NAMES = (
    "fen_only", "explanation_only", "fen_plus_unmasked",
    "fen_plus_strict_masked", "fen_plus_unrelated_foil")

# Longest patterns first, avoid leaving shortened coordinate fragments.
MOVE_HINT = re.compile(
    r"(?<![A-Za-z0-9])(?:"
    r"[a-h][1-8]\s*(?:-|→|to)\s*[a-h][1-8](?:\s*=\s*[QRBNqrbn])?"
    r"|[a-h][1-8][a-h][1-8][qrbn]?"
    r"|[KQRBN]?[a-h1-8]?x?[a-h][1-8](?:=[QRBN])?[+#]?"
    r"|O-O(?:-O)?[+#]?|0-0(?:-0)?[+#]?"
    r"|[a-h][1-8]"
    r")(?![A-Za-z0-9])",
    re.IGNORECASE)
MOVE_NUMBER = re.compile(r"(?<!\w)\d+\.(?:\.\.)?\s*")
PROMOTION_WORD = re.compile(r"\b(?:promot(?:e|es|ed|ion|ing)|underpromot\w*|queening)\b", re.I)
DIRECT_PHRASES = re.compile(r"\b(?:king|queen|rook|bishop|knight|pawn)\s+(?:to|on|from)\s+\[MOVE\]",re.I)


def mask_explicit_hints(explanation):
    if type(explanation) is not str or not explanation.strip():
        raise ValueError("R030_R5_HOLD_EMPTY_COMMENTARY")
    # Coordinate/SAN token-level mask, then move-number and promotion.
    masked=MOVE_NUMBER.sub("",explanation)
    masked=MOVE_HINT.sub("[MOVE]",masked)
    masked=PROMOTION_WORD.sub("[PROMOTION]",masked)
    masked=DIRECT_PHRASES.sub("[MOVE]",masked)
    if MOVE_HINT.search(masked) or PROMOTION_WORD.search(masked):
        raise ValueError("R030_R5_HOLD_EXPLICIT_MOVE_HINT_REMAINS")
    return masked


def hints_for_move(board, uci):
    try:
        move=chess.Move.from_uci(uci)
    except (TypeError,ValueError) as e:
        raise ValueError("R030_R5_HOLD_BAD_CANDIDATE_UCI") from e
    if not board.is_valid() or move not in board.legal_moves:
        raise ValueError("R030_R5_HOLD_CANDIDATE_NOT_LEGAL")
    san=board.san(move)
    return san


def packet(board, uci, unrelated_text=None):
    san=hints_for_move(board,uci)
    capture=evaluate_atom(board,{"kind":"move_is_capture","move_uci":uci,
                                 "expected":board.is_capture(chess.Move.from_uci(uci))})
    check=evaluate_atom(board,{"kind":"move_gives_check","move_uci":uci,
                               "expected":board.gives_check(chess.Move.from_uci(uci))})
    if not capture["atom_factually_correct"] or not check["atom_factually_correct"]:
        raise ValueError("R030_R5_HOLD_ACT_EVAL_INDEPENDENT_FACT_CHECK")
    # The template is intentionally marked as a synthetic protocol input.
    # Factual move-specific content is excluded from the masked explanation,
    # to isolate *explicit lexical leakage control*, NOT semantic faithfulness.
    raw=f"Candidate move {uci} (SAN {san}). It is {'a capture' if capture['actual'] else 'not a capture'} and {'gives check' if check['actual'] else 'does not give check'}."
    masked=mask_explicit_hints(raw)
    # Ensure exact selected UCI and SAN cannot be extracted verbatim.
    if uci.lower() in masked.lower() or san.lower() in masked.lower():
        raise ValueError("R030_R5_HOLD_SELECTED_MOVE_TOKEN_SURVIVED")
    if unrelated_text is not None:
        if type(unrelated_text) is not str or not unrelated_text.strip():
            raise ValueError("R030_R5_HOLD_UNRELATED_FOIL_TEXT")
        foil=mask_explicit_hints(unrelated_text)
    else:
        foil=None
    fen=board.fen(en_passant="fen")
    conds={
        "fen_only":{"fen":fen,"explanation":None},
        "explanation_only":{"fen":None,"explanation":masked},
        "fen_plus_unmasked":{"fen":fen,"explanation":raw},
        "fen_plus_strict_masked":{"fen":fen,"explanation":masked},
        "fen_plus_unrelated_foil":{"fen":fen,"explanation":foil}
    }
    if tuple(conds)!=CONTROL_NAMES:
        raise ValueError("R030_R5_HOLD_FIVE_EXPERIMENTAL_CONDITIONS")
    return {
        "root_uci_source_only_label_not_decoder_input":uci,
        "root_san_source_only_label_not_decoder_input":san,
        "act_eval_capture_truth":capture["actual"],
        "act_eval_check_truth":check["actual"],
        "explicit_uci_present_before_mask":uci.lower() in raw.lower(),
        "explicit_uci_absent_after_mask":uci.lower() not in masked.lower(),
        "explicit_san_absent_after_mask":san.lower() not in masked.lower(),
        "masking_is_lexical_not_semantic_proof":True,
        "synthetic_commentary_not_model_generated":True,
        "conditions":conds,
    }


def demonstrate(worlds):
    if len(worlds)!=2:
        raise ValueError("R030_R5_HOLD_TWO_EXPOSED_GAMES")
    # Build templates without looking at outcome judges; choose unrelated
    # text from the *other* event. Do not call it a random human-like sample.
    templates=[]
    for source,board,roots in worlds:
        if len(roots)!=2 or not board.is_valid():
            raise ValueError("R030_R5_HOLD_TWO_SOURCE_ROOTS")
        per=[]
        for root in roots:
            u=root["root"]
            san=hints_for_move(board,u)
            m=chess.Move.from_uci(u)
            per.append(
                f"Candidate move {u} (SAN {san}). It is "
                f"{'a capture' if board.is_capture(m) else 'not a capture'} and "
                f"{'gives check' if board.gives_check(m) else 'does not give check'}."
            )
        templates.append(per)
    cases=[]
    for i,(source,board,roots) in enumerate(worlds):
        examples=[]
        for k,root in enumerate(roots):
            # Different *original game* as unrelated explanation source.
            foil=templates[1-i][k]
            item=packet(board,root["root"],foil)
            if item["conditions"]["fen_plus_unrelated_foil"]["explanation"] is None:
                raise ValueError("R030_R5_HOLD_MISSING_FOIL")
            examples.append(item)
        cases.append({
            "case_id":source["case_id"],
            "event_family":source["event_family"],
            "original_legal_actions":board.legal_moves.count(),
            "candidate_control_packets":examples,
        })
    return {
        "schema":SCHEMA,
        "status":"REAL_SOURCE_POSITION_SYNTHETIC_COMMENTARY_MASK_PROTOCOL_ONLY",
        "parfenova_primary_drive_pdf":PRIMARY,
        "inherited_r4_acteval_checker":"harness/c3x_030_r4_acteval_symbolic_claim_verifier.py",
        "n_original_exposed_games":2,
        "n_candidate_moves":4,
        "n_condition_packets":20,
        "five_conditions":list(CONTROL_NAMES),
        "foil_origin":"different_historical_game_no_random_sampling",
        "strict_mask_is_regex_approximation_not_original_maximal_semantic_mask":True,
        "no_decoder_or_token_probability_model_called":True,
        "no_move_recovery_or_correctness_metric_computed":True,
        "no_independent_prospective_causal_claim":True,
        "cases":cases,
    }


def main():
    p=argparse.ArgumentParser()
    for name in ("source","predictions","out"):
        p.add_argument("--"+name,required=True)
    a=p.parse_args()
    original=authentic_cases(
        authentic_archive(Path(a.predictions),PRED_ZIP_SHA,PRED_MEMBER,PRED_JSON_SHA),
        authentic_archive(Path(a.source),SOURCE_ZIP_SHA,SOURCE_MEMBER,SOURCE_JSON_SHA))
    report=demonstrate(source_positions(original,FROZEN_EXPLORATORY_CASES))
    dest=Path(a.out)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    print("R030_R5_PARFENOVA_PROTOCOL_SOURCE_FROZEN",
          report["n_candidate_moves"],"CANDIDATES",
          report["n_condition_packets"],"CONTROL_PACKETS")


if __name__=="__main__":
    main()
