#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import defaultdict
from pathlib import Path
import g10_p19_source_census as p19

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--source",action="append",required=True,help="ID|PGN|URL|SHA256|ORDER|ECOLOGY")
 ap.add_argument("--history-root",default=".")
 ap.add_argument("--ply-lo",type=int,default=12);ap.add_argument("--ply-hi",type=int,default=160)
 ap.add_argument("--game-limit",type=int,default=50000)
 ap.add_argument("--per-source-cell-cap",type=int,default=4)
 ap.add_argument("--max-positions-per-source",type=int,default=32)
 ap.add_argument("--out",required=True)
 a=ap.parse_args()
 specs=[]
 for raw in a.source:
  z=raw.split("|")
  if len(z)!=6:raise SystemExit("P23_SOURCE_SPEC")
  sid,path,url,digest,order,ecology=z
  specs.append((int(order),sid,path,url,digest,ecology))
 specs=sorted(specs)
 if len(specs)!=3 or [x[0] for x in specs]!=[1,2,3]:raise SystemExit("P23_REQUIRE_THREE_ORDERED_SOURCES")
 excluded,hfiles=p19.historical_hashes(a.history_root)
 pools={};audit={}
 for order,sid,path,url,digest,ecology in specs:
  pools[sid],audit[sid]=p19.source_candidates(path,sid,excluded,a.ply_lo,a.ply_hi,a.game_limit)
  audit[sid].update({"url":url,"source_sha256":digest,"order":order,"ecology":ecology})
 fs=defaultdict(set)
 for sid,pool in pools.items():
  for rows in pool.values():
   for r in rows:fs[r["candidate_sha256"]].add(sid)
 crossdup={h for h,ss in fs.items() if len(ss)>1}
 for sid,pool in pools.items():
  for cell in list(pool):pool[cell]=[r for r in pool[cell] if r["candidate_sha256"] not in crossdup]
 allcells=[(ph,br,ta) for ph in p19.PHASES for br in p19.BRANCHES for ta in p19.TACTICS]
 selected=[];bysrc={};gates={}
 for order,sid,*_ in specs:
  out=[];used=set();cells=[]
  for cell in allcells:
   rows=sorted(pools[sid].get(cell,[]),key=lambda r:(r["trajectory_hash"],r["candidate_sha256"]))
   take=[]
   for r in rows:
    if r["candidate_sha256"] in used:continue
    used.add(r["candidate_sha256"]);take.append(r)
    if len(take)>=a.per_source_cell_cap:break
   if take:cells.append(cell);out.extend(take)
   if len(out)>=a.max_positions_per_source:break
  out=out[:a.max_positions_per_source]
  phases=sorted({z["cell"]["phase"] for z in out});branches=sorted({z["cell"]["branching"] for z in out});tactics=sorted({z["cell"]["tactical_surface"] for z in out})
  gate={"positions":len(out),"phase_levels":phases,"branching_levels":branches,"tactical_levels":tactics,
        "pass":len(out)>=16 and len(phases)>=2 and len(branches)>=2 and len(tactics)>=2}
  gates[sid]=gate;bysrc[sid]=out;selected.extend(out)
 passed=all(g["pass"] for g in gates.values())
 out={"schema":"c3x-g10-p23-candidate-census-v1","stage":"C3X 0.10.0-G10-P23",
      "verdict":"PASS_P23_CANDIDATE_POOL" if passed else "HOLD_P23_CANDIDATE_POOL",
      "authority":"OUTCOME_BLIND_ACQUISITION_CANDIDATE_POOL_ONLY",
      "selection":{"activation_predictions_consulted":False,"full_class_outcomes_consulted":False,"q0_outcomes_consulted":False,
                   "history_exclusion":True,"cross_source_duplicate_exclusion":True,"per_source_cell_cap":a.per_source_cell_cap,
                   "max_positions_per_source":a.max_positions_per_source,"ply_range":[a.ply_lo,a.ply_hi]},
      "source_audit":audit,"history_hashes_excluded":len(excluded),"history_json_files_scanned":hfiles,
      "cross_source_duplicate_fens_excluded":len(crossdup),"source_gates":gates,
      "positions":sorted(selected,key=lambda r:(next(x[0] for x in specs if x[1]==r["source_id"]),r["cell"]["phase"],r["cell"]["branching"],r["cell"]["tactical_surface"],r["trajectory_hash"]))}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P23_CANDIDATE_CENSUS",out["verdict"],{k:v["positions"] for k,v in gates.items()})
 if not passed:raise SystemExit("P23_CANDIDATE_POOL_HOLD")
if __name__=="__main__":main()
