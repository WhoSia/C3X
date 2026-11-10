#!/usr/bin/env python3
"""C3X 0.30/R6-C: semantic residual information in R5 'masked' templates.

Original Parfenova paper (read primary Drive PDF):
https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view

R6-A genuinely executed pinned small open model on 20 blind packets:
strict parsed target recovery unmasked 3/4, other arms 0/4. This DOES NOT
show zero information under masking. The synthetic R5 masked template
still reveals "a capture / not a capture" AND "gives check / does not".
Filter ALL legal actions by those claims, using original chess rules, and
quantify the ambiguity reduction vs FEN-only (all legal actions).

Crucially this is not original paper's generative model, not decoder
accuracy, not causal chess engine source state. It is an adversarial
information-leak audit of OUR protocol, using rules rather than LLM.
"""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

import chess

SCHEMA="c3x030-r6c-masked-semantic-residual-information-v1"
R5_AUDIT_SHA="4221f90ed5ab86ef38b05e47d248f5906048c7c5812d0430c2c48fc680760f0b"
CLAIMS=re.compile(r"\bIt is (not a capture|a capture) and "
                  r"(does not give check|gives check)\.", re.I)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def features_from_text(explanation):
    if type(explanation) is not str:
        raise ValueError("R030_R6C_HOLD_NO_MASKED_TEXT")
    hits=list(CLAIMS.finditer(explanation))
    if len(hits)!=1:
        raise ValueError("R030_R6C_HOLD_AMBIGUOUS_OR_MISSING_SEMANTIC_CLAIM")
    cap=hits[0].group(1).lower()=="a capture"
    check=hits[0].group(2).lower()=="gives check"
    return cap,check


def candidate_filter(board,capture=None,check=None):
    if (not isinstance(board,chess.Board) or not board.is_valid()
        or (capture is not None and type(capture) is not bool)
        or (check is not None and type(check) is not bool)):
        raise ValueError("R030_R6C_HOLD_INVALID_BOARD_OR_CLAIM")
    result=[]
    for move in board.legal_moves:
        if capture is not None and board.is_capture(move)!=capture: continue
        if check is not None and board.gives_check(move)!=check: continue
        result.append(move.uci())
    return sorted(result)


def analyze(audit,expected_sha):
    if expected_sha!=R5_AUDIT_SHA or audit.get("schema")!="c3x030-r5-parfenova-inspired-move-hint-mask-protocol-v1":
        raise ValueError("R030_R6C_HOLD_FROZEN_R5_AUDIT")
    cases=audit.get("cases")
    if not isinstance(cases,list) or len(cases)!=2:
        raise ValueError("R030_R6C_HOLD_TWO_HISTORIC_CASES")
    out=[]
    for case in cases:
        if len(case.get("candidate_control_packets",[]))!=2:
            raise ValueError("R030_R6C_HOLD_TWO_ROOTS_PER_CASE")
        for item in case["candidate_control_packets"]:
            cond=item["conditions"]
            if set(cond)!={"fen_only","explanation_only","fen_plus_unmasked",
                          "fen_plus_strict_masked","fen_plus_unrelated_foil"}:
                raise ValueError("R030_R6C_HOLD_FIVE_CONDITIONS")
            board=chess.Board(cond["fen_only"]["fen"])
            target=item["root_uci_source_only_label_not_decoder_input"]
            move=chess.Move.from_uci(target)
            if not board.is_valid() or move not in board.legal_moves:
                raise ValueError("R030_R6C_HOLD_INHERITED_CHESS_TARGET")
            masked=cond["fen_plus_strict_masked"]["explanation"]
            capture,check=features_from_text(masked)
            if capture!=item["act_eval_capture_truth"] or check!=item["act_eval_check_truth"]:
                raise ValueError("R030_R6C_HOLD_SEMANTIC_SOURCE_FACT_DRIFT")
            all_actions=candidate_filter(board)
            keep=candidate_filter(board,capture,check)
            onlycap=candidate_filter(board,capture=capture)
            onlycheck=candidate_filter(board,check=check)
            if target not in keep or not keep:
                raise ValueError("R030_R6C_HOLD_TRUE_TARGET_NOT_IN_RETAINED_SET")
            n=len(all_actions); k=len(keep)
            foiltext=cond["fen_plus_unrelated_foil"]["explanation"]
            foilcapture,foilcheck=features_from_text(foiltext)
            foilkeep=candidate_filter(board,foilcapture,foilcheck)
            out.append({
                "case_id":case["case_id"],"event_family":case["event_family"],
                "historical_root":target,
                "source_derived_capture_truth":capture,
                "source_derived_check_truth":check,
                "all_legal_moves":n,
                "number_matching_capture_alone":len(onlycap),
                "number_matching_check_alone":len(onlycheck),
                "remaining_masked_candidates":k,
                "masked_information_gain_bits_log2_count_ratio":math.log2(n/k),
                "masked_retains_source_root":True,
                "masked_uniquely_identifies_source_root":k==1,
                "masked_shrinks_legal_action_set":k<n,
                "unrelated_foil_candidates":len(foilkeep),
                "unrelated_foil_excludes_source_root":target not in foilkeep,
                "rule_based_enumeration_not_language_decoder":True,
            })
    if len(out)!=4:
        raise ValueError("R030_R6C_HOLD_FOUR_EXPOSED_ROOTS")
    return {
        "schema":SCHEMA,
        "status":"GENUINE_ORIGINAL_CHESS_BOARD_SYNTHETIC_MASK_SEMANTIC_LEAK_AUDIT",
        "original_drive_parfenova_pdf":"https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view",
        "frozen_R5_audit_sha256":expected_sha,
        "original_actual_R6_small_decoder_run":"https://github.com/WhoSia/C3X/actions/runs/42763551104",
        "number_exposed_root_candidates":len(out),
        "total_masked_cases_with_remaining_semantic_information":sum(x["masked_shrinks_legal_action_set"] for x in out),
        "mask_uniquely_identified_n":sum(x["masked_uniquely_identifies_source_root"] for x in out),
        "mean_masked_information_gain_bits":sum(x["masked_information_gain_bits_log2_count_ratio"] for x in out)/4,
        "not_actual_decoder_recovery_accuracy":True,
        "not_full_Parfenova_maximal_masking":True,
        "not_200_puzzles_or_generalizable":True,
        "rows":out,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--audit",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    if digest(a.audit)!=R5_AUDIT_SHA:
        raise ValueError("R030_R6C_HOLD_FROZEN_R5_AUDIT_BYTES")
    audit=json.loads(Path(a.audit).read_text(encoding="utf-8"))
    report=analyze(audit,R5_AUDIT_SHA)
    out=Path(a.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    for row in report["rows"]:
        print("R030_R6C_SEMANTIC_LEAK",row["event_family"],row["historical_root"],
              row["all_legal_moves"],"to",row["remaining_masked_candidates"],
              "bits",row["masked_information_gain_bits_log2_count_ratio"],flush=True)
    print("R030_R6C_RESULT_SHA",digest(out))


if __name__=="__main__":
    main()
