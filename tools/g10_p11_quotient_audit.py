#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,itertools
from collections import Counter,defaultdict
from pathlib import Path
from fractions import Fraction

STATES=("00","01","10","11")
EDITS=("TARGET","SUBSET","SHAM")

def load(p): return json.loads(Path(p).read_text())
def collect(root):
    out=[]
    for p in Path(root).rglob("*.json"):
        try:x=load(p)
        except Exception:continue
        if x.get("schema")=="c3x-g10-p10-opportunity-world-v1" and x.get("active"):out.append(x)
    return out
def vec(ch,b):
    a=set(ch["board_topology"][b]["available_bounds"])
    return "".join("1" if q in a else "0" for q in ("UPPER","LOWER"))
def counts(ws,src=None):
    out=defaultdict(lambda:defaultdict(Counter))
    for w in ws:
        if src and w["source_id"]!=src:continue
        for ch in w.get("chains",[]):
            x=vec(ch,"B0")
            for d in EDITS:out[w["engine"]][d][(x,vec(ch,d))]+=1
    return out
def partitions(seq):
    if not seq:
        yield [];return
    f=seq[0]
    for rest in partitions(seq[1:]):
        yield [[f]]+[b[:] for b in rest]
        for i in range(len(rest)):
            z=[b[:] for b in rest];z[i]=[f]+z[i];yield z
def canon(p):return tuple(sorted(tuple(sorted(b)) for b in p))
def all_parts():
    seen=set();out=[]
    for p in partitions(list(STATES)):
        k=canon(p)
        if k not in seen:seen.add(k);out.append(k)
    return sorted(out,key=lambda p:(-len(p),p))
def bm(p):return {s:i for i,b in enumerate(p) for s in b}
def agg(c,p):
    m=bm(p);z=Counter()
    for (x,y),n in c.items():z[(m[x],m[y])]+=n
    return z
def support(c):return {k for k,v in c.items() if v}
def exact_common_support(c,p):
    ens=sorted(c)
    if len(ens)<3:return False
    for d in EDITS:
        ss=[frozenset(support(agg(c[e][d],p))) for e in ens]
        if len(set(ss))!=1:return False
    return True
def row_block(c,state,p):
    m=bm(p);k=len(p);vals=[0]*k
    for (x,y),n in c.items():
        if x==state:vals[m[y]]+=n
    n=sum(vals)
    if not n:return None
    return vals,tuple(Fraction(v,n) for v in vals),tuple(i for i,v in enumerate(vals) if v)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--worlds",required=True)
    ap.add_argument("--primary",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    ws=collect(a.worlds);primary=load(a.primary)
    finest=primary["quotient_search"]["finest_exact_common_support_quotients"]
    if len(finest)!=1:raise SystemExit(f"P11_AUDIT_EXPECT_ONE_FINEST {len(finest)}")
    p=canon(finest[0]["partition"])
    c=counts(ws)
    sources=sorted({w["source_id"] for w in ws})

    src={}
    for s in sources:
        cs=counts(ws,s)
        ex=[q for q in all_parts() if len(q)>1 and exact_common_support(cs,q)]
        src[s]={
          "candidate_exact":exact_common_support(cs,p),
          "all_nontrivial_exact_common_support":[[list(b) for b in q] for q in ex]
        }

    fiber_rows=[];support_tests=0;support_fail=0;prob_tests=0;prob_fail=0;untestable=0
    for e in sorted(c):
        for d in EDITS:
            op=c[e][d]
            for bi,b in enumerate(p):
                if len(b)<2:continue
                rows=[(s,row_block(op,s,p)) for s in b]
                observed=[x for x in rows if x[1] is not None]
                if len(observed)<2:
                    untestable+=1
                    fiber_rows.append({"engine":e,"edit":d,"block":bi,"states":list(b),"status":"UNTESTABLE_MISSING_ROW",
                                      "rows":{s:(None if r is None else {"counts":r[0],"prob":[str(x) for x in r[1]],"support":r[2]}) for s,r in rows}})
                    continue
                support_tests+=1;prob_tests+=1
                supports={r[1][2] for r in observed}
                probs={r[1][1] for r in observed}
                sf=len(supports)!=1;pf=len(probs)!=1
                support_fail+=int(sf);prob_fail+=int(pf)
                fiber_rows.append({"engine":e,"edit":d,"block":bi,"states":list(b),
                                  "status":"FAIL" if (sf or pf) else "PASS",
                                  "support_consistent":not sf,"probability_consistent":not pf,
                                  "rows":{s:{"counts":r[0],"prob":[str(x) for x in r[1]],"support":r[2]} for s,r in observed}})

    source_robust=all(v["candidate_exact"] for v in src.values())
    if not source_robust:
        verdict="POOLED_ONLY_SOURCE_FRAGILE"
    elif support_fail:
        verdict="SOURCE_ROBUST_BUT_FIBER_INCONSISTENT"
    elif prob_fail:
        verdict="SOURCE_ROBUST_SUPPORT_CONSISTENT_PROBABILITY_INCONSISTENT"
    else:
        verdict="SOURCE_ROBUST_FIBER_CONSISTENT"

    out={
      "schema":"c3x-g10-p11-quotient-sufficiency-audit-v1",
      "status":"DEMOTION_ONLY_POST_RESULT_AUDIT",
      "candidate_partition":[list(b) for b in p],
      "candidate_name":finest[0]["name"],
      "verdict":verdict,
      "source_split":src,
      "source_robust":source_robust,
      "fiber_consistency":{
        "support_tests":support_tests,"support_failures":support_fail,
        "probability_tests":prob_tests,"probability_failures":prob_fail,
        "untestable_fibers":untestable,"rows":fiber_rows
      },
      "authority":{
        "can_strengthen_primary":False,
        "transport_law_blocked":(not source_robust) or support_fail>0 or prob_fail>0
      }
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P11_QUOTIENT_AUDIT",verdict)
    print("SOURCE",json.dumps(src,sort_keys=True))
    print("FIBER",support_tests,support_fail,prob_tests,prob_fail,untestable)
    print("LAW_BLOCKED",out["authority"]["transport_law_blocked"])
if __name__=="__main__":main()
