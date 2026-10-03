#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path

def load(p):return json.loads(Path(p).read_text())
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--defects",required=True)
 ap.add_argument("--policy",required=True)
 ap.add_argument("--out",required=True)
 a=ap.parse_args()
 d=load(a.defects);p=load(a.policy)
 rows=[x for x in d["cell_summary"] if x["source_count"]>=3]
 contexts={ (x["phase"],x["branching"],x["tactical_surface"]) for x in rows }
 pairs={x["engine_pair"] for x in rows}
 g=p["identifiability_gate"]
 support=(len(rows)>=g["min_context_enginepair_edit_cells_with_at_least_3_sources"]
          and len(contexts)>=g["min_distinct_context_cells"]
          and len(pairs)>=g["min_engine_pairs_represented"])
 recurrent=[x for x in rows if x["all_source_defect"]]
 rec_contexts={ (x["phase"],x["branching"],x["tactical_surface"]) for x in recurrent }
 rec_pairs={x["engine_pair"] for x in recurrent}
 total_defects=sum(x["defects"] for x in rows)
 strong=p["recurrence"]["strong_candidate"]
 if not support:
  verdict="HOLD_CONTEXT_BALANCED_DEFECT_SUPPORT_INSUFFICIENT"
 elif total_defects==0:
  verdict="DEVELOPMENT_CONTEXT_BALANCED_DEFECTS_COLLAPSE"
 elif (len(recurrent)>=strong["min_recurrent_cells"]
       and len(rec_contexts)>=strong["min_distinct_chess_contexts"]
       and len(rec_pairs)>=strong["min_engine_pairs"]):
  verdict="DEVELOPMENT_CONTEXT_BALANCED_DEFECT_RECURRENCE"
 else:
  verdict="DEVELOPMENT_CONTEXT_BALANCED_ENGINE_RELATIVE_DEFECTS_PERSIST"
 out={
  "schema":"c3x-g10-p14-stage-c-readout-v1","verdict":verdict,
  "support_cells":len(rows),"distinct_contexts":len(contexts),"engine_pairs":sorted(pairs),
  "total_defects":total_defects,"recurrent_cells":len(recurrent),
  "recurrent_contexts":len(rec_contexts),"recurrent_engine_pairs":sorted(rec_pairs),
  "supported_cell_rows":rows,"recurrent_cell_rows":recurrent,
  "authority":"DEVELOPMENT_CONTEXT_BALANCED_DEFECT_COMPARISON_ONLY"
 }
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G10_P14_STAGE_C",verdict)
 print("SUPPORT",len(rows),len(contexts),sorted(pairs))
 print("RECURRENT",len(recurrent),len(rec_contexts),sorted(rec_pairs),"DEFECTS",total_defects)
if __name__=="__main__":main()
