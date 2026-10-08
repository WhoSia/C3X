#!/usr/bin/env python3
"""C3X 0.13 P8-EP9 root-pair direct test on P7 frozen CECLUB FEN.

This is a retrospective, source-frozen near-equal pair, NOT a new holdout.
Compare two MULTIPV root alternatives under genuine UCI searchmoves at same depth.
The main and qsearch TT cutoff masks affect many nodes/search paths, and no
strategic concept mediation or cross-engine transport is inferred.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
import chess

SOURCE_GAME="https://lichess.org/broadcast/ceclub-primera-division-linares-2026/round-6/HLnCaWdO/0YxrjUCr"
SOURCE_SEGMENT_SHA256="e080dcbf8bcb1c99ac8ec8743673048b7063bbbddff89b9d4442ce431a01981c"
FEN="2rq1rk1/p4ppp/bp1bnn2/3pN3/2pP3P/1P2PPP1/PB2NRB1/R2Q2K1 w - - 1 17"
PAIR=("f3f4","g3g4")
DEPTHS=(8,12)
MODES=("OFF","MAIN","QSEARCH","BOTH")

def raw(binary,depth,mode):
    board=chess.Board(FEN)
    assert board.is_valid() and board.turn==chess.WHITE
    assert all(chess.Move.from_uci(m) in board.legal_moves for m in PAIR)
    env=dict(os.environ,C3X_P8_EP9_BLOCK_CUTOFF=mode)
    with subprocess.Popen([str(binary)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,text=True,bufsize=1,env=env) as p:
        lines=[]
        def send(*cmd):
            p.stdin.write("\n".join(cmd)+"\n");p.stdin.flush()
        def await_line(prefix):
            for _ in range(100000):
                x=p.stdout.readline()
                if not x:raise RuntimeError("UCI EOF "+prefix+repr(lines[-8:]))
                lines.append(x.strip())
                if x.startswith(prefix):return
            raise RuntimeError("Excess UCI traffic")
        send("uci");await_line("uciok")
        send("setoption name Threads value 1","setoption name Hash value 16",
             "setoption name MultiPV value 2","ucinewgame","isready")
        await_line("readyok")
        send("position fen "+FEN,"go depth "+str(depth)+" searchmoves "+" ".join(PAIR))
        await_line("bestmove ");send("quit");p.wait(timeout=10)
    info={}
    for x in lines:
        if not x.startswith("info depth ") or " pv " not in x or not re.search(r"\bscore (?:cp|mate) -?\d+",x):
            continue
        this_depth=int(re.search(r"\bdepth (\d+)",x).group(1))
        mp=re.search(r"\bmultipv (\d+)",x)
        if this_depth!=depth or not mp:continue
        rank=int(mp.group(1))
        if rank not in (1,2):continue
        kind,score=re.search(r"\bscore (cp|mate) (-?\d+)",x).groups()
        move=x.split(" pv ",1)[1].split()[0]
        info[rank]={"root_move":move,"score_kind":kind,"score_white_cp":int(score) if kind=="cp" else None,
                    "score_mate_white":int(score) if kind=="mate" else None,
                    "nodes":int(re.search(r"\bnodes (\d+)",x).group(1)),
                    "pv":x.split(" pv ",1)[1].split()[:12]}
    if set(info)!={1,2} or {info[1]["root_move"],info[2]["root_move"]}!=set(PAIR):
        raise ValueError("Incomplete true MultiPV pair: "+str(info))
    best=next(x.split()[1] for x in reversed(lines) if x.startswith("bestmove "))
    if best!=info[1]["root_move"]:raise ValueError("UCI bestmove does not match MultiPV1")
    telemetry=[x for x in lines if x.startswith("info string c3x_p8_ep9 ")]
    if len(telemetry)>1 or (mode!="OFF" and len(telemetry)!=1):
        raise ValueError("Missing/duplicate TT telemetry")
    counts={}
    if telemetry:
        for field in telemetry[0].split()[3:]:
            k,v=field.split("=",1);counts[k]=int(v)
        if counts.get("mode")!=MODES.index(mode):raise ValueError("Wrong mask mode")
    scores={v["root_move"]:v["score_white_cp"] for v in info.values()}
    return {"bestmove":best,"by_rank":info,"pair_scores_white_cp":scores,
            "a_minus_b_cp":scores[PAIR[0]]-scores[PAIR[1]] if all(v is not None for v in scores.values()) else None,
            "telemetry":counts}

def semantic(x):
    return {"bestmove":x["bestmove"],"by_rank":x["by_rank"],"a_minus_b_cp":x["a_minus_b_cp"]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline",required=True);p.add_argument("--instrumented",required=True)
    p.add_argument("--output",required=True);a=p.parse_args()
    rows=[]
    for depth in DEPTHS:
        for repeat in (1,2):
            base=raw(a.baseline,depth,"OFF")
            sham=raw(a.instrumented,depth,"OFF")
            exact=semantic(base)==semantic(sham)
            masks={name:raw(a.instrumented,depth,name) for name in MODES[1:]} if exact else {}
            rows.append({"depth":depth,"cold_repeat":repeat,"baseline":base,"sham":sham,"sham_exact":exact,"masks":masks})
            print("EP9_DIRECT_ROOT_PAIR",depth,repeat,"SHAM",exact,
                  "ROOT_CHOICES",{k:v["bestmove"] for k,v in masks.items()},flush=True)
    exact=all(x["sham_exact"] for x in rows)
    x={"schema":"c3x-013-p8ep9-previously-frozen-ceclub-direct-root-multipv-v1",
       "status":"SOURCE_NATIVE_ROOT_PAIR_PATH_INTERVENTION_NO_STRATEGIC_CERTIFICATION",
       "game_url":SOURCE_GAME,"source_segment_sha256":SOURCE_SEGMENT_SHA256,
       "historical_P7_reused":True,"independent_holdout":False,
       "root_FEN":FEN,"pair_uci":list(PAIR),"depths":list(DEPTHS),
       "unmodified_vs_counter_sham_exact":exact,
       "cells":rows,
       "masking_scope":"Only TT early bound returns MAIN and/or QSEARCH, TT reads and other uses remain",
       "cross_engine_validated":False,"chess_concept_caused_engine_preference":False,
       "human_preference_claim":False,"C3X_014":"UNOPENED_UNNAMED"}
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(x,indent=2)+"\n")
    print("EP9_DIRECT_PAIR_RESULT",{
      "sham_all":exact,"baseline_moves":[z["baseline"]["bestmove"] for z in rows],
      "mask_changes":{mode:sum(z["masks"][mode]["bestmove"]!=z["sham"]["bestmove"]
                              for z in rows if mode in z["masks"])
                      for mode in ("MAIN","QSEARCH","BOTH")}},flush=True)
    if not exact:raise SystemExit("EP9_ROOT_PAIR_SHAM_NOT_EQUIVALENT_HOLD")
if __name__=="__main__":main()
