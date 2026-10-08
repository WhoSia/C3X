#!/usr/bin/env python3
"""P6-E actual pawn blocker-set birth witnesses; source-locked, no engine causality."""
import argparse,io,json,hashlib
from pathlib import Path
import chess,chess.pgn
from harness.c3x_013_p5_source_partition import extract

def blockers(board,square,color):
    f,r=chess.square_file(square),chess.square_rank(square)
    return sorted(chess.square_name(other) for other in board.pieces(chess.PAWN,not color)
                  if abs(chess.square_file(other)-f)<=1 and
                  (chess.square_rank(other)>r if color else chess.square_rank(other)<r))

def event_kind(origin,target,move,piece,captured,old_blockers):
    if captured is not None and captured in old_blockers:
        return "MIXED_CAPTURE_AND_ADVANCE" if origin!=target else "BLOCKER_CAPTURED"
    if origin!=target:return "PAWN_ADVANCE_THRESHOLD"
    if piece and piece.piece_type==chess.PAWN:return "OPPONENT_PAWN_MOVED_OUT_OF_BAND"
    return "OTHER_BLOCKER_CHANGE"

def game_events(entry):
    game=chess.pgn.read_game(io.StringIO(entry["raw"].decode("utf-8","replace")))
    out={"broadcast":entry["broadcast"],"game_url":entry["game_url"],
         "source_sha256":entry["sha"],"events":[]}
    if game is None or game.errors:
        out["status"]="HOLD_PGN_VARIANT";return out
    board=game.board()
    for ply,move in enumerate(game.mainline_moves(),1):
        if move not in board.legal_moves:
            out.update({"status":"HOLD_ILLEGAL_MOVE","failed_ply":ply});return out
        original=board.copy(stack=False)
        piece=original.piece_at(move.from_square)
        capture=original.is_capture(move)
        enpassant=original.is_en_passant(move)
        capt_sq=(move.to_square + (-8 if piece.color else 8)) if enpassant else move.to_square
        captured=(chess.square_name(capt_sq) if capture and
                  original.piece_at(capt_sq) and original.piece_at(capt_sq).piece_type==chess.PAWN else None)
        board.push(move)
        if not board.is_valid():
            out.update({"status":"HOLD_INVALID_BOARD","failed_ply":ply});return out
        for color in (chess.WHITE,chess.BLACK):
            for sq in board.pieces(chess.PAWN,color):
                origin=move.from_square if (piece and piece.piece_type==chess.PAWN and
                       piece.color==color and sq==move.to_square) else sq
                former=original.piece_at(origin)
                if not former or former.piece_type!=chess.PAWN or former.color!=color:continue
                prev=blockers(original,origin,color)
                post=blockers(board,sq,color)
                if not prev or post:continue
                out["events"].append({
                    "ply":ply,"uci":move.uci(),"newly_passed_color":"white" if color else "black",
                    "pawn_before":chess.square_name(origin),"pawn_after":chess.square_name(sq),
                    "blockers_before":prev,"blockers_after":post,
                    "captured_enemy_pawn_square":captured,
                    "moving_piece":chess.piece_symbol(piece.piece_type) if piece else None,
                    "pawn_promotion":bool(move.promotion),"en_passant":enpassant,
                    "event_class":event_kind(origin,sq,move,piece,captured,prev),
                    "fen_before_sha256":hashlib.sha256(original.fen(en_passant="fen").encode()).hexdigest(),
                    "fen_after_sha256":hashlib.sha256(board.fen(en_passant="fen").encode()).hexdigest()})
    out["status"]="LEGAL_FULL_GAME"
    out["length_ply"]=ply if "ply" in locals() else 0
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--source",required=True)
    ap.add_argument("--output",required=True);args=ap.parse_args()
    chosen=extract(args.source)
    games=[game_events(x) for x in chosen]
    events=[e for g in games if g["status"]=="LEGAL_FULL_GAME" for e in g["events"]]
    counts={c:sum(x["event_class"]==c for x in events)
            for c in sorted(set(x["event_class"] for x in events))}
    obj={"schema":"c3x-013-p6e-passed-birth-witnesses-v1",
         "status":"EXPLORATORY_BOARD_RULE_EVENT_RECONSTRUCTION",
         "source_sha256":hashlib.sha256(Path(args.source).read_bytes()).hexdigest(),
         "total_frozen_groups":16,
         "valid_complete_games":sum(g["status"]=="LEGAL_FULL_GAME" for g in games),
         "total_new_passed_pawn_birth_events":len(events),
         "event_classes":counts,"games":games,
         "engine_preference_measured":False,"causal_explanation_granted":False}
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n")
    print("P6_E_BIRTH_EVENT_COUNTS",obj["valid_complete_games"],len(events),counts)
    assert len(chosen)==16
    assert all(not e["blockers_after"] and e["blockers_before"] for e in events)
    if any(g["status"] not in ("LEGAL_FULL_GAME","HOLD_PGN_VARIANT") for g in games):
        raise SystemExit("P6_E_SOURCE_OR_REPLAY_HOLD")
if __name__=="__main__":
    main()
