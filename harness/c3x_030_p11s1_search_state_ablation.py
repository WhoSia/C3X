#!/usr/bin/env python3
"""C3X 0.30 P11/S1: full-strength same-process search-state ablation.

Reuses P11's already disclosed 20 source FENs as DEVELOPMENT cohort, not
independent confirmation. Four search protocols:
- cold: fresh process every query
- retained: same engine same game, no explicit reset
- clear_hash: same engine same game, Clear Hash before every query
- new_game: same engine, distinct python-chess game token per query

No NNUE, no Skill<20 and no source-code edits. This can compare UCI commands
and measured outputs but does not prove transposition-table-only causality.
"""
from collections import Counter
import argparse
import hashlib
import json
import math
from pathlib import Path

import chess
import chess.engine
from c3x_030_p11_repeatability_cohort import positions, SOURCE_COMMIT

SCHEMA="c3x030-p11s1-fullstrength-search-state-factorial-v1"
ARMS=("cold_fresh_process","same_game_retained","same_game_clear_hash","same_process_new_game")
REPEATS=6
NODE_LIMIT=12000

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def engine_configuration():
    return {"Threads":1,"Hash":16,"Use NNUE":False,
            "Skill Level":20,"UCI_LimitStrength":False}

def check_options(engine):
    needed={"Threads","Hash","Use NNUE","Skill Level","UCI_LimitStrength","Clear Hash"}
    missing=needed-set(engine.options)
    if missing:
        raise ValueError("P11S1_HOLD_MISSING_UCI_OPTIONS:"+",".join(sorted(missing)))

def trial(engine, board, game):
    response=engine.play(board,chess.engine.Limit(nodes=NODE_LIMIT),
                         info=chess.engine.INFO_ALL,game=game)
    if response.move not in board.legal_moves:
        raise ValueError("P11S1_HOLD_ILLEGAL_BESTMOVE")
    info=response.info
    nodes,depth=info.get("nodes"),info.get("depth")
    if type(nodes) is not int or nodes<1 or type(depth) is not int or depth<1:
        raise ValueError("P11S1_HOLD_MISSING_NATIVE_STATS")
    score=info.get("score")
    return {"move_uci":response.move.uci(),"nodes_actual":nodes,
            "depth":depth,"score_cp_or_null":score.pov(board.turn).score() if score else None,
            "pv_first_uci_or_null":info["pv"][0].uci() if info.get("pv") else None}

def summarize(rows):
    if len(rows)!=REPEATS:
        raise ValueError("P11S1_HOLD_REPETITION_COUNT")
    moves=Counter(r["move_uci"] for r in rows)
    probabilities=[n/REPEATS for n in moves.values()]
    return {"distinct_move_count":len(moves),"observed_switch":len(moves)>1,
            "counts":dict(sorted(moves.items())),
            "entropy_bits":-sum(p*math.log2(p) for p in probabilities),
            "actual_nodes_total":sum(r["nodes_actual"] for r in rows),
            "actual_nodes_min":min(r["nodes_actual"] for r in rows),
            "actual_nodes_max":max(r["nodes_actual"] for r in rows)}

def measure(binary, board, arm):
    rows=[]
    if arm=="cold_fresh_process":
        for _ in range(REPEATS):
            with chess.engine.SimpleEngine.popen_uci(binary,timeout=120) as eng:
                check_options(eng)
                eng.configure(engine_configuration())
                rows.append(trial(eng,board,object()))
    else:
        with chess.engine.SimpleEngine.popen_uci(binary,timeout=120) as eng:
            check_options(eng)
            eng.configure(engine_configuration())
            same_game=object()
            for _ in range(REPEATS):
                if arm=="same_game_clear_hash":
                    # Genuine Stockfish UCI button, NOT a new engine and NOT a new game.
                    eng.configure({"Clear Hash":None})
                elif arm not in ("same_game_retained","same_process_new_game"):
                    raise ValueError("P11S1_HOLD_UNKNOWN_ARM")
                game=object() if arm=="same_process_new_game" else same_game
                rows.append(trial(eng,board,game))
    return rows

def run(binary):
    cohort=positions()
    if len(cohort)!=20:raise ValueError("P11S1_HOLD_COHORT")
    out={"schema":SCHEMA,"source_commit":SOURCE_COMMIT,"binary_sha256":digest(binary),
         "development_cohort_reuses_p11_positions":True,
         "independent_confirmatory_cohort":False,
         "native_source_code_modified":False,
         "configuration":engine_configuration(),
         "requested_node_limit":NODE_LIMIT,"repeats":REPEATS,
         "condition_semantics":{
             "cold_fresh_process":"new OS process per search",
             "same_game_retained":"same process and same python-chess game token, retained TT and search state",
             "same_game_clear_hash":"same process, same game token, UCI Clear Hash before each trial",
             "same_process_new_game":"same process, new python-chess game token per trial -> UCI ucinewgame when changed"},
         "cohort":{}}
    for pos_id,entry in cohort.items():
        board=chess.Board(entry["fen"])
        record=dict(entry,arms={})
        for arm in ARMS:
            rows=measure(binary,board,arm)
            record["arms"][arm]={"trials":rows,"summary":summarize(rows)}
        out["cohort"][pos_id]=record
        print("P11S1_POSITION",pos_id,
              {a:record["arms"][a]["summary"]["distinct_move_count"] for a in ARMS},
              flush=True)
    out["native_searches"]=len(cohort)*len(ARMS)*REPEATS
    out["native_nodes_total"]=sum(r["summary"]["actual_nodes_total"]
        for c in out["cohort"].values() for r in c["arms"].values())
    out["within_arm_switch_position_counts"]={
        arm:sum(int(v["arms"][arm]["summary"]["observed_switch"])
                for v in out["cohort"].values()) for arm in ARMS}
    out["cross_arm_disagreements_with_cold_reference"]={}
    for arm in ARMS:
        cnt=0
        for v in out["cohort"].values():
            cold=v["arms"]["cold_fresh_process"]["summary"]["counts"]
            if len(cold)!=1:
                raise ValueError("P11S1_HOLD_COLD_REFERENCE_NOT_STABLE")
            ref=next(iter(cold))
            cnt+=sum(t["move_uci"]!=ref for t in v["arms"][arm]["trials"])
        out["cross_arm_disagreements_with_cold_reference"][arm]=cnt
    out["no_intentional_strength_prng"]=True
    out["source_event_to_root_causality_proven"]=False
    out["clear_hash_isolation_caveat"]=(
        "Clear Hash resets TT entries, but other state, timers, history and Python protocol "
        "can persist; new-game signal may reset more than TT. This is not a complete causal isolation.")
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--stockfish",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    out=run(args.stockfish)
    dest=Path(args.out)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
    print("C3X_P11S1_REAL_SEARCHES",out["native_searches"],
          "NODES",out["native_nodes_total"],
          "SWITCH",out["within_arm_switch_position_counts"],
          "DISAGREE",out["cross_arm_disagreements_with_cold_reference"],
          "SHA",digest(dest),flush=True)

if __name__=="__main__":main()
