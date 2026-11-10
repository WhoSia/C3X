#!/usr/bin/env python3
"""C3X 0.30/P2: CCC-inspired symbolic *differential* chess concept probes.

Owned primary: Kim et al. (2024) Concept-Guided Chess Commentary
https://drive.google.com/file/d/1XpI5v0HJe_LNfa3HfKIlnEDVkJ-Fct74/view

Important: NOT the original trained concept extraction model, not CCC's
concept accuracy, not a causal attribution of original Stockfish scores.
These are explicitly-defined board measurements, NOT generic human claims
such as 'this is the strategic reason for best move'.
"""
import argparse
import hashlib
import json
from pathlib import Path

import chess

CCC_DRIVE="https://drive.google.com/file/d/1XpI5v0HJe_LNfa3HfKIlnEDVkJ-Fct74/view"
SCHEMA="c3x030-p2-concept-contrastive-symbolic-postmove-facts-v1"
PIECE_MATERIAL_CP={chess.PAWN:100,chess.KNIGHT:320,chess.BISHOP:330,
                   chess.ROOK:500,chess.QUEEN:900}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def own_passed_pawns(board,color):
    """An own pawn has no enemy pawn on its file or adjacent files AHEAD.

    Orthodox passed pawn definition, independent of dynamic chess value.
    """
    pawns=board.pieces(chess.PAWN,color)
    enemy=board.pieces(chess.PAWN,not color)
    result=[]
    for sq in pawns:
        file=chess.square_file(sq)
        rank=chess.square_rank(sq)
        blocked=False
        for e in enemy:
            if abs(chess.square_file(e)-file)<=1:
                erank=chess.square_rank(e)
                if (erank>rank if color==chess.WHITE else erank<rank):
                    blocked=True
                    break
        if not blocked:
            result.append(chess.square_name(sq))
    return sorted(result)


def pawn_islands(board,color):
    occupied_files=sorted({chess.square_file(s) for s in board.pieces(chess.PAWN,color)})
    return sum(i==0 or f-occupied_files[i-1]>1 for i,f in enumerate(occupied_files))


def material_balance_cp(board,mover):
    return sum(v*(len(board.pieces(t,mover))-len(board.pieces(t,not mover)))
               for t,v in PIECE_MATERIAL_CP.items())


def attacked_enemy_nonking(board,mover):
    targets=[]
    for sq,piece in board.piece_map().items():
        if piece.color!=mover and piece.piece_type!=chess.KING:
            if board.is_attacked_by(mover,sq):
                targets.append(chess.square_name(sq)+":"+piece.symbol())
    return sorted(targets)


def unprotected_attacked_own_nonking(board,mover):
    targets=[]
    for sq,piece in board.piece_map().items():
        if piece.color==mover and piece.piece_type!=chess.KING:
            if board.is_attacked_by(not mover,sq) and not board.is_attacked_by(mover,sq):
                targets.append(chess.square_name(sq)+":"+piece.symbol())
    return sorted(targets)


def king_ring_enemy_attacked_squares(board,mover):
    """Count attacked adjacent squares, not an engine king-safety evaluation."""
    king=board.king(mover)
    if king is None:
        raise ValueError("C3X_P2_HOLD_NO_KING")
    return sorted(chess.square_name(sq) for sq in chess.SQUARES
                  if chess.square_distance(king,sq)==1
                  and board.is_attacked_by(not mover,sq))


def concept_facts_after(board,move):
    if not isinstance(board,chess.Board) or not board.is_valid() or move not in board.legal_moves:
        raise ValueError("C3X_P2_HOLD_BOARD_OR_MOVE")
    mover=board.turn
    after=board.copy(stack=True)
    after.push(move)
    if not after.is_valid():
        raise ValueError("C3X_P2_HOLD_INVALID_AFTER_MOVE")
    return {
        "own_material_advantage_simple_piece_values_cp":material_balance_cp(after,mover),
        "own_passed_pawn_squares":own_passed_pawns(after,mover),
        "own_pawn_island_count":pawn_islands(after,mover),
        "enemy_nonking_occupied_squares_attacked_by_own_pieces":attacked_enemy_nonking(after,mover),
        "own_nonking_pieces_attacked_but_not_defended_in_attack_graph":unprotected_attacked_own_nonking(after,mover),
        "own_king_adjacent_squares_attacked_by_enemy":king_ring_enemy_attacked_squares(after,mover),
        "opponent_legal_response_count_after_move":
            after.legal_moves.count() if not after.is_game_over(claim_draw=False) else 0,
        "attack_graph_includes_pinned_piece_attacks_not_guaranteed_legal_capture":True,
    }


