#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,statistics
from collections import defaultdict
from pathlib import Path

def load(p):return json.loads(Path(p).read_text())
def rows(root,schema):
 out=[]
 for p in Path(root).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")==schema:out.append(x)
 return out
def metric(xs):
 tp=sum(x["activation"]==1 and x["prediction"]==1 for x in xs)
 fn=sum(x["activation"]==1 and x["prediction"]==0 for x in xs)
 tn=sum(x["activation"]==0 and x["prediction"]==0 for x in xs)
 fp=sum(x["activation"]==0 and x["prediction"]==1 for x in xs)
 rec=tp/(tp+fn) if tp+fn else None;spec=tn/(tn+fp) if tn+fp else None
 ba=(rec+spec)/2 if rec is not None and spec is not None else None
 pred_rate=sum(x["prediction"] for x in xs)/len(xs) if xs else None
 obs_rate=sum(x["activation"] for x in xs)/len(xs) if xs else None
 return {"n":len(xs),"tp":tp,"fn":fn,"tn":tn,"fp":fp,"balanced_accuracy":ba,
         "positive_recall":rec,"negative_specificity":spec,
         "predicted_active_rate":pred_rate,"observed_activation_rate":obs_rate,
         "activation_calibration_offset":(obs_rate-pred_rate) if xs else None}
def fstats(xs):
 out={}
 for f in ("base_max_gap_cp","candidate_side_event_imbalance","family_event_count_target"):
  vals=[float(x[f]) for x in xs]
  out[f]={"mean":sum(vals)/len(vals),"median":statistics.median(vals),"min":min(vals),"max":max(vals)}
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--full-rows",required=True);ap.add_argument("--prediction-seal",required=True);ap.add_argument("--primary",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
 rr=rows(a.full_rows,"c3x-g10-p23-full-class-row-v1");P=load(a.prediction_seal);A=load(a.primary)
 pm={x["uid"]:x for x in P["predictions"]}
 joined=[]
 for r in rr:
  p=pm[r["uid"]];z=dict(r);z.update({k:p[k] for k in ("base_max_gap_cp","candidate_side_event_imbalance","family_event_count_target")});joined.append(z)
 if len(joined)!=100 or A.get("verdict")!="FAIL_P23_ACTIVATION_TRANSPORT":raise SystemExit("P23_SECONDARY_INPUT")
 def group(key):
  out={}
  for v in sorted({x[key] for x in joined}):
   xs=[x for x in joined if x[key]==v]
   out[v]={"metrics":metric(xs),"features":fstats(xs)}
  return out
 sf={}
 for s in sorted({x["source_id"] for x in joined}):
  sf[s]={}
  for f in ("MOVE_ORDER","CUTOFF"):
   xs=[x for x in joined if x["source_id"]==s and x["family"]==f]
   sf[s][f]=metric(xs)
 out={"schema":"c3x-g10-p23-secondary-diagnostic-v1","stage":"C3X 0.10.0-G10-P23",
      "primary_verdict":A["verdict"],"authority":"POST_PRIMARY_DIAGNOSTIC_ONLY_NO_RESCUE",
      "overall":metric(joined),"by_source":group("source_id"),"by_family":group("family"),"by_engine":group("engine"),"source_by_family":sf,
      "diagnostic_questions":[
       "Is failure concentrated in one engine or mediator family?",
       "Does source ecology primarily alter activation prevalence/calibration?",
       "Are feature distributions shifted across sources?"
      ],
      "forbidden":["refit R1","change thresholds","drop source","family rescue","upgrade primary verdict","Q0 re-entry"]}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
