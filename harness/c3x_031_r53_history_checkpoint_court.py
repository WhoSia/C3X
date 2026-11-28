#!/usr/bin/env python3
"""R53: matched checkpoint read/write replay, two R51 cases. Four fresh searches.
Contacts are candidate mediators, not causal proof. No private raw logs in public output.
"""
import argparse,json
from collections import Counter
from pathlib import Path
from c3x_031_r47_frozen_discovery import load_frozen,sha,require,NET,BIN
from c3x_031_r48_new_cohort_intervention import DISCOVERY
from c3x_031_r51_root_guard_contrast import R48
from c3x_030_r23_native_replay import run,records
from c3x_030_r33_gate_panel import events
from c3x_031_p2_treatment import matched
from c3x_031_r41_history_contact_court import snapshot,compare
from c3x_031_r40_checkpoint_tt_court import fields

CASES=(("R47-024","1"),("R47-049","0"))
def inspect(folder,lines):
    initial=snapshot(folder);current={k:v[:] for k,v in initial.items()}
    cp=[fields(l) for l in lines if l.startswith("C3X_R41_CP ")]
    end=[fields(l) for l in lines if l.startswith("C3X_R41_END ")]
    require(len(cp)==len(end)==1 and cp[0]["attempt"]=="27","checkpoint missing")
    starts=[r for r in records(lines,"START") if r["attempt"]=="27"]
    cand=[r for r in records(lines,"CANDIDATE") if r["attempt"]=="27"]
    require(len(starts)==1 and cand and cand[0]["count"]=="1","root alignment")
    require(all(cp[0][k]==starts[0][k] for k in ("alpha","beta")),"window drift")
    first={};written=set();counts=Counter();draws=[];total=0;y1=None
    with (folder/"r41_events.txt").open() as f:
        for line in f:
            serial,n,idx,op,val=line.split();total+=1;idx,val=int(idx),int(val)
            require(int(serial)==total,"serial drift")
            if op=="E":
                require(n=="endpoint" and y1 is None and val==int(cand[0]["value"]),"first return drift")
                y1=total;continue
            if op=="D":
                require(n=="draw" and val==-1+(idx&2),"draw drift")
                if y1 is None:draws.append((idx,val))
                continue
            require(n in current and op in ("R","U","W") and 0<=idx<len(current[n]),"unknown access or pointer")
            token=(n,idx)
            if op in ("R","U"):
                require(current[n][idx]==val,"read/write replay drift")
                if y1 is None and token not in written:first.setdefault((n,idx,op),total)
            else:
                current[n][idx]=val
                if y1 is None:written.add(token)
            if y1 is None:counts[n,op]+=1
    require(y1 is not None and total==int(end[0]["accesses"]),"trace incomplete")
    return {"initial":initial,"first":first,"counts":counts,"draws":draws,"cp":cp[0],"y1":y1,"total":total,"root":cand[0]}

def main():
    p=argparse.ArgumentParser()
    for k in ("census","discovery","prior","folder","base","observer","net","out","receipt"):p.add_argument(k,type=Path)
    a=p.parse_args()
    for f,h in ((a.discovery,DISCOVERY),(a.prior,R48),(a.base,BIN),(a.net,NET)):require(sha(f.read_bytes())==h,"identity drift "+f.name)
    cases={r["id"]:r for r in load_frozen(a.census,a.folder)}
    prior={r["id"]:r for r in json.loads(a.prior.read_text())["cases"]}
    frozen={r["id"]:r for r in json.loads(a.discovery.read_text())["cases"]}
    rows=[]
    for ident,g in CASES:
        target=frozen[ident]["targets"][g]["target"];arms={}
        for name,skip in (("sham",0),("both",1)):
            folder=a.out/ident/name
            env={"C3X_R33_OBSERVE":"1","C3X_R33_TARGET":target["event"],"C3X_R33_SKIP_FUTILITY":str(skip),"C3X_R33_SKIP_NULL":str(skip),
                 "C3X_R29_PROBES":"0","C3X_R31_OBSERVE":"0","C3X_NO_TT_PICKER":"0","C3X_NO_TT_VALUE":"0","C3X_R29_MASK_MOVE":"0","C3X_R29_MASK_VALUE":"0","C3X_R41_HISTORY":"1"}
            uci,proof=run(a.observer,{"history":cases[ident]["moves"]},a.net,folder,logging=True,paired=False,nnue=True,nodes=32000,environment=env)
            lines=(folder/"stderr.txt").read_text().splitlines()
            old=prior[ident]["targets"][g]["arms"][name]
            original="\n".join(l for l in lines if not l.startswith(("C3X_R41_CP ","C3X_R41_END ")))+"\n"
            require(sha(original.encode())==old["trace_sha256"][0]==old["trace_sha256"][1],"original trace parity")
            require(proof["best"]==old["best"],"best drift")
            e=matched(events(lines),target)
            require(e["close"]["value"]==old["child_return"],"child drift")
            arms[name]=inspect(folder,lines)
            print("R53_ARM",ident,name,json.dumps({"cp":arms[name]["cp"],"first_root":arms[name]["root"],"total":arms[name]["total"]},sort_keys=True),flush=True)
        a0,b0=arms["sham"],arms["both"]
        require(all(a0["cp"][k]==b0["cp"][k] for k in ("attempt","alpha","beta","root_depth","completed")),"arm context")
        row={"id":ident,"target_group":g,"contact":compare(a0,b0),"checkpoints":{k:v["cp"] for k,v in arms.items()},"first_roots":{k:v["root"] for k,v in arms.items()},"parity":True}
        rows.append(row);print("R53_CASE",json.dumps(row,sort_keys=True),flush=True)
    result={"scope":"two selected new-development cases; passive scalar checkpoint contact, not mediation","native_searches":4,"original_trace_parity":4,"cases":rows,"observer_sha256":sha(a.observer.read_bytes())}
    a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("R53_RECEIPT_SHA",sha(a.receipt.read_bytes()),flush=True)
if __name__=="__main__":main()
