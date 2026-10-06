#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import g10_p19_engine_support as p19

def load(p):return json.loads(Path(p).read_text())
def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def find_binary(root,e):
 xs=list(Path(root).rglob(f"c3x-p16-{e}"))
 if len(xs)!=1:raise SystemExit(f"P21_BUILD_{e}_{len(xs)}")
 xs[0].chmod(0o755);return xs[0]
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--corpus",required=True);ap.add_argument("--pair-freeze",required=True);ap.add_argument("--build-dir",required=True);ap.add_argument("--shard",type=int,required=True);ap.add_argument("--shards",type=int,required=True);ap.add_argument("--out-dir",required=True);a=ap.parse_args()
 corp=load(a.corpus);pf=load(a.pair_freeze)
 bypid={f"p21:{z['source_id']}:{z['trajectory_hash'][:12]}":z for z in corp["positions"]}
 admitted=[(pid,z) for pid,z in sorted(pf["positions"].items()) if z.get("admitted")]
 out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True);n=0
 for idx,(pid,z) in enumerate(admitted):
  if idx%a.shards!=a.shard:continue
  meta=bypid[pid];pair=z["pair"];route=meta["router_grammar"];ch=p19.choose_chain(meta["fen"],pair,route)
  active=sorted(e for e,v in z.get("engine_views",{}).items() if v.get("active"));eng={}
  for e in active:
   b=find_binary(a.build_dir,e)
   if sha_file(b)!=pf["variants"][e]["sha256"]:raise SystemExit(f"P21_SHA_{e}")
   if ch is None:eng[e]={"structural":False,"supported":False,"boards":None};continue
   A=pair["A"]["uci"];B=pair["B"]["uci"];root=out/f".private-{idx}-{e}"
   boards={"TARGET":p19.ps.measure(b,pf["variants"][e]["protocol"],ch["target_fen"],A,B,20000,2,root,"target"),
           "SUBSET":p19.ps.measure(b,pf["variants"][e]["protocol"],ch["subset_fen"],A,B,20000,2,root,"subset"),
           "SHAM":p19.ps.measure(b,pf["variants"][e]["protocol"],ch["sham_fen"],A,B,20000,2,root,"sham")}
   eng[e]={"structural":True,"supported":all(v["supported"] for v in boards.values()),"boards":boards}
  row={"schema":"c3x-g10-p21-phase-e-chain-world-v1","stage":"C3X 0.10.0-G10-P21","position_id":pid,"source_id":z["source_id"],"context":meta["context"],"router_grammar":route,"pair":pair,"active_engines":active,"chain":ch,"engines":eng,"p21_intervention_outcomes_consulted":False}
  (out/f"{idx:03d}.json").write_text(json.dumps(row,indent=2,sort_keys=True)+"\n");n+=1
 print("P21_CHAIN_SHARD",a.shard,n)
if __name__=="__main__":main()
