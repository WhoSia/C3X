#!/usr/bin/env python3
"""Engine-free chess microstructure for preselected March source positions.

This is geometric/legal CHESS context, not a claim that a motif causes any
native chess-engine root choice. No Stockfish, no move ranking, no thresholds
learned from engine results. Works with python-chess==1.11.2.
"""
import argparse
import hashlib
import json
from pathlib import Path
import chess

MARCH_SHA = "d79e48633be2b683176f1a6d4650aeea1b7584f11c85c2349a5bddda113febee"
MAJOR = (chess.QUEEN,chess.ROOK,chess.BISHOP,chess.KNIGHT)

def ray_between(a,b):
    return chess.between(a,b)

def absolute_pins(board,color):
    """Only legal geometry: pinning a friendly piece to own king."""
    king=board.king(color)
    if king is None:
        raise ValueError("INVALID_KING_POSITION")
    out=[]
    for sq in chess.SQUARES:
        piece=board.piece_at(sq)
        if piece is None or piece.color!=color or piece.piece_type==chess.KING:
            continue
        if board.is_pinned(color,sq):
            mask=board.pin(color,sq)
            out.append({"pinned_square":chess.square_name(sq),
                        "pinned_piece":chess.piece_name(piece.piece_type),
                        "king_square":chess.square_name(king),
                        "legal_pin_line_mask":f"{int(mask):016x}"})
    return sorted(out,key=lambda x:x["pinned_square"])

def checks_and_captures(board):
    checks=[]
    captures=[]
    for move in board.legal_moves:
        key=move.uci()
        if board.gives_check(move):
            checks.append(key)
        if board.is_capture(move):
            captures.append(key)
    return sorted(checks),sorted(captures)

def relative_pin_rays(board,color):
    """Geometric x-rays only; king pins excluded, no tactical success claim."""
    out=[]
    enemy=not color
    for slider_sq,piece in board.piece_map().items():
        if piece.color!=enemy or piece.piece_type not in (chess.BISHOP,chess.ROOK,chess.QUEEN):
            continue
        attacks=board.attacks(slider_sq)
        for front in attacks:
            f=board.piece_at(front)
            if f is None or f.color!=color or f.piece_type==chess.KING:
                continue
            # Candidate ray: slider -> defender piece -> valuable back piece.
            rays=chess.SQUARES if piece.piece_type==chess.QUEEN else chess.SQUARES
            for back in rays:
                rear=board.piece_at(back)
                if rear is None or rear.color!=color or rear.piece_type==chess.KING:
                    continue
                between=ray_between(slider_sq,back)
                if not between or not (between & chess.BB_SQUARES[front]):
                    continue
                if chess.popcount(between & board.occupied) != 1:
                    continue
                if piece.piece_type==chess.BISHOP and not (
                    abs(chess.square_file(slider_sq)-chess.square_file(back))==
                    abs(chess.square_rank(slider_sq)-chess.square_rank(back))):
                    continue
                if piece.piece_type==chess.ROOK and not (
                    chess.square_file(slider_sq)==chess.square_file(back) or
                    chess.square_rank(slider_sq)==chess.square_rank(back)):
                    continue
                out.append((chess.square_name(slider_sq),
                            chess.square_name(front),chess.square_name(back),
                            piece.symbol().lower(),f.symbol().lower(),rear.symbol().lower()))
    return [dict(zip(("attacker","blocker","rear_target","attacker_type",
                      "blocker_type","rear_type"), row)) for row in sorted(set(out))]

def passed_pawns(board,color):
    out=[]
    their_pawns=board.pieces(chess.PAWN,not color)
    for sq in board.pieces(chess.PAWN,color):
        f=chess.square_file(sq)
        rank=chess.square_rank(sq)
        passed=True
        for opp in their_pawns:
            if abs(chess.square_file(opp)-f)>1:
                continue
            ahead=(chess.square_rank(opp)>rank if color==chess.WHITE
                   else chess.square_rank(opp)<rank)
            if ahead:
                passed=False
                break
        if passed:
            out.append(chess.square_name(sq))
    return sorted(out)

def board_features(fen4):
    fields=fen4.split()
    if len(fields)!=4:
        raise ValueError("FEN4_FIELD_COUNT")
    b=chess.Board(fen4+" 0 1")
    if not b.is_valid():
        raise ValueError("INVALID_BOARD")
    checks,captures=checks_and_captures(b)
    result={
        "fen4":fen4,
        "turn":"white" if b.turn else "black",
        "legal_move_count":b.legal_moves.count(),
        "check_status":b.is_check(),
        "legal_check_moves":checks,
        "legal_capture_moves":captures,
        "absolute_pins_white":absolute_pins(b,chess.WHITE),
        "absolute_pins_black":absolute_pins(b,chess.BLACK),
        "relative_xray_rays_white_defender":relative_pin_rays(b,chess.WHITE),
        "relative_xray_rays_black_defender":relative_pin_rays(b,chess.BLACK),
        "passed_pawns_white":passed_pawns(b,chess.WHITE),
        "passed_pawns_black":passed_pawns(b,chess.BLACK),
        "unknown_or_unproven":[
            "tactical pin exploitation", "forced skewer", "fork conversion",
            "SEE exchange value", "overloading", "deflection",
            "king mating net", "motif causes final Stockfish choice"]
    }
    return result

def compute(march):
    selected=march["selected"]
    if len(selected)!=16 or len({r["fen4"] for r in selected})!=16:
        raise ValueError("MARCH_FROZEN_SIXTEEN_DENOMINATOR")
    records=[]
    for expected,row in enumerate(selected,1):
        if row["id"]!=expected:
            raise ValueError("MARCH_SOURCE_INDEX")
        ft=board_features(row["fen4"])
        if ft["legal_move_count"]!=row["source_root_legal_count"]:
            raise ValueError("MARCH_LEGAL_DENOMINATOR_DRIFT")
        records.append({"id":expected,"source_game_sha256":row["source_game_sha256"],
                        "features":ft})
    return {"schema":"c3x021-march16-blind-chess-geometric-microfeatures-v1",
            "phase":"BEFORE_MARCH_NATIVE_ENGINE_OUTCOMES",
            "source_sha256":MARCH_SHA,"positions":records,
            "limits":"Geometric relative x-ray rays and legal pins are candidate chess structures, not forced tactical value."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--march",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    raw=Path(a.march).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=MARCH_SHA:
        raise ValueError("MARCH_SOURCE_SHA_DRIFT")
    report=compute(json.loads(raw))
    out=Path(a.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print("C3X021_BLIND_CHESS_MICROSTRUCTURE_FROZEN",len(report["positions"]),
          hashlib.sha256(out.read_bytes()).hexdigest())
if __name__=="__main__":
    main()
