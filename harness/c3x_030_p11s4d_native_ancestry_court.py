#!/usr/bin/env python3
"""C3X P11/S4-D read-only, original-vs-instrumented native search ancestry COURT.

Preserve complete stderr for capped source-trace events rather than clipping to
10 lines; measure TT-hit→normal-return and root-candidate raw move ancestry
compatibility. Same raw move code is NOT a demonstrated dynamic value mediator;
early returns and qsearch are explicitly uninstrumented.
"""
import argparse,hashlib,json,os,queue,re,subprocess,threading
from collections import Counter
from pathlib import Path

from c3x_030_p11s4a_native_trace_court import parse_info,compare_records
from c3x_030_p11s4a_native_trace_court import SOURCE_IDS

SCHEMA="c3x030-p11s4d-native-original-readonly-ancestry-observation-v1"
S4B_SHA="081ee839f883d538081f1d2d15c43db1aa31cb12e4e713e1cda81815d5e59300"
KINDS=("probe","normal_return","root_candidate")
REQUIRED=("key","ply","parent_move_raw","depth")

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def parse_event(line):
    if not line.startswith("C3X_S4D "):return None
    pairs=dict(re.findall(r"([a-z_]+)=(-?[0-9]+|[a-z_]+)",line))
    if pairs.get("kind") not in KINDS:
        raise ValueError("S4D_HOLD_INVALID_NATIVE_EVENT_TYPE")
    if "seq" not in pairs:
        raise ValueError("S4D_HOLD_MISSING_SEQ")
    relevant=("key","ply","parent_move_raw","hit") if pairs["kind"]=="probe" else (
        ("key","ply","parent_move_raw","best_value") if pairs["kind"]=="normal_return"
        else ("root_move_raw","root_value","root_depth"))
    if not all(k in pairs for k in relevant):
        raise ValueError("S4D_HOLD_INCOMPLETE_NATIVE_EVENT")
    return dict(pairs,raw=line)

def native(binary,fen,key):
    env=os.environ.copy()
    env["C3X_S4D_TARGET_KEY"]=str(key)
    p=subprocess.Popen([str(Path(binary).resolve())],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,text=True,bufsize=1,env=env)
    out=queue.Queue();errs=[]
    def drain(stream,callback):
        for line in stream:callback(line.rstrip("\n\r"))
    threads=[threading.Thread(target=drain,args=(p.stdout,out.put),daemon=True),
             threading.Thread(target=drain,args=(p.stderr,errs.append),daemon=True)]
    for t in threads:t.start()
    def send(cmd):
        p.stdin.write(cmd+"\n");p.stdin.flush()
    def until(start):
        seen=[]
        for _ in range(150000):
            try:line=out.get(timeout=60)
            except queue.Empty:raise ValueError("S4D_HOLD_ENGINE_TIMEOUT:"+start)
            seen.append(line)
            if line.startswith(start):return seen
        raise ValueError("S4D_HOLD_OUTPUT_FLOOD")
    try:
        send("uci");until("uciok")
        for line in ("setoption name Threads value 1","setoption name Hash value 16",
            "setoption name Use NNUE value false","setoption name Skill Level value 20",
            "setoption name UCI_LimitStrength value false","ucinewgame","isready"):
            send(line)
        until("readyok")
        results=[]
        for trial in range(2):
            send("position fen "+fen);send("go nodes 12000")
            lines=until("bestmove ")
            candidates=[v for v in lines if v.startswith("info ") and " score " in v and " pv " in v]
            if not candidates:raise ValueError("S4D_HOLD_MISSING_NATIVE_INFO")
            last=parse_info(candidates[-1])
            last["bestmove"]=lines[-1].split()[1]
            if not last["nodes"] or not last["depth"]:raise ValueError("S4D_HOLD_NO_SEARCH_NODES")
            results.append(last)
        send("quit");p.wait(timeout=15)
        for t in threads:t.join(timeout=10)
        if p.returncode!=0:raise ValueError("S4D_HOLD_NONZERO_NATIVE_EXIT")
        traces=[t for x in errs if (t:=parse_event(x))]
        other=[x for x in errs if not x.startswith("C3X_S4D ")]
        return {"trials":results,"trace_events":traces,"stderr_other":other[:20]}
    finally:
        if p.poll() is None:p.kill()
        try:p.wait(timeout=5)
        except subprocess.TimeoutExpired:pass

