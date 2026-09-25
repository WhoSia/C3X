#!/usr/bin/env python3
"""P22 outcome-blind design lane.
No selective intervention outcome is available to this module.
"""
import argparse,hashlib,json,math
from collections import Counter
from pathlib import Path
import p21_boundary as p21

STAGE="C3X 0.7.0-G9.4-P22"
CORE_FAMILIES=("KQQvKQ","KQRvKQ","KQQvKR","KQRvKR","KRBvKB","KRNvKB","KRBvKN","KRNvKN")
CARRIER_FAMILIES=("KQQPvKQP","KQRPvKQP","KQQPvKRP","KQRPvKRP","KRBPvKBP","KRNPvKBP","KRBPvKNP","KRNPvKNP")
HEADER=["sha","family","side","square","sf_main","sf_q","sf_qshare","berserk_main","berserk_q","berserk_qshare","ethereal_main","ethereal_q","ethereal_qshare","inanis_tt_main","inanis_pawn_q"]
def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def h(o):return hashlib.sha256(canon(o)).hexdigest()
def load_pool(path,lane):
 x=json.loads(Path(path).read_text());want=f"c3x-p22-{lane}-pool-v1"
 if x.get("schema")!=want or x.get("scientific_stage")!=STAGE or x.get("engine_outcomes_consulted") is not False:raise SystemExit("P22_POOL_AUTHORITY")
 return x
def engines(specs):return [p21.parse_engine(x) for x in specs]
def census(a,lane):
 x=load_pool(a.stage_a,lane);fam=a.family;es=engines(a.engine);rows=[]
 for i,c in enumerate([z for z in x["candidates"] if z["material_seed_name"]==fam]):
  sh={};
  for e in es:sh[e[0]]=p21.baseline_arm(e,c,a.nodes)
  ina=p21.run_inanis(a.inanis,c["fen"],"SHAM",a.nodes)
  z=p21.feature_map(sh);rows.append({"candidate_sha256":c["candidate_sha256"],"material_seed_name":fam,"side_to_move":c["side_to_move"],"square":c["square"],"vertex":c["vertex"],"fen":c["fen"],"world":c["world"],"sham":sh,"features":z,"inanis_sham":{"hits":ina["hits"],"bestmove":ina["bestmove"]}})
  print("P22_CENSUS",lane,fam,i+1,flush=True)
 out={"schema":f"c3x-p22-{lane}-census-v1","scientific_stage":STAGE,"lane":lane,"family":fam,"stage_a_sha256":p21.sha_file(a.stage_a),"selective_outcomes_consulted":False,"nodes":a.nodes,"rows":rows};out["receipt_sha256"]=h(out);Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
def collect(census_dir,lane):
 rows=[];files=sorted(Path(census_dir).rglob("*.json"));seen=set()
 for p in files:
  x=json.loads(p.read_text());
  if x.get("schema")!=f"c3x-p22-{lane}-census-v1" or x.get("scientific_stage")!=STAGE or x.get("selective_outcomes_consulted") is not False:continue
  if x["family"] in seen:raise SystemExit("P22_CENSUS_DUP")
  seen.add(x["family"]);rows.extend(x["rows"])
 expected=set(CORE_FAMILIES if lane=="core" else CARRIER_FAMILIES)
 if seen!=expected:raise SystemExit(f"P22_CENSUS_SET {sorted(seen)}")
 return rows
def export_tsv(a):
 rows=collect(a.census_dir,a.lane);lines=["\t".join(HEADER)]
 for r in sorted(rows,key=lambda q:q["candidate_sha256"]):
  z=r["features"];hh=r["inanis_sham"]["hits"]
  vals=[r["candidate_sha256"],r["material_seed_name"],r["side_to_move"],r["square"],*[format(float(v),".17g") for v in z],str(int(hh.get("tt_main_hits",0))),str(int(hh.get("pawn_q_hits",0)))]
  lines.append("\t".join(vals))
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text("\n".join(lines)+"\n");print("P22_TSV",a.lane,len(rows),p21.sha_file(a.out))
def seal(a):
 pool=load_pool(a.stage_a,a.lane);rows=collect(a.census_dir,a.lane);by={r["candidate_sha256"]:r for r in rows};sel=[x.strip() for x in Path(a.selected).read_text().splitlines() if x.strip()]
 if len(sel)!=96 or len(set(sel))!=96 or any(x not in by for x in sel):raise SystemExit("P22_SELECTION_AUTHORITY")
 rr=json.loads(Path(a.rust_report).read_text());cc=json.loads(Path(a.cpp_cert).read_text());ra=json.loads(Path(a.r_audit).read_text());xs=json.loads(Path(a.cross_seal).read_text())
 if not all(x.get("gate_pass") is True for x in (rr,cc,ra)) or xs.get("authorization")!="P22-SELECTIVE-INTERVENTION-AUTHORIZED":raise SystemExit("P22_BALANCE_CERT_FAIL")
 chosen=[by[x] for x in sel];q=Counter((r["material_seed_name"],r["side_to_move"]) for r in chosen)
 if len(q)!=16 or any(v!=6 for v in q.values()):raise SystemExit("P22_QUOTA_FAIL")
 cells=[]
 for r in chosen:cells.append({"candidate_sha256":r["candidate_sha256"],"material_seed_name":r["material_seed_name"],"side_to_move":r["side_to_move"],"square":r["square"],"vertex":r["vertex"],"fen":r["fen"],"world":r["world"],"sham":r["sham"],"features":r["features"],"inanis_sham":r["inanis_sham"]})
 out={"schema":f"c3x-p22-{a.lane}-precommit-v1","scientific_stage":STAGE,"lane":a.lane,"stage_a_sha256":p21.sha_file(a.stage_a),"census_tsv_sha256":p21.sha_file(a.census_tsv),"selected_sha256":p21.sha_file(a.selected),"selective_outcomes_consulted":False,"p21_cells_reused":False,"p21_post_hold_witness_cells_reused":False,"selection":{"algorithm":"P22_RUST_64START_QUOTA_BEST_IMPROVEMENT_V1","selected_count":96,"per_family_side":6,"primary_gate":0.50,"rust":rr,"cpp":cc,"r":ra,"cross_language":xs},"cells":sorted(cells,key=lambda z:z["candidate_sha256"])};out["receipt_sha256"]=h(out);Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P22_PRECOMMIT_PASS",a.lane,out["receipt_sha256"])
def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 for cmd,lane in (("core-census","core"),("carrier-census","carrier")):
  p=sp.add_parser(cmd);p.add_argument("--stage-a",required=True);p.add_argument("--engine",action="append",required=True);p.add_argument("--inanis",required=True);p.add_argument("--family",required=True);p.add_argument("--nodes",type=int,default=80000);p.add_argument("--out",required=True);p.set_defaults(fn=lambda a,l=lane:census(a,l))
 p=sp.add_parser("export-tsv");p.add_argument("--lane",choices=("core","carrier"),required=True);p.add_argument("--census-dir",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=export_tsv)
 p=sp.add_parser("seal");p.add_argument("--lane",choices=("core","carrier"),required=True);p.add_argument("--stage-a",required=True);p.add_argument("--census-dir",required=True);p.add_argument("--census-tsv",required=True);p.add_argument("--selected",required=True);p.add_argument("--rust-report",required=True);p.add_argument("--cpp-cert",required=True);p.add_argument("--r-audit",required=True);p.add_argument("--cross-seal",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=seal)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
