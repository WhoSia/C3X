#!/usr/bin/env python3
"""C3X 0.30/P6 — provenance-first conditional chess strategy annotation.

Prior art in user's own Drive:
- Shivkumar et al. (2026), chess board -> structured annotations -> LM text
  (IEEE Access DOI 10.1109/ACCESS.2026.3725218).
- Bhaskar, Cheng & Chen (2026), QUEEN, chess-expert-conditioned future
  position explanations (arXiv 2610.03695).
- Cui, Ling & Ng (2026) §4.1 opponent-ranked partial strategy trees.
- Jacovi & Goldberg (2020) don't equate fluency/plausibility with faithfulness.

This implementation ONLY reproduces a *deterministic structured annotation
stage* that faithfully verbalizes actual legal source-engine response
branches. No model training, encoder weights, PPO, logit lens, LLM generation
or original papers' evaluation is claimed.

Input: P4 source tree (genuinely engine-created or transparently mocked in
tests), with FEN and two separately forced root moves.
Output: replay-verified atomic Korean conditional annotations. Every source
move in EVERY trace must be legal and agree with the full P4 tree.
"""
import argparse
import hashlib
import json
from pathlib import Path

import chess

from c3x_recursive_strategy import SCHEMA as P4_SCHEMA

SCHEMA="c3x030-p6-evidence-linked-conditional-strategy-annotation-v1"
SHIVKUMAR_DRIVE="https://drive.google.com/file/d/1BOP1Qx7kApbNWKCf7KbKbowPrTTTP6IR/view"
QUEEN_DRIVE="https://drive.google.com/file/d/1I1HikAacandg5b75R0zymJlgxAQ41gbG/view"
CUI_DRIVE="https://drive.google.com/file/d/19zqCJXM631qasR9uIyg4GuBZxIBO7czw/view"
JACOVI_DRIVE="https://drive.google.com/file/d/11ltQLiTQxQuFiKMJb5jnVtK5U--WtNXP/view"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def replay_trace(root_board,trace,expected_sans=None):
    if not isinstance(trace,list) or len(trace)>5 or not trace:
        raise ValueError("P6_HOLD_TRACE_LENGTH")
    board=root_board.copy(stack=True)
    sans=[]
    for u in trace:
        try:
            move=chess.Move.from_uci(u)
        except ValueError as err:
            raise ValueError("P6_HOLD_INVALID_UCI") from err
        if move not in board.legal_moves:
            raise ValueError("P6_HOLD_ILLEGAL_SOURCE_MOVE")
        sans.append(board.san(move))
        board.push(move)
    if expected_sans is not None and sans!=expected_sans:
        raise ValueError("P6_HOLD_SAN_INCONSISTENCY")
    return sans,board


