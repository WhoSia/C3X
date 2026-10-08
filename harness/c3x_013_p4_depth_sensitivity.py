#!/usr/bin/env python3
"""C3X 0.13 P4: frozen historic P16 pair across Stockfish depth regimes."""
import argparse
import hashlib
import json
from pathlib import Path
import chess
import chess.engine

DEPTHS=(8,10,12,14,16)

def measure(exe,fen,moves,depth):
    board=chess.Board(fen)
    if not board.is_valid() or any(chess.Move.from_uci(m) not in board.legal_moves for m in moves):
        raise ValueError("P16_INVALID_FROZEN_BOARD_OR_ROOT")
    with chess.engine.SimpleEngine.popen_uci(exe,timeout=30) as engine:
        engine.configure({"Threads":1,"Hash":16})
        infos=engine.analyse(board,chess.engine.Limit(depth=depth),
                            multipv=2,root_moves=[chess.Move.from_uci(m) for m in moves])
    data={}
    for info in infos:
        pv=info.get("pv") or []
        if not pv or info.get("score") is None:continue
        cp=info["score"].pov(board.turn).score(mate_score=None)
        if cp is not None:data[pv[0].uci()]={"cp":cp,"depth":info.get("depth"),"nodes":info.get("nodes")}
    if any(m not in data or data[m]["depth"]!=depth for m in moves):
        return {"status":"HOLD_NOT_COMPLETE_OR_MATE","raw":data}
    return {"status":"COMPLETE_DEPTH_PAIR_CP","a_cp":data[moves[0]]["cp"],
            "b_cp":data[moves[1]]["cp"],"delta_cp":data[moves[0]]["cp"]-data[moves[1]]["cp"],
            "raw":data}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--certificate",required=True)
    a.add_argument("--engine",default="/usr/games/stockfish")
    a.add_argument("--out",required=True)
    args=a.parse_args()
    p=Path(args.certificate)
    c=json.loads(p.read_text())
    assert c["scientific_stage"]=="C3X 0.7.0-G9.5-P16" and c["engine"]=="ethereal"
    assert c["counterfactual_boards"]["SHAM"]["fen"]==c["counterfactual_boards"]["SUBSET"]["fen"]
    moves=[c["pair"][v]["uci"] for v in ("A","B")]
    out={"schema":"c3x-013-p4-engine-budget-sensitivity-v1",
         "status":"DEVELOPMENT_ONLY_NOT_CROSS_ENGINE_CAUSAL_TRANSFER",
         "prior_archived_engine":"Ethereal",
         "current_engine":"Stockfish16",
         "source_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
         "engine_sha256":hashlib.sha256(Path(args.engine).read_bytes()).hexdigest(),
         "root_pair":moves,"depths":list(DEPTHS),"worlds":{},
         "concept_certified":False,"human_benefit_certified":False,
         "causal_transport_certified":False}
    for name in ("B0","TARGET","SHAM"):
        fen=c["counterfactual_boards"][name]["fen"]
        rows={}
        for depth in DEPTHS:
            runs=[measure(args.engine,fen,moves,depth) for _ in range(2)]
            exact=(all(z["status"]=="COMPLETE_DEPTH_PAIR_CP" for z in runs)
                   and runs[0]["delta_cp"]==runs[1]["delta_cp"])
            gap=runs[0].get("delta_cp") if exact else None
            rows[str(depth)]={"repeats":runs,"repeat_exact":exact,
                              "delta_cp":gap,"within50cp":abs(gap)<=50 if gap is not None else None,
                              "preferred_uci":moves[0] if gap is not None and gap>0 else moves[1]
                              if gap is not None and gap<0 else None}
        signs=[(1 if z["delta_cp"]>0 else -1 if z["delta_cp"]<0 else 0)
               for z in rows.values() if z["delta_cp"] is not None]
        out["worlds"][name]={"fen_sha256":hashlib.sha256(fen.encode()).hexdigest(),
                             "depth_profiles":rows,
                             "sign_switch_across_depth":len(set(signs))>1,
                             "complete_depths":len(signs)}
    out["any_depth_direction_switch"]=any(z["sign_switch_across_depth"] for z in out["worlds"].values())
    out["all_3_worlds_all_5_depths_repeated"]=all(v["complete_depths"]==len(DEPTHS) for v in out["worlds"].values())
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(out,indent=2)+"\n")
    print("C3X_013_P4_COMPLETED",out["all_3_worlds_all_5_depths_repeated"])
    print("C3X_013_P4_ANY_SIGN_SWITCH",out["any_depth_direction_switch"])
    print("C3X_013_P4_CAUSAL_TRANSPORT",False)

if __name__=="__main__":
    main()
