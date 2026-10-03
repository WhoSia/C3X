#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import defaultdict
from pathlib import Path

ORDER=("G0_LEGACY_PHYSICAL","G1_SAME_PIECE_COLLATERAL","G2_SAME_TYPE_SIDE_COLLATERAL","G3_SIDE_ROLE_COLLATERAL","G4_GLOBAL_COLLATERAL")

def load(p): return json.loads(Path(p).read_text())
def ckey(c): return "|".join((c["phase"],c["branching"],c["tactical_surface"]))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--stage-a",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    x=load(a.stage_a)
    if x.get("schema")!="c3x-g10-p15-stage-a-v1": raise SystemExit("P16_BAD_P15_STAGE_A")
    rows=x["position_rows"]
    cells=defaultdict(list)
    for r in rows: cells[ckey(r["context"])].append(r)
    policy={}
    diag={}
    for k,rr in sorted(cells.items()):
        n=len(rr)
        cov={}
        for g in ORDER:
            yes=sum(1 for r in rr if r["grammars"][g]["chain_count"]>0)
            cov[g]={"n":n,"yes":yes,"fraction":yes/n if n else 0}
        route="ABSTAIN"
        if n>=3:
            for g in ORDER:
                if cov[g]["fraction"]>=0.50:
                    route=g;break
        policy[k]=route
        diag[k]={"development_pairs":n,"coverage":cov,"route":route}
    routed={k:v for k,v in policy.items() if v!="ABSTAIN"}
    counts=defaultdict(int)
    for g in routed.values():counts[g]+=1
    out={
      "schema":"c3x-g10-p16-router-freeze-v1",
      "stage":"C3X 0.9.0-G10-P16",
      "status":"ROUTER_FROZEN_PRE_HELDOUT_SOURCE",
      "inputs":{
        "p15_stage_a_only":True,
        "p15_stage_b_read":False,
        "heldout_source_bytes_read":False,
        "engine_preference_outcomes_read":False,
        "defect_outcomes_read":False
      },
      "rule":{
        "context_key":["phase","branching","tactical_surface"],
        "min_development_pairs":3,
        "coverage_threshold":0.50,
        "grammar_order":list(ORDER),
        "no_backoff":True
      },
      "policy":policy,
      "routed_cells":sorted(routed),
      "abstain_cells":sorted(k for k,v in policy.items() if v=="ABSTAIN"),
      "grammar_cell_counts":dict(sorted(counts.items())),
      "diagnostics":diag,
      "global_comparator":"G2_SAME_TYPE_SIDE_COLLATERAL"
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P16_ROUTER_FREEZE",len(routed),"ROUTED",len(out["abstain_cells"]),"ABSTAIN")
    print("COUNTS",json.dumps(out["grammar_cell_counts"],sort_keys=True))
    for k in sorted(policy):print("ROUTE",k,policy[k],diag[k]["development_pairs"])
if __name__=="__main__":main()
