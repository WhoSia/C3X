#!/usr/bin/env python3
"""P8-EP4: all-source audited TCEC continuation confluence and real two-engine root values.

NO cherry-picked score selection: sole prospectively identified chess-support witness.
"""
import argparse,hashlib,json
from pathlib import Path
import chess
from harness.c3x_013_p8e1_pinned_ethereal import observe
from harness.c3x_013_p6r1_birth_rival_support import births
from harness.c3x_013_p7r1_tactical_support import hazard

COHORT="240501f203478560f22cd32614ba56b0870749cb0e890f7bc4a219d4ce955796"
SOURCE="r5k1/6p1/p5qn/4p2p/2ppP3/3Q3P/1P1B1PP1/R5K1 w - - 0 25"
COMMON="r5k1/6p1/p5qn/4p2p/3pP3/1p1Q3P/3B1PP1/R5K1 w - - 0 26"
A,B,R="b2b3","b2b4","c4b3"
ETH_COMMIT="0e47e9b67f345c75eb965d9fb3e2493b6a11d09a"
DEPTHS=(8,12,16)

def verify_source(blob):
    d=json.loads(blob)
    assert d["schema"]=="c3x-013-p8-ep3-heldout-chess-legal-confluence-census-v1"
    assert d["frozen_new_segment_list_sha256"]==COHORT
    assert len(d["records"])==32 and d["source_denominator"]==32
    witnesses=[]
    eligible=[]
    for row in d["records"]:
        for ply,world in row["worlds"].items():
            for w in world.get("census",{}).get("witnesses",[]):
                witnesses.append((row,ply,world,w))
                if (w["same_opponent_reply_uci"] and w["normal_vs_en_passant"] and
                    w["passed_birth_toggled"] and w["root_capture_hazard_equal"]):
                    eligible.append((row,ply,world,w))
    assert len(witnesses)==14 and len(eligible)==1
    row,ply,world,w=eligible[0]
    assert row["source_rank"]==111 and ply=="48"
    assert row["broadcast"]=="TCEC S30: Playoff & Swiss 10 | Playoff | Cat 2"
    assert row["game_url"]=="https://lichess.org/broadcast/tcec-s30-playoff-swiss-10-playoff-cat-2/round-1/kpZI9MVi/1oANqqKQ"
    assert world["fen"]==SOURCE and w["exact_common_full_fen"]==COMMON
    assert (w["single"],w["double"])==(A,B)
    assert w["reply_after_single"]["reply"]==w["reply_after_double"]["reply"]==R
    assert w["reply_after_single"]["kind"]=="NORMAL_CAPTURE"
    assert w["reply_after_double"]["kind"]=="EN_PASSANT"
    board=chess.Board(world["fen"])
    assert board.is_valid() and board.turn==chess.WHITE
    a,b=chess.Move.from_uci(A),chess.Move.from_uci(B)
    assert a in board.legal_moves and b in board.legal_moves
    assert a.from_square==b.from_square and hazard(board,a)==hazard(board,b)
    born_a,born_b=births(board,a),births(board,b)
    assert not born_a and born_b==[{"color":"black","pawn_after":"c4"}]
    successor={}
    for move,label in ((a,"single"),(b,"double")):
        t=board.copy(stack=False);t.push(move)
        reply=chess.Move.from_uci(R)
        assert reply in t.legal_moves
        er=t.is_en_passant(reply)
        t.push(reply)
        assert t.fen(en_passant="fen")==COMMON
        successor[label]={"after_root":board.copy(stack=False).fen() if False else None,
                          "reply_en_passant":er,
                          "full_fen_after_reply":t.fen(en_passant="fen")}
    assert not successor["single"]["reply_en_passant"] and successor["double"]["reply_en_passant"]
    return row,ply,w,board,successor,len(witnesses)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-court",required=True)
    p.add_argument("--stockfish",default="/usr/games/stockfish")
    p.add_argument("--ethereal",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    blob=Path(args.source_court).read_bytes()
    row,ply,w,board,successor,num_witnesses=verify_source(blob)
    results={"schema":"c3x-013-p8-ep4-heldout-tcec-two-engine-continuation-v1",
             "stage":"C3X 0.13 P8-EP4",
             "source_parent_sha256":hashlib.sha256(blob).hexdigest(),
             "frozen_source_groups":32,"exact_legal_confluence_witnesses":num_witnesses,
             "eligible_birth_toggled_tactical_matched":1,
             "source_rank":row["source_rank"],"source_broadcast":row["broadcast"],
             "source_game_url":row["game_url"],
             "source_game_sha256":row["source_game_sha256"],"source_ply":int(ply),
             "source_root_fen":SOURCE,"root_pair":{"a":A,"b":B},
             "shared_black_legal_reply":R,"birth_single":w["passed_birth_single"],
             "birth_double":w["passed_birth_double"],
             "exact_equal_six_field_converged_fen":COMMON,
             "continuation_branches":successor,
             "ethereal_source_commit":ETH_COMMIT,
             "stockfish_binary_sha256":hashlib.sha256(Path(args.stockfish).read_bytes()).hexdigest(),
             "ethereal_binary_sha256":hashlib.sha256(Path(args.ethereal).read_bytes()).hexdigest(),
             "engines":{},"identifiable_engine_caused_by_passer":False,
             "source_independent_provider_tested":False,
             "C3X_014":"CANDIDATE_ONLY_UNOPENED"}
    for engine,exe in (("Stockfish",args.stockfish),
                       ("Ethereal_classical",args.ethereal)):
        panel={}
        for depth in DEPTHS:
            trials=[observe(exe,board,{"a":A,"b":B},depth) for _ in (0,1)]
            exact=all(t["status"]=="CP_DIRECTION_ONLY" for t in trials)
            exact=exact and trials[0]["gap_cp"]==trials[1]["gap_cp"]
            recapture={name:(len(pv)>=2 and pv[1]==R)
                       for name,pv in ((root,trials[0].get("raw",{}).get(uci,{}).get("pv",[]))
                           for root,uci in (("a",A),("b",B)))}
            panel[str(depth)]={"trials":trials,"repeat_exact":exact,
                "root_a_minus_b_cp":trials[0].get("gap_cp") if exact else None,
                "PV_immediate_black_reply_is_shared_capture":recapture}
        gaps=[panel[str(d)]["root_a_minus_b_cp"] for d in DEPTHS]
        results["engines"][engine]={"panel":panel,
            "all_repeats_exact":all(panel[str(d)]["repeat_exact"] for d in DEPTHS),
            "all_depth_nonmate":all(v is not None for v in gaps),
            "sign_stable":all(v is not None for v in gaps) and
                len({(v>0)-(v<0) for v in gaps})==1 and gaps[0]!=0,
            "both_PV_roots_select_shared_capture":all(
                panel[str(d)]["PV_immediate_black_reply_is_shared_capture"]["a"] and
                panel[str(d)]["PV_immediate_black_reply_is_shared_capture"]["b"]
                for d in DEPTHS)}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(results,indent=2)+"\n")
    print("P8EP4_HELDOUT_TCEC_EXACT_FEN_CONFLUENCE",COMMON)
    print("P8EP4_TWO_ENGINE_ROOT_GAPS",{
        name:{depth:x["root_a_minus_b_cp"] for depth,x in e["panel"].items()}
        for name,e in results["engines"].items()})
    print("P8EP4_REPLY_PV_AND_SCIENTIFIC_AUTHORITY",{
        name:e["both_PV_roots_select_shared_capture"] for name,e in results["engines"].items()},
        "CAUSAL_MECHANISM",results["identifiable_engine_caused_by_passer"])
    assert not results["identifiable_engine_caused_by_passer"]
if __name__=="__main__":
    main()
