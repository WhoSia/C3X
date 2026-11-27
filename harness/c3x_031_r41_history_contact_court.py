#!/usr/bin/env python3
"""Observed scalar-history contact at the frozen P3-B checkpoint; no rescue."""
import argparse
from array import array
from collections import Counter
import json
import sys
from pathlib import Path

from c3x_030_r23_native_replay import run
from c3x_030_r33_gate_panel import events
from c3x_031_r40_checkpoint_tt_court import HIST, NET, R33, digest, require, fields

LAYOUT={"main":(8192,2),"capture":(8192,2),"cont":(4194304,2),"counter":(1024,4)}

def snapshot(folder):
    require(sys.byteorder=="little","R41 little-endian build only")
    expected=list(LAYOUT.items())
    rows=[line.split() for line in (folder/"r41_layout.txt").read_text().splitlines()]
    require([(n,(int(size)//int(width),int(width))) for n,size,width in rows]==expected,"layout drift")
    with (folder/"r41_snapshot.bin").open("rb") as f:
        result={}
        for n,(count,width) in expected:
            a=array("h" if width==2 else "i")
            require(a.itemsize==width,"scalar ABI")
            a.fromfile(f,count)
            result[n]=a
        require(f.read(1)==b"","snapshot trailing bytes")
    return result

def contact(folder, lines, expected_y1):
    initial=snapshot(folder)
    current={n:a[:] for n,a in initial.items()}
    cp=[fields(l) for l in lines if l.startswith("C3X_R41_CP ")]
    end=[fields(l) for l in lines if l.startswith("C3X_R41_END ")]
    require(len(cp)==len(end)==1,"missing checkpoint")
    p=cp[0]
    require(p["attempt"]=="17" and p["root_depth"]=="14" and p["completed"]=="13"
            and p["alpha"]=="2025" and p["beta"]=="2771","wrong physical boundary")
    counts=Counter()
    first={}
    written=set()
    draws=[]
    y1=None
    total=0
    with (folder/"r41_events.txt").open() as f:
        for line in f:
            serial,n,idx,op,val=line.split()
            total+=1
            require(int(serial)==total,"lost event")
            idx,val=int(idx),int(val)
            if op=="E":
                require(n=="endpoint" and y1 is None and val==expected_y1,"wrong Y1")
                y1=total
                continue
            if op=="D":
                require(n=="draw" and val==-1+(idx&2),"draw arithmetic drift")
                if y1 is None: draws.append((idx,val))
                continue
            require(n in current and op in ("R","U","W") and 0<=idx<len(current[n]),"unmapped scalar or pointer escape")
            token=(n,idx)
            if op in ("R","U"):
                require(current[n][idx]==val,"read differs from snapshot/write replay")
                if y1 is None and token not in written:
                    # R: native conversion; U: arithmetic read inside update.
                    first.setdefault((n,idx,op),total)
            else:
                current[n][idx]=val
                if y1 is None: written.add(token)
            if y1 is None: counts[n,op]+=1
    require(total==int(end[0]["accesses"]) and y1 is not None,"incomplete trace")
    return {"initial":initial,"first":first,"counts":counts,"draws":draws,"cp":p,"y1":y1,"total":total}

def compare(a,b):
    out={}
    for n in LAYOUT:
        diff={i for i,(x,y) in enumerate(zip(a["initial"][n],b["initial"][n])) if x!=y}
        row={"different_cells":len(diff)}
        for name,arm in (("sham",a),("both",b)):
            row[name]={}
            for op in ("R","U"):
                seen=[(i,s) for (family,i,k),s in arm["first"].items() if family==n and k==op and i in diff]
                earliest=min(seen,key=lambda x:x[1]) if seen else None
                row[name][op]={"count":len(seen),"first":None if earliest is None else
                    {"index":earliest[0],"serial":earliest[1],"sham_value":a["initial"][n][earliest[0]],"both_value":b["initial"][n][earliest[0]]}}
        out[n]=row
    return {"families":out,"draw_calls_before_y1":{"sham":len(a["draws"]),"both":len(b["draws"])},
            "draw_values_before_y1":{"sham":dict(Counter(v for _,v in a["draws"])),"both":dict(Counter(v for _,v in b["draws"]))},
            "counts_before_y1":{k:{f"{n}:{op}":v for (n,op),v in x["counts"].items()} for k,x in (("sham",a),("both",b))},
            "total_access_events":{"sham":a["total"],"both":b["total"]}}

def main():
    p=argparse.ArgumentParser()
    for name in ("history","net","baseline","observer","output"): p.add_argument(name,type=Path)
    a=p.parse_args()
    require(digest(a.history)==HIST and digest(a.net)==NET and digest(a.baseline)==R33,"source identity")
    case=next(r for r in json.loads(a.history.read_text())["sample"] if r["id"]=="P2-028")
    a.output.mkdir(parents=True,exist_ok=True)
    receipts={}
    for depth in (15,16):
        logs={}
        for name,skip in (("sham",0),("both",1)):
            parity=[]
            repeats=[]
            for label,binary,on in (("base",a.baseline,0),("off",a.observer,0),("on0",a.observer,1),("on1",a.observer,1)):
                folder=a.output/f"d{depth}-{name}-{label}"
                env={"C3X_R33_OBSERVE":"1","C3X_R33_TARGET":"19",
                     "C3X_R33_SKIP_FUTILITY":str(skip),"C3X_R33_SKIP_NULL":str(skip),
                     "C3X_R29_PROBES":"0","C3X_R31_OBSERVE":"0","C3X_NO_TT_PICKER":"0","C3X_NO_TT_VALUE":"0",
                     "C3X_R29_MASK_MOVE":"0","C3X_R29_MASK_VALUE":"0","C3X_R41_HISTORY":str(on)}
                uci,proof=run(binary,{"history":case["moves"]},a.net,folder,logging=True,paired=False,nnue=True,depth=depth,environment=env)
                lines=(folder/"stderr.txt").read_text().splitlines()
                match=[x for x in events(lines) if x["open"]["event"]=="19"]
                require(len(match)==1 and match[0]["open"]["key"]=="18244396700095567446"
                        and match[0]["open"]["nodes"]=="7477"
                        and match[0]["close"]["value"]==("-2500" if skip else "-2429"),"target drift")
                require(proof["best"]["completed"]==str(depth),"incomplete depth")
                parity.append((uci,proof,[l for l in lines if l.startswith(("C3X_R23_","C3X_R33_"))]))
                if on:
                    repeats.append(contact(folder,lines,2280 if skip else 2265))
                else:
                    require(not (folder/"r41_events.txt").exists(),"off trace leakage")
            require(all(x==parity[0] for x in parity[1:]),"native observer changed result")
            require(repeats[0]==repeats[1],"cold contact mismatch")
            logs[name]=repeats[0]
            print("R41_PARITY",depth,name,"accesses",repeats[0]["total"],flush=True)
        receipts[str(depth)]=compare(logs["sham"],logs["both"])
    result={"native_searches":16,"scope":"one exposed source game, two dependent depth prefixes; scalar history only; no physical transplant",
            "cases":receipts,"observer_sha256":digest(a.observer),"mediator_sufficiency":"HOLD"}
    (a.output/"R41_AGGREGATE.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True),flush=True)

if __name__=="__main__":main()
