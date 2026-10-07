#!/usr/bin/env python3
from __future__ import annotations
import argparse,glob,json
from collections import defaultdict
from pathlib import Path

ORDER=["P23_PRAGUE_MASTERS_2026","P23_BIEL_OPEN_MASTERS_2026","P23_SAINT_LOUIS_RAPID_2026"]
ECOLOGY={
 "P23_PRAGUE_MASTERS_2026":"elite classical round-robin",
 "P23_BIEL_OPEN_MASTERS_2026":"large classical open/Swiss",
 "P23_SAINT_LOUIS_RAPID_2026":"elite rapid round-robin"
}
def load(p):return json.loads(Path(p).read_text())
def rows(root):
 out=[]
 for p in Path(root).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g10-p23-executable-support-world-v1":out.append(x)
 return out
def snapshot(rr,k):
 picked=[r for r in rr if int(r["source_rank"])<=k]
 bysrc=defaultdict(int);eng=set();positions=0;cells=[]
 for r in picked:
  measurable=sorted(e for e,v in r["engines"].items() if v.get("measurable"))
  if measurable:
   positions+=1
  for e in measurable:
   eng.add(e)
   for fam in ("MOVE_ORDER","CUTOFF"):
    bysrc[r["source_id"]]+=1
    cells.append({"position_id":r["position_id"],"source_id":r["source_id"],"source_rank":r["source_rank"],
                  "engine":e,"family":fam,"context":r["context"],"router_grammar":r["router_grammar"],
                  "base_supported":bool(r["engines"][e].get("base_supported"))})
 vals=[bysrc[s] for s in ORDER]
 ratio=(max(vals)/min(vals)) if min(vals)>0 else None
 passed=(all(v>=12 for v in vals) and len(cells)>=54 and positions>=18 and len(eng)>=2 and ratio is not None and ratio<=2.0)
 return {"cycle":k,"routed_chain_positions":positions,"engine_family_cells":len(cells),"cells_by_source":{s:bysrc[s] for s in ORDER},
         "engines":sorted(eng),"source_balance_ratio":ratio,"pass":passed,"cells":cells}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--candidate-census",required=True);ap.add_argument("--support-root",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
 c=load(a.candidate_census);rr=rows(a.support_root)
 if c.get("verdict")!="PASS_P23_CANDIDATE_POOL":raise SystemExit("P23_CANDIDATE_NOT_PASS")
 maxrank=max((int(z["source_rank"]) for z in rr),default=0);trail=[];sealed=None
 for k in range(1,maxrank+1):
  s=snapshot(rr,k);trail.append({x:s[x] for x in s if x!="cells"})
  if s["pass"] and sealed is None:sealed=s;break
 if sealed is None:
  final=snapshot(rr,maxrank) if maxrank else {"routed_chain_positions":0,"engine_family_cells":0,"cells_by_source":{s:0 for s in ORDER},"engines":[],"source_balance_ratio":None,"cells":[]}
  verdict="HOLD_P23_EXECUTABLE_SUPPORT"
  selected=[]
 else:
  final=sealed;verdict="PASS_P23_EXECUTABLE_SUPPORT";selected=sealed["cells"]
 out={"schema":"c3x-g10-p23-executable-support-seal-v1","stage":"C3X 0.10.0-G10-P23","verdict":verdict,
      "prefix_semantics":"CYCLIC_BALANCED_PREFIX","sealed_cycle":sealed["cycle"] if sealed else None,
      "frozen_quotas":{"sources":3,"ecologies":2,"routed_chain_positions":18,"engine_family_cells":54,
                       "per_source_engine_family_cells":12,"engines":2,"pairwise_source_balance_ratio_max":2.0},
      "source_ecologies":ECOLOGY,"trail":trail,
      "final_support":{k:final[k] for k in ("routed_chain_positions","engine_family_cells","cells_by_source","engines","source_balance_ratio")},
      "selected_support_cells":selected,
      "activation_predictions_consulted":False,"full_class_outcomes_consulted":False,"q0_outcomes_consulted":False}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P23_SUPPORT_SEAL",verdict,json.dumps(out["final_support"],sort_keys=True),"CYCLE",out["sealed_cycle"])
 if verdict!="PASS_P23_EXECUTABLE_SUPPORT":raise SystemExit("P23_EXECUTABLE_SUPPORT_HOLD")
if __name__=="__main__":main()
