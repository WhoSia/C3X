#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import defaultdict
from pathlib import Path

def load(p):return json.loads(Path(p).read_text())

def rate(rows):
    return None if not rows else sum(r["label"] for r in rows)/len(rows)

def sign(x,eps=1e-12):
    if x is None:return None
    if x>eps:return 1
    if x<-eps:return -1
    return 0

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dataset",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    x=load(a.dataset);rows=x["rows"]
    sources=sorted({r["source_id"] for r in rows})
    inds=sorted(rows[0]["indicators"])
    indicator_effects={}
    stable=[];reversal=[];undefined=[]
    for ind in inds:
        per={}
        signs=[]
        for s in sources:
            rr=[r for r in rows if r["source_id"]==s]
            t=[r for r in rr if r["indicators"][ind]]
            f=[r for r in rr if not r["indicators"][ind]]
            rt,rf=rate(t),rate(f)
            d=None if rt is None or rf is None else rt-rf
            per[s]={"true_n":len(t),"true_rate":rt,"false_n":len(f),"false_rate":rf,"effect_delta":d,"sign":sign(d)}
            signs.append(sign(d))
        indicator_effects[ind]=per
        if any(z is None for z in signs):undefined.append(ind)
        elif signs[0]*signs[1]<0:reversal.append(ind)
        elif signs[0]==signs[1] and signs[0]!=0:stable.append(ind)
    fields=("pair_geometry","phase","branching","tactical_surface","relation_atom_family","side_role","piece_type","grammar_complexity_bin","total_collateral_bin")
    categorical={}
    for field in fields:
        levels=sorted({str(r["raw"].get(field)) for r in rows})
        categorical[field]={}
        for lev in levels:
            categorical[field][lev]={}
            for s in sources:
                rr=[r for r in rows if r["source_id"]==s and str(r["raw"].get(field))==lev]
                categorical[field][lev][s]={"n":len(rr),"survival_rate":rate(rr)}
    src_summary={}
    for s in sources:
        rr=[r for r in rows if r["source_id"]==s]
        src_summary[s]={"n":len(rr),"positive":sum(r["label"] for r in rr),"rate":rate(rr)}
    out={
      "schema":"c3x-g10-p17-posthold-primitive-atlas-v1",
      "status":"POST_HOLD_DEMOTION_ONLY",
      "can_strengthen_primary":False,
      "sources":sources,
      "source_summary":src_summary,
      "indicator_effects":indicator_effects,
      "stable_same_sign_indicators":stable,
      "sign_reversal_indicators":reversal,
      "undefined_effect_indicators":undefined,
      "categorical_survival":categorical,
      "interpretation":[
        "Source-invariant primitive direction is required before any feature is promoted toward a law-like susceptibility claim.",
        "Sign reversals diagnose transport failure, not evidence for a more complex opaque model.",
        "This atlas cannot reopen fresh confirmation or change the P17 calibration HOLD."
      ]
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P17_POSTHOLD_ATLAS_PASS")
    print("SOURCE",json.dumps(src_summary,sort_keys=True))
    print("STABLE",stable)
    print("REVERSAL",reversal)
    print("UNDEFINED",undefined)
if __name__=="__main__":main()
