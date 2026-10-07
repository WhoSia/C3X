#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import defaultdict
from pathlib import Path

def load(p):return json.loads(Path(p).read_text())
def rows(root):
 out=[]
 for p in Path(root).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g10-p23-full-class-row-v1":out.append(x)
 return out
def metrics(xs):
 tp=sum(r["activation"]==1 and r["prediction"]==1 for r in xs)
 fn=sum(r["activation"]==1 and r["prediction"]==0 for r in xs)
 tn=sum(r["activation"]==0 and r["prediction"]==0 for r in xs)
 fp=sum(r["activation"]==0 and r["prediction"]==1 for r in xs)
 rec=tp/(tp+fn) if tp+fn else None;spec=tn/(tn+fp) if tn+fp else None
 ba=(rec+spec)/2 if rec is not None and spec is not None else None
 return {"n":len(xs),"positives":tp+fn,"negatives":tn+fp,"tp":tp,"fn":fn,"tn":tn,"fp":fp,
         "balanced_accuracy":ba,"positive_recall":rec,"negative_specificity":spec}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--rows",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
 rr=rows(a.rows)
 if len(rr)!=100:raise SystemExit(f"P23_FINAL_ROW_COUNT {len(rr)}")
 bad=[r["uid"] for r in rr if r.get("base_identity") is not True or r.get("activation") is None]
 pooled=metrics(rr) if not bad else None
 bysrc={}
 if not bad:
  for s in sorted({r["source_id"] for r in rr}):bysrc[s]=metrics([r for r in rr if r["source_id"]==s])
 eligible=[s for s,m in bysrc.items() if m["positives"]>0 and m["negatives"]>0]
 robust=[s for s in eligible if bysrc[s]["balanced_accuracy"] is not None and bysrc[s]["balanced_accuracy"]>=0.60]
 if bad:
  verdict="HOLD_INSTRUMENT_TRANSPARENCY"
 elif pooled["positives"]==0:
  verdict="HOLD_NO_POSITIVE_ACTIVATION"
 else:
  pooled_pass=(pooled["balanced_accuracy"]>=0.70 and pooled["positive_recall"]>=0.50 and pooled["negative_specificity"]>=0.70)
  source_pass=len(robust)>=2
  if pooled_pass and source_pass:verdict="PASS_P23_ACTIVATION_TRANSPORT"
  elif pooled_pass:verdict="PARTIAL_PASS_P23_ACTIVATION_TRANSPORT_SOURCE_ROBUSTNESS"
  else:verdict="FAIL_P23_ACTIVATION_TRANSPORT"
 out={"schema":"c3x-g10-p23-final-adjudication-v1","stage":"C3X 0.10.0-G10-P23","verdict":verdict,
      "row_count":len(rr),"base_identity_failures":bad,"pooled":pooled,"by_source":bysrc,
      "sources_with_both_classes":eligible,"sources_passing_ba_0_60":robust,
      "frozen_thresholds":{"balanced_accuracy":0.70,"positive_recall":0.50,"negative_specificity":0.70,
                           "source_balanced_accuracy":0.60,"source_count_with_both_classes":2},
      "q0_outcomes_consulted":False,
      "interpretation_rule":"Primary prospective verdict only. No post-outcome refit, family rescue, source exclusion, or calibration rescue."}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