def annotate(source):
    if (source.get("schema")!=P4_SCHEMA
        or source.get("same_engine_not_independent_judge") is not True
        or source.get("complete_opponent_reply_universe") is not False
        or source.get("not_original_cui_verbalizer_or_human_eval") is not True
        or len(source.get("roots",[]))!=2):
        raise ValueError("P6_HOLD_SOURCE_TREE_EVIDENCE_IDENTITY")
    try:
        root_board=chess.Board(source["fen"])
    except (ValueError,KeyError) as err:
        raise ValueError("P6_HOLD_INVALID_ROOT_FEN") from err
    if not root_board.is_valid() or root_board.is_game_over(claim_draw=False):
        raise ValueError("P6_HOLD_INVALID_ROOT_FEN")
    report=[]
    for idx,root in enumerate(source["roots"]):
        candidate=root["root_uci"]
        move=chess.Move.from_uci(candidate)
        if (move not in root_board.legal_moves
            or root["root_san"]!=root_board.san(move)
            or root.get("source_opponent_k")!=2
            or root.get("opponent_layers")!=2
            or root.get("leaf_count")!=4
            or len(root.get("tree",[]))!=2):
            raise ValueError("P6_HOLD_ROOT_SOURCE_FACT_OR_TREE_CONTRACT")
        clauses=[]
        observed_traces=set()
        first_seen=set()
        for first in root["tree"]:
            if first.get("terminal") or first.get("opponent_rank_1based") not in (1,2):
                raise ValueError("P6_HOLD_UNEXPECTED_TERMINAL_OR_RANK")
            r1=first["opponent_move"]["action_uci"]
            own1=first["own_best_move_or_null"]["action_uci"]
            trace3=[candidate,r1,own1]
            actual3,_=replay_trace(root_board,trace3)
            if (first["opponent_move"]["action_san"]!=actual3[1] or
                first["own_best_move_or_null"]["action_san"]!=actual3[2] or
                first["trace_uci"]!=trace3):
                raise ValueError("P6_HOLD_FIRST_BRANCH_SOURCE_CONFLICT")
            first_seen.add(r1)
            second_seen=set()
            deeper=first["next_opponent_replies"]
            if len(deeper)!=2:
                raise ValueError("P6_HOLD_SECOND_BRANCHING_NOT_COMPLETE_K2")
            for second in deeper:
                if second.get("terminal") or second.get("opponent_rank_1based") not in (1,2):
                    raise ValueError("P6_HOLD_SECOND_RANK_OR_TERMINAL")
                r2=second["opponent_move"]["action_uci"]
                own2=second["own_best_move_or_null"]["action_uci"]
                trace=[candidate,r1,own1,r2,own2]
                sans,_=replay_trace(root_board,trace)
                if (second["trace_uci"]!=trace
                    or second["opponent_move"]["action_san"]!=sans[3]
                    or second["own_best_move_or_null"]["action_san"]!=sans[4]):
                    raise ValueError("P6_HOLD_SECOND_BRANCH_SOURCE_CONFLICT")
                if tuple(trace) in observed_traces:
                    raise ValueError("P6_HOLD_DUPLICATE_SOURCE_PATH")
                observed_traces.add(tuple(trace))
                second_seen.add(r2)
                first_label="A" if idx==0 else "B"
                message=(f"후보 {first_label} {sans[0]} 다음 상대가 {sans[1]}로 응수하면 "
                         f"엔진은 {sans[2]}를 제안한다. 이어 상대가 {sans[3]}를 두면 "
                         f"내 대응은 {sans[4]}다.")
                clauses.append({
                    "candidate_index":idx,
                    "candidate_root_uci":candidate,
                    "opponent_rank_first":first["opponent_rank_1based"],
                    "opponent_rank_second":second["opponent_rank_1based"],
                    "trace_uci":trace,
                    "trace_san":sans,
                    "korean_explanation":message,
                    "proof_kind":"REPLAYED_CHESS_RULES_PLUS_SOURCE_SELECTED_MOVES",
                    "grounding":"CUI_SOURCE_CONDITIONAL_TREE_2_OPPONENT_LAYERS",
                    "branch_quality_or_opponent_probability_claimed":False,
                    "independent_engine_quality_claimed":False,
                    "physical_original_stockfish_decision_causality_claimed":False,
                })
            if len(second_seen)!=2:
                raise ValueError("P6_HOLD_SECOND_DUPLICATE_ACTION")
        if len(first_seen)!=2 or len(observed_traces)!=4:
            raise ValueError("P6_HOLD_FIRST_DUPLICATE_OR_PATH_COUNT")
        if observed_traces!={tuple(x["trace_uci"]) for x in root["leaf_paths"]}:
            raise ValueError("P6_HOLD_SOURCE_LEAF_SET_MISMATCH")
        report.append({
            "root_uci":candidate,
            "root_san":root["root_san"],
            "source_opponent_coverage_only_k2":True,
            "distinct_complete_source_branches":4,
            "atomic_conditional_annotations":clauses,
        })
    if len({x["root_uci"] for x in report})!=2:
        raise ValueError("P6_HOLD_IDENTICAL_ROOTS")
    return {
        "schema":SCHEMA,
        "source_fen":source["fen"],
        "method":"Cui two-layer actual source tree => chess-law replay-verified annotation",
        "original_papers_drive":{
            "Cui_strategy":CUI_DRIVE,
            "Shivkumar_staged_annotation":SHIVKUMAR_DRIVE,
            "QUEEN_conditional_reasons":QUEEN_DRIVE,
            "Jacovi_explanation_faithfulness":JACOVI_DRIVE,
        },
        "roots":report,
        "fully_replay_verified_annotations":8,
        "no_LLM_inference_or_original_paper_full_replication":True,
        "no_independent_referee_for_new_user_fen":True,
        "no_search_causality_conclusion":True,
    }


def markdown(result):
    if result.get("schema")!=SCHEMA:
        raise ValueError("P6_HOLD_WRONG_ANNOTATION")
    lines=["# C3X — 실제 미래 대응을 설명하는 조건부 전략", "",
           "다음 문장은 **체스 규칙으로 수순을 재생하고 원본 엔진의 실제 선택을 확인한** 문장이다. "
           "선택한 상대 응수에 관한 설명이며 상대의 모든 수에 대한 보장은 아니다.", ""]
    for root in result["roots"]:
        lines.append(f"## 후보 {root['root_san']} ({root['root_uci']})")
        lines.append("")
        for c in root["atomic_conditional_annotations"]:
            lines.append("- "+c["korean_explanation"])
        lines.append("")
    lines+=["**검증 범위:** 원본 엔진이 고른 k=2 상대 응수 두 계층, 총 8개 합법 경로. "
             "다른 엔진의 모든 응수에 대한 우위, 원래 엔진 내부 선택의 인과성, "
             "사람의 학습 효과는 아직 입증되지 않았다.",
             "",f"- [Cui 전략나무 원문 Drive]({CUI_DRIVE})",
             f"- [Shivkumar 구조화 주석 원문 Drive]({SHIVKUMAR_DRIVE})",
             f"- [QUEEN 원문 Drive]({QUEEN_DRIVE})",
             f"- [Jacovi & Goldberg 충실성 원문 Drive]({JACOVI_DRIVE})",""]
    return "\n".join(lines)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--source-sha",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--out-md",required=True)
    args=p.parse_args()
    if (len(args.source_sha)!=64 or any(c not in "0123456789abcdef" for c in args.source_sha)
        or sha(args.source)!=args.source_sha):
        raise ValueError("P6_HOLD_ORIGINAL_SOURCE_SHA")
    data=annotate(json.loads(Path(args.source).read_text(encoding="utf-8")))
    data["original_source_sha256"]=args.source_sha
    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False,
                              allow_nan=False)+"\n",encoding="utf-8")
    md=Path(args.out_md)
    md.parent.mkdir(parents=True,exist_ok=True)
    md.write_text(markdown(data),encoding="utf-8")
    print("C3X_P6_RULE_VERIFIED_CONDITIONAL_ANNOTATIONS",
          data["fully_replay_verified_annotations"],
          "ANNOTATIONS_SHA",sha(out),"KOREAN_MD_SHA",sha(md),flush=True)


if __name__=="__main__":
    main()
