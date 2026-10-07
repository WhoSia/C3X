#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import Counter,defaultdict
from pathlib import Path

GCOMP={"G0_LEGACY_PHYSICAL":0,"G1_SAME_PIECE_COLLATERAL":1,"G2_SAME_TYPE_SIDE_COLLATERAL":2,"G3_SIDE_ROLE_COLLATERAL":3,"G4_GLOBAL_COLLATERAL":4}
def load(p):return json.loads(Path(p).read_text())
def key(c):return "|".join((c["phase"],c["branching"],c["tactical_surface"]))
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--census",required=True);ap.add_argument("--router",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
 c=load(a.census);r=load(a.router)
 if c.get("verdict")!="PASS_HELDOUT_WORLD_ECOLOGY_READY":raise SystemExit("P22_CENSUS_NOT_READY")
 if r.get("schema")!="c3x-g10-p16-router-freeze-v1" or r.get("status")!="ROUTER_FROZEN_PRE_HELDOUT_SOURCE":raise SystemExit("P22_ROUTER")
 rows=[];abst=[];bysrc=defaultdict(list)
 for z in c["positions"]:
  g=r["policy"].get(key(z["cell"]),"ABSTAIN");o=dict(z);o["context"]=dict(z["cell"]);o["router_grammar"]=g;o["selection_grammar_complexity"]=None if g=="ABSTAIN" else GCOMP[g]
  if g=="ABSTAIN":abst.append(o)
  else:rows.append(o);bysrc[z["source_id"]].append(o)
 srcs=sorted(bysrc);cells=sorted({key(z["context"]) for z in rows});ph=sorted({z["context"]["phase"] for z in rows});br=sorted({z["context"]["branching"] for z in rows});ta=sorted({z["context"]["tactical_surface"] for z in rows})
 passed=len(rows)>=24 and len(cells)>=6 and len(ph)>=2 and len(br)>=2 and len(ta)>=2 and all(len(bysrc[s])>=10 for s in srcs) and len(srcs)>=2
 out={"schema":"c3x-g10-p22-heldout-router-projection-v1","stage":"C3X 0.10.0-G10-P22","verdict":"PASS_HELDOUT_ROUTER_SUPPORT" if passed else "HOLD_HELDOUT_ROUTER_SUPPORT",
      "authority":"PRE_PAIR_PRE_PREDICTION_ONLY","inputs":{"activation_predictions_consulted":False,"full_class_outcomes_consulted":False,"router_status":r["status"]},
      "gate":{"routed_positions":len(rows),"abstained_positions":len(abst),"routed_cells":len(cells),"phase_levels":ph,"branching_levels":br,"tactical_levels":ta,"positions_by_source":{s:len(bysrc[s]) for s in srcs},"router_grammar_counts":dict(Counter(z["router_grammar"] for z in rows))},
      "frozen_gate":{"min_routed_positions":24,"min_routed_cells":6,"min_positions_per_source":10,"min_phase_levels":2,"min_branching_levels":2,"min_tactical_levels":2},
      "positions":sorted(rows,key=lambda z:(z["source_id"],z["trajectory_hash"])),"abstentions":[{"source_id":z["source_id"],"candidate_sha256":z["candidate_sha256"],"context":z["context"]} for z in abst]}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P22_ROUTER",out["verdict"],json.dumps(out["gate"],sort_keys=True))
 if not passed:raise SystemExit("P22_ROUTER_HOLD")
if __name__=="__main__":main()
