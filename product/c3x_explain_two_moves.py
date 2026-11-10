#!/usr/bin/env python3
"""C3X 0.30/P1: a REAL learner-facing two-move contrastive explainer.

Original question: C3X 1.md (2026-08-14), held in Google Drive.
The output is a rule-grounded, search-backed educational report: NOT
proof of the physical cause of Stockfish's own original root decision.

Prior-art donors (original owned Drive):
Cui et al. (2026), response-contingent strategy communication;
Hebbar et al. (2026) ACT-Eval, atomic chess fact verification;
Parfenova (2026), verbal explanation target leakage caveats.

Inputs: any valid nonterminal FEN, and TWO explicitly legal UCI moves.
This first product vertical intentionally has no LLM or Maia assumptions.
It deliberately suppresses shared attributes and tells the learner
what evidence DOES and does not distinguish the two actions.

Root values use forced root analysis with the SAME engine at depths
8 and 10; downstream scores use SAME engine (depth 8), not an independent
referee. Child opponent replies are engine-ranked MultiPV top-k, not
all replies. Never call downstream reply set 'worst-case over all'.
"""
import argparse
import hashlib
import json
from pathlib import Path

import chess
import chess.engine

ENGINE_GIT_COMMIT="68e1e9b3811e16cad014b590d7443b9063b3eb52"
SOURCE_PRIMARY_DRIVE="https://drive.google.com/file/d/1zbNnM9shiG-IU-oFCbgB3Z5oMeKlZyNf/view"
ACT_EVAL_PRIMARY_DRIVE="https://drive.google.com/file/d/1BOHr8mZzY6vp14PBr2MrAiJH9vJDQStA/view"

SCHEMA="c3x030-p1-actual-chess-educational-contrastive-explainer-v1"
ROOT_DEPTHS=(8,10)
REPLY_DEPTH=8
REPLIES_K=3


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_board_and_pair(fen, first, second):
    try:
        board=chess.Board(fen)
        aa=chess.Move.from_uci(first)
        bb=chess.Move.from_uci(second)
    except (TypeError,ValueError) as err:
        raise ValueError("C3X_PRODUCT_HOLD_BAD_FEN_OR_UCI") from err
    if not board.is_valid() or board.is_game_over(claim_draw=False):
        raise ValueError("C3X_PRODUCT_HOLD_INVALID_OR_TERMINAL_POSITION")
    if aa==bb or aa not in board.legal_moves or bb not in board.legal_moves:
        raise ValueError("C3X_PRODUCT_HOLD_TWO_DISTINCT_LEGAL_CANDIDATES")
    return board,aa,bb


def measured_features(board, move):
    if move not in board.legal_moves:
        raise ValueError("C3X_PRODUCT_HOLD_NOT_LEGAL_FOR_FEATURES")
    before=board.copy(stack=True)
    original_mover=before.turn
    captured=before.is_capture(move)
    checked=before.gives_check(move)
    san=before.san(move)
    mover_piece=before.piece_at(move.from_square)
    if mover_piece is None:
        raise ValueError("C3X_PRODUCT_HOLD_MISSING_MOVER_PIECE")
    after=board.copy(stack=True)
    after.push(move)
    # Immediately after a root move, it is opponent's turn. These are
    # exact legal counts, NOT a heuristic assertion about long-term strategy.
    replies=after.legal_moves.count() if not after.is_game_over(claim_draw=False) else 0
    score={
        "uci":move.uci(),
        "san":san,
        "moving_piece":mover_piece.symbol().upper(),
        "is_capture":captured,
        "gives_check":checked,
        "is_promotion":move.promotion is not None,
        "opponent_immediate_legal_replies":replies,
        "opponent_in_check_after_move":after.is_check(),
        "opponent_turn_after_move": "white" if after.turn else "black",
        "original_mover":"white" if original_mover else "black"
    }
    if checked!=score["opponent_in_check_after_move"]:
        raise ValueError("C3X_PRODUCT_HOLD_CHECK_FACT_DRIFT")
    return score


def engine_score(info,board,origin_turn,requested_depth):
    if (type(info.get("depth")) is not int or info["depth"]<requested_depth
        or type(info.get("nodes")) is not int or info["nodes"]<=0
        or info.get("score") is None):
        raise ValueError("C3X_PRODUCT_HOLD_INCOMPLETE_REAL_ENGINE")
    pov=info["score"].pov(origin_turn)
    return {
        "mover_cp_or_null_if_mate":pov.score(),
        "mover_mate_plies_or_null":pov.mate() if pov.is_mate() else None,
        "depth":info["depth"],
        "nodes":info["nodes"],
        "pv_uci":[m.uci() for m in info.get("pv",[])[:8]],
    }


