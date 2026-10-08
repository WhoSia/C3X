#!/usr/bin/env python3
"""P8-EP2: exact natural chess continuation confluence + real two-engine root values."""
import argparse,hashlib,json
from pathlib import Path
import chess
import chess.engine
from c3x_explain.concepts import snapshot
from harness.c3x_013_p6r1_birth_rival_support import births
from harness.c3x_013_p7r1_tactical_support import hazard
from harness.c3x_013_p8e1_pinned_ethereal import observe

FEN="1r1qk2r/4bppp/QN1pp1b1/2P5/1p2n1P1/4B2P/PPPN1P2/R3K2R w KQk - 1 17"
ROOTS={"a":"a2a3","b":"a2a4"}
REPLY="b4a3"
DEPTHS=(8,12,16)

def root_worlds():
    board=chess.Board(FEN)
    assert board.is_valid() and board.turn==chess.WHITE
    worlds={}
    for name,uci in ROOTS.items():
        q=board.copy(stack=False)
        m=chess.Move.from_uci(uci)
        assert m in q.legal_moves
        q.push(m)
        r=chess.Move.from_uci(REPLY)
        assert r in q.legal_moves
        before_reply=q.copy(stack=False)
        is_ep=q.is_en_passant(r)
        q.push(r)
        worlds[name]={"after_root":before_reply,"after_reply":q,
                      "reply_is_en_passant":is_ep}
    assert worlds["a"]["reply_is_en_passant"] is False
    assert worlds["b"]["reply_is_en_passant"] is True
    assert worlds["a"]["after_reply"].fen(en_passant="fen")==worlds["b"]["after_reply"].fen(en_passant="fen")
    assert not births(board,chess.Move.from_uci(ROOTS["a"]))
    assert any(z["color"]=="white" and z["pawn_after"]=="a4"
               for z in births(board,chess.Move.from_uci(ROOTS["b"])))
    assert hazard(board,chess.Move.from_uci(ROOTS["a"]))==hazard(
        board,chess.Move.from_uci(ROOTS["b"]))
    return board,worlds

def merged_position_score(exe,board):
    def once():
        with chess.engine.SimpleEngine.popen_uci(exe,timeout=45) as eng:
            eng.configure({"Threads":1,"Hash":16})
            info=eng.analyse(board,chess.engine.Limit(depth=12))
        score=info.get("score")
        cp=score.pov(board.turn).score(mate_score=None) if score else None
        return {"depth":info.get("depth"),"score_root_side_cp":cp,
                "pv":[m.uci() for m in info.get("pv",[])[:8]]}
    trials=[once(),once()]
    valid=all(z["depth"]==12 and z["score_root_side_cp"] is not None for z in trials)
    same=valid and trials[0]["score_root_side_cp"]==trials[1]["score_root_side_cp"]
    return {"trials":trials,"repeat_exact":same,"status":"MERGED_WORLD_CP_ONLY" if same else "HOLD"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--stockfish",default="/usr/games/stockfish")
    p.add_argument("--ethereal",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    original,worlds=root_worlds()
    convergence=worlds["a"]["after_reply"].fen(en_passant="fen")
    result={"schema":"c3x-013-p8-ep2-natural-en-passant-confluence-v1",
            "stage":"C3X 0.13 P8-EP2","source_fen":FEN,
            "source_fen_sha256":hashlib.sha256(FEN.encode()).hexdigest(),
            "source_game":"2026 NZ South Island Championship, Lichess broadcast round1, frozen P7 source game ply32",
            "root_moves":ROOTS,"shared_legal_opponent_reply":REPLY,
            "after_root":{
                k:{"fen":v["after_root"].fen(en_passant="fen"),
                   "opponent_reply_is_en_passant":v["reply_is_en_passant"],
                   "white_passed_pawn_count":snapshot(v["after_root"],chess.WHITE)["own_passed_pawn_count"]}
                for k,v in worlds.items()},
            "after_legal_reply":{
                k:v["after_reply"].fen(en_passant="fen") for k,v in worlds.items()},
            "convergent_identical_full_fen":True,"common_terminal_of_two_moves":convergence,
            "after_root_white_passed_count_delta_B_minus_A":
                snapshot(worlds["b"]["after_root"],chess.WHITE)["own_passed_pawn_count"]
                -snapshot(worlds["a"]["after_root"],chess.WHITE)["own_passed_pawn_count"],
            "stockfish_binary_sha256":hashlib.sha256(Path(a.stockfish).read_bytes()).hexdigest(),
            "ethereal_binary_sha256":hashlib.sha256(Path(a.ethereal).read_bytes()).hexdigest(),
            "ethereal_source_commit":"0e47e9b67f345c75eb965d9fb3e2493b6a11d09a",
            "raw_root_measurements":{},"merged_world_evaluations":{},
            "causal_mediation_identified":False,"independent_chess_game_replication":False,
            "C3X_014":"CANDIDATE_ONLY_NO_NAME"}
    assert result["after_root_white_passed_count_delta_B_minus_A"]==1
    pairs={"a":ROOTS["a"],"b":ROOTS["b"]}
    for name,exe in (("Stockfish",a.stockfish),("Ethereal_classical",a.ethereal)):
        by_depth={}
        for depth in DEPTHS:
            trials=[observe(exe,original,pairs,depth) for _ in (1,2)]
            valid=all(z["status"]=="CP_DIRECTION_ONLY" for z in trials)
            same=valid and trials[0]["gap_cp"]==trials[1]["gap_cp"]
            recapture={}
            for k in ("a","b"):
                pv=(trials[0].get("raw",{}).get(pairs[k],{}).get("pv",[])
                    if same else [])
                recapture[k]=len(pv)>=2 and pv[1]==REPLY
            by_depth[str(depth)]={"trials":trials,"repeat_exact":same,
                                   "gap_a2a3_minus_a2a4_cp":trials[0].get("gap_cp") if same else None,
                                   "PV_second_ply_recap_as_b4a3":recapture}
        result["raw_root_measurements"][name]=by_depth
        result["merged_world_evaluations"][name]=merged_position_score(
            exe,worlds["a"]["after_reply"])
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(result,indent=2)+"\n")
    print("P8EP2_EXACT_CONTINUATION_FEN_CONFLUENCE",result["convergent_identical_full_fen"])
    print("P8EP2_ROOT_GAPS", {engine:{d:row["gap_a2a3_minus_a2a4_cp"]
        for d,row in data.items()} for engine,data in result["raw_root_measurements"].items()})
    print("P8EP2_CHESS_CONCEPT_CAUSAL_AUTHORITY",False)
    assert result["convergent_identical_full_fen"]
if __name__=="__main__":main()
