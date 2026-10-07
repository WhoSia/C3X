#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import defaultdict
from pathlib import Path
def load(p):return json.loads(Path(p).read_text())
def pid(z):return f"p22:{z['source_id']}:{z['trajectory_hash'][:12]}"
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--corpus",required=True);ap.add_argument("--pair-freeze",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
 corp=load(a.corpus);pf=load(a.pair_freeze);ctx={pid(z):z for z in corp["positions"]};rows=[];srcfam=defaultdict(int);eng=set();famcells=0
 for p,z in sorted(pf["positions"].items()):
  if not z.get("admitted"):continue
  if p not in ctx:raise SystemExit("P22_PAIR_JOIN "+p)
  active=sorted(e for e,v in z.get("engine_views",{}).items() if v.get("active"))
  famcells+=2*len(active);srcfam[z["source_id"]]+=2*len(active);eng.update(active)
  rows.append({"position_id":p,"source_id":z["source_id"],"active_engines":active,"engine_family_cells":2*len(active),"pair":z["pair"],"context":ctx[p]["context"],"router_grammar":ctx[p]["router_grammar"]})
 sources=sorted({z["source_id"] for z in corp["positions"]})
 passed=len(rows)>0 and famcells>=36 and len(eng)>=2 and len(sources)>=2 and all(srcfam[s]>0 for s in sources)
 out={"schema":"c3x-g10-p22-heldout-pair-gate-v1","stage":"C3X 0.10.0-G10-P22","verdict":"PASS_HELDOUT_PAIR_SUPPORT" if passed else "HOLD_HELDOUT_PAIR_SUPPORT","routed_positions":len(corp["positions"]),"admitted_positions":len(rows),"active_engine_family_cells":famcells,"active_engine_family_cells_by_source":dict(srcfam),"active_engines":sorted(eng),"sources":sources,"frozen_minimums":{"engine_family_cells":36,"engines":2,"sources":2},"activation_predictions_consulted":False,"full_class_outcomes_consulted":False,"positions":rows}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P22_PAIR_GATE",out["verdict"],"ADMITTED",len(rows),"FAMILY_CELLS",famcells,dict(srcfam))
 if not passed:raise SystemExit("P22_PAIR_HOLD")
if __name__=="__main__":main()
