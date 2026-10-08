#!/usr/bin/env python3
"""C3X 0.13 P8-EP9 real SF16 source-native TT cutoff path court.

Reuses prior G9.4 distinction between TT read/semantic use/bound cutoff.
Observational sham compares identical upstream SF16 builds, one with counters.
Masked arms block ONLY return at two distinct TT cutoff sites.
No actual chess-concept-mediated reason may be certified from this court.
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

TCEC="r5k1/6p1/p5qn/4p2p/2ppP3/3Q3P/1P1B1PP1/R5K1 w - - 0 25"
CECLUB="2rq1rk1/p4ppp/bp1bnn2/3pN3/2pP3P/1P2PPP1/PB2NRB1/R2Q2K1 w - - 1 17"
DEPTHS=(8,12)
MODES=("OFF","MAIN","QSEARCH","BOTH")

def worlds():
    root=chess.Board(TCEC)
    assert root.is_valid()
    out={"TCEC_ROOT":root}
    for label,uci in (("TCEC_B2B3","b2b3"),("TCEC_B2B4","b2b4")):
        b=root.copy(stack=True)
        m=chess.Move.from_uci(uci)
        assert m in b.legal_moves
        b.push(m)
        assert b.turn==chess.BLACK
        out[label]=b
    # Historically frozen P7 R1/R2 CECLUB rank40; not a new holdout
    # Game segment SHA e080dcbf8bcb1c99ac8ec8743673048b7063bbbddff89b9d4442ce431a01981c
    # Previously observed near-equal root pair f3f4 versus g3g4 at d8/12/16
    c=chess.Board(CECLUB)
    assert c.is_valid() and c.turn==chess.WHITE
    out["CECLUB_ROOT"]=c
    for label,uci in (("CECLUB_F3F4","f3f4"),("CECLUB_G3G4","g3g4")):
        t=c.copy(stack=True)
        m=chess.Move.from_uci(uci)
        assert m in t.legal_moves
        t.push(m)
        assert t.turn==chess.BLACK
        out[label]=t
    # Independent chess sanity control, not an independent source-game replicate.
    out["INITIAL_POSITION"]=chess.Board()
    return out

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):
            h.update(chunk)
    return h.hexdigest()

def run(binary, board, depth, mode):
    env=dict(os.environ,C3X_P8_EP9_BLOCK_CUTOFF=mode)
    with subprocess.Popen([str(binary)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,text=True,bufsize=1,env=env) as p:
        lines=[]
        def send(*cmds):
            p.stdin.write("\n".join(cmds)+"\n")
            p.stdin.flush()
        def expect(prefix):
            for _ in range(100000):
                line=p.stdout.readline()
                if not line:
                    raise RuntimeError(f"Engine EOF waiting for {prefix}: {lines[-10:]}")
                lines.append(line.rstrip())
                if line.startswith(prefix):
                    return line.rstrip()
            raise RuntimeError("Unbounded UCI response")
        send("uci")
        expect("uciok")
        send("setoption name Threads value 1","setoption name Hash value 16",
             "setoption name MultiPV value 1","ucinewgame","isready")
        expect("readyok")
        send("position fen "+board.fen(en_passant="fen"),"go depth "+str(depth))
        expect("bestmove ")
        send("quit")
        p.wait(timeout=10)
    infos=[line for line in lines if line.startswith("info depth ")
           and re.search(r"\bscore (?:cp|mate) -?\d+\b",line)
           and " pv " in line]
    if not infos:raise ValueError("No final completed UCI score")
    final=infos[-1]
    d=int(re.search(r"\bdepth (\d+)",final).group(1))
    if d!=depth:raise ValueError(f"Unfinished depth {d}!={depth}")
    kind,num=re.search(r"\bscore (cp|mate) (-?\d+)",final).groups()
    pv=final.split(" pv ",1)[1].split()
    best=next(line.split()[1] for line in reversed(lines) if line.startswith("bestmove "))
    if pv[0]!=best:raise ValueError("PV head != bestmove")
    telemetry=[line for line in lines if line.startswith("info string c3x_p8_ep9 ")]
    if len(telemetry)>1:raise ValueError("More than one telemetry output")
    if mode!="OFF" and not telemetry:raise ValueError("Missing native telemetry")
    stats={}
    if telemetry:
        for x in telemetry[0].split()[3:]:
            k,v=x.split("=",1);stats[k]=int(v)
        assert stats["mode"]==MODES.index(mode)
        for prefix in ("main","q"):
            assert stats[prefix+"_probes"]>=stats[prefix+"_hits"]>=0
            assert stats[prefix+"_eligible"]>=stats[prefix+"_taken"]+stats[prefix+"_blocked"]
        if mode=="OFF":
            assert stats["main_blocked"]==stats["q_blocked"]==0
        if mode=="MAIN":
            assert stats["main_taken"]==stats["q_blocked"]==0
        if mode=="QSEARCH":
            assert stats["main_blocked"]==stats["q_taken"]==0
        if mode=="BOTH":
            assert stats["main_taken"]==stats["q_taken"]==0
    return {"bestmove":best,"pv":pv,"score_kind":kind,"score_stm":int(num),
            "score_white_cp":(int(num) if board.turn==chess.WHITE else -int(num)) if kind=="cp" else None,
            "depth":d,"nodes":int(re.search(r"\bnodes (\d+)",final).group(1)),
            "telemetry":stats,"all_info_count":len(infos)}

def semantics(x):
    return {k:x[k] for k in ("bestmove","pv","score_kind","score_stm","depth","nodes")}

def measure(args):
    cells=[]
    base=Path(args.baseline)
    traced=Path(args.instrumented)
    hashes={"baseline":sha256(base),"instrumented":sha256(traced)}
    for label,board in worlds().items():
        for depth in DEPTHS:
            for trial in range(2):
                baseline=run(base,board,depth,"OFF")
                sham=run(traced,board,depth,"OFF")
                exact=semantics(baseline)==semantics(sham)
                row={"world":label,"source_fen":board.fen(en_passant="fen"),
                     "depth":depth,"cold_trial":trial+1,"baseline":baseline,"instrumented_OFF":sham,
                     "noop_observer_equivalence":exact,"modes":{}}
                if exact:
                    for mode in ("MAIN","QSEARCH","BOTH"):
                        masked=run(traced,board,depth,mode)
                        row["modes"][mode]=masked
                cells.append(row)
                print("EP9_CELL",label,depth,trial+1,
                      "NOOP",exact,"MASKED_RUN",bool(row["modes"]),flush=True)
    all_equivalent=all(z["noop_observer_equivalence"] for z in cells)
    engaged={mode:sum(r["modes"][mode]["telemetry"][("main" if mode=="MAIN" else "q")+"_blocked"]
                      for r in cells if mode in r["modes"]) for mode in ("MAIN","QSEARCH")}
    changes={mode:sum(semantics(r["instrumented_OFF"])!=semantics(r["modes"][mode])
                      for r in cells if mode in r["modes"])
                 for mode in ("MAIN","QSEARCH","BOTH")}
    panel={"schema":"c3x-013-p8ep9-stockfish16-native-tt-cutoff-path-intervention-v1",
           "status":"OBSERVATIONAL_SHAM_AND_BOUND_RETURN_INTERVENTION_NOT_STRATEGIC_CAUSAL_AUTHORITY",
           "engine_source":"official-stockfish/Stockfish tag sf_16; checked pinned commit in native patch manifest",
           "source_and_build_hashes":hashes,
           "depths":list(DEPTHS),"repeats_per_world_depth":2,
           "worlds":len(worlds()),"cells":cells,
           "historical_CECLUB_origin":{"P7_R1_rank":40,"game_segment_sha256":"e080dcbf8bcb1c99ac8ec8743673048b7063bbbddff89b9d4442ce431a01981c","root_FEN":CECLUB,"pair":["f3f4","g3g4"],"scientifically_fresh":False},
           "observer_noop_exact_all":all_equivalent,
           "masked_runs_authorized":all_equivalent,
           "masked_mode_engagement":engaged,
           "masked_output_changed_cells":changes,
           "scientific_units":"2 previously used, distinct Lichess broadcasts (TCEC P8 and CECLUB P7) plus an artificial starting-position control; reused histories, same provider; repeated trials and after-root positions NOT independent games",
           "other_TT_uses_preserved":True,
           "causal_engine_mechanism_established":False,
           "chess_concept_causal_mediation_established":False,
           "C3X_014":"UNOPENED_UNNAMED"}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(panel,indent=2)+"\n")
    print("EP9_SOURCE_NATIVE_RESULT",json.dumps({
        "noop_equivalent":all_equivalent,"engagement":engaged,
        "masked_change_cells":changes,"count":len(cells)}),flush=True)
    if not all_equivalent:raise SystemExit("EP9_OBSERVER_SHAM_NOT_EQUIVALENT__CAUSAL_REJECTED")
    if not any(engaged.values()):raise SystemExit("EP9_NO_TARGETED_TT_CUTOFF_ENGAGEMENT_HOLD")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline",required=True)
    p.add_argument("--instrumented",required=True)
    p.add_argument("--output",required=True)
    measure(p.parse_args())

if __name__=="__main__":main()
