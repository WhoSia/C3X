#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import Counter,defaultdict
from pathlib import Path

GCOMP={
 "G0_LEGACY_PHYSICAL":0,
 "G1_SAME_PIECE_COLLATERAL":1,
 "G2_SAME_TYPE_SIDE_COLLATERAL":2,
 "G3_SIDE_ROLE_COLLATERAL":3,
 "G4_GLOBAL_COLLATERAL":4
}
def load(p): return json.loads(Path(p).read_text())
def key(c): return "|".join((c["phase"],c["branching"],c["tactical_surface"]))

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--census",required=True)
 ap.add_argument("--router",required=True)
 ap.add_argument("--out",required=True)
 a=ap.parse_args()
 c=load(a.census); r=load(a.router)
 if c.get("verdict")!="PASS_FRESH_EVENT_WORLD_ECOLOGY_READY": raise SystemExit("P19_CENSUS_NOT_READY")
 if r.get("schema")!="c3x-g10-p16-router-freeze-v1": raise SystemExit("P19_ROUTER_SCHEMA")
 if r.get("status")!="ROUTER_FROZEN_PRE_HELDOUT_SOURCE": raise SystemExit("P19_ROUTER_NOT_FROZEN")
 rows=[]; abst=[]; bysrc=defaultdict(list)
 for z in c["positions"]:
   ck=key(z["cell"]); g=r["policy"].get(ck,"ABSTAIN")
   out=dict(z); out["context"]=dict(z["cell"]); out["router_grammar"]=g
   out["selection_grammar_complexity"]=None if g=="ABSTAIN" else GCOMP[g]
   if g=="ABSTAIN": abst.append(out); continue
   rows.append(out); bysrc[z["source_id"]].append(out)
 srcs=sorted(bysrc)
 cells=sorted({key(z["context"]) for z in rows})
 phases=sorted({z["context"]["phase"] for z in rows})
 branches=sorted({z["context"]["branching"] for z in rows})
 tactics=sorted({z["context"]["tactical_surface"] for z in rows})
 h2_by_source={s:sum(z["selection_grammar_complexity"]<=1 and z["context"]["phase"]!="REDUCED" for z in bysrc[s]) for s in srcs}
 grammar_counts=Counter(z["router_grammar"] for z in rows)
 # Frozen before engine outcomes: this is an eligibility/power gate only.
 passed=(len(rows)>=24 and len(cells)>=6 and len(phases)>=2 and len(branches)>=2 and len(tactics)>=2
         and all(len(bysrc[s])>=10 for s in srcs)
         and all(h2_by_source[s]>=3 for s in srcs))
 out={
   "schema":"c3x-g10-p19-router-projection-v1","stage":"C3X 0.9.0-G10-P19",
   "verdict":"PASS_ROUTED_FRESH_WORLD_POSITIVITY" if passed else "HOLD_ROUTED_FRESH_WORLD_SUPPORT_INSUFFICIENT",
   "authority":"PRE_ENGINE_OUTCOME_ELIGIBILITY_ONLY",
   "inputs":{"census_verdict":c["verdict"],"router_status":r["status"],
             "engine_outcomes_consulted":False,"counterfactual_outcomes_consulted":False},
   "gate":{"routed_positions":len(rows),"abstained_positions":len(abst),"routed_cells":len(cells),
           "phase_levels":phases,"branching_levels":branches,"tactical_levels":tactics,
           "positions_by_source":{s:len(bysrc[s]) for s in srcs},
           "h2_rule_eligible_pre_engine_by_source":h2_by_source,
           "router_grammar_counts":dict(sorted(grammar_counts.items()))},
   "frozen_gate":{"min_routed_positions":24,"min_routed_cells":6,"min_positions_per_source":10,
                  "min_h2_rule_eligible_per_source":3,"min_phase_levels":2,
                  "min_branching_levels":2,"min_tactical_levels":2},
   "positions":sorted(rows,key=lambda z:(z["source_id"],z["trajectory_hash"])),
   "abstentions":[{"source_id":z["source_id"],"candidate_sha256":z["candidate_sha256"],
                   "context":z["context"]} for z in abst]
 }
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G10_P19_ROUTER",out["verdict"])
 print("GATE",json.dumps(out["gate"],sort_keys=True))
if __name__=="__main__": main()
