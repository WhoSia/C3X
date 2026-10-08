#!/usr/bin/env python3
"""C3X 0.13 P3: archived Ethereal P16 worlds observed with independent Stockfish16.
Complete-depth move-pair scores only, no engine-causal transport verdict.
"""
import argparse
import hashlib
import json
from pathlib import Path
import chess
import chess.engine

def engine_pair(path, fen, roots):
    b=chess.Board(fen)
    if not b.is_valid():
        raise ValueError("INVALID_ARCHIVED_CHESS_BOARD")
    moves=[chess.Move.from_uci(x) for x in roots]
    if any(move not in b.legal_moves for move in moves):
        raise ValueError("P16_LEGAL_MOVE_MISMATCH")
    with chess.engine.SimpleEngine.popen_uci(path,timeout=20) as engine:
        engine.configure({"Threads":1,"Hash":16})
        out=engine.analyse(b,chess.engine.Limit(depth=12),
                           multipv=2,root_moves=moves)
        engine_id=engine.id
    data={}
    for x in out:
        if not x.get("pv") or x.get("score") is None:
            continue
        cp=x["score"].pov(b.turn).score(mate_score=None)
        if cp is not None:
            data[x["pv"][0].uci()]={"cp":cp,"depth":x.get("depth"),"nodes":x.get("nodes")}
    if set(data)!=set(roots) or data[roots[0]]["depth"]!=12 or data[roots[1]]["depth"]!=12:
        return {"status":"HOLD_MISSING_CP_OR_UNFINISHED_DEPTH","raw":data,"engine_id":engine_id}
    return {"status":"COMPARABLE_CP_AT_COMPLETE_DEPTH12",
            "a_cp":data[roots[0]]["cp"],
            "b_cp":data[roots[1]]["cp"],
            "delta_cp":data[roots[0]]["cp"]-data[roots[1]]["cp"],
            "pv_details":data,"engine_id":engine_id}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--certificate",required=True)
    ap.add_argument("--engine",default="/usr/games/stockfish")
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    certpath=Path(a.certificate)
    cert=json.loads(certpath.read_text())
    assert cert["scientific_stage"]=="C3X 0.7.0-G9.5-P16"
    assert cert["engine"]=="ethereal"
    assert cert["counterfactual_boards"]["SHAM"]["fen"]==cert["counterfactual_boards"]["SUBSET"]["fen"]
    pair=[cert["pair"][m]["uci"] for m in ("A","B")]
    old_native={k:cert["decision_cells"][k]["native_bestmove"] for k in ("B0","TARGET","SHAM")}
    o={"schema":"c3x-013-p3-historical-cross-engine-diagnostic-v1",
       "status":"SECOND_ENGINE_DESCRIPTIVE_DIAGNOSTIC_ONLY",
       "historical_engine":"Ethereal",
       "new_engine":"Stockfish",
       "frozen_pair":pair,
       "source_certificate_sha256":hashlib.sha256(certpath.read_bytes()).hexdigest(),
       "engine_binary_sha256":hashlib.sha256(Path(a.engine).read_bytes()).hexdigest(),
       "old_engine_native_rank_choices":old_native,
       "worlds":{},
       "budget_comparability_to_old_P16":False,
       "cross_engine_causal_transport_proven":False,
       "chess_native_concept_proven":False,
       "human_understanding_proven":False}
    for name in ("B0","TARGET","SHAM"):
        fen=cert["counterfactual_boards"][name]["fen"]
        r=[engine_pair(a.engine,fen,pair) for _ in range(2)]
        exact=(all(x["status"]=="COMPARABLE_CP_AT_COMPLETE_DEPTH12" for x in r) and
               r[0]["delta_cp"]==r[1]["delta_cp"])
        score=r[0].get("delta_cp") if exact else None
        chosen=(pair[0] if score is not None and score>0 else
                pair[1] if score is not None and score<0 else None)
        o["worlds"][name]={"fen":fen,"fen_sha256":hashlib.sha256(fen.encode()).hexdigest(),
                            "repeats":r,"repeat_exact":exact,
                            "delta_a_minus_b_cp":score,"preferred_at_depth12":chosen,
                            "direction_matches_prior_Ethereal_native_rank":(
                                chosen==old_native[name]) if chosen is not None else None,
                            "within_50cp_at_depth12":abs(score)<=50 if score is not None else None}
    o["all_three_worlds_within50"]=all(x["within_50cp_at_depth12"] is True for x in o["worlds"].values())
    o["all_repeats_exact"]=all(x["repeat_exact"] for x in o["worlds"].values())
    o["all_prior_direction_matches"]=all(x["direction_matches_prior_Ethereal_native_rank"] is True for x in o["worlds"].values())
    out=Path(a.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(o,indent=2)+"\n")
    print("C3X_013_P3_REPEAT_EXACT",o["all_repeats_exact"])
    print("C3X_013_P3_DIRECTION_MATCH",o["all_prior_direction_matches"])
    print("C3X_013_P3_ENGINE_TRANSPORT_PROVEN",False)

if __name__=="__main__":
    main()
