#!/usr/bin/env python3
"""P22 selective lane. This file is frozen before P22 balance results exist."""
import argparse,copy,hashlib,json,shutil,tempfile
from pathlib import Path
import p21_boundary as p21
STAGE="C3X 0.7.0-G9.4-P22"
def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=hashlib.sha256(canon(o)).hexdigest();return o
def load_pre(path,lane):
 x=json.loads(Path(path).read_text());
 if x.get("schema")!=f"c3x-p22-{lane}-precommit-v1" or x.get("scientific_stage")!=STAGE or x.get("selective_outcomes_consulted") is not False:raise SystemExit("P22_PRECOMMIT_AUTHORITY")
 if x.get("selection",{}).get("cross_language",{}).get("authorization")!="P22-SELECTIVE-INTERVENTION-AUTHORIZED":raise SystemExit("P22_SELECTIVE_NOT_AUTHORIZED")
 return x
def specs(xs):return [p21.parse_engine(x) for x in xs]
def vertex(a,lane):
 pre=load_pre(a.precommit,lane);tmp=p21.do_vertex(pre,specs(a.engine),a.inanis,a.family,a.nodes,lane)
 tmp["schema"]=f"c3x-p22-{lane}-vertex-result-v1";tmp["scientific_stage"]=STAGE;tmp["p22_precommit_sha256"]=p21.sha_file(a.precommit);tmp["p21_cells_reused"]=False;tmp["selective_outcomes_consulted"]=True;seal(tmp)
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(tmp,indent=2,sort_keys=True)+"\n");print("P22_VERTEX_PASS",lane,a.family,tmp["receipt_sha256"])
def bridge_adjudicate(a,lane):
 pre=load_pre(a.precommit,lane)
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);n=0
  for p in sorted(Path(a.results).rglob(f"p22-{lane}-vertex-*.json")):
   x=json.loads(p.read_text())
   if x.get("schema")!=f"c3x-p22-{lane}-vertex-result-v1" or x.get("scientific_stage")!=STAGE:raise SystemExit("P22_RESULT_AUTHORITY")
   q=td/p.name.replace("p22-","p21-",1);shutil.copyfile(p,q);n+=1
  if n!=8:raise SystemExit(f"P22_RESULT_COUNT {lane} {n}/8")
  tmp=td/"adjudication.json";ns=argparse.Namespace(precommit=a.precommit,results=str(td),out=str(tmp))
  if lane=="core":p21.core_adjudicate(ns)
  else:p21.carrier_adjudicate(ns)
  x=json.loads(tmp.read_text());x["schema"]=f"c3x-p22-{lane}-adjudication-v1";x["scientific_stage"]=STAGE;x["p22_precommit_sha256"]=p21.sha_file(a.precommit);x["fresh_balanced_support"]=True;x["p21_cells_reused"]=False;seal(x)
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(x,indent=2,sort_keys=True)+"\n");print("P22_ADJUDICATE_PASS",lane,x.get("verdict"),x["receipt_sha256"])
def synthesize(a):
 core=json.loads(Path(a.core).read_text());car=json.loads(Path(a.carrier).read_text())
 if core.get("schema")!="c3x-p22-core-adjudication-v1" or car.get("schema")!="c3x-p22-carrier-adjudication-v1":raise SystemExit("P22_SYNTH_INPUT")
 cv=core.get("verdict");iv=car.get("verdict");heavy=core.get("square_fingerprints",{}).get("HEAVY_HEAVY",{});minor=core.get("square_fingerprints",{}).get("MINOR_MINOR",{})
 core_heavy_all=bool(heavy) and all(v=="CURVED/QSEARCH/negative" for v in heavy.values());minor_common=len(set(minor.values()))==1 if minor else False
 if not core_heavy_all:verdict="P20_RELATION_BOUNDARY_NOT_FRESHLY_REPLICATED"
 elif minor_common:verdict="EXPOSURE_BALANCED_HEAVY_REPLICATION_BUT_MINOR_CONVERGED"
 else:verdict="EXPOSURE_BALANCED_RELATION_BOUNDARY_REPLICATED"
 inanis=car.get("inanis_square_summary",{})
 broader=False
 try:
  hh=inanis["HEAVY_HEAVY"]["PAWN_Q"]
  broader=(hh.get("action_rate",0)>0 or hh.get("fine_rate",0)>0)
 except Exception:pass
 out={"schema":"c3x-p22-synthesis-v1","scientific_stage":STAGE,"core_verdict":cv,"carrier_verdict":iv,"verdict":verdict,"exposure_only_status":"DEFEATED_WITHIN_P22_BALANCED_SUPPORT" if verdict=="EXPOSURE_BALANCED_RELATION_BOUNDARY_REPLICATED" else "NOT_DEFEATED","broader_qsearch_persistent_memory_status":"BOUNDED_SUPPORT" if broader and core_heavy_all else "NOT_ESTABLISHED","channel_homology_claimed":False,"structural_zero_imputation":False,"authority_ceiling":"FOUR_ENGINE_FROZEN_ARCHITECTURE_SET_AND_EXACT_WORLD_FAMILIES_ONLY","core_sha256":p21.sha_file(a.core),"carrier_sha256":p21.sha_file(a.carrier)};seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P22_SYNTHESIS",verdict,out["broader_qsearch_persistent_memory_status"])
def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 for cmd,lane in (("core-vertex","core"),("carrier-vertex","carrier")):
  p=sp.add_parser(cmd);p.add_argument("--precommit",required=True);p.add_argument("--engine",action="append",required=True);p.add_argument("--inanis",required=True);p.add_argument("--family",required=True);p.add_argument("--nodes",type=int,default=300000);p.add_argument("--out",required=True);p.set_defaults(fn=lambda a,l=lane:vertex(a,l))
 for cmd,lane in (("core-adjudicate","core"),("carrier-adjudicate","carrier")):
  p=sp.add_parser(cmd);p.add_argument("--precommit",required=True);p.add_argument("--results",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=lambda a,l=lane:bridge_adjudicate(a,l))
 p=sp.add_parser("synthesize");p.add_argument("--core",required=True);p.add_argument("--carrier",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=synthesize)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
