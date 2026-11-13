#!/usr/bin/env python3
"""S4E source native invocation-link pilot, no mediator claim.

Three SHA-frozen S4B developer chess positions; original vs read-only C++
invocation stack source. Real per-process IDs, parent IDs, probe/normal-return/
scope-exit/root-candidate records, and explicit bounded truncation caveat.
"""
import argparse,hashlib,json,os,queue,re,subprocess,threading
from collections import Counter
from pathlib import Path
from c3x_030_p11s4a_native_trace_court import parse_info,compare_records

SOURCE_SHA="081ee839f883d538081f1d2d15c43db1aa31cb12e4e713e1cda81815d5e59300"
SCHEMA="c3x030-p11s4e-native-invocation-parent-trace-v1"
SOURCE_POS=("queens_gambit_ply4","sicilian_najdorf_ply4","english_ply4")
KINDS=("probe","normal_return","scope_exit","root_candidate")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def parse_event(line):
    if not line.startswith("C3X_S4E "):return None
    pairs=dict(re.findall(r"([a-z_]+)=(-?[0-9]+|[a-z_]+)",line))
    if pairs.get("kind") not in KINDS:raise ValueError("S4E_HOLD_UNRECOGNIZED_SOURCE_EVENT")
    if "id" not in pairs:raise ValueError("S4E_HOLD_MISSING_INVOCATION_ID")
    if pairs["kind"]!="root_candidate" and ("parent" not in pairs or "ply" not in pairs):
        raise ValueError("S4E_HOLD_MISSING_PARENT_LINK")
    return dict(pairs,raw=line)

def search(binary,fen,key):
    env=os.environ.copy();env["C3X_S4E_KEY"]=str(key)
    p=subprocess.Popen([str(Path(binary).resolve())],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,env=env,text=True,bufsize=1)
    q=queue.Queue();err=[]
    def reader(stream,store):
        for line in stream:store(line.rstrip("\r\n"))
    threads=(threading.Thread(target=reader,args=(p.stdout,q.put),daemon=True),
             threading.Thread(target=reader,args=(p.stderr,err.append),daemon=True))
    for t in threads:t.start()
    def send(x):p.stdin.write(x+"\n");p.stdin.flush()
    def read_until(marker):
        lines=[]
        while True:
            try:line=q.get(timeout=45)
            except queue.Empty:raise ValueError("S4E_HOLD_NATIVE_RESPONSE_TIMEOUT")
            lines.append(line)
            if line.startswith(marker):return lines
            if len(lines)>100000:raise ValueError("S4E_HOLD_UCI_OUTPUT_FLOOD")
    try:
        send("uci");read_until("uciok")
        for v in ("setoption name Threads value 1","setoption name Hash value 16",
                  "setoption name Use NNUE value false","setoption name Skill Level value 20",
                  "setoption name UCI_LimitStrength value false","ucinewgame","isready"):send(v)
        read_until("readyok")
        results=[]
        for trial in range(2):
            send("position fen "+fen);send("go nodes 12000")
            lines=read_until("bestmove ")
            native_info=[x for x in lines if x.startswith("info ") and " score " in x and " pv " in x]
            if not native_info:raise ValueError("S4E_HOLD_NATIVE_INFO")
            z=parse_info(native_info[-1]);z["bestmove"]=lines[-1].split()[1]
            if not z["nodes"] or not z["depth"]:raise ValueError("S4E_HOLD_REAL_WORK")
            results.append(z)
        send("quit");p.wait(timeout=15)
        for t in threads:t.join(timeout=5)
        if p.returncode:raise ValueError("S4E_HOLD_ENGINE_FAILURE")
        other_limit = 4096 if env.get("C3X_S4K_CAPTURE_FULL_STDERR") == "1" else 20
        return {"trials":results,"events":[x for z in err if (x:=parse_event(z))],
                "other_stderr":[z for z in err if not z.startswith("C3X_S4E ")][:other_limit]}
    finally:
        if p.poll() is None:p.kill()
        try:p.wait(timeout=5)
        except subprocess.TimeoutExpired:pass

