#!/usr/bin/env python3
"""C3X022-P2-R1 pre-native legal recapture game tree (SEE-like NOT Stockfish see_ge).

For EACH legal root move on frozen TWIC1664 board, enumerate legal captures of
the arrived piece on its destination square then recursive legal recaptures,
allow standing pat. Return best material gain to responder in centipawn-ish
piece units. This is a legal board model, not a C++ score nor path mediation.
"""
import argparse,hashlib,json
from pathlib import Path
import chess
from c3x_021_P1_atomic_decision_transition_graph import profile

PIECE_POINTS={chess.PAWN:100,chess.KNIGHT:320,chess.BISHOP:330,
              chess.ROOK:500,chess.QUEEN:900,chess.KING:20000}
MAX_RECAPTURE_DEPTH=6
SCHEMA="c3x022-P2-R1-newTWIC1664-legal-SEE-like-recapture-tree-v1"

def nominal_capture_value(board,move):
    if not board.is_capture(move):return 0
    victim=board.piece_at(move.to_square)
    if board.is_en_passant(move):
        return PIECE_POINTS[chess.PAWN]
    if victim is None:raise ValueError("LEGAL_CAPTURE_WITHOUT_VICTIM")
    return PIECE_POINTS[victim.piece_type]

def legal_exchange_gain(board,target,remaining):
    """Max forced-beneficial gain for side to move; can always abstain.

    Only legal captures AT original destination square, including pinned
    disqualifications and king safety; no other tactical plans considered.
    """
    if remaining<=0:return 0
    best=0
    captures=sorted((m for m in board.legal_moves
                     if m.to_square==target and board.is_capture(m)),
                    key=lambda m:m.uci())
    for m in captures:
        gain=nominal_capture_value(board,m)
        if m.promotion:gain+=PIECE_POINTS[m.promotion]-PIECE_POINTS[chess.PAWN]
        board.push(m)
        rival=legal_exchange_gain(board,target,remaining-1)
        board.pop()
        best=max(best,gain-rival)
    return best

def move_exchange_features(board,move):
    if move not in board.legal_moves:raise ValueError("ROOT_MOVE_ILLEGAL")
    move_is_capture=board.is_capture(move)
    captured_at_root=nominal_capture_value(board,move)
    mover=board.piece_at(move.from_square)
    if mover is None:raise ValueError("ROOT_PIECE_MISSING")
    board.push(move)
    target=move.to_square
    first=sorted(m.uci() for m in board.legal_moves
                 if m.to_square==target and board.is_capture(m))
    exposure=legal_exchange_gain(board,target,MAX_RECAPTURE_DEPTH)
    opp_check=board.is_check()
    board.pop()
    return {"UCI":move.uci(),"mover_piece":mover.symbol(),
            "mover_nominal_value":PIECE_POINTS[mover.piece_type],
            "root_capture":move_is_capture,"root_material_capture_points":captured_at_root,
            "legal_opponent_first_destination_captures":first,
            "legal_first_destination_capture_count":len(first),
            "responder_optimal_legal_exchange_gain":exposure,
            "root_material_win_minus_exchange_exposure":captured_at_root-exposure,
            "first_reply_in_check":opp_check,
            "see_like_depth_cap":MAX_RECAPTURE_DEPTH,
            "not_stockfish_see_ge":True}

def prepare(source):
    if source.get("phase")!="NEW_TWIC1664_SOURCE_ONLY_BEFORE_ANY_NEW_NATIVE_OUTCOME":
        raise ValueError("NOT_NEW_SOURCE_ONLY")
    rows=source["selected"]
    if len(rows)!=16 or [x["id"] for x in rows]!=list(range(1,17)):
        raise ValueError("NOT_PRESELECTED_SIXTEEN")
    if len({x["fen4"] for x in rows})!=16:raise ValueError("FEN4_DUPLICATE")
    result={"schema":SCHEMA,"phase":"PRE_NATIVE_ALL_ACTIONS_CHESS_AND_EXCHANGE_FROZEN",
            "original_TWIC_zip_sha256":source["original_twic_archive_SHA256"],
            "positions":[],"method":"legal same-destination forced captures with stand-pat; six-ply cap; Stockfish see_ge not equated"}
    for row in rows:
        b=chess.Board(row["fen4"]+" "+str(row["source_halfmove_clock"])+" "+str(row["source_fullmove_number"]))
        if not b.is_valid():raise ValueError("INVALID_SOURCE_CHESS_BOARD")
        m=profile(b)
        if m["legal_root_move_count"]!=row["source_root_legal_count"]:
            raise ValueError("ROOT_SOURCE_CHESS_MOVE_COUNT_DRIFT")
        ex=[move_exchange_features(b,move) for move in sorted(b.legal_moves,key=lambda x:x.uci())]
        if set(x["UCI"] for x in ex)!=set(y["move"] for y in m["moves"]):
            raise ValueError("SEE_LIKE_ROOT_MOVE_CENSUS_DRIFT")
        result["positions"].append({"id":row["id"],"source_game_sha256":row["source_game_sha256"],
                                    "fen4":row["fen4"],"profile":m,"legal_exchange_tree":ex})
    result["summary"]={"distinct_chess_boards":16,"all_legal_root_moves":sum(len(x["legal_exchange_tree"]) for x in result["positions"]),
                       "any_stockfish_used":False,"any_outcome_based_selection":False,
                       "all_legal_replies_legal_including_pins":True}
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--source-sha",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    raw=Path(a.source).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=a.source_sha:raise ValueError("SOURCE_GIT_SHA_MISMATCH")
    report=prepare(json.loads(raw))
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("C3X022_P2_R1_ALL16_LEGAL_SEE_LIKE_SOURCE_FROZEN",
          report["summary"],hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
