#!/usr/bin/env python3
"""R51: reconstruct sealed logs once, audit root-guard transmission.
Three post-outcome cases, two archived arms and two new component arms.
No new independent cohort, no raw publisher games in public receipt.
"""
import argparse,json
from pathlib import Path
from c3x_031_r47_frozen_discovery import load_frozen,sha,require,CENSUS,BIN,NET
from c3x_030_r33_gate_panel import trial
from c3x_031_p2_treatment import matched
from c3x_030_r23_native_replay import records
from c3x_031_r48_new_cohort_intervention import DISCOVERY

R48="96d45e1ebe57bfc46f7e0bc5bfeb5fb1eb48c69e9b9df396e22a56c5c1812005"
CASES=(("R47-024","1"),("R47-049","0"),("R47-029","0"))
def trace(path,target):
    lines=path.read_text().splitlines()
    starts=records(lines,"START")
    ends=records(lines,"END")
    cand=records(lines,"CANDIDATE")
    by={}
    for c in cand:by.setdefault(c["attempt"],[]).append(c)
    row=next(c for c in cand if c["id"]==target["candidate"])
    require(row["attempt"]==target["attempt"] and row["move"]==target["root"],"root ancestor identity")
    return starts,ends,by,row

def compare(a,b,target):
    sa,ea,ca,ra=a;sb,eb,cb,rb=b
    # Matching contexts require identical iteration, depth, ordinal and input window.
    ctx=("attempt","iteration","adjusted","alpha","beta","roots")
    ck=("move","count","depth","alpha","beta")
    out={"target_root_returns":[ra,rb],"first_value_difference":None,"first_update_difference":None,
         "first_context_or_order_difference":None,"matched_candidates":0,"matched_attempts":0}
    for x,y in zip(sa,sb):
        if any(x[k]!=y[k] for k in ctx):
            out["first_context_or_order_difference"]={"type":"attempt","a":x,"b":y};break
        out["matched_attempts"]+=1
        ar,br=ca.get(x["attempt"],[]),cb.get(y["attempt"],[])
        diverged=False
        for u,v in zip(ar,br):
            if any(u[k]!=v[k] for k in ck):
                out["first_context_or_order_difference"]={"type":"candidate","a":u,"b":v}
                diverged=True;break
            out["matched_candidates"]+=1
            for field,key in (("value","first_value_difference"),("update","first_update_difference")):
                if u[field]!=v[field] and out[key] is None:
                    out[key]={"a":u,"b":v,"margin_a":int(u["value"])-int(u["alpha"]),"margin_b":int(v["value"])-int(v["alpha"])}
        if diverged:break
        if len(ar)!=len(br):
            out["first_context_or_order_difference"]={"type":"candidate_count","attempt":x["attempt"],"a":len(ar),"b":len(br)};break
    if out["first_context_or_order_difference"] is None and len(sa)!=len(sb):
        out["first_context_or_order_difference"]={"type":"attempt_count","a":len(sa),"b":len(sb)}
    out["note"]="same observed root context only; internal state and branch identity not certified"
    return out

def main():
    p=argparse.ArgumentParser()
    for k in ("census","discovery","prior","folder","patch","net","out","receipt"):p.add_argument(k,type=Path)
    a=p.parse_args()
    for path,h in ((a.discovery,DISCOVERY),(a.prior,R48),(a.patch,BIN),(a.net,NET)):
        require(sha(path.read_bytes())==h,"identity drift "+path.name)
    prior={r["id"]:r for r in json.loads(a.prior.read_text())["cases"]}
    frozen={r["id"]:r for r in json.loads(a.discovery.read_text())["cases"]}
    cohort={r["id"]:r for r in load_frozen(a.census,a.folder)}
    rows=[]
    for ident,g in CASES:
        target=frozen[ident]["targets"][g]["target"]
        original=prior[ident]["targets"][g]
        arms={}
        traces={}
        specs=[("sham",False,False),("both",True,True)]
        if ident=="R47-024":specs += [("futility_only",True,False),("null_only",False,True)]
        for label,f,n in specs:
            name=ident+"/"+g+"/"+label
            v=trial(a,cohort[ident],name,binary=a.patch,observer=True,target=int(target["event"]),skip_f=f,skip_n=n)
            e=matched(v["events"],target);close=e["close"]
            require(close["skip_f"]==str(int(f)) and close["skip_n"]==str(int(n)),"activation")
            if label in ("sham","both"):
                old=original["arms"][label]
                require(v["trace"]==old["trace_sha256"][0]==old["trace_sha256"][1] and v["proof"]["best"]==old["best"] and close["value"]==old["child_return"],"sealed replay drift")
            traces[label]=trace(a.out/name/"stderr.txt",target)
            arms[label]={"target_close":close,"best":v["proof"]["best"],"trace_sha256":v["trace"]}
        comparisons={k:compare(traces["sham"],t,target) for k,t in traces.items() if k!="sham"}
        row={"id":ident,"group":g,"target":target,"arms":arms,"root_comparisons":comparisons}
        rows.append(row)
        print("R51_CASE",json.dumps(row,sort_keys=True),flush=True)
    result={"scope":"post-outcome mechanistic case studies, six hash-bound trace replays and two new component arms; no H transport","cases":rows,"native_searches":8,"replayed_searches":6,"new_component_searches":2,"prior_sha256":R48}
    a.receipt.parent.mkdir(parents=True,exist_ok=True)
    a.receipt.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("R51_RECEIPT_SHA",sha(a.receipt.read_bytes()),flush=True)
if __name__=="__main__":main()
