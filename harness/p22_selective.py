#!/usr/bin/env python3
"""P22 selective lane. Scientific rules are frozen; implementation repairs do not alter cells, modes, nodes, gates, or adjudication rules."""
import argparse,hashlib,json,tempfile
from pathlib import Path
import p20_transport as p20
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
  c={k:r[k] for k in ("candidate_sha256","material_seed_name","side_to_move","square","vertex","fen","world")};cells.append({"candidate":c,"sham":r["sham"],"features":r["features"],"inanis_sham":r["inanis_sham"]})
 smd=pre["selection"]["cpp"].get("smd",[]);heavy_smd={k:float(smd[i]) for i,k in enumerate(p21.FEATURES)} if len(smd)==len(p21.FEATURES) else {}
 x={"schema":f"c3x-p21-{lane}-precommit-v1","scientific_stage":"C3X 0.7.0-G9.4-P21","authorization":"P21-CORE-INTERVENTION-AUTHORIZED" if lane=="core" else "P21-CARRIER-INTERVENTION-AUTHORIZED","selective_outcomes_consulted":False,"p20_binaries":pre["p20_binaries"],"inanis_binary_sha256":pre["inanis_binary_sha256"],"committed_cells":cells,"precommit_sha256":pre["receipt_sha256"],"exposure_balance_pass":True,"heavy_vs_minor_smd":heavy_smd}
 Path(path).write_text(json.dumps(x,indent=2,sort_keys=True)+"\n");return x
def baseline(c,run):
 w=p20.world_value(c,run["semantic"]["bestmove"])
 if w is None:raise SystemExit("P22_WORLD_JOIN_FAIL_SHAM "+c["candidate_sha256"])
 return {"receipt":run,"world":w,"action_changed":False,"fine_changed":False,"coarse_changed":False}
def arm(c,base_run,base_world,run):
 w=p20.world_value(c,run["semantic"]["bestmove"])
 if w is None:raise SystemExit("P22_WORLD_JOIN_FAIL "+c["candidate_sha256"])
 return {"receipt":run,"world":w,"action_changed":run["semantic"]["bestmove"]!=base_run["semantic"]["bestmove"],"fine_changed":(w["wdl"],w["precise_dtz"])!=(base_world["wdl"],base_world["precise_dtz"]),"coarse_changed":w["wdl"]!=base_world["wdl"]}
def vertex(a,lane):
 pre=load_pre(a.precommit,lane);eng=p20.parse_engines(a.engine)
 for t in p21.P20_TARGETS:
  if p21.sha_file(eng[t]["path"])!=pre["p20_binaries"][t]["sha256"] or eng[t]["protocol"]!=pre["p20_binaries"][t]["protocol"]:raise SystemExit("P22_ENGINE_IDENTITY_FAIL "+t)
 if p21.sha_file(a.inanis)!=pre["inanis_binary_sha256"]:raise SystemExit("P22_INANIS_IDENTITY_FAIL")
 src=[r for r in pre["cells"] if r["material_seed_name"]==a.family]
 if len(src)!=12:raise SystemExit(f"P22_VERTEX_CELL_COUNT {a.family} {len(src)}/12")
 rows=[]
 for i,r in enumerate(src,1):
  c={k:r[k] for k in ("candidate_sha256","material_seed_name","side_to_move","square","vertex","fen","world")}
  rec={"candidate_sha256":c["candidate_sha256"],"family":a.family,"square":c["square"],"vertex":c["vertex"],"side_to_move":c["side_to_move"],"fen":c["fen"],"targets":{}}
  for t in p21.P20_TARGETS:
   br=p20.run_search(eng[t],c["fen"],"SHAM",a.nodes);b=baseline(c,br);arms={"00":b}
   for bits,mode in (("10","MASK_MAIN"),("01","MASK_QSEARCH"),("11","MASK_MAIN_QSEARCH"),("ALL","MASK_ALL")):
    arms[bits]=arm(c,br,b["world"],p20.run_search(eng[t],c["fen"],mode,a.nodes))
   rec["targets"][t]={"arms":arms}
  modes=p21.CORE_INANIS if lane=="core" else p21.CARRIER_INANIS
  ibr=p21.run_inanis(a.inanis,c["fen"],"SHAM",a.nodes);ib=baseline(c,ibr);ia={"SHAM":ib}
  for name,mode in modes.items():
   if name!="SHAM":ia[name]=arm(c,ibr,ib["world"],p21.run_inanis(a.inanis,c["fen"],mode,a.nodes))
  rec["inanis"]={"arms":ia};rows.append(rec);print("P22_VERTEX",lane,a.family,i,flush=True)
 x={"schema":f"c3x-p22-{lane}-vertex-result-v1","scientific_stage":STAGE,"lane":lane,"family":a.family,"precommit_sha256":pre["receipt_sha256"],"p22_precommit_sha256":p21.sha_file(a.precommit),"rows":rows,"p21_cells_reused":False,"selective_outcomes_consulted":True};seal(x)
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(x,indent=2,sort_keys=True)+"\n");print("P22_VERTEX_PASS",lane,a.family,x["receipt_sha256"])
def bridge_adjudicate(a,lane):
 pre=load_pre(a.precommit,lane)
 with tempfile.TemporaryDirectory() as td0:
  td=Path(td0);cp=td/"compat-pre.json";compat_pre(pre,lane,cp);n=0
  for p in sorted(Path(a.results).rglob(f"p22-{lane}-vertex-*.json")):
   x=json.loads(p.read_text())
   if x.get("schema")!=f"c3x-p22-{lane}-vertex-result-v1" or x.get("scientific_stage")!=STAGE:raise SystemExit("P22_RESULT_AUTHORITY")
   x["schema"]=f"c3x-p21-{lane}-vertex-v1";x["scientific_stage"]="C3X 0.7.0-G9.4-P21";(td/p.name.replace("p22-","p21-",1)).write_text(json.dumps(x,sort_keys=True)+"\n");n+=1
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
 core_heavy_all=bool(heavy) and all(tuple(v)==("CURVED","QSEARCH",-1) for v in heavy.values());minor_common=bool(minor) and len({tuple(v) for v in minor.values()})==1 and next(iter({tuple(v) for v in minor.values()}))[0]=="CURVED"
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
