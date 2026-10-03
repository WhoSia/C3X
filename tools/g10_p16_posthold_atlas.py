#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import defaultdict,Counter
from pathlib import Path

def load(p): return json.loads(Path(p).read_text())

def pack(rows,keyfn):
    d=defaultdict(Counter)
    for r in rows:
        k=keyfn(r);z=d[k]
        z["n"]+=1;z["routed"]+=int(r["routed"]);z["g2"]+=int(r["global_g2"]);z[r["category"]]+=1
    out={}
    for k,z in sorted(d.items()):
        out[k]=dict(z)
        out[k]["routed_fraction"]=z["routed"]/z["n"] if z["n"] else None
        out[k]["g2_fraction"]=z["g2"]/z["n"] if z["n"] else None
        out[k]["difference"]=z["routed"]-z["g2"]
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--validation",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    v=load(a.validation)
    rows=v["position_rows"]
    by_grammar=pack(rows,lambda r:r["router_grammar"])
    by_phase=pack(rows,lambda r:r["context"]["phase"])
    by_branch=pack(rows,lambda r:r["context"]["branching"])
    by_tact=pack(rows,lambda r:r["context"]["tactical_surface"])
    gains=[r for r in rows if r["category"]=="ROUTED_ONLY"]
    losses=[r for r in rows if r["category"]=="G2_ONLY"]
    out={
      "schema":"c3x-g10-p16-posthold-atlas-v1",
      "status":"POST_HOLD_DEMOTION_ONLY",
      "can_strengthen_primary":False,
      "primary_verdict":v["verdict"],
      "by_router_grammar":by_grammar,
      "by_phase":by_phase,
      "by_branching":by_branch,
      "by_tactical_surface":by_tact,
      "routed_only_positions":gains,
      "g2_only_positions":losses,
      "interpretation":[
        "The router's net held-out gain is concentrated in contexts assigned the stricter G0 legacy grammar rather than looser grammars.",
        "G1 and G2 routed cells show no net paired advantage over GLOBAL_G2 in this held-out ecology.",
        "G3 produces no positive held-out positions.",
        "The result does not satisfy the preregistered positivity gate and cannot reopen defect replay."
      ]
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P16_POSTHOLD_ATLAS_PASS",v["verdict"])
    print("GRAMMAR",json.dumps(by_grammar,sort_keys=True))
    print("PHASE",json.dumps(by_phase,sort_keys=True))
    print("BRANCH",json.dumps(by_branch,sort_keys=True))
    print("TACT",json.dumps(by_tact,sort_keys=True))
    print("ROUTED_ONLY",json.dumps(gains,sort_keys=True))
    print("G2_ONLY",json.dumps(losses,sort_keys=True))
if __name__=="__main__":main()
