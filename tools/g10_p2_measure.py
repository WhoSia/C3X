from __future__ import annotations
import argparse,json
from pathlib import Path
from typing import Any
import chess,chess.engine
from c3x_g10.question_identity import ELO_BANDS,compute_identity

DISTRACTOR_FENS=[
    chess.Board("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2").fen(),
    chess.Board("rnbqkbnr/ppp1pppp/8/3p4/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 0 2").fen(),
    chess.Board("rnbqkbnr/pppp1ppp/8/4p3/2P5/8/PP1PPPPP/RNBQKBNR w KQkq - 0 2").fen(),
    chess.Board("rnbqkbnr/ppp1pppp/8/3p4/8/5N2/PPPPPPPP/RNBQKB1R w KQkq - 0 2").fen(),
    chess.Board("rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2").fen(),
]

def configure(engine):
    opts={}
    if "Threads" in engine.options:opts["Threads"]=1
    if "Hash" in engine.options:opts["Hash"]=16
    if opts:engine.configure(opts)

def score_cp(info,board):
    s=info.get("score")
    if s is None:return None
    pov=s.pov(board.turn)
    v=pov.score(mate_score=100000)
    return None if v is None else int(v)

def observe(engine,board,nodes,game_token):
    infos=engine.analyse(board,chess.engine.Limit(nodes=int(nodes)),multipv=3,game=game_token)
    if isinstance(infos,dict):infos=[infos]
    out=[]
    for rank,info in enumerate(infos,1):
        pv=info.get("pv") or []
        if not pv:continue
        m=pv[0]
        out.append({"rank":rank,"uci":m.uci(),"san":board.san(m),"score_cp":score_cp(info,board),"pv_uci":[x.uci() for x in pv[:12]]})
    return {"nodes_limit":int(nodes),"candidates":out}

def fresh_once(path,fen,nodes):
    e=chess.engine.SimpleEngine.popen_uci(path);configure(e)
    try:return observe(e,chess.Board(fen),nodes,object())
    finally:e.quit()

def fresh_repeats(path,fen,n=5):
    return [fresh_once(path,fen,5000) for _ in range(n)]

def clean_repeats(path,fen,n=5):
    e=chess.engine.SimpleEngine.popen_uci(path);configure(e);out=[]
    try:
        for _ in range(n):out.append(observe(e,chess.Board(fen),5000,object()))
        return out
    finally:e.quit()

def history_repeats(path,fen,n=5):
    e=chess.engine.SimpleEngine.popen_uci(path);configure(e);out=[]
    try:
        for i in range(n):
            token=object()
            observe(e,chess.Board(DISTRACTOR_FENS[i%len(DISTRACTOR_FENS)]),5000,token)
            out.append(observe(e,chess.Board(fen),5000,token))
        return out
    finally:e.quit()

def set_maia_position(maia,case):
    initial=case.get("initial_fen") or chess.STARTING_FEN
    moves=" ".join(case.get("moves_before_uci") or [])
    cmd="position startpos" if initial==chess.STARTING_FEN else f"position fen {initial}"
    if moves:cmd+=f" moves {moves}"
    maia.cmd_position(cmd)

def maia_policies(maia,case):
    out={}
    for elo in ELO_BANDS:
        maia.self_elo=int(elo);maia.oppo_elo=int(elo);set_maia_position(maia,case)
        _chosen,top=maia.score_moves()
        out[str(elo)]={x["move"].uci():float(x["policy"]) for x in top}
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--bank",required=True);ap.add_argument("--shard",type=int,required=True);ap.add_argument("--shards",type=int,default=3)
    ap.add_argument("--stockfish",required=True);ap.add_argument("--berserk",required=True);ap.add_argument("--ethereal",required=True)
    ap.add_argument("--maia-checkpoint",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args()
    bank=json.load(open(a.bank,encoding="utf-8"))
    cases=[x for i,x in enumerate(bank["cases"]) if i%a.shards==a.shard]
    from maia3.uci import Maia3UCIEngine,parse_args as maia_parse_args
    cfg=maia_parse_args(["--model","maia3-5m","--checkpoint-path",a.maia_checkpoint,"--device","cpu","--no-use-amp","--use-uci-history","--multipv","20","--temperature","0"])
    maia=Maia3UCIEngine(cfg);maia.ensure_model_loaded()
    rows=[]
    for idx,c in enumerate(cases,1):
        row=json.loads(json.dumps(c));fen=row["position_fen"]
        fresh=fresh_repeats(a.stockfish,fen,5)
        clean=clean_repeats(a.stockfish,fen,5)
        hist=history_repeats(a.stockfish,fen,5)
        budgets={
            "stockfish_2k":fresh_once(a.stockfish,fen,2000),
            "stockfish_10k":fresh_once(a.stockfish,fen,10000),
            "stockfish_40k":fresh_once(a.stockfish,fen,40000),
        }
        engines={
            "berserk":fresh_once(a.berserk,fen,10000),
            "ethereal":fresh_once(a.ethereal,fen,10000),
        }
        row["measurements"]={"fresh_5k":fresh,"clean_5k":clean,"history_5k":hist,"budget_nonprimary":budgets,"cross_engine_10k":engines,"maia_policy":maia_policies(maia,row)}
        row["identity"]=compute_identity(row)
        row["certificate_outcomes_opened"]=False
        rows.append(row)
        print("G10_P2_MEASURE",a.shard,idx,len(cases),row["case_id"],row["identity"]["stable"],row["identity"]["fresh"]["u2_repeatability"],row["identity"]["engine_scope"]["scope"],flush=True)
    Path(a.out).write_text(json.dumps({"schema":"c3x-g10-p2-measure-shard-v1","shard":a.shard,"case_count":len(rows),"cases":rows,"certificate_outcomes_opened":False},indent=2,sort_keys=True)+"\n",encoding="utf-8")
if __name__=="__main__":main()
