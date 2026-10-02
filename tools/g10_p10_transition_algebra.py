#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from collections import Counter,defaultdict
from pathlib import Path

BOARDS=("B0","TARGET","SUBSET","SHAM")
BOUNDS=("UPPER","LOWER")

def load(p): return json.loads(Path(p).read_text())
def collect(root):
    out=[]
    for p in Path(root).rglob("*.json"):
        try:x=load(p)
        except:continue
        if x.get("schema")=="c3x-g10-p10-opportunity-world-v1": out.append(x)
    return out
def vec(ch,b):
    a=set(ch["board_topology"][b]["available_bounds"])
    return tuple(int(q in a) for q in BOUNDS)
def bits(v): return "".join(map(str,v))
def hamming(a,b): return sum(x!=y for x,y in zip(a,b))
def entropy(c):
    n=sum(c.values())
    return 0.0 if not n else -sum((v/n)*math.log2(v/n) for v in c.values() if v)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--worlds",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    worlds=[w for w in collect(a.worlds) if w.get("active")]

    trans=defaultdict(Counter)
    engine_trans=defaultdict(lambda:defaultdict(Counter))
    source_trans=defaultdict(lambda:defaultdict(Counter))
    chain_rows=[]
    for w in worlds:
        for ch in w.get("chains",[]):
            b0=vec(ch,"B0")
            row={"engine":w["engine"],"source_id":w["source_id"],"position_id":w["position_id"],"chain_id":ch["chain_id"],"from":bits(b0)}
            for dest in ("TARGET","SUBSET","SHAM"):
                dv=vec(ch,dest); key=f"B0->{dest}"
                edge=(bits(b0),bits(dv))
                trans[key][edge]+=1
                engine_trans[w["engine"]][key][edge]+=1
                source_trans[w["source_id"]][key][edge]+=1
                row[dest]={"to":bits(dv),"hamming":hamming(b0,dv)}
            chain_rows.append(row)

    states=["00","01","10","11"]
    full_edges=[(x,y) for x in states for y in states]
    summary={}
    for key,c in trans.items():
        seen=set(c)
        forbidden=[list(e) for e in full_edges if e not in seen]
        selfloops=sum(v for (x,y),v in c.items() if x==y)
        flips=sum(v for (x,y),v in c.items() if x!=y)
        summary[key]={
          "n":sum(c.values()),"distinct_edges":len(c),
          "edge_counts":{f"{x}->{y}":v for (x,y),v in sorted(c.items())},
          "forbidden_edges":forbidden,
          "self_loop_fraction":selfloops/sum(c.values()) if c else None,
          "change_fraction":flips/sum(c.values()) if c else None,
          "edge_entropy_bits":entropy(c)
        }

    # Bound persistence / creation / destruction.
    bound_stats={}
    for dest in ("TARGET","SUBSET","SHAM"):
        c=Counter()
        for r in chain_rows:
            src=r["from"]; dst=r[dest]["to"]
            for i,q in enumerate(BOUNDS):
                a0=int(src[i]); b0=int(dst[i])
                if a0==1 and b0==1:c[f"{q}_PERSIST"]+=1
                elif a0==1 and b0==0:c[f"{q}_DESTROY"]+=1
                elif a0==0 and b0==1:c[f"{q}_CREATE"]+=1
                else:c[f"{q}_ABSENT"]+=1
        bound_stats[dest]=dict(c)

    # Engine-conditional operator variation using L1 distance between edge distributions.
    def edge_dist(c):
        n=sum(c.values())
        return {e:v/n for e,v in c.items()} if n else {}
    engine_pair={}
    ens=sorted(engine_trans)
    for i in range(len(ens)):
        for j in range(i+1,len(ens)):
            e1,e2=ens[i],ens[j]; ek=f"{e1}|{e2}"; engine_pair[ek]={}
            for key in ("B0->TARGET","B0->SUBSET","B0->SHAM"):
                p=edge_dist(engine_trans[e1][key]); q=edge_dist(engine_trans[e2][key])
                supp=set(p)|set(q)
                tv=0.5*sum(abs(p.get(x,0)-q.get(x,0)) for x in supp)
                engine_pair[ek][key]={"total_variation":tv}

    # Quotient by common B0/TARGET count and fiber sizes.
    qcount=Counter()
    fibers=defaultdict(Counter)
    for w in worlds:
        for ch in w.get("chains",[]):
            sig=[]
            for b in BOARDS:sig.extend(vec(ch,b))
            sig="".join(map(str,sig))
            k=sum(a*b for a,b in zip(vec(ch,"B0"),vec(ch,"TARGET")))
            qcount[str(k)]+=1; fibers[str(k)][sig]+=1

    # Same position+chain transport of transition edge across engines.
    bypc=defaultdict(list)
    for r in chain_rows:bypc[(r["position_id"],r["source_id"],r["chain_id"])].append(r)
    transport={}
    for dest in ("TARGET","SUBSET","SHAM"):
        groups=0; unanimous=0
        for rows in bypc.values():
            if len(rows)<2:continue
            groups+=1
            edges={(r["from"],r[dest]["to"]) for r in rows}
            unanimous+=int(len(edges)==1)
        transport[dest]={"multi_engine_groups":groups,"unanimous_groups":unanimous,"unanimous_fraction":unanimous/groups if groups else None}

    out={
      "schema":"c3x-g10-p10-transition-algebra-v1",
      "status":"DEVELOPMENT_ONLY_NO_CONFIRMATORY_AUTHORITY",
      "active_worlds":len(worlds),
      "chain_rows":len(chain_rows),
      "transition_summary":summary,
      "bound_stats":bound_stats,
      "engine_operator_total_variation":engine_pair,
      "quotient_fibers":{
        "coarse_counts":dict(qcount),
        "fiber_distinct_signature_counts":{k:len(v) for k,v in sorted(fibers.items())},
        "fiber_entropy_bits":{k:entropy(v) for k,v in sorted(fibers.items())}
      },
      "cross_engine_transition_transport":transport,
      "firewall":{"certificate_labels_used":False,"event_ablation_used":False,"post_outcome_refit":False},
      "confirmatory_authority":False
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P10_TRANSITION_ALGEBRA_PASS")
    print("ROWS",len(chain_rows))
    print("SUMMARY",json.dumps(summary,sort_keys=True))
    print("BOUND",json.dumps(bound_stats,sort_keys=True))
    print("TV",json.dumps(engine_pair,sort_keys=True))
    print("FIBERS",json.dumps(out["quotient_fibers"],sort_keys=True))
    print("TRANSPORT",json.dumps(transport,sort_keys=True))
if __name__=="__main__":main()
