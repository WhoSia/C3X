#!/usr/bin/env python3
"""P34-R3: unmodified Stockfish16 UCI 'eval' trace at EXACT SAME boards.

This isolates a static score (including hybrid/PSQ routing) from subsequent
search, not internal NNUE feature semantics or source-mediation causality.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import chess
from c3x_029_p32_original_history_reply_value_native import (
    replay_original,FROZEN_SOURCE_SHA256,need,
)

REGEX = re.compile(r"(?m)^\s*(Classical evaluation|NNUE evaluation|Final evaluation)\s+([+-]?\d+(?:\.\d+)?)\s+\(white side\)")

def parse_trace(text):
    if "Final evaluation: none (in check)" in text:
        return {"status":"IN_CHECK_EVAL_NOT_AVAILABLE"}
    m={label:float(val) for label,val in REGEX.findall(text)}
    if set(m)!={"Classical evaluation","NNUE evaluation","Final evaluation"}:
        return {"status":"HOLD_EVAL_TRACE_MISSING","labels_found":sorted(m)}
    return {"status":"DIRECT_STATIC_TRACE_OK",
            "classical_white_pawns":m["Classical evaluation"],
            "nnue_white_pawns":m["NNUE evaluation"],
            "final_white_pawns":m["Final evaluation"],
            "raw_nnue_minus_classical_white_pawns":m["NNUE evaluation"]-m["Classical evaluation"]}

def trace(engine_path, history):
    need(all(isinstance(m,str) for m in history),"HISTORY_UCI_TYPE")
    stdin=("uci\nsetoption name Threads value 1\nsetoption name Hash value 16\n"+
           "setoption name Use NNUE value true\nucinewgame\nisready\n"+
           "position startpos moves "+" ".join(history)+"\neval\nquit\n")
    result=subprocess.run([engine_path],input=stdin,encoding="utf-8",
          stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=90,check=True)
    need("uciok" in result.stdout and "readyok" in result.stdout,"UCI_HANDSHAKE")
    return parse_trace(result.stdout),result.stdout

def build(source, previous, engine):
    need(previous["schema"]=="c3x029-p34-equal-requested-node-foil-plan-NNUE-classical-v1",
         "P34_SCHEMA")
    mapping={x["id"]:x for x in source["selected"]}
    output=[]
    for record in previous["records"]:
        source_case=mapping[record["case_id"]]
        board=replay_original(source_case)
        history=source_case["full_original_mainline_uci"][:source_case["source_ply_before_original_move"]]
        root=chess.Move.from_uci(record["root_uci"])
        need(root in board.legal_moves,"ROOT_ILLEGAL")
        board.push(root)
        branches=[("immediately_after_root",None)]
        ref=record["reference_by_mode"]
        for mode in ("classical","nnue"):
            ranks=ref[mode]
            worst=min(r["root_value_cp"] for r in ranks)
            for r in ranks:
                if r["root_value_cp"]==worst:
                    branches.append(("after_"+mode+"_worst_reply",r["reply"]))
                    break
        uniq=set()
        for label,reply in branches:
            state=board.copy(stack=True)
            moves=history+[record["root_uci"]]
            if reply:
                mv=chess.Move.from_uci(reply)
                need(mv in state.legal_moves,"REFERENCE_REPLY_NOT_LEGAL")
                state.push(mv);moves.append(reply)
            key=tuple(moves)
            if key in uniq:continue
            uniq.add(key)
            numerical,raw=trace(engine,moves)
            output.append({"case_id":record["case_id"],"root":record["root_uci"],
                           "scope":label,"reply":reply,
                           "fen":state.fen(en_passant="fen"),
                           "position_history_length":len(moves),
                           "mover_root_color":"white" if (not board.turn)==chess.WHITE else "black",
                           "is_in_check":state.is_check(),
                           "trace":numerical,
                           "raw_trace_sha256":hashlib.sha256(raw.encode()).hexdigest()})
            print("P34_R3",record["case_id"],record["root_uci"],label,reply,
                  numerical,flush=True)
    return {"schema":"c3x029-p34-r3-source-eval-trace-v1",
           "claim_ceiling":"source direct static evaluator trace, NOT learned NNUE features or causation",
           "source_sha256":FROZEN_SOURCE_SHA256,
           "p34_conditions":"same original full game UCI history; direct eval with Use NNUE true",
           "records":output}

def main():
    p=argparse.ArgumentParser()
    for name in ("source","p34","engine","out"):p.add_argument("--"+name,required=True)
    args=p.parse_args()
    b=Path(args.source).read_bytes()
    need(hashlib.sha256(b).hexdigest()==FROZEN_SOURCE_SHA256,"SOURCE_SHA")
    old=Path(args.p34).read_bytes()
    result=build(json.loads(b),json.loads(old),args.engine)
    result["p34_json_sha256"]=hashlib.sha256(old).hexdigest()
    Path(args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    need(len(result["records"])>=8,"TOO_FEW_WORLDS")
if __name__=="__main__":main()