def inspect(events):
    by_id={}
    counts=Counter()
    for e in events:
        counts[e["kind"]]+=1
        id=e["id"]
        rec=by_id.setdefault(id,{"kinds":[],"parent_ids":[],"returns":[]})
        rec["kinds"].append(e["kind"])
        if "parent" in e:rec["parent_ids"].append(e["parent"])
        if e["kind"]=="normal_return":rec["returns"].append(e["value"])
    if not counts["probe"] or not counts["root_candidate"]:
        raise ValueError("S4E_HOLD_SOURCE_SIGNAL_NOT_OBSERVED")
    inconsistent={k:v["parent_ids"] for k,v in by_id.items()
                  if len(set(v["parent_ids"]))>1}
    if inconsistent:raise ValueError("S4E_HOLD_INCONSISTENT_PARENT_BY_INVOCATION")
    normal_with_probe=sum("probe" in x["kinds"] and "normal_return" in x["kinds"]
                          for x in by_id.values())
    exits_with_probe=sum("probe" in x["kinds"] and "scope_exit" in x["kinds"]
                         for x in by_id.values())
    # Cap means some emitted events are incomplete. Never mislabel missing as no event.
    return {"counts":dict(counts),"unique_logged_invocations":len(by_id),
            "normal_returns_with_same_invocation_probe":normal_with_probe,
            "scoped_exits_with_same_invocation_probe":exits_with_probe,
            "source_log_capped_per_process":True,
            "actual_complete_search_tree":False,
            "root_candidate_last_child_is_proven_value_source":False,
            "causal_parent_return_mediation_proven":False}

def execute(original_json,original_binary,logger_binary):
    if sha(original_json)!=SOURCE_SHA:raise ValueError("S4E_HOLD_ORIGINAL_S4B_RAW_SHA")
    src=json.loads(Path(original_json).read_bytes())
    if src.get("status")!="PASS_EXACT_NATIVE_SOURCE_HIT_MASK_WITH_CONTROLS":
        raise ValueError("S4E_HOLD_ORIGINAL_SOURCE_STATUS")
    if src["unmodified_original_binary_sha256"]!=sha(original_binary):
        raise ValueError("S4E_HOLD_BASELINE_BINARY_DRIFT")
    if sha(original_binary)==sha(logger_binary):
        raise ValueError("S4E_HOLD_SAME_BINARIES")
    report={"schema":SCHEMA,"prior_source_sha":SOURCE_SHA,
            "original_stockfish_binary_sha":sha(original_binary),
            "instrumented_binary_sha":sha(logger_binary),
            "no_native_intervention":True,"not_independent_cohort":True,
            "causal_return_to_root_proven":False,"positions":{}}
    for pos in SOURCE_POS:
        info=src["positions"][pos]
        base=search(original_binary,info["fen"],info["target_original_TT_key"])
        log=search(logger_binary,info["fen"],info["target_original_TT_key"])
        match=compare_records({"trials":base["trials"]},dict(trials=log["trials"],events=[]))
        audit=inspect(log["events"])
        report["positions"][pos]={"fen":info["fen"],"history_uci":info["history_uci"],
          "original_target_key":info["target_original_TT_key"],
          "original":base["trials"],"logged":log["trials"],
          "noninterference":match["noninterference_pass"],"trace_audit":audit,
          "events":log["events"],"other_stderr":log["other_stderr"]}
        print("S4E_REAL_INVOCATION",pos,"noninterference",match["noninterference_pass"],
              "audit",audit,flush=True)
    report["native_searches"]=len(SOURCE_POS)*2*2
    report["actual_native_nodes"]=sum(row["nodes"] for p in report["positions"].values()
        for group in ("original","logged") for row in p[group])
    report["noninterference_pass"]=all(p["noninterference"] for p in report["positions"].values())
    report["some_probes_linked_to_same_invocation_returns"]=all(
        p["trace_audit"]["normal_returns_with_same_invocation_probe"]>0
        for p in report["positions"].values())
    report["status"]=("PASS_INCOMPLETE_INVOCATION_TRACE" if
        report["noninterference_pass"] and report["some_probes_linked_to_same_invocation_returns"]
        else "HOLD_SOURCE_LOGGER_INTERFERENCE_OR_MISSING_LINK")
    return report

def main():
    ap=argparse.ArgumentParser()
    for a in ("prior-original","baseline","logger","out"):ap.add_argument("--"+a,required=True)
    z=vars(ap.parse_args());d=execute(z["prior_original"],z["baseline"],z["logger"])
    f=Path(z["out"]);f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
    print("S4E_NATIVE_COURT",d["status"],"SEARCHES",d["native_searches"],
          "NODES",d["actual_native_nodes"],"SHA256",sha(f),flush=True)
    if not d["status"].startswith("PASS_"):raise SystemExit(2)
if __name__=="__main__":main()