def root_analysis(board,move,engine,depth):
    result=engine.analyse(board,chess.engine.Limit(depth=depth),
                          root_moves=[move],game=object(),info=chess.engine.INFO_ALL)
    rec=engine_score(result,board,board.turn,depth)
    if not result.get("pv") or result["pv"][0]!=move:
        raise ValueError("C3X_PRODUCT_HOLD_FORCED_ROOT_PV_DRIFT")
    return rec


def ranked_replies_and_own_responses(board,move,engine):
    child=board.copy(stack=True)
    child.push(move)
    if child.is_game_over(claim_draw=False):
        return {"reply_source":"TERMINAL_NO_OPPONENT","reply_lines":[],"opponent_replies_total":0,
                "sampled_reply_count":0}
    n=child.legal_moves.count()
    k=min(REPLIES_K,n)
    infos=engine.analyse(child,chess.engine.Limit(depth=REPLY_DEPTH),
                         multipv=k,game=object(),info=chess.engine.INFO_ALL)
    if isinstance(infos,dict):
        infos=[infos]
    replies=[]
    for info in infos:
        score=engine_score(info,child,board.turn,REPLY_DEPTH)
        pv=info.get("pv")
        if not pv or pv[0] not in child.legal_moves:
            raise ValueError("C3X_PRODUCT_HOLD_BAD_RANKED_OPPONENT_REPLY")
        opponent=pv[0]
        after=child.copy(stack=True)
        san=child.san(opponent)
        after.push(opponent)
        if after.is_game_over(claim_draw=False):
            own_reply=None
            own_depth=None
            own_score=None
        else:
            judge=engine.analyse(after,chess.engine.Limit(depth=REPLY_DEPTH),
                                 game=object(),info=chess.engine.INFO_ALL)
            own_score=engine_score(judge,after,board.turn,REPLY_DEPTH)
            if not judge.get("pv") or judge["pv"][0] not in after.legal_moves:
                raise ValueError("C3X_PRODUCT_HOLD_OWN_FOLLOWUP_MISSING")
            own_reply=judge["pv"][0].uci()
            own_depth=judge["depth"]
        replies.append({
            "opponent_reply_uci":opponent.uci(),
            "opponent_reply_san":san,
            "engine_ranked_reply_candidate_mover_score":score,
            "measured_own_contingent_followup_uci_or_null":own_reply,
            "own_followup_depth_or_null":own_depth,
            "after_opponent_reply_fresh_engine_value":own_score,
        })
    if len(replies)!=k or len({r["opponent_reply_uci"] for r in replies})!=k:
        raise ValueError("C3X_PRODUCT_HOLD_REPLY_COVERAGE_OR_DUPLICATE")
    return {
        "reply_source":"TOP_K_SAME_STOCKFISH_MULTI_PV_NOT_FULL_OPPONENT_UNIVERSE",
        "opponent_replies_total":n,
        "sampled_reply_count":k,
        "reply_lines":replies
    }


def difference_facts(a,b):
    if a["original_mover"]!=b["original_mover"]:
        raise ValueError("C3X_PRODUCT_HOLD_PERSPECTIVE_MISMATCH")
    keys=("moving_piece","is_capture","gives_check","is_promotion",
          "opponent_immediate_legal_replies")
    different={}
    shared={}
    for key in keys:
        if a[key]==b[key]:
            shared[key]=a[key]
        else:
            different[key]={"candidate_a":a[key],"candidate_b":b[key]}
    return {"different_measured_facts":different,
            "suppressed_shared_measured_facts":shared,
            "shared_features_not_proposed_as_differentiating_reasons":True}