def contrast(board,uci_a,uci_b):
    try:
        a=chess.Move.from_uci(uci_a)
        b=chess.Move.from_uci(uci_b)
    except ValueError as err:
        raise ValueError("C3X_P2_HOLD_BAD_UCI") from err
    if a==b or a not in board.legal_moves or b not in board.legal_moves:
        raise ValueError("C3X_P2_HOLD_TWO_DISTINCT_LEGAL_ROOTS")
    af=concept_facts_after(board,a)
    bf=concept_facts_after(board,b)
    dif={}
    common={}
    for key in af:
        if key=="attack_graph_includes_pinned_piece_attacks_not_guaranteed_legal_capture":
            continue
        if af[key]==bf[key]:
            common[key]=af[key]
        else:
            dif[key]={"first":af[key],"second":bf[key]}
    return {
        "schema":SCHEMA,
        "source_original_fen":board.fen(en_passant="fen"),
        "mover":"white" if board.turn else "black",
        "root_moves_uci":[a.uci(),b.uci()],
        "complete_rule_based_concept_facts":{a.uci():af,b.uci():bf},
        "concept_dimensions_different":dif,
        "concept_dimensions_shared_suppressed":common,
        "no_automatic_engine_score_attribution":True,
        "not_original_2024_CCC_learned_concept_model":True,
        "not_long_term_strategy_claim":True,
        "owned_primary_pdf":CCC_DRIVE,
    }


DESCRIPTIONS={
"own_material_advantage_simple_piece_values_cp":"원래 수를 두는 쪽의 단순 기물 가치 차이 (cp 환산, 실제 엔진 평가가 아님)",
"own_passed_pawn_squares":"패스폰 위치 (동일·인접 파일 전방에 적 폰이 없는 폰)",
"own_pawn_island_count":"폰 섬 수 (연속된 폰 존재 파일의 그룹 수)",
"enemy_nonking_occupied_squares_attacked_by_own_pieces":"공격받는 적 기물 칸 (기물 공격 그래프)",
"own_nonking_pieces_attacked_but_not_defended_in_attack_graph":"공격받지만 방어자가 없는 우리 기물 칸 (공격 그래프)",
"own_king_adjacent_squares_attacked_by_enemy":"상대가 공격하는 우리 킹 주변 8칸 중 해당 칸",
"opponent_legal_response_count_after_move":"상대의 즉시 합법 응수 수",
}


def markdown_append(report):
    if report.get("schema")!=SCHEMA:
        raise ValueError("C3X_P2_HOLD_BAD_CONCEPT_REPORT")
    moves=report["root_moves_uci"]
    lines=["## 5. 선행연구에서 가져온 기물·폰 구조 개념의 실제 차이",
           "",
           "아래 항목은 **Kim 등의 Concept-Guided Chess Commentary에서 착안한 규칙 기반 측정**이다. "
           "원 논문의 학습된 추출기와 동일하다고 주장하지 않는다.",
           ""]
    if report["concept_dimensions_different"]:
        for key,row in report["concept_dimensions_different"].items():
            lines.append(f"- **{DESCRIPTIONS[key]}:** `{moves[0]}`={row['first']}; "
                         f"`{moves[1]}`={row['second']}")
    else:
        lines.append("정의한 개념들에서는 차이가 없으므로 차별 원인을 만들어 쓰지 않는다.")
    lines+=["",
        f"비교에서 같았던 개념 **{len(report['concept_dimensions_shared_suppressed'])}개**는 "
        "차별 원인으로 출력하지 않았다.",
        "공격 그래프는 핀 된 기물의 공격도 셀 수 있고, 킹 주변의 공격 칸 수가 "
        "Stockfish의 실제 king-safety 평가값을 뜻하지 않는다.",
        "이 지표들이 달라졌다는 사실과 **그 때문에 원본 엔진이 해당 수를 골랐다는 인과 설명**은 다르다.",
        "",
        f"- [Kim et al. (2024) CCC 원문, Google Drive]({CCC_DRIVE})",
        ""]
    return "\n".join(lines)


def main():
    p=argparse.ArgumentParser()
    for n in ("base-report-json","out-json","out-md"):
        p.add_argument("--"+n,required=True)
    a=p.parse_args()
    original=json.loads(Path(a.base_report_json).read_text(encoding="utf-8"))
    if original.get("schema")!="c3x030-p1-actual-chess-educational-contrastive-explainer-v1":
        raise ValueError("C3X_P2_HOLD_NOT_ORIGINAL_PRODUCT_REPORT")
    board=chess.Board(original["input_fen"])
    moves=[v["move_uci"] for v in original["root_candidates"]]
    result=contrast(board,*moves)
    out=Path(a.out_json)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    outmd=Path(a.out_md)
    outmd.parent.mkdir(parents=True,exist_ok=True)
    outmd.write_text(markdown_append(result),encoding="utf-8")
    print("C3X_P2_REAL_RULE_BASED_CONCEPT_CONTRAST",
          moves,"different",len(result["concept_dimensions_different"]),
          "common_suppressed",len(result["concept_dimensions_shared_suppressed"]),
          "json_sha256",sha(out),flush=True)


if __name__=="__main__":
    main()
