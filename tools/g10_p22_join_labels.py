#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter,defaultdict

def load(p): return json.loads(Path(p).read_text())
def objs(root):
    out=[]
    for p in Path(root).rglob("*.json"):
        try:o=load(p)
        except:continue
        out.append(o)
    return out
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--profiles",required=True);ap.add_argument("--p20-int",required=True);ap.add_argument("--p21-int",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args()
    ps=[o for o in objs(a.profiles) if o.get("schema")=="c3x-g10-p22-preintervention-profile-v1"]
    p20={o["case_id"]:o for o in objs(a.p20_int) if o.get("schema")=="c3x-g10-p20-class-screen-row-v1"}
    p21={(o["position_id"],o["engine"],o["family"]):o for o in objs(a.p21_int) if o.get("schema")=="c3x-g10-p21-fresh-transport-cell-v1"}
    rows=[];missing=[];unstable=[]
    for x in sorted(ps,key=lambda z:z["uid"]):
        if not x["feature_repeatable"]:unstable.append(x["uid"])
        y=dict(x);y["activation_label_present"]=True
        if x["origin"]=="P20":
            case,fam=x["uid"].rsplit("||",1);src=p20.get(case)
            if src is None:missing.append(x["uid"]);continue
            arm={"MOVE_ORDER":"NO_MOVE","CUTOFF":"NO_CUTOFF"}[fam]
            base=(x["base_support_pattern"]=="111");klass=bool(src["arms"][arm]["supported"])
        else:
            z=p21.get((x["position_id"],x["engine"],x["family"]))
            if z is None:missing.append(x["uid"]);continue
            base=bool(z["base_support"]);klass=bool(z["class_support"])
        y["base_support"]=base;y["full_class_support"]=klass;y["activation"]=int(base!=klass)
        rows.append(y)
    byfam=defaultdict(Counter);byeng=defaultdict(Counter);bysrc=defaultdict(Counter)
    for r in rows:
        byfam[r["family"]][r["activation"]]+=1;byeng[r["engine"]][r["activation"]]+=1;bysrc[r["source_id"]][r["activation"]]+=1
    positives=[r for r in rows if r["activation"]==1];neg=len(rows)-len(positives)
    gate={
      "rows":len(rows),"positives":len(positives),"negatives":neg,
      "positive_engines":sorted({r["engine"] for r in positives}),
      "positive_sources":sorted({r["source_id"] for r in positives}),
      "family_counts":{k:dict(v) for k,v in byfam.items()},
      "engine_counts":{k:dict(v) for k,v in byeng.items()},
      "source_counts":{k:dict(v) for k,v in bysrc.items()},
      "missing_labels":missing,"unstable_profiles":unstable
    }
    fam_ok=any(v.get(1,0)>=4 for v in byfam.values())
    passed=(not missing and not unstable and len(positives)>=8 and neg>=24 and len(gate["positive_engines"])>=2 and len(gate["positive_sources"])>=2 and fam_ok)
    out={"schema":"c3x-g10-p22-development-dataset-v1","stage":"C3X 0.10.0-G10-P22",
         "verdict":"PASS_DEVELOPMENT_SUPPORT" if passed else "HOLD_DEVELOPMENT_SUPPORT",
         "profile_target_firewall":True,"gate":gate,"rows":rows}
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"verdict":out["verdict"],"gate":gate},indent=2,sort_keys=True))
    if not passed: raise SystemExit("P22_DEVELOPMENT_HOLD")
if __name__=="__main__":main()
