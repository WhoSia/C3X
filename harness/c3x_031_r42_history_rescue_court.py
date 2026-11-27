#!/usr/bin/env python3
"""R42 sparse conditional rescue: two reciprocal directions, self-copy, placebo.
Frozen R41 contact cells; exact receiver and donor raw images; no node reset.
"""
import argparse
import json
import re
from pathlib import Path
from c3x_030_r23_native_replay import run
from c3x_030_r33_gate_panel import events
from c3x_031_r40_checkpoint_tt_court import HIST, NET, digest, require, fields

SNAP={"sham":"b79d1e09960d0129c7754fd01feebdaa48178121512b850e1c8a90c4526d4cd6",
      "both":"df436ffc49e785cadea02cbf632ca6cb4ce5e89bca286a972d9f339fc1d04629"}
H7=(("main",6556),("main",7738),("cont",1427258),("cont",1741626),
    ("cont",1743516),("cont",1743674),("counter",369))
P2=(("cont",1427100),("cont",1741468))
LAYOUT={"main":(0,8192,2),"capture":(16384,8192,2),"cont":(32768,4194304,2),
        "counter":(8421376,1024,4)}

def expected_image(a,b,keys):
    require(len(a)==len(b)==8425472,"snapshot length")
    x=bytearray(a)
    for n,i in keys:
        start,count,w=LAYOUT[n]
        require(0<=i<count,"cell index")
        off=start+i*w
        x[off:off+w]=b[off:off+w]
    return bytes(x)

def endpoints(lines):
    starts={int(x["attempt"]):x for l in lines if l.startswith("C3X_R23_START ") for x in [fields(l)]}
    candidates=[fields(l) for l in lines if l.startswith("C3X_R23_CANDIDATE ")]
    out={}
    for attempt,depth,alpha,label in ((17,14,2289,"Y1"),(18,15,None,"Y2")):
        found=[x for x in candidates if x["attempt"]==str(attempt) and x["move"]=="f4e5"]
        s=starts.get(attempt,{})
        # R23 uses iteration, not adjusted depth, for the physical root iteration.
        aligned=len(found)==1 and s.get("iteration")==str(depth)
        if label=="Y1": aligned=aligned and found[0].get("alpha")==str(alpha) if found else False
        if label=="Y2": aligned=aligned and s.get("alpha")=="1973" and s.get("beta")=="2677"
        out[label]={"aligned":bool(aligned),"candidate":found[0] if len(found)==1 else None,"start":s}
    return out

def root_trace(lines): return [l for l in lines if l.startswith(("C3X_R23_","C3X_R33_"))]

def main():
    p=argparse.ArgumentParser()
    for n in ("history","net","observer","donors","output"): p.add_argument(n,type=Path)
    a=p.parse_args()
    require(digest(a.history)==HIST and digest(a.net)==NET,"input source identity")
    case=next(r for r in json.loads(a.history.read_text())["sample"] if r["id"]=="P2-028")
    a.output.mkdir(parents=True,exist_ok=True)
    result={}
    completed=0
    for depth in (15,16):
        original={k:next(a.donors.rglob(f"d{depth}-{k}-on0/r41_snapshot.bin")) for k in SNAP}
        for k,f in original.items(): require(digest(f)==SNAP[k],"donor SHA")
        for name,skip in (("sham",0),("both",1)):
            receiver=original[name]
            donor=original["both" if name=="sham" else "sham"]
            base_lines=(receiver.parent/"stderr.txt").read_text().splitlines()
            base_endpoint=endpoints(base_lines)
            require(all(x["aligned"] for x in base_endpoint.values()),"archived endpoint identity")
            parent=receiver.read_bytes()
            other=donor.read_bytes()
            for mode,source,keys in (("self",receiver,H7),("H7",donor,H7),("P2",donor,P2)):
                image=expected_image(parent,source.read_bytes(),keys)
                repeats=[]
                for rep in (0,1):
                    folder=a.output/f"d{depth}-{name}-{mode}-{rep}"
                    env={"C3X_R33_OBSERVE":"1","C3X_R33_TARGET":"19","C3X_R33_SKIP_FUTILITY":str(skip),
                         "C3X_R33_SKIP_NULL":str(skip),"C3X_R29_PROBES":"0","C3X_R31_OBSERVE":"0",
                         "C3X_NO_TT_PICKER":"0","C3X_NO_TT_VALUE":"0","C3X_R29_MASK_MOVE":"0",
                         "C3X_R29_MASK_VALUE":"0","C3X_R41_HISTORY":"1","C3X_R42_MODE":mode,
                         "C3X_R42_RECEIVER":str(receiver.resolve()),"C3X_R42_DONOR":str(source.resolve())}
                    uci,proof=run(a.observer,{"history":case["moves"]},a.net,folder,logging=True,
                                  paired=False,nnue=True,depth=depth,environment=env)
                    completed+=1
                    lines=(folder/"stderr.txt").read_text().splitlines()
                    require((folder/"r41_snapshot.bin").read_bytes()==image,"post-restore entire image mismatch")
                    marker=[fields(l) for l in lines if l.startswith("C3X_R42_RESTORE ")]
                    require(marker==[{"mode":mode,"cells":str(len(keys))}],"restore marker")
                    match=[x for x in events(lines) if x["open"]["event"]=="19"]
                    require(len(match)==1 and match[0]["open"]["key"]=="18244396700095567446"
                            and match[0]["open"]["nodes"]=="7477"
                            and match[0]["close"]["value"]==("-2500" if skip else "-2429"),"event drift")
                    require(proof["best"]["completed"]==str(depth),"depth drift")
                    if mode=="self": require(root_trace(lines)==root_trace(base_lines),"self copy changed root trace")
                    row={"endpoints":endpoints(lines),"best":proof["best"],"trace":root_trace(lines),"uci":uci,
                         "checkpoint":next(fields(l) for l in lines if l.startswith("C3X_R41_CP "))}
                    require(row["checkpoint"]["nodes"]==("7717" if skip else "7699"),"node accounting changed before checkpoint")
                    repeats.append(row)
                require(repeats[0]==repeats[1],"cold restore repeat mismatch")
                row=repeats[0]
                # retain full raw files outside compact summary.
                row.pop("trace"); row.pop("uci")
                row["own_natural"]=base_endpoint
                result[f"{depth}/{name}/{mode}"]=row
                print("R42_RESULT",depth,name,mode,json.dumps(row,sort_keys=True),flush=True)
    receipt={"native_searches":completed,"cells_contact":H7,"cells_placebo":P2,
             "observer_sha256":digest(a.observer),"results":result,
             "scope":"conditional scalar H7 intervention, one exposed source; no node-counter reset, no unique mediator claim"}
    require(completed==24,"denominator")
    (a.output/"R42_AGGREGATE.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
if __name__=="__main__":main()
