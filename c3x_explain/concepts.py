from __future__ import annotations
from typing import Any
import chess

CENTER=(chess.D4,chess.E4,chess.D5,chess.E5)
START_MINOR={
    chess.WHITE:(chess.B1,chess.G1,chess.C1,chess.F1),
    chess.BLACK:(chess.B8,chess.G8,chess.C8,chess.F8),
}

def _doubled_pawn_files(board:chess.Board,color:chess.Color)->int:
    n=0
    pawns=board.pieces(chess.PAWN,color)
    for f in range(8):
        if len([sq for sq in pawns if chess.square_file(sq)==f])>=2:n+=1
    return n

def _isolated_pawns(board:chess.Board,color:chess.Color)->int:
    pawns=board.pieces(chess.PAWN,color);n=0
    for sq in pawns:
        f=chess.square_file(sq)
        neigh={f-1,f+1}
        if not any(chess.square_file(o) in neigh for o in pawns):n+=1
    return n

def _passed_pawns(board:chess.Board,color:chess.Color)->int:
    ours=board.pieces(chess.PAWN,color);theirs=board.pieces(chess.PAWN,not color);n=0
    for sq in ours:
        f=chess.square_file(sq);r=chess.square_rank(sq)
        blocked=False
        for o in theirs:
            of,orr=chess.square_file(o),chess.square_rank(o)
            if abs(of-f)>1:continue
            if color==chess.WHITE and orr>r:blocked=True;break
            if color==chess.BLACK and orr<r:blocked=True;break
        if not blocked:n+=1
    return n

def _king_shield_proxy(board:chess.Board,color:chess.Color)->int:
    k=board.king(color)
    if k is None:return 0
    kf,kr=chess.square_file(k),chess.square_rank(k)
    forward=1 if color==chess.WHITE else -1;n=0
    rr=kr+forward
    if not 0<=rr<8:return 0
    for f in (kf-1,kf,kf+1):
        if 0<=f<8:
            p=board.piece_at(chess.square(f,rr))
            if p and p.color==color and p.piece_type==chess.PAWN:n+=1
    return n

def _minor_home_count(board:chess.Board,color:chess.Color)->int:
    n=0
    for sq in START_MINOR[color]:
        p=board.piece_at(sq)
        if p and p.color==color and p.piece_type in (chess.KNIGHT,chess.BISHOP):n+=1
    return n

def _center_control(board:chess.Board,color:chess.Color)->int:
    return sum(any(board.is_attacked_by(color,sq) for _ in (0,)) for sq in CENTER)

def _center_occupancy(board:chess.Board,color:chess.Color)->int:
    return sum(bool((p:=board.piece_at(sq)) and p.color==color) for sq in CENTER)

def _open_files(board:chess.Board)->int:
    pawns=board.pieces(chess.PAWN,chess.WHITE)|board.pieces(chess.PAWN,chess.BLACK)
    return sum(not any(chess.square_file(sq)==f for sq in pawns) for f in range(8))

def snapshot(board:chess.Board,perspective:chess.Color)->dict[str,int]:
    """Exact board-derived proxies only. Names deliberately avoid semantic overclaim."""
    opp=not perspective
    return {
        "own_center_control_count":_center_control(board,perspective),
        "opp_center_control_count":_center_control(board,opp),
        "own_center_occupancy_count":_center_occupancy(board,perspective),
        "opp_center_occupancy_count":_center_occupancy(board,opp),
        "own_minor_home_count":_minor_home_count(board,perspective),
        "opp_minor_home_count":_minor_home_count(board,opp),
        "own_doubled_pawn_file_count":_doubled_pawn_files(board,perspective),
        "opp_doubled_pawn_file_count":_doubled_pawn_files(board,opp),
        "own_isolated_pawn_count":_isolated_pawns(board,perspective),
        "opp_isolated_pawn_count":_isolated_pawns(board,opp),
        "own_passed_pawn_count":_passed_pawns(board,perspective),
        "opp_passed_pawn_count":_passed_pawns(board,opp),
        "own_king_shield_proxy":_king_shield_proxy(board,perspective),
        "opp_king_shield_proxy":_king_shield_proxy(board,opp),
        "open_file_count":_open_files(board),
    }

def after_move(board:chess.Board,move:chess.Move,perspective:chess.Color)->dict[str,int]:
    q=board.copy(stack=False);q.push(move);return snapshot(q,perspective)

def candidate_delta(board:chess.Board,played:chess.Move,alternative:chess.Move)->dict[str,Any]:
    """played minus alternative. Difference is descriptive, never causal."""
    perspective=board.turn
    p=after_move(board,played,perspective);a=after_move(board,alternative,perspective)
    d={k:p[k]-a[k] for k in p if p[k]!=a[k]}
    return {"played_uci":played.uci(),"alternative_uci":alternative.uci(),
            "played_snapshot":p,"alternative_snapshot":a,"played_minus_alternative":d}
