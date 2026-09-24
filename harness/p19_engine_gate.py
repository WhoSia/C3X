#!/usr/bin/env python3
import argparse,json,re,subprocess
from pathlib import Path

FIELDS=("bestmove","score","wdl","pv")

def parse_bins(items):
    out={}
    for x in items:
        k,p=x.split("=",1); out[k]=p
    if not out: raise SystemExit("need at least one --binary label=path")
    return out

def run(binary,mode,nodes):
    fen="8/8/3k4/8/3K4/8/4R3/8 w - - 0 1"
    p=subprocess.Popen([binary],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
    cmds=["uci",f"setoption name C3X_TTReadMode value {mode}",
          "setoption name C3X_Telemetry value true",
          "setoption name Threads value 1","setoption name Hash value 64",
          "setoption name SyzygyProbeLimit value 0","setoption name UCI_ShowWDL value true",
          "setoption name Clear Hash","isready",f"position fen {fen}",f"go nodes {nodes}"]
    for c in cmds: p.stdin.write(c+"\n")
    p.stdin.flush(); lines=[]
    for line in p.stdout:
        line=line.rstrip("\n"); lines.append(line)
        if line.startswith("bestmove "): break
    p.terminate()
    try: rest,_=p.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        p.kill(); rest,_=p.communicate(timeout=5)
    if rest: lines.extend(rest.splitlines())
    best=next((x for x in reversed(lines) if x.startswith("bestmove ")),None)
    infos=[x for x in lines if x.startswith("info depth ") and " score " in x and " pv " in x]
    tel=next((x for x in lines if x.startswith("info string c3x_ttread_v1 ")),None)
    if not best or not infos or not tel:
        raise RuntimeError("incomplete C3X receipt\n"+"\n".join(lines[-80:]))
    final=infos[-1]; bt=best.split()
    def grab(pat):
        m=re.search(pat,final); return m.group(1) if m else None
    return {"bestmove":bt[1],"score":grab(r"\bscore ((?:cp|mate) -?\d+)"),
            "wdl":grab(r"\bwdl (\d+ \d+ \d+)"),"pv":grab(r"\bpv (.+)$"),
            "telemetry_line":tel}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--binary",action="append",required=True)
    ap.add_argument("--nodes",type=int,default=30000)
    ap.add_argument("--out")
    a=ap.parse_args(); bins=parse_bins(a.binary); out={}
    for label,path in bins.items():
        ma=run(path,"MASK_ALL",a.nodes); legacy=run(path,"MASKED",a.nodes)
        same=all(ma[f]==legacy[f] for f in FIELDS)
        out[label]={"full_mask_equivalence":same,
                    "mask_all":{f:ma[f] for f in FIELDS},
                    "masked":{f:legacy[f] for f in FIELDS},
                    "telemetry_namespace_ok":ma["telemetry_line"].startswith("info string c3x_ttread_v1 ")}
        if not same or not out[label]["telemetry_namespace_ok"]:
            raise SystemExit("P19-ENGINE-GATE-FAIL "+label)
    payload={"schema":"c3x-p19-engine-lineage-gate-v1","verdict":"PASS","targets":out}
    s=json.dumps(payload,indent=2,sort_keys=True)
    if a.out:
        Path(a.out).parent.mkdir(parents=True,exist_ok=True); Path(a.out).write_text(s+"\n")
    print(s)

if __name__=="__main__": main()