def correlate(traces,key):
    counts=Counter(z["kind"] for z in traces)
    probe=[x for x in traces if x["kind"]=="probe" and x["key"]==str(key) and x["hit"]=="1"]
    returns=[x for x in traces if x["kind"]=="normal_return" and x["key"]==str(key)]
    roots=[x for x in traces if x["kind"]=="root_candidate"]
    root_raw={x["root_move_raw"] for x in roots}
    return {
        "count_by_site":dict(counts),
        "target_hit_count":len(probe),"target_normal_return_count":len(returns),
        "root_candidate_logs":len(roots),
        "hit_parent_raw_values":sorted({p["parent_move_raw"] for p in probe}),
        "return_parent_raw_values":sorted({p["parent_move_raw"] for p in returns}),
        "raw_parent_move_also_observed_in_root_candidates":sorted(
            {p["parent_move_raw"] for p in probe if p["parent_move_raw"] in root_raw}),
        "raw_value_medation_PROVEN":False,
        "trace_is_complete_search_tree":False,
        "logging_covers_early_returns":False,
        "notes":"The raw move values identify compatible root candidates only; no dynamic edge or returned value propagation is asserted."}

def execute(previous,baseline,logger):
    if sha(previous)!=S4B_SHA:raise ValueError("S4D_HOLD_ORIGINAL_S4B_SHA")
    src=json.loads(Path(previous).read_bytes())
    if src.get("status")!="PASS_EXACT_NATIVE_SOURCE_HIT_MASK_WITH_CONTROLS":
        raise ValueError("S4D_HOLD_PARENT_SOURCE_STATUS")
    if src.get("unmodified_original_binary_sha256")!=sha(baseline):
        raise ValueError("S4D_HOLD_ORIGINAL_BINARY_SHA")
    if sha(baseline)==sha(logger):raise ValueError("S4D_HOLD_IDENTICAL_BINARY")
    report={"schema":SCHEMA,"source_commit":src["source_commit"],
            "prior_original_S4B_sha256":S4B_SHA,
            "baseline_binary_sha256":sha(baseline),
            "trace_binary_sha256":sha(logger),
            "read_only_instrumentation":True,
            "new_holdout_dataset":False,
            "actual_TT_intervention_in_this_experiment":False,
            "native_causal_mediator_proven":False,"positions":{}}
    for id in SOURCE_IDS:
        p=src["positions"][id];key=p["target_original_TT_key"]
        old=native(baseline,p["fen"],key)
        new=native(logger,p["fen"],key)
        audit=compare_records({"trials":old["trials"]}, {"trials":new["trials"],"events":[]})
        trace=correlate(new["trace_events"],key)
        report["positions"][id]={
            "fen":p["fen"],"original_chess_history_uci":p["history_uci"],
            "prior_first_hit_key":key,
            "unmodified_trials":old["trials"],
            "read_only_traced_trials":new["trials"],
            "noninterference_comparison":audit,"event_structure":trace,
            "source_raw_events":new["trace_events"],
            "other_stderr":new["stderr_other"]}
        print("S4D_REAL_NATIVE",id,"noninterference",audit["noninterference_pass"],
              "events",trace["count_by_site"],"candidate_overlap",
              len(trace["raw_parent_move_also_observed_in_root_candidates"]),flush=True)
    report["actual_native_searches"]=len(SOURCE_IDS)*2*2
    report["actual_native_nodes"]=sum(t["nodes"] for v in report["positions"].values()
        for arm in ("unmodified_trials","read_only_traced_trials") for t in v[arm])
    report["all_noninterference_pass"]=all(
        v["noninterference_comparison"]["noninterference_pass"]
        for v in report["positions"].values())
    report["all_three_trace_sites_observed"]=all(
        all(v["event_structure"]["count_by_site"].get(k,0)>0 for k in KINDS)
        for v in report["positions"].values())
    report["status"]=("PASS_PARTIAL_SOURCE_ANCESTRY_OBSERVATION_ONLY" if
        report["all_noninterference_pass"] and report["all_three_trace_sites_observed"]
        else "HOLD_INCOMPLETE_TRACE_OR_INTERFERING_SOURCE_LOG")
    return report

def main():
    p=argparse.ArgumentParser()
    for x in ("prior-original","baseline","logger","out"):p.add_argument("--"+x,required=True)
    a=vars(p.parse_args())
    r=execute(a["prior_original"],a["baseline"],a["logger"])
    dest=Path(a["out"]);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(r,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
    print("S4D_ACTUAL_SOURCE_ANCESTRY_COURT",r["status"],"SEARCHES",
        r["actual_native_searches"],"NODES",r["actual_native_nodes"],
        "SHA256",sha(dest),flush=True)
    if not r["status"].startswith("PASS_"):raise SystemExit(2)
if __name__=="__main__":main()
