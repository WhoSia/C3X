from __future__ import annotations
from typing import Any
import chess

PIECE_VALUE={
    chess.PAWN:1,
    chess.KNIGHT:3,
    chess.BISHOP:3,
    chess.ROOK:5,
    chess.QUEEN:9,
    chess.KING:100,
}

def _piece_doc(piece: chess.Piece|None)->dict[str,Any]|None:
    if piece is None:return None
    return {"color":"white" if piece.color else "black","piece_type":chess.piece_name(piece.piece_type),"value":PIECE_VALUE[piece.piece_type]}

def _captured_piece(board:chess.Board,move:chess.Move)->chess.Piece|None:
    if board.is_en_passant(move):
        sq=move.to_square + (-8 if board.turn==chess.WHITE else 8)
        return board.piece_at(sq)
    return board.piece_at(move.to_square)

def _absolute_pins(board:chess.Board,color:chess.Color)->set[int]:
    return {sq for sq in board.piece_map() if (p:=board.piece_at(sq)) and p.color==color and board.is_pinned(color,sq)}

def verified_move_evidence(board:chess.Board,move:chess.Move)->list[dict[str,Any]]:
    """Board-verifiable facts only. No claim here states why an engine preferred the move."""
    if move not in board.legal_moves:raise ValueError(f"illegal move: {move.uci()}")
    mover=board.turn;enemy=not mover;san=board.san(move);captured=_captured_piece(board,move)
    pins_before=_absolute_pins(board,enemy)
    out:list[dict[str,Any]]=[]
    if board.is_capture(move):
        out.append({"kind":"capture","san":san,"captured":_piece_doc(captured),"verified":True})
    if board.is_castling(move):out.append({"kind":"castling","san":san,"verified":True})
    if move.promotion:
        out.append({"kind":"promotion","san":san,"promotes_to":chess.piece_name(move.promotion),"verified":True})
    q=board.copy(stack=False);q.push(move)
    if q.is_checkmate():out.append({"kind":"checkmate","san":san,"verified":True})
    elif q.is_check():out.append({"kind":"check","san":san,"verified":True})
    attacked=[]
    moved=q.piece_at(move.to_square)
    if moved:
        for sq in sorted(q.attacks(move.to_square)):
            p=q.piece_at(sq)
            if p and p.color==enemy:
                attacked.append({"square":chess.square_name(sq),"piece":_piece_doc(p)})
    valuable=[z for z in attacked if z["piece"]["value"]>=3 or z["piece"]["piece_type"]=="king"]
    if len(valuable)>=2:
        out.append({"kind":"multi_attack","san":san,"attacked":valuable,"verified":True,
                    "scope":"moved piece attacks at least two enemy pieces of value >=3 or the king"})
    pins_after=_absolute_pins(q,enemy)
    created=[]
    for sq in sorted(pins_after-pins_before):
        p=q.piece_at(sq)
        if p:created.append({"square":chess.square_name(sq),"piece":_piece_doc(p)})
    if created:
        out.append({"kind":"absolute_pin_created","san":san,"pinned":created,"verified":True,
                    "scope":"enemy piece is absolutely pinned to its king after the move"})
    return out

def tactical_contrast(board:chess.Board,played:chess.Move,alternative:chess.Move)->dict[str,Any]:
    p=verified_move_evidence(board,played);a=verified_move_evidence(board,alternative)
    pk={z["kind"] for z in p};ak={z["kind"] for z in a}
    return {
        "played_uci":played.uci(),
        "alternative_uci":alternative.uci(),
        "played_evidence":p,
        "alternative_evidence":a,
        "played_only_kinds":sorted(pk-ak),
        "alternative_only_kinds":sorted(ak-pk),
        "shared_kinds":sorted(pk&ak),
    }
