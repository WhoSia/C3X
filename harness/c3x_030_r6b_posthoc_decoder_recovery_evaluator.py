#!/usr/bin/env python3
"""C3X 0.30/R6-B: AFTER-the-fact evaluator for actual isolated decoder results.

This executable must run in a different GitHub Actions step after ALL
independent R6-A arm decoders have written their SHA-logged outputs.
The decoder never sees this module's target-bearing audit file.

The four R5 targets are source-nominated *historical candidate moves*, not
LLM-generated moves or independent Lichess reference best solutions. Thus
we report only nominated-target recovery (not Parfenova ref correctness).
"""
import argparse
import hashlib
import json
from pathlib import Path

import chess

from c3x_030_r6a_actual_open_decoder_blind_arm import (
    ARMS,SCHEMA as DECODER_SCHEMA,MODEL_ID,MODEL_REVISION
)
from c3x_030_r5_parfenova_move_mask_control_protocol import SCHEMA as R5_SCHEMA

EVAL_SCHEMA="c3x030-r6b-open-decoder-nominated-candidate-recovery-v1"
R5_AUDIT_SHA="4221f90ed5ab86ef38b05e47d248f5906048c7c5812d0430c2c48fc680760f0b"
ARM_SHA={
"explanation_only":"71497e2bdbb7e240eaf1cb6a29e1bf3d8d4e19ce0e0a9fe02e9e9bafece5aea5",
"fen_only":"3709dd687f468170af80446f7ebe853b51328a866161c572597b96abf0504bbc",
"fen_plus_strict_masked":"178a33cfbe5b722d54aa7fb22de4d440bbc06df5d079465bea7188aab2db4de8",
"fen_plus_unmasked":"9a245d1066fa05f4822d34e0c5208851e09f746d9099375b205198b50191d4f6",
"fen_plus_unrelated_foil":"20ab9f46fca00b1f6fdb2f0483b8554f0c6bb7aba6dc37be4484528f4233795e",
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def evaluate(audit,reports, audit_sha,expected_audit_sha=R5_AUDIT_SHA):
    if audit_sha!=expected_audit_sha or audit.get("schema")!=R5_SCHEMA:
        raise ValueError("R030_R6_HOLD_FROZEN_R5_AUDIT_SHA")
    cases=audit.get("cases")
    if (not isinstance(cases,list) or len(cases)!=2
        or any(len(c.get("candidate_control_packets",[]))!=2 for c in cases)):
        raise ValueError("R030_R6_HOLD_EXACT_FOUR_TARGETS")
    targets=[]
    for case in cases:
        for item in case["candidate_control_packets"]:
            u=item["root_uci_source_only_label_not_decoder_input"]
            b=chess.Board(item["conditions"]["fen_only"]["fen"])
            move=chess.Move.from_uci(u)
            if move not in b.legal_moves:
                raise ValueError("R030_R6_HOLD_NOMINATED_TARGET_ILLEGAL")
            targets.append((u,b,case["event_family"]))
    if set(reports)!=set(ARMS):
        raise ValueError("R030_R6_HOLD_MISSING_DECODER_ARM")
    rows=[]
    for arm in ARMS:
        report=reports[arm]
        if (report.get("schema")!=DECODER_SCHEMA or report.get("arm")!=arm
            or report.get("model_id")!=MODEL_ID
            or report.get("model_revision")!=MODEL_REVISION
            or report.get("input_blind_arm_sha256")!=ARM_SHA[arm]
            or report.get("no_truth_manifest_access_in_decoder") is not True
            or report.get("isolated_chat_context_every_entry") is not True
            or not isinstance(report.get("results"),list)
            or len(report["results"])!=4):
            raise ValueError("R030_R6_HOLD_DECODER_PROVENANCE_OR_FOUR_CASES")
        correct=0
        valid=0
        parsed=0
        details=[]
        for ordinal,item in enumerate(report["results"]):
            if item.get("ordinal")!=ordinal:
                raise ValueError("R030_R6_HOLD_DECODER_ORDINAL_DRIFT")
            target, board, family=targets[ordinal]
            u=item.get("parsed_uci_or_null")
            if u is not None and type(u) is not str:
                raise ValueError("R030_R6_HOLD_PARSED_TYPE")
            parsed+=u is not None
            try:
                legal=(u is not None and chess.Move.from_uci(u) in board.legal_moves)
            except ValueError:
                legal=False
            valid+=bool(legal)
            match=u==target
            correct+=match
            details.append({
                "ordinal":ordinal,"event_family":family,
                "historical_source_nominated_target":target,
                "decoder_uci_or_null":u,"uci_parsed":u is not None,
                "legal_for_original_board":bool(legal),
                "target_exact_match":match,
                "is_original_reference_best_move":False,
            })
        rows.append({"arm":arm,"n":4,"parsed_count":parsed,
                     "legal_count":valid,"nominated_target_recovered":correct,
                     "nominated_target_recovery_rate":correct/4.0,
                     "details":details})
    return {
        "schema":EVAL_SCHEMA,
        "owned_original_parfenova_pdf":
          "https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view",
        "inherited_r5_audit_sha":audit_sha,
        "model_id":MODEL_ID,"model_revision":MODEL_REVISION,
        "actual_open_weight_decoder_executed":True,
        "number_historically_exposed_original_positions":2,
        "number_historically_nominated_targets":4,
        "reference_best_move_comparison_not_available":True,
        "not_original_llm_generated_explanation":True,
        "not_original_paper_200_endgame_puzzles":True,
        "no_all_legal_token_probability_scores_yet":True,
        "no_causal_source_chess_mediation":True,
        "one_candidate_per_paired_case_can_share_fen":True,
        "reported_intervals_or_generalization":False,
        "arms":rows,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--audit",required=True)
    p.add_argument("--predictions-dir",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    audit_sha=digest(a.audit)
    if audit_sha!=R5_AUDIT_SHA:
        raise ValueError("R030_R6_HOLD_AUDIT_BYTES_BEFORE_PREDICTION_JOIN")
    audit=json.loads(Path(a.audit).read_text(encoding="utf-8"))
    reports={}
    for arm in ARMS:
        fn=Path(a.predictions_dir)/("R6_REAL_DECODER_"+arm+".json")
        reports[arm]=json.loads(fn.read_text(encoding="utf-8"))
    result=evaluate(audit,reports,audit_sha)
    out=Path(a.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    for arm in result["arms"]:
        print("R030_R6_REAL_SMALL_DECODER",arm["arm"],"nominated_match",
              arm["nominated_target_recovered"],"/4","legal",arm["legal_count"],"/4")
    print("R030_R6_EVALUATION_SHA256",digest(out))


if __name__=="__main__":
    main()
