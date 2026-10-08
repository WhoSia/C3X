#!/usr/bin/env python3
"""P6-R2 frozen NATURAL root pair; no causal concept or human result."""
import argparse,hashlib,json
from pathlib import Path
import chess,chess.engine
from c3x_explain.concepts import candidate_delta
from harness.c3x_013_p6r1_birth_rival_support import births,capture_kind

FEN="1r3nk1/1pp1bqp1/6pp/p7/3PNQ2/2P4P/PP3PP1/4RRK1 w - - 0 27"
PAIR=["f4c7","f4h6"]
DEPTHS=[8,12,16]

def score(exe,board,moves,depth):
    with chess.engine.SimpleEngine.popen_uci(exe,timeout=35) as e:
        e.configure({"Threads":1,"Hash":16})
        rows=e.analyse(board,chess.engine.Limit(depth=depth),multipv=2,root_moves=moves)
    by={}
    for row in rows:
        if not row.get("pv") or not row.get("score"):continue
        cp=row["score"].pov(board.turn).score(mate_score=None)
        if cp is None:continue
        by[row["pv"][0].uci()]={"cp":cp,"depth":row.get("depth"),
                               "pv":[x.uci() for x in row["pv"][:10]]}
    if any(m.uci() not in by for m in moves):return {"status":"HOLD_MATE_OR_MISSING","raw":by}
    a,b=[by[m.uci()] for m in moves]
    if a["depth"]!=b["depth"] or a["depth"]!=depth:
        return {"status":"HOLD_COMPLETED_DEPTH","raw":by}
    return {"status":"COMPARABLE_CP_NOT_CAUSAL","cp_a":a["cp"],"cp_b":b["cp"],
            "delta_cp":a["cp"]-b["cp"],"depth":depth,"raw":by}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--engine",default="/usr/games/stockfish")
    a.add_argument("--output",required=True)
    args=a.parse_args()
    b=chess.Board(FEN)
    moves=[chess.Move.from_uci(x) for x in PAIR]
    assert b.is_valid() and b.turn==chess.WHITE
    assert all(m in b.legal_moves for m in moves)
    assert moves[0].from_square==moves[1].from_square
    assert capture_kind(b,moves[0])==capture_kind(b,moves[1])=="CAPTURE_p"
    birth_a,birth_b=[births(b,m) for m in moves]
    assert len(birth_a)>=1 and not birth_b
    feature=candidate_delta(b,*moves)
    out={"schema":"c3x-013-p6r2-real-game-birth-pair-v1",
         "status":"DEVELOPMENT_ONLY_NOT_CAUSAL_REASON",
         "source_frozen_FEN":FEN,"fen_sha256":hashlib.sha256(FEN.encode()).hexdigest(),
         "pair":PAIR,"births_played":birth_a,"births_rival":birth_b,
         "features_played_minus_rival":feature["played_minus_alternative"],
         "engine_sha256":hashlib.sha256(Path(args.engine).read_bytes()).hexdigest(),
         "source_cohort_total_groups":16,"birth_bearing_games":9,
         "strict_rival_support_worlds":1,"measurements":{},
         "explanation_authority":False}
    for d in DEPTHS:
        trials=[score(args.engine,b,moves,d) for _ in (0,1)]
        valid=all(z["status"]=="COMPARABLE_CP_NOT_CAUSAL" for z in trials)
        rep=valid and trials[0]["delta_cp"]==trials[1]["delta_cp"]
        gap=trials[0].get("delta_cp")
        out["measurements"][str(d)]={"trials":trials,"repeat_exact":rep,
              "within_50cp":bool(rep and abs(gap)<=50),"status":"DEVELOPMENT_MEASURED" if rep else "HOLD"}
    data=list(out["measurements"].values())
    out["all_depth_support"]=all(z["within_50cp"] for z in data)
    out["consistent_nonzero_direction"]=(all(z["repeat_exact"] for z in data) and
        len({(z["trials"][0]["delta_cp"]>0)-(z["trials"][0]["delta_cp"]<0) for z in data})==1)
    out["reason_certificates"]=[]
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(out,indent=2)+"\n")
    print("P6R2_REAL_GAME_BIRTH_ROOT_GAPS",
          {d:x["trials"][0].get("delta_cp") for d,x in out["measurements"].items()})
    print("P6R2_ALL_DEPTH_NEAR_EQUAL",out["all_depth_support"])
    assert not out["explanation_authority"]
if __name__=="__main__":main()
