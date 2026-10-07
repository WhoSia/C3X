#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from pathlib import Path

SOURCE_META={
 "P23_PRAGUE_MASTERS_2026":{"time_control_class":"CLASSICAL","field_structure_class":"ROUND_ROBIN_OR_CLOSED"},
 "P23_BIEL_OPEN_MASTERS_2026":{"time_control_class":"CLASSICAL","field_structure_class":"OPEN_OR_SWISS"},
 "P23_SAINT_LOUIS_RAPID_2026":{"time_control_class":"RAPID","field_structure_class":"ROUND_ROBIN_OR_CLOSED"},
}
CANDIDATES={
 "C0_GLOBAL":["r1"],
 "C1_ENGINE":["r1","eng_berserk","eng_ethereal"],
 "C2_ECOLOGY":["r1","is_rapid","is_open"],
 "C3_ENGINE_ECOLOGY":["r1","eng_berserk","eng_ethereal","is_rapid","is_open"],
}
LAMBDAS=[0.1,1.0,10.0]
THRESHOLDS=[0.20,0.25,0.30,0.35,0.40,0.45,0.50]

def load(p): return json.loads(Path(p).read_text())
def rows(root,schema):
 out=[]
 for p in Path(root).rglob("*.json"):
  try:x=load(p)
  except Exception:continue
  if x.get("schema")==schema:out.append(x)
 return out
def sig(z):
 if z>=0:
  q=math.exp(-z);return 1/(1+q)
 q=math.exp(z);return q/(1+q)
def feats(r,names):
 vals={"r1":float(r["prediction"]),
       "eng_berserk":float(r["engine"]=="berserk"),
       "eng_ethereal":float(r["engine"]=="ethereal"),
       "is_rapid":float(r["time_control_class"]=="RAPID"),
       "is_open":float(r["field_structure_class"]=="OPEN_OR_SWISS")}
 return [1.0]+[vals[n] for n in names]
def fit(train,names,lam):
 p=len(names)+1;w=[0.0]*p;lr=0.08
 for _ in range(12000):
  g=[0.0]*p
  for r in train:
   x=feats(r,names);e=sig(sum(a*b for a,b in zip(w,x)))-r["activation"]
   for j in range(p):g[j]+=e*x[j]
  for j in range(1,p):g[j]+=lam*w[j]
  scale=max(1,len(train))
  step=max(abs(v)/scale for v in g)
  for j in range(p):w[j]-=lr*g[j]/scale
  if step<1e-8:break
 return w
def predict(w,r,names):return sig(sum(a*b for a,b in zip(w,feats(r,names))))
def logloss(ps,ys):
 eps=1e-12
 return -sum(y*math.log(max(eps,min(1-eps,p)))+(1-y)*math.log(max(eps,min(1-eps,1-p))) for p,y in zip(ps,ys))/len(ys)
def metrics(ps,ys,t):
 pred=[int(p>=t) for p in ps]
 tp=sum(a==1 and y==1 for a,y in zip(pred,ys));fn=sum(a==0 and y==1 for a,y in zip(pred,ys))
 tn=sum(a==0 and y==0 for a,y in zip(pred,ys));fp=sum(a==1 and y==0 for a,y in zip(pred,ys))
 rec=tp/(tp+fn) if tp+fn else None;spec=tn/(tn+fp) if tn+fp else None
 ba=(rec+spec)/2 if rec is not None and spec is not None else None
 brier=sum((p-y)**2 for p,y in zip(ps,ys))/len(ys)
 return {"tp":tp,"fn":fn,"tn":tn,"fp":fp,"positive_recall":rec,"negative_specificity":spec,"balanced_accuracy":ba,"brier":brier}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--prediction-seal",required=True);ap.add_argument("--full-rows",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
 P=load(a.prediction_seal);pm={x["uid"]:x for x in P["predictions"]}
 rr=rows(a.full_rows,"c3x-g10-p23-full-class-row-v1")
 data=[]
 for r in rr:
  p=pm[r["uid"]];src=r["source_id"]
  if src not in SOURCE_META:raise SystemExit("P24_DEV_UNKNOWN_SOURCE "+src)
  z={"uid":r["uid"],"source_id":src,"engine":r["engine"],"family":r["family"],
     "prediction":int(r["prediction"]),"activation":int(r["activation"]),**SOURCE_META[src]}
  data.append(z)
 if len(data)!=100:raise SystemExit("P24_DEV_EXPECTED_100")
 sources=sorted(SOURCE_META)
 report={}
 for cid,names in CANDIDATES.items():
  report[cid]={}
  for lam in LAMBDAS:
   held=[]
   folds={}
   for src in sources:
    tr=[r for r in data if r["source_id"]!=src];te=[r for r in data if r["source_id"]==src]
    w=fit(tr,names,lam);ps=[predict(w,r,names) for r in te];ys=[r["activation"] for r in te]
    ll=logloss(ps,ys);held.extend(zip(ps,ys))
    folds[src]={"n":len(te),"log_loss":ll,"coefficients":w}
   ps=[p for p,_ in held];ys=[y for _,y in held]
   entry={"mean_heldout_log_loss":logloss(ps,ys),"folds":folds,"thresholds":{}}
   for t in THRESHOLDS:entry["thresholds"][str(t)]=metrics(ps,ys,t)
   report[cid][str(lam)]=entry
 best=min((v["mean_heldout_log_loss"],cid,lam) for cid in report for lam,v in ((float(k),vv) for k,vv in report[cid].items()))
 out={"schema":"c3x-g10-p24-development-calibration-audit-v1","stage":"C3X 0.10.0-G10-P24",
      "authority":"DEVELOPMENT_DIAGNOSTIC_ONLY_NO_P24_SCIENTIFIC_AUTHORITY",
      "source_identity_predictor_used":False,"p23_rows":len(data),
      "candidate_features":CANDIDATES,"penalty_grid":LAMBDAS,"threshold_grid":THRESHOLDS,
      "best_raw_development_candidate":{"mean_heldout_log_loss":best[0],"candidate":best[1],"penalty":best[2]},
      "report":report,
      "interpretation_ceiling":[
       "P23 is development data only; these coefficients are never used for P24 transfer adjudication.",
       "P24 calibration coefficients must be fit from the separately presealed P24 calibration cohort.",
       "No source identity or tournament-specific one-hot is admissible."
      ]}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P24_DEV_CALIBRATION_AUDIT",json.dumps(out["best_raw_development_candidate"],sort_keys=True))
if __name__=="__main__":main()