def generate(board,uci_a,uci_b,engine):
    original,aa,bb=verify_board_and_pair(board.fen(en_passant="fen"),uci_a,uci_b)
    rows=[]
    for move in (aa,bb):
        features=measured_features(original,move)
        root_depths={str(d):root_analysis(original,move,engine,d) for d in ROOT_DEPTHS}
        alternatives=ranked_replies_and_own_responses(original,move,engine)
        rows.append({"move_uci":move.uci(),"facts":features,
                     "forced_root_evaluations":root_depths,
                     "opponent_reply_probe":alternatives})
    d=difference_facts(rows[0]["facts"],rows[1]["facts"])
    cp=[]
    for depth in ROOT_DEPTHS:
        left=rows[0]["forced_root_evaluations"][str(depth)]["mover_cp_or_null_if_mate"]
        right=rows[1]["forced_root_evaluations"][str(depth)]["mover_cp_or_null_if_mate"]
        cp.append(left-right if left is not None and right is not None else None)
    flip=(cp[0] is not None and cp[1] is not None and cp[0]*cp[1]<0)
    could_be_tie=(any(v is None for v in cp) or min(abs(v) for v in cp)<=20 or flip)
    return {
        "schema":SCHEMA,"input_fen":original.fen(en_passant="fen"),
        "native_source_stockfish_commit":ENGINE_GIT_COMMIT,
        "score_perspective":"ORIGINAL_ROOT_MOVER",
        "forced_root_depths":list(ROOT_DEPTHS),
        "reply_selection_depth":REPLY_DEPTH,
        "reply_top_k":REPLIES_K,
        "root_candidates":rows,
        "contrastive_measured_facts":d,
        "candidate_A_minus_B_cp_by_depth_or_null":dict(zip(map(str,ROOT_DEPTHS),cp)),
        "candidate_preference_sign_flipped_across_depths":flip,
        "small_gap_or_mate_caution":could_be_tie,
        "no_full_reply_worst_case_claim":True,
        "no_independent_judge":True,
        "no_source_search_causal_mediation_claim":True,
        "not_claiming_chesscom_quality_superiority":True,
        "original_question_drive_url":SOURCE_PRIMARY_DRIVE,
        "act_eval_owned_primary_drive_url":ACT_EVAL_PRIMARY_DRIVE,
    }


