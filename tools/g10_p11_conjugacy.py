#!/usr/bin/env python3
from __future__ import annotations
import argparse,itertools,json,math
from collections import Counter,defaultdict
from pathlib import Path

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
    s=set(ch["board_topology"][b]["available_bounds"])
    return "".join("1" if q in s else "0" for q in ("UPPER","LOWER"))

def counts(worlds,source_filter=None):
    out=defaultdict(lambda:defaultdict(Counter))
    for w in worlds:
        if source_filter and w["source_id"]!=source_filter:continue
        e=w["engine"]
        for ch in w.get("chains",[]):
            x=vec(ch,"B0")
            for d in EDITS:
                y=vec(ch,d)
                out[e][d][(x,y)]+=1
    return out

def identity_map():
    return {s:s for s in STATES}
def swap_map():
    return {s:s[::-1] for s in STATES}
def affine_maps():
    maps=[]
    for swap in (False,True):
        for b in STATES:
            m={}
            for s in STATES:
                x=s[::-1] if swap else s
                y="".join(str(int(x[i])^int(b[i])) for i in range(2))
                m[s]=y
            maps.append(m)
    return dedup_maps(maps)
def s4_maps():
    return [{s:t for s,t in zip(STATES,p)} for p in itertools.permutations(STATES)]
def dedup_maps(ms):
    seen=set();out=[]
    for m in ms:
        k=tuple(m[s] for s in STATES)
        if k not in seen:seen.add(k);out.append(m)
    return out
def map_name(m):
    return "|".join(f"{s}>{m[s]}" for s in STATES)
def transform(c,m):
    z=Counter()
    for (x,y),n in c.items():z[(m[x],m[y])]+=n
    return z
def support(c): return {e for e,n in c.items() if n>0}
def joint_tv(a,b):
    na=sum(a.values());nb=sum(b.values())
    if not na or not nb:return None
    keys=set(a)|set(b)
    return 0.5*sum(abs(a[k]/na-b[k]/nb) for k in keys)
def row_tv(a,b):
    vals=[]
    for x in STATES:
        aa={y:a[(x,y)] for y in STATES};bb={y:b[(x,y)] for y in STATES}
        na=sum(aa.values());nb=sum(bb.values())
        if na and nb:
            vals.append(0.5*sum(abs(aa[y]/na-bb[y]/nb) for y in STATES))
    return sum(vals)/len(vals) if vals else None
def eval_map(c,e1,e2,m):
    per={};obs=0;rt=[];jt=[]
    for d in EDITS:
        a=transform(c[e1][d],m);b=c[e2][d]
        sa,sb=support(a),support(b)
        sym=sorted(sa^sb)
        obs+=len(sym)
        rv=row_tv(a,b);jv=joint_tv(a,b)
        if rv is not None:rt.append(rv)
        if jv is not None:jt.append(jv)
        per[d]={
          "support_symmetric_difference_count":len(sym),
          "support_only_edges":[list(x) for x in sym],
          "row_kernel_tv":rv,
          "joint_edge_tv":jv
        }
    return {
      "map":m,"map_name":map_name(m),
      "support_obstruction":obs,
      "mean_row_kernel_tv":sum(rt)/len(rt) if rt else None,
      "mean_joint_edge_tv":sum(jt)/len(jt) if jt else None,
      "per_edit":per
    }
def score(z):
    return (z["support_obstruction"],
            float("inf") if z["mean_row_kernel_tv"] is None else z["mean_row_kernel_tv"],
            float("inf") if z["mean_joint_edge_tv"] is None else z["mean_joint_edge_tv"])
def best_group(c,e1,e2,maps):
    allz=[eval_map(c,e1,e2,m) for m in maps]
    allz.sort(key=score)
    best=allz[0]
    return {"best":best,"ties_primary":[z for z in allz if z["support_obstruction"]==best["support_obstruction"]],"map_count":len(allz)}

def partitions(seq):
    # canonical set partitions.
    if not seq:
        yield []
        return
    first=seq[0]
    for rest in partitions(seq[1:]):
        yield [[first]]+[b[:] for b in rest]
        for i in range(len(rest)):
            z=[b[:] for b in rest]
            z[i]=[first]+z[i]
            yield z
def canonical_partition(p):
    blocks=[tuple(sorted(b)) for b in p]
    return tuple(sorted(blocks))
def all_partitions():
    seen=set();out=[]
    for p in partitions(list(STATES)):
        k=canonical_partition(p)
        if k not in seen:seen.add(k);out.append(k)
    return sorted(out,key=lambda p:(-len(p),p))
def block_map(p):
    m={}
    for i,b in enumerate(p):
        for s in b:m[s]=i
    return m
def agg(c,p):
    bm=block_map(p);z=Counter()
    for (x,y),n in c.items():z[(bm[x],bm[y])]+=n
    return z
def partition_name(p):
    return "{"+"|".join("".join(b) for b in p)+"}"
