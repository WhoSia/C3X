#!/usr/bin/env python3
"""C3X P8-EP10: pre-fixed single TT return ordinal interventions on frozen CECLUB.

Source family: official sf_16, instrumented EP9 vs EP10. Exact root MultiPV2.
A positive flip in this grid is exploratory, NOT a cross-world causal law.
"""
import argparse, json, os, re, subprocess, hashlib
from pathlib import Path
import chess

FEN="2rq1rk1/p4ppp/bp1bnn2/3pN3/2pP3P/1P2PPP1/PB2NRB1/R2Q2K1 w - - 1 17"
PAIR=("f3f4","g3g4")
DEPTHS=(8,12)
ORDINALS=(1,2,4,8,16,32,64,128)
SITES=("MAIN","QSEARCH")
NEGATIVE=1000000000

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def analyze(binary,depth,site="NONE",ordinal=0,require_ep10=False):
    b=chess.Board(FEN)
    assert b.is_valid() and all(chess.Move.from_uci(x) in b.legal_moves for x in PAIR)
    env=dict(os.environ,C3X_P8_EP9_BLOCK_CUTOFF="OFF",
             C3X_P8_EP10_SITE=site,C3X_P8_EP10_ORDINAL=str(ordinal))
    with subprocess.Popen([binary],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
             stderr=subprocess.STDOUT,text=True,bufsize=1,env=env) as p:
        logs=[]
        def send(*args):
            p.stdin.write("\n".join(args)+"\n");p.stdin.flush()
        def wait(prefix):
            for i in range(100000):
                line=p.stdout.readline()
                if not line:raise RuntimeError("Unexpected engine EOF "+repr(logs[-10:]))
                logs.append(line.strip())
                if line.startswith(prefix):return
            raise RuntimeError("UCI traffic exhausted")
        send("uci");wait("uciok")
        send("setoption name Threads value 1","setoption name Hash value 16",
             "setoption name MultiPV value 2","ucinewgame","isready")
        wait("readyok")
        send("position fen "+FEN,"go depth "+str(depth)+" searchmoves "+" ".join(PAIR))
        wait("bestmove ");send("quit");p.wait(timeout=10)
    infos={}
    for line in logs:
        if not line.startswith("info depth ") or " pv " not in line or " multipv " not in line:continue
        d=int(re.search(r"\bdepth (\d+)",line).group(1))
        if d!=depth:continue
        m=re.search(r"\bscore (cp|mate) (-?\d+)",line)
        if not m:continue
        rank=int(re.search(r"\bmultipv (\d+)",line).group(1))
        move=line.split(" pv ",1)[1].split()[0]
        infos[rank]={"move":move,"score_kind":m.group(1),"score":int(m.group(2)),
                     "nodes":int(re.search(r"\bnodes (\d+)",line).group(1)),
                     "pv":line.split(" pv ",1)[1].split()[:12]}
    if set(infos)!={1,2} or {infos[1]["move"],infos[2]["move"]}!=set(PAIR):
        raise ValueError("Unqualified true root MultiPV: "+str(infos))
    best=[x.split()[1] for x in logs if x.startswith("bestmove ")]
    if len(best)!=1 or best[0]!=infos[1]["move"]:
        raise ValueError("Incorrect bestmove")
    ep10=[x for x in logs if x.startswith("info string c3x_p8_ep10 ")]
    if len(ep10)>1 or (require_ep10 and len(ep10)!=1):
        raise ValueError("EP10 telemetry absent/ambiguous")
    tt={}
    if ep10:
        for token in ep10[0].split()[3:]:
            k,v=token.split("=",1);tt[k]=int(v)
        expected_site={"NONE":0,"MAIN":1,"QSEARCH":2}[site]
        if tt["site"]!=expected_site or tt["ordinal"]!=ordinal or tt["blocked"]>1:
            raise ValueError("TT event selector integrity")
        if site=="NONE" and tt["blocked"]!=0:raise ValueError("Sham unexpectedly intervened")
        if site!="NONE" and ordinal<=min(tt["main_seen"] if site=="MAIN" else tt["q_seen"],128) and tt["blocked"]!=1:
            raise ValueError("Eligible event not blocked")
    pvs={i["move"]:i for i in infos.values()}
    a,b=pvs[PAIR[0]],pvs[PAIR[1]]
    gap=(a["score"]-b["score"]) if a["score_kind"]==b["score_kind"]=="cp" else None
    return {"bestmove":best[0],"gap_white_cp":gap,"ranks":infos,"target":tt}

