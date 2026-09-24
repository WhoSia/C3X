#!/usr/bin/env python3
"""Post-HOLD exposure-balance feasibility witness for P21.

This is explicitly NON-AUTHORITATIVE for P21 causal inference. It consumes only
SHAM census telemetry and the already-frozen failed core precommit. It asks a
design-feasibility question: does any simple deterministic within-stratum swap
path reach the original <=0.50 SMD gate while preserving 6-per-side-per-vertex?
If yes, the P21 HOLD localizes to the frozen selector rather than to absence of
support in the constituted pool. It must not be used to reopen P21.
"""
import argparse,json,math
from pathlib import Path
from collections import defaultdict

FEATURES=tuple(
 f"{t}:{kind}"
 for t in ("stockfish_19","berserk","ethereal")
 for kind in ("LOG_MAIN","LOG_Q","Q_SHARE")
)
THRESHOLD=0.50

def smd(a,b):
 ma=sum(a)/len(a);mb=sum(b)/len(b)
 va=sum((x-ma)**2 for x in a)/(len(a)-1)
 vb=sum((x-mb)**2 for x in b)/(len(b)-1)
 den=math.sqrt((va+vb)/2)
 if den<=1e-15:return 0.0 if abs(ma-mb)<1e-12 else float("inf")
 return abs(ma-mb)/den

def metrics(rows,selected):
 h=[rows[s] for s in selected if rows[s]["square"]=="HEAVY_HEAVY"]
 m=[rows[s] for s in selected if rows[s]["square"]=="MINOR_MINOR"]
 vals={k:smd([r["features"][k] for r in h],[r["features"][k] for r in m]) for k in FEATURES}
 return max(vals.values()),vals

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--precommit",required=True)
 ap.add_argument("--census-dir",required=True)
 ap.add_argument("--out",required=True)
 a=ap.parse_args()
 pre=json.loads(Path(a.precommit).read_text())
 if pre.get("authorization")!="P21-CORE-HOLD" or pre.get("selective_outcomes_consulted") is not False:
  raise SystemExit("P21_DIAG_REQUIRES_FROZEN_PREOUTCOME_HOLD")
 fs=sorted(Path(a.census_dir).rglob("p21-core-census-*.json"))
 if len(fs)!=8:raise SystemExit(f"P21_DIAG_CENSUS_COUNT {len(fs)}/8")
 rows={};strata=defaultdict(list)
 for p in fs:
  x=json.loads(p.read_text())
  if x.get("selective_outcomes_consulted") is not False:raise SystemExit("P21_DIAG_OUTCOME_LEAK")
  for r in x["rows"]:
   if not r["all_p20_targets_engaged"]:continue
   c=r["candidate"];s=c["candidate_sha256"]
   rows[s]={
    "sha":s,"family":c["material_seed_name"],"side":c["side_to_move"],"square":c["square"],
    "features":r["features"],
    "inanis_tt_main":int(r["inanis_sham"]["engagement"]["TT_MAIN"]),
    "inanis_pawn_q":int(r["inanis_sham"]["engagement"]["PAWN_Q"])
   }
   strata[(c["material_seed_name"],c["side_to_move"])].append(s)
 selected={r["candidate"]["candidate_sha256"] for r in pre["committed_cells"]}
 if len(selected)!=96 or any(s not in rows for s in selected):raise SystemExit("P21_DIAG_PRECOMMIT_IDENTITY")
 for key,pool in strata.items():
  if sum(s in selected for s in pool)!=6:raise SystemExit("P21_DIAG_STRATUM_QUOTA "+str(key))
 start,start_vec=metrics(rows,selected)
 history=[];steps=0
 while steps<100:
  cur,curvec=metrics(rows,selected)
  best=None
  for key in sorted(strata):
   inside=sorted(s for s in strata[key] if s in selected)
   outside=sorted(s for s in strata[key] if s not in selected)
   for out_sha in inside:
    for in_sha in outside:
     cand=set(selected);cand.remove(out_sha);cand.add(in_sha)
     val,vec=metrics(rows,cand)
     item=(val,in_sha,out_sha,vec,key)
     if best is None or item[:3]<best[:3]:best=item
  if best is None or best[0]>=cur-1e-12:break
  val,in_sha,out_sha,vec,key=best
  selected.remove(out_sha);selected.add(in_sha);steps+=1
  history.append({"step":steps,"stratum":{"family":key[0],"side":key[1]},"out":out_sha,"in":in_sha,"max_smd":val,"smd":vec})
  if val<=THRESHOLD+1e-12:break
 final,final_vec=metrics(rows,selected)
 engagement=all(rows[s]["inanis_tt_main"]>0 and rows[s]["inanis_pawn_q"]>0 for s in selected)
 out={
  "schema":"c3x-p21-post-hold-exposure-feasibility-v1",
  "scientific_stage":"C3X 0.7.0-G9.4-P21",
  "authority":"POST_HOLD_NONAUTHORITATIVE_DESIGN_DIAGNOSTIC",
  "may_reopen_p21":False,
  "selective_intervention_outcomes_consulted":False,
  "source_precommit_sha256":pre["precommit_sha256"],
  "original_authorization":pre["authorization"],
  "threshold":THRESHOLD,
  "start_max_smd":start,"start_smd":start_vec,
  "steps":steps,
  "final_max_smd":final,"final_smd":final_vec,
  "feasible_witness_found":final<=THRESHOLD+1e-12,
  "quota_preserved":"6 per side per material vertex",
  "inanis_postselection_engagement_gate_pass":engagement,
  "selected_candidate_sha256":sorted(selected),
  "swap_history":history,
  "interpretation":"If feasible_witness_found=true, P21 remains HOLD because its selector was frozen; the result only shows that lack of pool support is not the reason for the balance failure."
 }
 Path(a.out).parent.mkdir(parents=True,exist_ok=True)
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P21_EXPOSURE_FEASIBILITY",json.dumps({k:out[k] for k in ("steps","start_max_smd","final_max_smd","feasible_witness_found","inanis_postselection_engagement_gate_pass")},sort_keys=True))

if __name__=="__main__":main()