def make_markdown(report):
    if report.get("schema")!=SCHEMA:
        raise ValueError("C3X_PRODUCT_HOLD_BAD_REPORT")
    a,b=report["root_candidates"]
    lines=[
        "# C3X — 두 후보 수의 차이는 무엇인가?",
        "",
        "이 보고서는 실제 Stockfish 검색과 체스 규칙 검사로 만든 교육용 비교다. "
        "**엔진이 왜 최종 수를 골랐는지의 내부 인과 증명은 아니다.**",
        "",
        f"**후보 A:** {a['facts']['san']} (`{a['move_uci']}`) · "
        f"**후보 B:** {b['facts']['san']} (`{b['move_uci']}`)",
        "",
        "## 1. 두 후보의 엔진 평가 (처음 수를 두는 쪽의 관점)",
        "",
        "| 탐색 깊이 | 후보 A (cp) | 후보 B (cp) | A−B (cp) |",
        "|---|---:|---:|---:|",
    ]
    for depth in ROOT_DEPTHS:
        av=a["forced_root_evaluations"][str(depth)]["mover_cp_or_null_if_mate"]
        bv=b["forced_root_evaluations"][str(depth)]["mover_cp_or_null_if_mate"]
        diff=report["candidate_A_minus_B_cp_by_depth_or_null"][str(depth)]
        lines.append(f"| {depth} | {av if av is not None else 'mate'} | "
                     f"{bv if bv is not None else 'mate'} | "
                     f"{diff if diff is not None else '미정'} |")
    lines += ["",
        "깊이 8과 10은 같은 Stockfish의 유한 깊이 탐색 결과다. "
        "두 깊이의 점수 차이를 통계적 신뢰구간으로 해석하지 않는다.",
        "",
        "## 2. 공통 특징을 제외한 실제 차이",
        "",
    ]
    different=report["contrastive_measured_facts"]["different_measured_facts"]
    if different:
        name={
            "moving_piece":"움직인 기물",
            "is_capture":"즉각 포획 여부",
            "gives_check":"즉각 체크 여부",
            "is_promotion":"승격 여부",
            "opponent_immediate_legal_replies":"상대의 즉시 합법 대응 수"
        }
        for k,v in different.items():
            lines.append(f"- **{name[k]}:** A={v['candidate_a']}, B={v['candidate_b']} "
                         "(체스 규칙에서 직접 확인)")
    else:
        lines.append("이 측정 범위에서는 구별되는 즉각 특징을 확인하지 못했다. "
                     "따라서 근거 없이 전략적 원인을 창작하지 않는다.")
    lines += ["",
        "같은 값으로 측정된 특징은 차별 원인으로 주장하지 않았다. "
        "상대의 합법 대응 수가 적다는 것만으로 해당 수가 더 좋다는 뜻은 아니다.",
        "",
        "## 3. 상대가 다르게 대응한다면? (실제 엔진 탐색)",
        "",
    ]
    for x in (a,b):
        probe=x["opponent_reply_probe"]
        lines.append(f"### {x['facts']['san']} 이후")
        lines.append(f"전체 합법 응수 {probe['opponent_replies_total']}개 중 "
                     f"같은 Stockfish의 depth {REPLY_DEPTH} MultiPV 상위 "
                     f"{probe['sampled_reply_count']}개만 확인했다.")
        if not probe["reply_lines"]:
            lines.append("더 둘 수 없는 종료 국면이다.")
        for reply in probe["reply_lines"]:
            follow=reply["measured_own_contingent_followup_uci_or_null"]
            score=reply["after_opponent_reply_fresh_engine_value"]
            val=("종료 국면" if score is None else
                 ("mate" if score["mover_cp_or_null_if_mate"] is None
                  else str(score["mover_cp_or_null_if_mate"])+" cp"))
            lines.append(f"- 상대 **{reply['opponent_reply_san']}** "
                         f"(`{reply['opponent_reply_uci']}`) → "
                         f"그다음 내 엔진 수: `{follow or '종료'}` · "
                         f"재검색한 가치: **{val}**")
        lines.append("")
    lines += ["## 4. 이 해설을 어디까지 믿을까?", ""]
    if report["small_gap_or_mate_caution"]:
        lines.append("**주의:** 작은 점수차, 깊이 간 부호 전환 또는 메이트 점수 때문에 "
                     "두 수의 미세한 우열을 확정하지 않는다.")
    else:
        lines.append("두 깊이에서 후보 간 점수 차가 유지됐더라도 "
                     "보다 깊은 검색이나 독립 엔진 평가 전에는 최종 확정하지 않는다.")
    lines += [
        "실험한 상대 응수는 전수조사가 아니며, 따라서 가능한 모든 응수에 대한 "
        "최악값이나 최적 전략의 존재를 입증하지 않는다.",
        "즉각적인 전술·합법 수 차이는 검증 가능하지만, 장기 전략의 인과적 이유는 "
        "독립적인 추가 실험 없이는 단정하지 않는다.",
        "",
        "## 참고 방법",
        "",
        f"- [최초 C3X 질문, 원본 Drive]({SOURCE_PRIMARY_DRIVE})",
        f"- [ACT-Eval 원문, 원본 Drive]({ACT_EVAL_PRIMARY_DRIVE})",
        "- Stockfish16 실제 UCI 검색, 두 깊이의 강제 후보와 "
        "최대 3개 상대 응수에 대한 재검색",
        "",
    ]
    return "\n".join(lines)


def main():
    p=argparse.ArgumentParser()
    for name in ("fen","move-a","move-b","engine","out-json","out-md"):
        p.add_argument("--"+name,required=True)
    a=p.parse_args()
    board,m1,m2=verify_board_and_pair(a.fen,a.move_a,a.move_b)
    with chess.engine.SimpleEngine.popen_uci(a.engine,timeout=120) as e:
        if ("stockfish" not in e.id.get("name","").lower()
            or not {"Use NNUE","Threads","Hash"}.issubset(e.options)):
            raise ValueError("C3X_PRODUCT_HOLD_NOT_STOCKFISH_OR_UNPINNED_OPTIONS")
        e.configure({"Use NNUE":False,"Threads":1,"Hash":16})
        data=generate(board,m1.uci(),m2.uci(),e)
    data["actual_engine_binary_sha256"]=sha(a.engine)
    dest=Path(a.out_json)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(data,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    md=Path(a.out_md)
    md.parent.mkdir(parents=True,exist_ok=True)
    md.write_text(make_markdown(data),encoding="utf-8")
    print("C3X_PRODUCT_REAL_ENGINE_COMPARISON",data["root_candidates"][0]["facts"]["san"],
          "VS",data["root_candidates"][1]["facts"]["san"],
          "REPORT_SHA",sha(dest),"MARKDOWN_SHA",sha(md),flush=True)


if __name__=="__main__":
    main()
