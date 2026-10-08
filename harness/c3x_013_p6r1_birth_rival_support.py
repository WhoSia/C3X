#!/usr/bin/env python3
"""P6-R1: strict alternate-root support at first real passed-pawn birth per game."""
import argparse,hashlib,io,json
from pathlib import Path
import chess,chess.pgn
from c3x_explain.concepts import snapshot
from harness.c3x_013_p5_source_partition import extract
from harness.c3x_013_p6e_pawn_birth_events import game_events,blockers

def births(board,move):
    old=board.copy(stack=False)
    piece=old.piece_at(move.from_square)
    new=old.copy(stack=False);new.push(move)
    out=[]
    for color in (chess.WHITE,chess.BLACK):
        for sq in new.pieces(chess.PAWN,color):
            origin=move.from_square if (piece and piece.piece_type==chess.PAWN and
                  piece.color==color and sq==move.to_square) else sq
            prev=old.piece_at(origin)
            if not prev or prev.color!=color or prev.piece_type!=chess.PAWN:continue
            if blockers(old,origin,color) and not blockers(new,sq,color):
                out.append({"color":"white" if color else "black",
                            "pawn_after":chess.square_name(sq)})
    return out

def capture_kind(board,move):
    if not board.is_capture(move):return "QUIET"
    sq=move.to_square+(-8 if board.turn else 8) if board.is_en_passant(move) else move.to_square
    piece=board.piece_at(sq)
    return "CAPTURE_"+chess.piece_symbol(piece.piece_type) if piece else "UNKNOWN_CAPTURE"

def delta(board,move):
    p=board.turn
    before=snapshot(board,p)
    after=board.copy(stack=False);after.push(move)
    post=snapshot(after,p)
    return {k:post[k]-before[k] for k in before if post[k]!=before[k]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--source",required=True)
    ap.add_argument("--output",required=True);z=ap.parse_args()
    selected=extract(z.source)
    records=[]
    for entry in selected:
        row={"broadcast":entry["broadcast"],"game_url":entry["game_url"],
             "source_game_sha256":entry["sha"]}
        prior=game_events(entry)
        if prior["status"]!="LEGAL_FULL_GAME":
            row["status"]="HOLD_SOURCE_REPLAY"
            records.append(row);continue
        if not prior["events"]:
            row["status"]="HOLD_NO_PASSED_BIRTH"
            records.append(row);continue
        event=min(prior["events"],key=lambda e:(e["ply"],e["uci"]))
        game=chess.pgn.read_game(io.StringIO(entry["raw"].decode("utf-8","replace")))
        moves=list(game.mainline_moves())
        root=chess.Board()
        for move in moves[:event["ply"]-1]:
            assert move in root.legal_moves
            root.push(move)
        played=moves[event["ply"]-1]
        assert played.uci()==event["uci"] and played in root.legal_moves
        moving=root.piece_at(played.from_square)
        klass=capture_kind(root,played)
        matched=[]
        broad=[]
        for alt in sorted(root.legal_moves,key=lambda m:m.uci()):
            if alt==played or alt.from_square!=played.from_square:continue
            broad.append(alt.uci())
            if capture_kind(root,alt)!=klass or bool(alt.promotion)!=bool(played.promotion):
                continue
            if births(root,alt):continue
            matched.append(alt)
        row.update({"status":"RIVAL_SUPPORT_PRESENT" if matched else "HOLD_NO_MATCHED_LEGAL_RIVAL",
                    "event_ply":event["ply"],"root_fen":root.fen(en_passant="fen"),
                    "played":played.uci(),"played_birth_count":len(births(root,played)),
                    "root_capture_class":klass,"same_mover_other_legal":len(broad),
                    "strict_eligible_rival_count":len(matched)})
        if matched:
            alt=matched[0]
            row["frozen_rival"]=alt.uci()
            row["feature_delta_played"]=delta(root,played)
            row["feature_delta_rival"]=delta(root,alt)
            row["feature_confound_warning"]=True
        records.append(row)
    out={"schema":"c3x-013-p6r1-natural-birth-rival-positivity-v1",
         "source_sha256":hashlib.sha256(Path(z.source).read_bytes()).hexdigest(),
         "status":"SOURCE_SUPPORT_CENSUS_ONLY_NO_ENGINE_OUTCOME",
         "original_groups":16,"records":records,
         "status_counts":{k:sum(r["status"]==k for r in records)
                           for k in sorted({r["status"] for r in records})},
         "engine_measurement":None,"causal_concept_explanation":False}
    Path(z.output).parent.mkdir(parents=True,exist_ok=True)
    Path(z.output).write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    print("P6_R1_STRICT_RIVAL_SUPPORT",out["status_counts"])
    assert len(records)==16 and not out["causal_concept_explanation"]
if __name__=="__main__":main()
