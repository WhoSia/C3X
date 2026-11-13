#!/usr/bin/env python3
"""S4-H2 source-only eligible TT-hit discovery; no score/PV/bestmove parsing.

All registered FENs stay in the denominator, including ineligible FENs.
The program does not read any root value from stdout; only detects the
'bestmove ' protocol terminator to know that a search finished.
"""
import argparse, hashlib, json, os, queue, re, subprocess, threading
from pathlib import Path

EVENT=re.compile(r"^C3X_S4H2_ELIGIBLE ordinal=(\d+) key=(\d+) ply=1 hit_before=1$")
MAX_KEY=(1<<64)-1

def choose(lines):
    matched=[]
    for line in lines:
        if not line.startswith("C3X_S4H2_ELIGIBLE"):continue
        m=EVENT.fullmatch(line)
        if m is None:raise ValueError("S4H2_ELIGIBILITY_MALFORMED_EVENT")
        ordinal,key=map(int,m.groups())
        if ordinal>=4096 or key<=0 or key>MAX_KEY:
            raise ValueError("S4H2_ELIGIBILITY_BAD_ORDINAL_OR_KEY")
        if ordinal!=len(matched):
            raise ValueError("S4H2_ELIGIBILITY_GAP_OR_DUPLICATE")
        matched.append(key)
    return {"eligible": bool(matched),
            "frozen_key":str(matched[0]) if matched else None,
            "source_hit_events_logged":len(matched),
            "source_hits_truncated_possible":len(matched)==4096,
            "selection_only_uses_pre_mask_source_keys":True}

def probe(binary,fen):
    env=os.environ.copy()
    env["C3X_S4H2_ELIGIBILITY_MODE"]="1"
    env["C3X_S4G_MASK_KEY"]="0"
    env["C3X_S4G_MASK_LIMIT"]="0"
    env["C3X_S4E_KEY"]="0"
    p=subprocess.Popen([str(Path(binary).resolve())],stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,env=env)
    stdout=queue.Queue()
    stderr=[]
    def pump(out,callback):
        for line in out:callback(line.rstrip("\r\n"))
    threads=[
      threading.Thread(target=pump,args=(p.stdout,stdout.put),daemon=True),
      threading.Thread(target=pump,args=(p.stderr,stderr.append),daemon=True)]
    for t in threads:t.start()
    def send(msg):
        p.stdin.write(msg+"\n")
        p.stdin.flush()
    def until(prefix):
        for _ in range(100001):
            try:line=stdout.get(timeout=45)
            except queue.Empty:raise ValueError("S4H2_ELIGIBILITY_ENGINE_TIMEOUT")
            # Never store bestmove, PV, score or info lines, nor use their values.
            if line.startswith(prefix):return
        raise ValueError("S4H2_ELIGIBILITY_UCI_FLOOD")
    try:
        send("uci");until("uciok")
        for cmd in ("setoption name Threads value 1",
                    "setoption name Hash value 16",
                    "setoption name Use NNUE value false",
                    "setoption name Skill Level value 20",
                    "setoption name UCI_LimitStrength value false",
                    "ucinewgame","isready"):
            send(cmd)
        until("readyok")
        for _ in range(2):
            send("position fen "+fen)
            send("go nodes 12000")
            until("bestmove ")
        send("quit")
        p.wait(timeout=20)
        for t in threads:t.join(timeout=5)
        if p.returncode:raise ValueError("S4H2_ELIGIBILITY_ENGINE_NONZERO")
        other=[line for line in stderr if line and not line.startswith("C3X_S4H2_ELIGIBLE")]
        if other:
            raise ValueError("S4H2_ELIGIBILITY_UNEXPECTED_STDERR")
        return choose(stderr)
    finally:
        if p.poll() is None:
            p.kill()
            p.wait(timeout=5)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--binary",required=True)
    p.add_argument("--protocol",required=True)
    p.add_argument("--split",choices=("development","holdout"),required=True)
    p.add_argument("--max-cases",type=int,default=0)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    raw=Path(a.protocol).read_bytes()
    protocol=json.loads(raw)
    if protocol.get("schema")!="c3x030-s4h2-preoutcome-native-execution-protocol-v1":
        raise ValueError("S4H2_ELIGIBILITY_PROTOCOL_SCHEMA")
    cases=[r for r in protocol["cases"] if r["split"]==a.split]
    if a.max_cases < 0:raise ValueError("S4H2_ELIGIBILITY_NEGATIVE_MAX")
    if a.max_cases:cases=cases[:a.max_cases]
    outcomes=[]
    for c in cases:
        discovery=probe(a.binary,c["fen"])
        outcomes.append({"case_id":c["case_id"],"game_id":c["game_id"],
                         "split":c["split"],**discovery})
        print("S4H2_ELIGIBILITY",c["case_id"],"eligible",discovery["eligible"],
              "events",discovery["source_hit_events_logged"],flush=True)
    result={"schema":"c3x030-s4h2-source-only-eligibility-receipts-v1",
      "protocol_sha256":hashlib.sha256(raw).hexdigest(),
      "binary_sha256":hashlib.sha256(Path(a.binary).read_bytes()).hexdigest(),
      "split":a.split,"cases":outcomes,
      "source_probes_only":True,"engine_scores_read":False,
      "engine_bestmove_read":False,"engine_pv_read":False,
      "new_engine_searches":2*len(outcomes),
      "treatment_searches":0,"no_causal_effect_or_superiority_claim":True}
    dest=Path(a.out)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("S4H2_OUTCOME_BLIND_ELIGIBILITY",len(outcomes),result["new_engine_searches"])

if __name__=="__main__":main()
