#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"harness"))
import g10_p20_class_screen as screen
import p32_event_court as p32

def load(p):return json.loads(Path(p).read_text())
def objects(root):
 out=[]
 for p in Path(root).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g10-p23-executable-support-world-v1":out.append(x)
 return out
def find_binary(root,e):
 xs=list(Path(root).rglob(f"c3x-p20-{e}"))
 if len(xs)!=1:raise SystemExit(f"P23_FULL_BUILD_{e}_{len(xs)}")
 xs[0].chmod(0o755);return xs[0]
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--prediction-seal",required=True);ap.add_argument("--support-root",required=True)
 ap.add_argument("--build-dir",required=True);ap.add_argument("--shard",type=int,required=True);ap.add_argument("--shards",type=int,required=True);ap.add_argument("--out-dir",required=True)
 a=ap.parse_args();P=load(a.prediction_seal);rows=objects(a.support_root);wm={(x["position_id"],e):x for x in rows for e in x["engines"]}
 preds=sorted(P["predictions"],key=lambda z:z["uid"]);out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True);n=0
 for i,pred in enumerate(preds):
  if i%a.shards!=a.shard:continue
  pid=pred["position_id"];e=pred["engine"];fam=pred["family"];w=wm.get((pid,e))
  if w is None:raise SystemExit("P23_FULL_JOIN "+pred["uid"])
  er=w["engines"][e]
  if not er.get("measurable"):raise SystemExit("P23_FULL_UNMEASURABLE "+pred["uid"])
  arm={"MOVE_ORDER":"NO_MOVE","CUTOFF":"NO_CUTOFF"}[fam]
  b=find_binary(a.build_dir,e);protocol=p32.protocol_for(e);A=w["pair"]["A"]["uci"];B=w["pair"]["B"]["uci"]
  res={}
  for mode in ("BASE",arm):
   boards={}
   for bn,key in (("TARGET","target_fen"),("SUBSET","subset_fen"),("SHAM","sham_fen")):
    boards[bn]=screen.measure(b,protocol,w["chain"][key],A,B,out/f".private-{i}-{mode}-{bn}",mode)
   res[mode]={"boards":boards,"supported":all(z["supported"] for z in boards.values())}
  expected=bool(er.get("base_supported"))
  base_ok=res["BASE"]["supported"]==expected
  activation=int(res[arm]["supported"]!=res["BASE"]["supported"]) if base_ok else None
  row={"schema":"c3x-g10-p23-full-class-row-v1","stage":"C3X 0.10.0-G10-P23","uid":pred["uid"],
       "position_id":pid,"source_id":pred["source_id"],"engine":e,"family":fam,"prediction":int(pred["prediction"]),
       "expected_support_seal_base":expected,"base_identity":base_ok,"base":res["BASE"],"full_class_arm":arm,"full_class":res[arm],
       "activation":activation,"q0_outcome_opened":False}
  (out/f"{i:03d}.json").write_text(json.dumps(row,indent=2,sort_keys=True)+"\n");n+=1
 print("P23_FULL_CLASS_SHARD",a.shard,"ROWS",n)
if __name__=="__main__":main()
