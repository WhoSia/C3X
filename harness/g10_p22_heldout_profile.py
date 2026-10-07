#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"));sys.path.insert(0,str(ROOT/"harness"))
import g10_p19_engine_support as p19
import g10_p21_phase_e_carrier as carrier
import g10_p22_profile_census as prof

def load(p):return json.loads(Path(p).read_text())
def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def find_p16(root,e):
 xs=list(Path(root).rglob(f"c3x-p16-{e}"))
 if len(xs)!=1:raise SystemExit(f"P22_P16_BUILD_{e}_{len(xs)}")
 xs[0].chmod(0o755);return xs[0]
def find_p20c(root,e):
 xs=list(Path(root).rglob(f"c3x-p20c-{e}"))
 if len(xs)!=1:raise SystemExit(f"P22_P20C_BUILD_{e}_{len(xs)}")
 xs[0].chmod(0o755);return xs[0]
def pid(z):return f"p22:{z['source_id']}:{z['trajectory_hash'][:12]}"
def predict(r):
 g=float(r["base_max_gap_cp"]);imb=float(r["candidate_side_event_imbalance"]);t=float(r["family_event_count_target"])
 if g>74.5:return 0
 if g<=30.5:return int(imb>0.19)
 return int(t>1926.5)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--corpus",required=True);ap.add_argument("--pair-freeze",required=True)
 ap.add_argument("--p16-build-dir",required=True);ap.add_argument("--p20c-build-dir",required=True)
 ap.add_argument("--shard",type=int,required=True);ap.add_argument("--shards",type=int,required=True);ap.add_argument("--out-dir",required=True)
 a=ap.parse_args();corp=load(a.corpus);pf=load(a.pair_freeze);meta={pid(z):z for z in corp["positions"]}
 admitted=[(p,z) for p,z in sorted(pf["positions"].items()) if z.get("admitted")]
 out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True);n=0
 for idx,(p,z) in enumerate(admitted):
  if idx%a.shards!=a.shard:continue
  m=meta[p];pair=z["pair"];route=m["router_grammar"];ch=p19.choose_chain(m["fen"],pair,route)
  if ch is None:raise SystemExit("P22_CHAIN_NONE "+p)
  A=pair["A"]["uci"];B=pair["B"]["uci"]
  for e,v in sorted(z["engine_views"].items()):
   if not v.get("active"):continue
   b=find_p16(a.p16_build_dir,e)
   if sha_file(b)!=pf["variants"][e]["sha256"]:raise SystemExit("P22_SHA_"+e)
   root=out/f".private-base-{idx}-{e}"
   boards={"TARGET":p19.ps.measure(b,pf["variants"][e]["protocol"],ch["target_fen"],A,B,20000,2,root,"target"),
           "SUBSET":p19.ps.measure(b,pf["variants"][e]["protocol"],ch["subset_fen"],A,B,20000,2,root,"subset"),
           "SHAM":p19.ps.measure(b,pf["variants"][e]["protocol"],ch["sham_fen"],A,B,20000,2,root,"sham")}
   b2=find_p20c(a.p20c_build_dir,e)
   for fam in ("MOVE_ORDER","CUTOFF"):
    dyn=prof.profile(b2,carrier.p32.protocol_for(e),ch,pair,fam,out/f".private-prof-{idx}-{e}-{fam}")
    mi,inch=prof.mat_imbalance(m["fen"]);row={
      "schema":"c3x-g10-p22-heldout-profile-v1","stage":"C3X 0.10.0-G10-P22",
      "uid":p+"||"+e+"||"+fam,"position_id":p,"source_id":z["source_id"],"engine":e,"family":fam,
      "router_grammar":route,"pair":pair,"chain":ch,"base_boards":boards,**prof.boundary(boards),**dyn,
      "phase":m["context"]["phase"],"legal_branching":m["context"]["branching"],"tactical_surface":m["context"]["tactical_surface"],
      "material_imbalance":mi,"in_check":inch,"candidate_tactical_mode":prof.tactical(pair),
      "relation_atom_family":prof.relation_family(ch),"chain_type":ch.get("type","NA"),
      "prediction":None,"full_class_outcome_opened":False
    }
    row["prediction"]=predict(row)
    (out/f"{idx:03d}-{e}-{fam}.json").write_text(json.dumps(row,indent=2,sort_keys=True)+"\n");n+=1
 print("P22_HELDOUT_PROFILE_SHARD",a.shard,"ROWS",n)
if __name__=="__main__":main()
