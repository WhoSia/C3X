#!/usr/bin/env python3
"""C3X 0.14 P1: real source-disjoint SF16 native TT cutoff family susceptibility.

Only reads a publicly designated four-game development JSON, never the sealed
holdout manifest. Same input file and each legal pawn single/double pair are
fixed BEFORE engine outcomes. No chess strategic concept certificate.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
import chess

SOURCE_SHA="bbaef73beda60d9e03c9f83324651db3b130606be4c84cb9f8a170a958a96274"
DEPTHS=(8,12)
MODES=("OFF","MAIN","QSEARCH","BOTH")
SOURCE="TCEC-Chess/tcecgames S29-final commit 3dd69a40b3cf6ccc74144df7411ef4e8e2140286"

def sha_file(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def uci(binary,fen,pair,depth,mode):
    b=chess.Board(fen)
    assert b.is_valid() and b.turn==chess.WHITE
    assert len(pair)==2 and pair[0]!=pair[1]
    assert all(chess.Move.from_uci(m) in b.legal_moves for m in pair)
    env=dict(os.environ,C3X_P8_EP9_BLOCK_CUTOFF=mode)
    lines=[]
    with subprocess.Popen([binary],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
          stderr=subprocess.STDOUT,text=True,bufsize=1,env=env) as p:
        def write(*args):
            p.stdin.write("\n".join(args)+"\n");p.stdin.flush()
        def expect(prefix):
            for _ in range(100000):
                line=p.stdout.readline()
                if not line:raise RuntimeError("Premature engine EOF: "+str(lines[-10:]))
                lines.append(line.strip())
                if line.startswith(prefix):return
            raise RuntimeError("Unexpectedly long UCI response")
        write("uci");expect("uciok")
        write("setoption name Threads value 1","setoption name Hash value 16",
              "setoption name MultiPV value 2","ucinewgame","isready")
        expect("readyok")
        write("position fen "+fen,"go depth "+str(depth)+" searchmoves "+" ".join(pair))
        expect("bestmove ");write("quit")
        if p.wait(timeout=10)!=0:raise RuntimeError("SF16 nonzero exit")
    infos={}
    for line in lines:
        if " pv " not in line or not line.startswith("info depth ") or " multipv " not in line:continue
        md=re.search(r"\bdepth (\d+)",line)
        if not md or int(md.group(1))!=depth:continue
        rank=int(re.search(r"\bmultipv (\d+)",line).group(1))
        score=re.search(r"\bscore (cp|mate) (-?\d+)",line)
        if not score:continue
        pv=line.split(" pv ",1)[1].split()
        infos[rank]={"move":pv[0],"score_kind":score.group(1),
                     "score_white_cp":int(score.group(2)) if score.group(1)=="cp" else None,
                     "mate_white":int(score.group(2)) if score.group(1)=="mate" else None,
                     "nodes":int(re.search(r"\bnodes (\d+)",line).group(1)),
                     "pv":pv[:12]}
    if set(infos)!={1,2} or {v["move"] for v in infos.values()}!=set(pair):
        raise RuntimeError("MultiPV missing legal root pair "+str(infos))
    best=[line.split()[1] for line in lines if line.startswith("bestmove ")]
    if best!=[infos[1]["move"]]:raise RuntimeError("bestmove not top MultiPV")
    found=[line for line in lines if line.startswith("info string c3x_p8_ep9 ")]
    if len(found)>1:raise RuntimeError("multiple telemetry summaries")
    t={}
    if found:
        t={k:int(v) for k,v in (z.split("=",1) for z in found[0].split()[3:])}
        if t.get("mode")!=MODES.index(mode):raise RuntimeError("Wrong instrumented mode")
        if mode=="OFF" and (t["main_blocked"] or t["q_blocked"]):raise RuntimeError("Sham blocked event")
        if mode=="MAIN" and t["q_blocked"]:raise RuntimeError("MAIN touched QSEARCH")
        if mode=="QSEARCH" and t["main_blocked"]:raise RuntimeError("QSEARCH touched MAIN")
        if mode=="BOTH" and (t["main_taken"] or t["q_taken"]):raise RuntimeError("BOTH failed to mask")
    by_move={z["move"]:z for z in infos.values()}
    gap=(by_move[pair[0]]["score_white_cp"]-by_move[pair[1]]["score_white_cp"]
         if all(z["score_white_cp"] is not None for z in by_move.values()) else None)
    return {"bestmove":best[0],"ranked":infos,"pair_gap_cp":gap,
            "source_score_orientation":"white, pair first minus pair second",
            "native_tt_telemetry":t}

def outcomes(x):
    return {k:x[k] for k in ("bestmove","ranked","pair_gap_cp")}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--development",required=True)
    a.add_argument("--clean",required=True)
    a.add_argument("--instrumented",required=True)
    a.add_argument("--output",required=True)
    ns=a.parse_args()
    raw=Path(ns.development).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:
        raise SystemExit("P1_INPUT_DEVELOPMENT_SOURCE_SHA_MISMATCH")
    src=json.loads(raw)
    assert src["schema"]=="c3x-014-p1-tcec-s29-source-disjoint-intake-v1"
    assert src["eligibility_pass"] and src["holdout_game_count"]==4 and src["engine_scores_observed"] is False
    dev=src["development_games"]
    assert len(dev)==4 and len({d["opening_group_hash"] for d in dev})==4
    cells=[]
    for d in dev:
        fen=d["full_root_fen"];pair=d["candidate_pair_uci"]
        for depth in DEPTHS:
            for cold in (1,2):
                clean=uci(ns.clean,fen,pair,depth,"OFF")
                off=uci(ns.instrumented,fen,pair,depth,"OFF")
                sham=outcomes(clean)==outcomes(off)
                modes={}
                if sham:
                    for name in MODES[1:]:
                        modes[name]=uci(ns.instrumented,fen,pair,depth,name)
                        if not modes[name]["native_tt_telemetry"]:
                            raise RuntimeError("Missing native TT observation "+name)
                cells.append({"group":d["opening_group_hash"],"source_game_id":d["source_game_id"],
                    "source_round":d["source_headers"]["Round"],"fen":fen,
                    "pair":pair,"depth":depth,"cold_repeat":cold,
                    "clean":clean,"native_off":off,"sham_exact":sham,"modes":modes})
                print("P1_DEV_NATIVE_CELL",d["source_headers"]["Round"],pair,depth,cold,
                    "sham",sham,"choice",off["bestmove"],
                    "MAIN",modes.get("MAIN",{}).get("bestmove"),flush=True)
    all_sham=all(r["sham_exact"] for r in cells)
    flipped={mode:sum(x["modes"][mode]["bestmove"]!=x["native_off"]["bestmove"]
                      for x in cells if mode in x["modes"])
             for mode in ("MAIN","QSEARCH","BOTH")}
    independent_groups_flipping_main=len({z["group"] for z in cells if "MAIN" in z["modes"]
                                               and z["modes"]["MAIN"]["bestmove"]!=z["native_off"]["bestmove"]})
    out={"schema":"c3x-014-p1-real-s29-develop-tt-cutoff-susceptibility-v1",
         "status":"SOURCE_DISJOINT_DEVELOPMENT_PILOT_ONLY__SEALED_HOLDOUT_UNOPENED",
         "source":SOURCE,"source_file_sha256":src["origin"]["sha256"],
         "development_input_sha256":SOURCE_SHA,"engine":"native original SF16 vs EP9 source instrumentation",
         "binary_hashes":{"clean":sha_file(ns.clean),"instrumented":sha_file(ns.instrumented)},
         "independent_source_game_groups":len(dev),"holdout_used":False,
         "source_game_independence_not_strong_provider_diversity":True,
         "depths":list(DEPTHS),"cold_repeats":2,"cells":cells,"all_sham_exact":all_sham,
         "first_root_choice_flip_count_by_mask":flipped,
         "distinct_development_game_groups_with_MAIN_flip":independent_groups_flipping_main,
         "root_score_is_not_causal_concept_evidence":True,
         "C3X_014":"P1_DEVELOPMENT_PILOT_UNSEALED_HOLDOUT"}
    path=Path(ns.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2)+"\n")
    print("P1_DEVELOPMENT_NATIVE_VERDICT",json.dumps({
        "sham":all_sham,"depth_cases":len(cells),"source_groups":len(dev),
        "MAIN_flips":flipped["MAIN"],"different_games_MAIN":independent_groups_flipping_main}),flush=True)
    if not all_sham:raise SystemExit("P1_ENGINE_INSTRUMENTATION_SHAM_NOT_EQUIVALENT")
if __name__=="__main__":main()
