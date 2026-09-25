#!/usr/bin/env python3
"""P22 selective lane. Scientific rules remain frozen; this module only bridges the P22 receipt schema to the already-audited P21 executor/adjudicator implementation."""
import argparse,hashlib,json,shutil,tempfile
from pathlib import Path
import p21_boundary as p21
STAGE="C3X 0.7.0-G9.4-P22"
def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=hashlib.sha256(canon(o)).hexdigest();return o
def load_pre(path,lane):
 x=json.loads(Path(path).read_text())
 if x.get("schema")!=f"c3x-p22-{lane}-precommit-v1" or x.get("scientific_stage")!=STAGE or x.get("selective_outcomes_consulted") is not False:raise SystemExit("P22_PRECOMMIT_AUTHORITY")
 if x.get("selection",{}).get("cross_language",{}).get("authorization")!="P22-SELECTIVE-INTERVENTION-AUTHORIZED":raise SystemExit("P22_SELECTIVE_NOT_AUTHORIZED")
 return x
def compat_pre(pre,lane,path):
 cells=[]
 for r in pre["cells"]:
  c={k:r[k] for k in ("candidate_sha256","material_seed_name","side_to_move","square","vertex","fen","world")}
  cells.append({"candidate":c,"sham":r["sham"],"features":r["features"],"inanis_sham":r["inanis_sham"]})
 cpp=pre["selection"]["cpp"];smd=cpp.get("smd",[])
 heavy_smd={k:float(smd[i]) for i,k in enumerate(p21.FEATURES)} if len(smd)==len(p21.FEATURES) else {}
 x={"schema":f"c3x-p21-{lane}-precommit-v1","scientific_stage":"C3X 0.7.0-G9.4-P21","authorization":"P21-CORE-INTERVENTION-AUTHORIZED" if lane=="core" else "P21-CARRIER-INTERVENTION-AUTHORIZED","selective_outcomes_consulted":False,"p20_binaries":pre["p20_binaries"],"inanis_binary_sha256":pre["inanis_binary_sha256"],"committed_cells":cells,"precommit_sha256":pre["receipt_sha256"],"exposure_balance_pass":True,"heavy_vs_minor_smd":heavy_smd}
 Path(path).write_text(json.dumps(x,indent=2,sort_keys=True)+"\n");return x
def vertex(a,lane):
 pre=load_pre(a.precommit,lane)
 with tempfile.TemporaryDirectory() as td:
  cp=Path(td)/"compat-pre.json";compat_pre(pre,lane,cp)
  ns=argparse.Namespace(precommit=str(cp),engine=a.engine,inanis=a.inanis,family=a.family,out=a.out)
  p21.do_vertex(ns,lane)
 x=json.loads(Path(a.out).read_text());x["schema"]=f"c3x-p22-{lane}-vertex-result-v1";x["scientific_stage"]=STAGE;x["p22_precommit_sha256"]=p21.sha_file(a.precommit);x["p21_cells_reused"]=False;x["selective_outcomes_consulted"]=True;seal(x)
 Path(a.out).write_text(json.dumps(x,indent=2,sort_keys=True)+"\n");print("P22_VERTEX_PASS",lane,a.family,x["receipt_sha256"])