def quotient_eval(c,p,engines):
    supp={}
    for e in engines:
        supp[e]={d:support(agg(c[e][d],p)) for d in EDITS}
    exact=all(len({frozenset(supp[e][d]) for e in engines})==1 for d in EDITS)
    pair_tv={}
    for i in range(len(engines)):
        for j in range(i+1,len(engines)):
            e1,e2=engines[i],engines[j];key=f"{e1}|{e2}"
            pair_tv[key]={d:joint_tv(agg(c[e1][d],p),agg(c[e2][d],p)) for d in EDITS}
    return {"partition":[list(b) for b in p],"name":partition_name(p),"blocks":len(p),"exact_common_support":exact,"pair_joint_tv":pair_tv,
            "support":{e:{d:[list(x) for x in sorted(supp[e][d])] for d in EDITS} for e in engines}}

def obstruction_edges(best):
    out=[]
    for d,z in best["per_edit"].items():
        for e in z["support_only_edges"]:out.append({"edit":d,"edge":e})
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--worlds",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    worlds=collect(a.worlds)
    c=counts(worlds)
    engines=sorted(c)
    pairs=[(engines[i],engines[j]) for i in range(len(engines)) for j in range(i+1,len(engines))]

    sem=[identity_map(),swap_map()]
    d4=affine_maps();full=s4_maps()
    results={}
    for e1,e2 in pairs:
        k=f"{e1}|{e2}"
        results[k]={
          "semantic":best_group(c,e1,e2,sem),
          "square_automorphism":best_group(c,e1,e2,d4),
          "S4":best_group(c,e1,e2,full)
        }
        results[k]["semantic_obstruction_edges"]=obstruction_edges(results[k]["semantic"]["best"])
        results[k]["S4_obstruction_edges"]=obstruction_edges(results[k]["S4"]["best"])

    # Source-separated robustness, same hierarchy.
    source_results={}
    for src in sorted({w["source_id"] for w in worlds}):
        cs=counts(worlds,src)
        source_results[src]={}
        for e1,e2 in pairs:
            k=f"{e1}|{e2}"
            if e1 not in cs or e2 not in cs:continue
            source_results[src][k]={
              "semantic":best_group(cs,e1,e2,sem)["best"],
              "S4":best_group(cs,e1,e2,full)["best"]
            }

    qs=[quotient_eval(c,p,engines) for p in all_partitions()]
    exact_nontrivial=[q for q in qs if q["exact_common_support"] and q["blocks"]>1]
    maxblocks=max((q["blocks"] for q in exact_nontrivial),default=0)
    finest=[q for q in exact_nontrivial if q["blocks"]==maxblocks]
    hw=next(q for q in qs if canonical_partition(q["partition"])==canonical_partition([["00"],["01","10"],["11"]]))

    # Verdict by presealed hierarchy.
    sem_zero=all(results[k]["semantic"]["best"]["support_obstruction"]==0 for k in results)
    s4_zero=all(results[k]["S4"]["best"]["support_obstruction"]==0 for k in results)
    if sem_zero:verdict="DEVELOPMENT_SEMANTIC_CONJUGACY_CANDIDATE"
    elif s4_zero:verdict="DEVELOPMENT_NONSEMANTIC_GRAPH_ISOMORPHISM_ONLY"
    elif finest:verdict="DEVELOPMENT_FINE_NONCONJUGATE_COMMON_QUOTIENT_EXISTS"
    else:verdict="DEVELOPMENT_NONCONJUGATE_NO_NONTRIVIAL_COMMON_QUOTIENT"

    out={
      "schema":"c3x-g10-p11-conjugacy-v1",
      "status":"DEVELOPMENT_ONLY_NO_CONFIRMATORY_AUTHORITY",
      "verdict":verdict,
      "engines":engines,
      "world_count":len(worlds),
      "engine_pair_results":results,
      "source_separated_robustness":source_results,
      "quotient_search":{
        "partition_count":len(qs),
        "exact_nontrivial_count":len(exact_nontrivial),
        "finest_exact_common_support_block_count":maxblocks,
        "finest_exact_common_support_quotients":finest,
        "hamming_weight_quotient":hw,
        "all_partitions":qs
      },
      "falsification":{
        "semantic_conjugacy_all_pairs":sem_zero,
        "S4_conjugacy_all_pairs":s4_zero,
        "nontrivial_exact_common_support_quotient_exists":bool(finest)
      },
      "claim_ceiling":"DEVELOPMENT_CANDIDATE_ONLY",
      "automation_identity":{"actions_writeback":False}
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P11_CONJUGACY_PASS",verdict)
    for k,v in results.items():
        print("PAIR",k,
              "SEM",v["semantic"]["best"]["support_obstruction"],v["semantic"]["best"]["map_name"],v["semantic"]["best"]["mean_row_kernel_tv"],
              "D4",v["square_automorphism"]["best"]["support_obstruction"],v["square_automorphism"]["best"]["map_name"],
              "S4",v["S4"]["best"]["support_obstruction"],v["S4"]["best"]["map_name"],v["S4"]["best"]["mean_row_kernel_tv"])
    print("QUOTIENT",len(qs),len(exact_nontrivial),maxblocks,[q["name"] for q in finest])
    print("HAMMING",hw["exact_common_support"],hw["pair_joint_tv"])
    print("SOURCE",json.dumps(source_results,sort_keys=True))
if __name__=="__main__":main()
