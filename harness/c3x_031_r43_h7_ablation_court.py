#!/usr/bin/env python3
"""Frozen 16-mask screen: empty, full, all singletons, all leave-one-out.
Both receivers, fixed depth15, two cold repeats. Not exhaustive of H7.
"""
import argparse
import gzip
import json
from pathlib import Path
from c3x_030_r23_native_replay import run
from c3x_030_r33_gate_panel import events
from c3x_031_r40_checkpoint_tt_court import HIST, NET, digest, require, fields
from c3x_031_r42_history_rescue_court import SNAP,H7,expected_image,endpoints,root_trace

MASKS=tuple(sorted({0,127,*[1<<i for i in range(7)],*[127^(1<<i) for i in range(7)]}))
NAT={"sham":("2265","2238","0","d4e5"),"both":("2280","2256","1","f4e5")}

def signature(ep,best):
    if not all(x["aligned"] for x in ep.values()): return None
    y1,y2=ep["Y1"]["candidate"],ep["Y2"]["candidate"]
    return (y1["value"],y2["value"],y2["update"],best["move"])

def main():
    p=argparse.ArgumentParser()
    for n in ("history","net","observer","donors","output"):p.add_argument(n,type=Path)
    a=p.parse_args()
    require(digest(a.history)==HIST and digest(a.net)==NET,"source")
    case=next(r for r in json.loads(a.history.read_text())["sample"] if r["id"]=="P2-028")
    a.output.mkdir(parents=True,exist_ok=True)
    orig={k:next(a.donors.rglob(f"d15-{k}-on0/r41_snapshot.bin")) for k in SNAP}
    for k,f in orig.items(): require(digest(f)==SNAP[k],"snapshot SHA")
    result={}
    completed=0
    for mask in MASKS:
        keys=tuple(k for i,k in enumerate(H7) if mask&(1<<i))
        for name,skip in (("sham",0),("both",1)):
            other="both" if name=="sham" else "sham"
            receiver,donor=orig[name],orig[other]
            base_lines=(receiver.parent/"stderr.txt").read_text().splitlines()
            image=expected_image(receiver.read_bytes(),donor.read_bytes(),keys)
            repeats=[]
            for rep in (0,1):
                folder=a.output/f"m{mask:03}-{name}-{rep}"
                env={"C3X_R33_OBSERVE":"1","C3X_R33_TARGET":"19",
                     "C3X_R33_SKIP_FUTILITY":str(skip),"C3X_R33_SKIP_NULL":str(skip),
                     "C3X_R29_PROBES":"0","C3X_R31_OBSERVE":"0","C3X_NO_TT_PICKER":"0",
                     "C3X_NO_TT_VALUE":"0","C3X_R29_MASK_MOVE":"0","C3X_R29_MASK_VALUE":"0",
                     "C3X_R41_HISTORY":"1","C3X_R42_MODE":"mask","C3X_R43_MASK":str(mask),
                     "C3X_R42_RECEIVER":str(receiver.resolve()),"C3X_R42_DONOR":str(donor.resolve())}
                uci,proof=run(a.observer,{"history":case["moves"]},a.net,folder,logging=True,
                              paired=False,nnue=True,depth=15,environment=env)
                completed+=1
                lines=(folder/"stderr.txt").read_text().splitlines()
                require((folder/"r41_snapshot.bin").read_bytes()==image,"post-splice bytes")
                require([fields(l) for l in lines if l.startswith("C3X_R43_RESTORE ")]==
                        [{"mask":str(mask),"cells":str(len(keys))}],"mask marker")
                match=[x for x in events(lines) if x["open"]["event"]=="19"]
                require(len(match)==1 and match[0]["open"]["key"]=="18244396700095567446"
                        and match[0]["open"]["nodes"]=="7477"
                        and match[0]["close"]["value"]==("-2500" if skip else "-2429"),"event identity")
                require(proof["best"]["completed"]=="15","depth")
                cp=next(fields(l) for l in lines if l.startswith("C3X_R41_CP "))
                require(cp["nodes"]==("7717" if skip else "7699") and cp["completed"]=="13"
                        and cp["root_depth"]=="14" and cp["alpha"]=="2025" and cp["beta"]=="2771","checkpoint")
                ep=endpoints(lines)
                sig=signature(ep,proof["best"])
                if mask==0:
                    require(root_trace(lines)==root_trace(base_lines) and sig==NAT[name],"empty control")
                if mask==127:require(sig==NAT[other],"full control")
                row={"signature":sig,"endpoints":ep,"best":proof["best"],"checkpoint":cp,
                     "trace":root_trace(lines),"uci":uci,"events_sha256":digest(folder/"r41_events.txt"),
                     "snapshot_sha256":digest(folder/"r41_snapshot.bin")}
                repeats.append(row)
                # Preserve all original bytes losslessly; avoid large uncompressed CI artifacts.
                for filename in ("r41_events.txt","r41_snapshot.bin"):
                    f=folder/filename
                    with gzip.GzipFile(filename=str(f)+".gz",mode="wb",compresslevel=3,mtime=0) as g:
                        g.write(f.read_bytes())
                    f.unlink()
            require(repeats[0]==repeats[1],"cold repeat mismatch")
            row=repeats[0]
            row.pop("trace");row.pop("uci")
            row["donor_exact"]=row["signature"]==NAT[other]
            row["receiver_exact"]=row["signature"]==NAT[name]
            result[f"{mask}/{name}"]=row
            print("R43_RESULT",mask,name,json.dumps({"sig":row["signature"],"best":row["best"],
                  "donor_exact":row["donor_exact"],"receiver_exact":row["receiver_exact"]},sort_keys=True),flush=True)
    reciprocal=[m for m in MASKS if all(result[f"{m}/{n}"]["donor_exact"] for n in NAT)]
    receipt={"native_searches":completed,"depth":15,"masks":MASKS,"bit_order":H7,
             "reciprocal_exact_masks":reciprocal,"rows":result,"observer_sha256":digest(a.observer),
             "scope":"screen only; one exposed game; no generalization; empty+singletons can certify cardinality-one minimum within H7 if a singleton succeeds"}
    require(completed==64,"denominator")
    (a.output/"R43_AGGREGATE.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("R43_RECIPROCAL",json.dumps(reciprocal),flush=True)
if __name__=="__main__":main()
