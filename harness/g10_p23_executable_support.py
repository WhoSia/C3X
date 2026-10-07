#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"));sys.path.insert(0,str(ROOT/"harness"))
import g10_p19_engine_support as p19

def load(p):return json.loads(Path(p).read_text())
def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def find_binary(root,e):
 xs=list(Path(root).rglob(f"c3x-p16-{e}"))
 if len(xs)!=1:raise SystemExit(f"P23_BUILD_{e}_{len(xs)}")
 xs[0].chmod(0o755);return xs[0]
def measurable(boards):
 for b in boards.values():
  if not b.get("legal_pair"):return False
  if b.get("gap_cp_abs") is None:return False
  if not all(v.get("stable") for v in b.get("pair",{}).values()):return False
 return True
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--corpus",required=True);ap.add_argument("--pair-freeze",required=True);ap.add_argument("--build-dir",required=True)
 ap.add_argument("--shard",type=int,required=True);ap.add_argument("--shards",type=int,required=True);ap.add_argument("--out-dir",required=True);a=ap.parse_args()
 corp=load(a.corpus);pf=load(a.pair_freeze)
 bypid={f"p23:{z['source_id']}:{z['trajectory_hash'][:12]}":z for z in corp["positions"]}
 admitted=[(pid,z) for pid,z in sorted(pf["positions"].items()) if z.get("admitted")]
 out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True);n=0
 for idx,(pid,z) in enumerate(admitted):
  if idx%a.shards!=a.shard:continue
  meta=bypid.get(pid)
  if meta is None:raise SystemExit("P23_META_"+pid)
  pair=z["pair"];ch=p19.choose_chain(meta["fen"],pair,meta["router_grammar"])
  active=sorted(e for e,v in z.get("engine_views",{}).items() if v.get("active"));eng={}
  for e in active:
   b=find_binary(a.build_dir,e)
   if sha_file(b)!=pf["variants"][e]["sha256"]:raise SystemExit("P23_SHA_"+e)
   if ch is None:
    eng[e]={"measurable":False,"reason":"ROUTED_CHAIN_UNAVAILABLE","boards":None}
    continue
   A=pair["A"]["uci"];B=pair["B"]["uci"];root=out/f".private-{idx}-{e}"
   boards={"TARGET":p19.ps.measure(b,pf["variants"][e]["protocol"],ch["target_fen"],A,B,20000,2,root,"target"),
           "SUBSET":p19.ps.measure(b,pf["variants"][e]["protocol"],ch["subset_fen"],A,B,20000,2,root,"subset"),
           "SHAM":p19.ps.measure(b,pf["variants"][e]["protocol"],ch["sham_fen"],A,B,20000,2,root,"sham")}
   eng[e]={"measurable":measurable(boards),"reason":None if measurable(boards) else "BASE_MEASUREMENT_UNSTABLE_OR_ILLEGAL","boards":boards,
           "base_supported":all(v["supported"] for v in boards.values())}
  row={"schema":"c3x-g10-p23-executable-support-world-v1","stage":"C3X 0.10.0-G10-P23","position_id":pid,"source_id":meta["source_id"],
       "source_rank":meta["source_rank"],"source_order":meta["source_order"],"context":meta["context"],"router_grammar":meta["router_grammar"],
       "pair":pair,"chain":ch,"active_engines":active,"engines":eng,
       "activation_predictions_consulted":False,"full_class_outcomes_consulted":False,"q0_outcomes_consulted":False}
  (out/f"{idx:03d}.json").write_text(json.dumps(row,indent=2,sort_keys=True)+"\n");n+=1
 print("P23_SUPPORT_SHARD",a.shard,n)
if __name__=="__main__":main()