def bridge_adjudicate(a,lane):
 pre=load_pre(a.precommit,lane)
 with tempfile.TemporaryDirectory() as td0:
  td=Path(td0);cp=td/"compat-pre.json";compat_pre(pre,lane,cp);n=0
  for p in sorted(Path(a.results).rglob(f"p22-{lane}-vertex-*.json")):
   x=json.loads(p.read_text())
   if x.get("schema")!=f"c3x-p22-{lane}-vertex-result-v1" or x.get("scientific_stage")!=STAGE:raise SystemExit("P22_RESULT_AUTHORITY")
   x["schema"]=f"c3x-p21-{lane}-vertex-v1";x["scientific_stage"]="C3X 0.7.0-G9.4-P21"
   q=td/p.name.replace("p22-","p21-",1);q.write_text(json.dumps(x,sort_keys=True)+"\n");n+=1
  if n!=8:raise SystemExit(f"P22_RESULT_COUNT {lane} {n}/8")
  tmp=td/"adjudication.json";ns=argparse.Namespace(precommit=str(cp),result_dir=str(td),out=str(tmp))
  if lane=="core":p21.core_adjudicate(ns)
  else:p21.carrier_adjudicate(ns)
  x=json.loads(tmp.read_text())
 x["schema"]=f"c3x-p22-{lane}-adjudication-v1";x["scientific_stage"]=STAGE;x["p22_precommit_sha256"]=p21.sha_file(a.precommit);x["fresh_balanced_support"]=True;x["p21_cells_reused"]=False;seal(x)
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(x,indent=2,sort_keys=True)+"\n");print("P22_ADJUDICATE_PASS",lane,x["receipt_sha256"])
def synthesize(a):
 core=json.loads(Path(a.core).read_text());car=json.loads(Path(a.carrier).read_text())
 if core.get("schema")!="c3x-p22-core-adjudication-v1" or car.get("schema")!="c3x-p22-carrier-adjudication-v1":raise SystemExit("P22_SYNTH_INPUT")
 heavy=core.get("heavy_fingerprints",{});minor=core.get("minor_fingerprints",{})
 core_heavy_all=bool(heavy) and all(tuple(v)==("CURVED","QSEARCH",-1) for v in heavy.values())
 minor_common=bool(minor) and len({tuple(v) for v in minor.values()})==1 and next(iter({tuple(v) for v in minor.values()}))[0]=="CURVED"
 if not core_heavy_all:verdict="P20_RELATION_BOUNDARY_NOT_FRESHLY_REPLICATED"
 elif minor_common:verdict="EXPOSURE_BALANCED_HEAVY_REPLICATION_BUT_MINOR_CONVERGED"
 else:verdict="EXPOSURE_BALANCED_RELATION_BOUNDARY_REPLICATED"
 broader=bool(car.get("broader_qsearch_memory_carrier_support"))
 out={"schema":"c3x-p22-synthesis-v1","scientific_stage":STAGE,"core_relation_boundary_replicated":bool(core.get("core_relation_boundary_replicated")),"carrier_broader_qsearch_memory_support":broader,"verdict":verdict,"exposure_only_status":"DEFEATED_WITHIN_P22_BALANCED_SUPPORT" if verdict=="EXPOSURE_BALANCED_RELATION_BOUNDARY_REPLICATED" else "NOT_DEFEATED","broader_qsearch_persistent_memory_status":"BOUNDED_SUPPORT" if broader and core_heavy_all else "NOT_ESTABLISHED","channel_homology_claimed":False,"structural_zero_imputation":False,"robust_wdl_changed_any_arm":bool(core.get("robust_wdl_changed_any_arm")) or bool(car.get("robust_wdl_changed_any_arm")),"authority_ceiling":"FOUR_ENGINE_FROZEN_ARCHITECTURE_SET_AND_EXACT_WORLD_FAMILIES_ONLY","core_sha256":p21.sha_file(a.core),"carrier_sha256":p21.sha_file(a.carrier)};seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P22_SYNTHESIS",verdict,out["broader_qsearch_persistent_memory_status"])
def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 for cmd,lane in (("core-vertex","core"),("carrier-vertex","carrier")):
  p=sp.add_parser(cmd);p.add_argument("--precommit",required=True);p.add_argument("--engine",action="append",required=True);p.add_argument("--inanis",required=True);p.add_argument("--family",required=True);p.add_argument("--nodes",type=int,default=300000);p.add_argument("--out",required=True);p.set_defaults(fn=lambda a,l=lane:vertex(a,l))
 for cmd,lane in (("core-adjudicate","core"),("carrier-adjudicate","carrier")):
  p=sp.add_parser(cmd);p.add_argument("--precommit",required=True);p.add_argument("--results",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=lambda a,l=lane:bridge_adjudicate(a,l))
 p=sp.add_parser("synthesize");p.add_argument("--core",required=True);p.add_argument("--carrier",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=synthesize)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
