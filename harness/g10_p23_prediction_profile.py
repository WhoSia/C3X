#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"));sys.path.insert(0,str(ROOT/"harness"))
import p32_event_court as p32
import g10_p21_phase_e_carrier as carrier
import g10_p22_profile_census as prof

def load(p):return json.loads(Path(p).read_text())
def objects(root):
 out=[]
 for p in Path(root).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g10-p23-executable-support-world-v1":out.append(x)
 return out
def predict(r):
 g=float(r["base_max_gap_cp"]);imb=float(r["candidate_side_event_imbalance"]);t=float(r["family_event_count_target"])
 if g>74.5:return 0
 if g<=30.5:return int(imb>0.19)
 return int(t>1926.5)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--seal",required=True);ap.add_argument("--support-root",required=True)
 ap.add_argument("--build-dir",required=True);ap.add_argument("--shard",type=int,required=True);ap.add_argument("--shards",type=int,required=True);ap.add_argument("--out-dir",required=True)
 a=ap.parse_args();S=load(a.seal);rows=objects(a.support_root);idx={(x["position_id"],e):x for x in rows for e in x["engines"]}
 cells=sorted(S["selected_support_cells"],key=lambda z:(z["source_id"],z["position_id"],z["engine"],z["family"]))
 out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True);n=0
 for i,c in enumerate(cells):
  if i%a.shards!=a.shard:continue
  w=idx.get((c["position_id"],c["engine"]))
  if w is None:raise SystemExit("P23_PROFILE_JOIN "+c["position_id"]+" "+c["engine"])
  e=c["engine"];fam=c["family"];er=w["engines"][e]
  if not er.get("measurable"):raise SystemExit("P23_PROFILE_UNMEASURABLE "+c["position_id"]+" "+e)
  b=carrier.find_binary(a.build_dir,e);protocol=p32.protocol_for(e)
  dyn=prof.profile(b,protocol,w["chain"],w["pair"],fam,out/f".private-{i}-{e}-{fam}")
  row={"schema":"c3x-g10-p23-activation-prediction-profile-v1","stage":"C3X 0.10.0-G10-P23",
       "uid":c["position_id"]+"||"+e+"||"+fam,"position_id":c["position_id"],"source_id":c["source_id"],
       "engine":e,"family":fam,"context":c["context"],"router_grammar":c["router_grammar"],
       **prof.boundary(er["boards"]),**dyn,
       "full_class_outcome_opened":False,"q0_outcome_opened":False}
  row["prediction"]=predict(row)
  (out/f"{i:03d}.json").write_text(json.dumps(row,indent=2,sort_keys=True)+"\n");n+=1
 print("P23_PREDICTION_PROFILE_SHARD",a.shard,"ROWS",n)
if __name__=="__main__":main()
