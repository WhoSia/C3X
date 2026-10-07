#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import Counter,defaultdict
from pathlib import Path
GCOMP={"G0_LEGACY_PHYSICAL":0,"G1_SAME_PIECE_COLLATERAL":1,"G2_SAME_TYPE_SIDE_COLLATERAL":2,"G3_SIDE_ROLE_COLLATERAL":3,"G4_GLOBAL_COLLATERAL":4}
ORDER=["P23_PRAGUE_MASTERS_2026","P23_BIEL_OPEN_MASTERS_2026","P23_SAINT_LOUIS_RAPID_2026"]
def load(p):return json.loads(Path(p).read_text())
def key(c):return "|".join((c["phase"],c["branching"],c["tactical_surface"]))
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--census",required=True);ap.add_argument("--router",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
 c=load(a.census);r=load(a.router)
 if c.get("verdict")!="PASS_P23_CANDIDATE_POOL":raise SystemExit("P23_CENSUS_NOT_READY")
 if r.get("schema")!="c3x-g10-p16-router-freeze-v1" or r.get("status")!="ROUTER_FROZEN_PRE_HELDOUT_SOURCE":raise SystemExit("P23_ROUTER")
 ranks=defaultdict(int);rows=[];abst=[];bysrc=defaultdict(list)
 for z in c["positions"]:
  sid=z["source_id"];ranks[sid]+=1
  g=r["policy"].get(key(z["cell"]),"ABSTAIN");o=dict(z);o["context"]=dict(z["cell"]);o["router_grammar"]=g;o["source_rank"]=ranks[sid];o["source_order"]=ORDER.index(sid)+1
  o["selection_grammar_complexity"]=None if g=="ABSTAIN" else GCOMP[g]
  if g=="ABSTAIN":abst.append(o)
  else:rows.append(o);bysrc[sid].append(o)
 srcs=sorted(bysrc,key=lambda s:ORDER.index(s));passed=len(srcs)==3 and all(len(bysrc[s])>0 for s in ORDER)
 out={"schema":"c3x-g10-p23-router-projection-v1","stage":"C3X 0.10.0-G10-P23",
      "verdict":"PASS_P23_ROUTER_PROJECTION" if passed else "HOLD_P23_ROUTER_PROJECTION",
      "authority":"OUTCOME_BLIND_ROUTER_ASSIGNMENT_ONLY",
      "inputs":{"activation_predictions_consulted":False,"full_class_outcomes_consulted":False,"q0_outcomes_consulted":False},
      "gate":{"routed_positions":len(rows),"abstained_positions":len(abst),"positions_by_source":{s:len(bysrc[s]) for s in ORDER},
              "router_grammar_counts":dict(Counter(z["router_grammar"] for z in rows))},
      "positions":rows,"abstentions":[{"source_id":z["source_id"],"source_rank":z["source_rank"],"candidate_sha256":z["candidate_sha256"],"context":z["context"]} for z in abst]}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P23_ROUTER",out["verdict"],out["gate"])
 if not passed:raise SystemExit("P23_ROUTER_HOLD")
if __name__=="__main__":main()