def meaning(x):
    return {k:x[k] for k in ("bestmove","gap_white_cp","ranks")}

def run(args):
    rows=[]
    for depth in DEPTHS:
        for repeat in (1,2):
            base=analyze(args.ep9,depth)
            sham=analyze(args.ep10,depth,require_ep10=True)
            baseline_equal=meaning(base)==meaning(sham)
            negatives={}
            scans={}
            if baseline_equal:
                for site in SITES:
                    neg=analyze(args.ep10,depth,site,NEGATIVE,require_ep10=True)
                    negatives[site]=neg
                    for ordinal in ORDINALS:
                        result=analyze(args.ep10,depth,site,ordinal,require_ep10=True)
                        scans[f"{site}:{ordinal}"]=result
            row={"depth":depth,"repeat":repeat,"ep9_OFF":base,"ep10_NONE":sham,
                 "sham_exact":baseline_equal,"negative_controls":negatives,"scan":scans}
            rows.append(row)
            print("EP10_FIXED_GRID",depth,repeat,"sham",baseline_equal,
                  "actual_single_event_hits",sum(v["target"]["blocked"]==1 for v in scans.values()),
                  flush=True)
    all_sham=all(r["sham_exact"] for r in rows)
    all_neg=all(all(v["target"]["blocked"]==0 and meaning(v)==meaning(r["ep10_NONE"])
                    for v in r["negative_controls"].values()) for r in rows)
    changed={s:sum(v["bestmove"]!=r["ep10_NONE"]["bestmove"]
                   for r in rows for k,v in r["scan"].items() if k.startswith(s+":"))
             for s in SITES}
    touched={s:sum(v["target"]["blocked"]==1
                   for r in rows for k,v in r["scan"].items() if k.startswith(s+":"))
             for s in SITES}
    report={"schema":"c3x-013-p8ep10-single-event-fixed-grid-ceclub-v1",
            "status":"EXPLORATORY_SOURCE_LOCAL_SINGLE_EXECUTION_EVENT_COURT",
            "source":"Previously examined P7-R1/R2 CECLUB, NOT a new game",
            "source_game":"https://lichess.org/broadcast/ceclub-primera-division-linares-2026/round-6/HLnCaWdO/0YxrjUCr",
            "root_FEN":FEN,"pair":PAIR,"depths":DEPTHS,"cold_repeats":2,
            "fixed_ordinals":ORDINALS,"fixed_sites":SITES,
            "negative_control_ordinal":NEGATIVE,
            "source_SHA256":{"ep9":sha(args.ep9),"ep10":sha(args.ep10)},
            "sham_exact_all":all_sham,"negative_control_exact_all":all_neg,
            "touched_runs":touched,"first_move_changed_runs":changed,"rows":rows,
            "interpretation_ceiling":"one EXECUTION-occurrence TT bound return, not one invariant semantic TT object; multiple tests exploratory; no independent source/engine, no concept mediation",
            "original_chess_concept_proven":False,"causal_certificate_authorized":False,
            "C3X_014":"UNOPENED_UNNAMED"}
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(report,indent=2)+"\n")
    print("EP10_SINGLE_EVENT_RESULT",json.dumps({"sham_exact":all_sham,
                    "negative_control_exact":all_neg,
                    "touched":touched,"flip_counts":changed}),flush=True)
    if not all_sham or not all_neg:
        raise SystemExit("EP10_NOOP_OR_SENTINEL_CONTROL_FAILED__INTERVENTION_INVALID")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--ep9",required=True);p.add_argument("--ep10",required=True);p.add_argument("--out",required=True)
    run(p.parse_args())
