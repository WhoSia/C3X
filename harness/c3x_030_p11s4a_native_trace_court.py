#!/usr/bin/env python3
"""C3X 0.30 P11/S4-A actual UCI native source tracer non-interference gate.

Run original and strictly source-patched Stockfish16 with SAME legal history,
same UCI cold/warm protocol and fixed requested nodes. All observations are
produced by real Stockfish processes. Return HOLD if emitted probe/save events
are absent or engine decision/depth/nodes/score/PV change.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import queue
import re
import subprocess
import threading

import chess
from c3x_030_p11_repeatability_cohort import positions, SOURCE_COMMIT

SCHEMA="c3x030-p11s4a-stockfish16-readonly-TT-tracer-noninterference-v1"
SOURCE_IDS=("queens_gambit_ply4","sicilian_najdorf_ply4","english_ply4")
EVENT_RE=re.compile(r"^C3X_TT_EVENT kind=(probe|save) index=(\d+) ply=(\d+) key=(\d+) ")
DEPTH_RE=re.compile(r"\bdepth\s+(\d+)")
NODES_RE=re.compile(r"\bnodes\s+(\d+)")
SCORE_RE=re.compile(r"\bscore\s+(cp|mate)\s+(-?\d+)")
PV_RE=re.compile(r"\bpv\s+(.+)$")
LIMIT=12000

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def parse_info(line):
    depth=DEPTH_RE.search(line)
    nodes=NODES_RE.search(line)
    score=SCORE_RE.search(line)
    pv=PV_RE.search(line)
    return {"depth":int(depth.group(1)) if depth else None,
            "nodes":int(nodes.group(1)) if nodes else None,
            "score":(score.group(1),int(score.group(2))) if score else None,
            "pv":pv.group(1).split()[:12] if pv else None}

def trace_events(lines):
    data=[]
    for line in lines:
        if not line.startswith("C3X_TT_EVENT"):continue
        m=EVENT_RE.search(line)
        if not m:raise ValueError("S4A_HOLD_BAD_ENGINE_TRACE_EVENT")
        data.append({"kind":m.group(1),"index":int(m.group(2)),
                     "ply":int(m.group(3)),"key":m.group(4),"raw":line})
    return data

def play_session(binary,fen):
    cmd=[str(Path(binary).resolve())]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,text=True,bufsize=1)
    out=queue.Queue()
    errors=[]
    def drain(source,dest):
        try:
            for line in source:
                dest(line.rstrip("\r\n"))
        except Exception as exc:
            dest("C3X_DRAIN_ERROR:"+repr(exc))
    a=threading.Thread(target=drain,args=(p.stdout,out.put),daemon=True)
    b=threading.Thread(target=drain,args=(p.stderr,errors.append),daemon=True)
    a.start();b.start()
    def send(s):
        p.stdin.write(s+"\n")
        p.stdin.flush()
    def until(token):
        lines=[]
        while True:
            try:line=out.get(timeout=50)
            except queue.Empty:raise ValueError("S4A_HOLD_ENGINE_RESPONSE_TIMEOUT:"+token)
            lines.append(line)
            if line.startswith(token):return lines
            if len(lines)>80000:raise ValueError("S4A_HOLD_UCI_OUTPUT_FLOOD")
    try:
        send("uci");until("uciok")
        for line in ("setoption name Threads value 1",
                     "setoption name Hash value 16",
                     "setoption name Use NNUE value false",
                     "setoption name Skill Level value 20",
                     "setoption name UCI_LimitStrength value false",
                     "ucinewgame","isready"):
            send(line)
        until("readyok")
        rows=[]
        for _ in range(2):
            send("position fen "+fen)
            send("go nodes "+str(LIMIT))
            lines=until("bestmove ")
            last=[x for x in lines if x.startswith("info ") and " score " in x and " pv " in x]
            if not last:raise ValueError("S4A_HOLD_NO_UCI_INFO")
            result=parse_info(last[-1])
            result["bestmove"]=lines[-1].split()[1]
            result["full_info_last"]=last[-1]
            if result["nodes"] is None or result["nodes"]<1:
                raise ValueError("S4A_HOLD_NATIVE_NODES")
            rows.append(result)
        send("quit")
        p.wait(timeout=10)
        b.join(timeout=5)
        if p.returncode not in (0,None):raise ValueError("S4A_HOLD_ENGINE_EXIT")
        return {"trials":rows,"events":trace_events(errors),
                "stderr_other":[x for x in errors if not x.startswith("C3X_TT_EVENT")][:10]}
    finally:
        if p.poll() is None:p.kill()
        try:p.wait(timeout=5)
        except subprocess.TimeoutExpired:pass

def compare_records(base,logged):
    if len(base["trials"])!=len(logged["trials"]):
        raise ValueError("S4A_HOLD_REPETITIONS")
    keys=("bestmove","depth","nodes","score","pv")
    mismatches=[]
    for i,(b,l) in enumerate(zip(base["trials"],logged["trials"])):
        changed=[k for k in keys if b[k]!=l[k]]
        if changed:mismatches.append({"trial":i,"changed_fields":changed})
    events=logged["events"]
    counts=dict(Counter(x["kind"] for x in events))
    unique_plies=sorted(set(x["ply"] for x in events))
    return {"noninterference_pass":not mismatches,
            "events_both_probe_and_save":counts.get("probe",0)>0 and counts.get("save",0)>0,
            "events":counts,"ply_values":unique_plies,
            "mismatches":mismatches}

def run(baseline,patched,source,patched_source):
    if digest(baseline)==digest(patched):
        raise ValueError("S4A_HOLD_DIFFERENT_BINARIES_REQUIRED")
    p=positions()
    report={"schema":SCHEMA,"source_commit":SOURCE_COMMIT,
            "original_search_cpp_sha256":digest(source),
            "patched_search_cpp_sha256":digest(patched_source),
            "baseline_binary_sha256":digest(baseline),
            "instrumented_binary_sha256":digest(patched),
            "same_uci_settings":True,"requested_nodes":LIMIT,
            "two_trials_per_binary_per_position":True,
            "cohort_is_p11_discovery_not_new_holdout":True,
            "native_source_tt_event_causal_intervention":False,
            "source_events_have_proven_ancestor_root_correlation":False,
            "positions":{}}
    for id in SOURCE_IDS:
        if id not in p:raise ValueError("S4A_HOLD_PREDECLARED_POSITION")
        b=chess.Board(p[id]["fen"])
        if not b.is_valid():raise ValueError("S4A_HOLD_ILLEGAL_FEN")
        cold=play_session(baseline,p[id]["fen"])
        traced=play_session(patched,p[id]["fen"])
        diff=compare_records(cold,traced)
        report["positions"][id]={"fen":p[id]["fen"],"history_uci":p[id]["history_uci"],
                                 "baseline":cold["trials"],
                                 "instrumented":traced["trials"],
                                 "trace_event_count":len(traced["events"]),
                                 "trace_events":traced["events"],
                                 "audit":diff}
        print("S4A_REAL_EVENT",id,"audit",diff,"trace",len(traced["events"]),flush=True)
    report["real_native_searches"]=len(SOURCE_IDS)*2*2
    report["real_nodes_total"]=sum(sum(t["nodes"] for t in obj["baseline"]+obj["instrumented"])
        for obj in report["positions"].values())
    report["noninterference_pass"]=all(
        entry["audit"]["noninterference_pass"]
        and entry["audit"]["events_both_probe_and_save"]
        for entry in report["positions"].values())
    report["status"]="PASS_READONLY_MAIN_TT_TRACE" if report["noninterference_pass"] else "HOLD_TRACE_INTERFERES_OR_MISSING_EVENTS"
    return report

def main():
    a=argparse.ArgumentParser()
    for f in ("baseline","patched","source","patched-source","out"):
        a.add_argument("--"+f,required=True)
    z=vars(a.parse_args())
    report=run(z["baseline"],z["patched"],z["source"],z["patched_source"])
    out=Path(z["out"]);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
    print("S4A_NATIVE_TRACE_COURT",report["status"],"SEARCHES",report["real_native_searches"],
          "ACTUAL_NODES",report["real_nodes_total"],"SHA256",digest(out),flush=True)
    if not report["noninterference_pass"]:raise SystemExit(2)

if __name__=="__main__":main()
