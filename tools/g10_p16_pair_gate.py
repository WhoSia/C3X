#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import defaultdict
from pathlib import Path

def load(p): return json.loads(Path(p).read_text())
def pid(z): return f"p16:{z['source_id']}:{z['trajectory_hash'][:12]}"
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--corpus",required=True)
    ap.add_argument("--pair-freeze",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    corp=load(a.corpus);pf=load(a.pair_freeze)
    ctx={pid(z):z["context"] for z in corp["positions"]}
    route={pid(z):z["router_grammar"] for z in corp["positions"]}
    total=len(corp["positions"])
    admitted=[]
    srceng=defaultdict(set);cells=set()
    for p,z in sorted(pf["positions"].items()):
        if not z.get("admitted"): continue
        if p not in ctx: raise SystemExit("P16_PAIR_JOIN "+p)
        active=sorted(e for e,v in z.get("engine_views",{}).items() if v.get("active"))
        for e in active:srceng[z["source_id"]].add(e)
        c=ctx[p];cells.add("|".join((c["phase"],c["branching"],c["tactical_surface"])))
        admitted.append({"position_id":p,"source_id":z["source_id"],"context":c,"router_grammar":route[p],
                         "active_engines":active,"pair":z["pair"],"engine_views":z["engine_views"]})
    frac=len(admitted)/total if total else 0
    sources=sorted({z["source_id"] for z in corp["positions"]})
    src_ok=all(len(srceng[s])>=2 for s in sources)
    passed=frac>=0.45 and len(admitted)>=16 and len(cells)>=6 and src_ok
    out={
      "schema":"c3x-g10-p16-heldout-pair-gate-v1","stage":"C3X 0.9.0-G10-P16",
      "verdict":"PASS_HELDOUT_PAIR_POSITIVITY" if passed else "HOLD_HELDOUT_PAIR_SUPPORT_INSUFFICIENT",
      "total_positions":total,"admitted_pair_positions":len(admitted),"pair_fraction":frac,
      "pair_supported_context_cells":len(cells),"supported_cells":sorted(cells),
      "active_engines_by_source":{s:sorted(srceng[s]) for s in sources},
      "pair_outcomes_only":True,"intervention_outcomes_consulted":False,"defect_outcomes_consulted":False,
      "admitted_positions":admitted
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P16_PAIR_GATE",out["verdict"])
    print("PAIR",len(admitted),"/",total,frac,"CELLS",len(cells))
    print("ENGINES",out["active_engines_by_source"])
if __name__=="__main__":main()
