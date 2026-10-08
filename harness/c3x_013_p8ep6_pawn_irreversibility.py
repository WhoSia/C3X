#!/usr/bin/env python3
"""Check source premises of P8-EP6 pawn-count history-separation lemma."""
import argparse,json
from pathlib import Path
import chess
from harness.c3x_013_p8ep5_all_confluences_pv import witnesses

def verify(fen,first,second,r1,r2,common):
    root=chess.Board(fen)
    assert root.is_valid()
    n=len(root.pieces(chess.PAWN,root.turn))
    for move_uci,reply_uci in ((first,r1),(second,r2)):
        b=root.copy(stack=False)
        move=chess.Move.from_uci(move_uci)
        assert move in b.legal_moves
        assert b.piece_at(move.from_square).piece_type==chess.PAWN
        b.push(move)
        assert len(b.pieces(chess.PAWN,root.turn))==n
        reply=chess.Move.from_uci(reply_uci)
        assert reply in b.legal_moves and b.is_capture(reply)
        square=reply.to_square+(-8 if b.turn else 8) if b.is_en_passant(reply) else reply.to_square
        assert square==move.to_square
        victim=b.piece_at(square)
        assert victim and victim.piece_type==chess.PAWN and victim.color==root.turn
        b.push(reply)
        assert len(b.pieces(chess.PAWN,root.turn))==n-1
        assert b.halfmove_clock==0 and b.fen(en_passant="fen")==common
    return n

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    items=witnesses(Path(a.source).read_bytes())
    rows=[]
    for x in items:
        n=verify(x["source_fen"],x["root_pair"]["a"],x["root_pair"]["b"],
                 x["convergent_reply"]["a"]["reply"],x["convergent_reply"]["b"]["reply"],
                 x["common_six_field_fen"])
        rows.append({"source_rank":x["source_rank"],"ply":x["ply"],
                     "broadcast":x["broadcast"],"pawn_count_old":n,"pawn_count_after":n-1})
    out={"schema":"c3x-013-p8-ep6-pawn-irreversibility-premises-v1",
         "EP3_source_denominator_groups":32,"verified_confluence_cases":len(rows),
         "distinct_groups":len({z["broadcast"] for z in rows}),
         "history_separation_lemma":"All old history pawn counts >=N; all future pawn counts <=N-1; no old position recurs.",
         "generic_FEN_contains_repetition_history":False,
         "causal_chess_concept_established":False,"C3X_014":"UNOPENED_CANDIDATE",
         "cases":rows}
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    Path(a.output).write_text(json.dumps(out,indent=2)+"\n")
    print("P8EP6_IRREVERSIBLE_PAWN_PROOF_PREMISES",len(rows),out["distinct_groups"])
    assert len(rows)==14
if __name__=="__main__":main()
