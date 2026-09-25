#!/usr/bin/env python3
"""P23 fresh-world outcome-blind design lane after unused-P22 holdout support failure."""
import argparse,csv,hashlib,json,statistics
from collections import Counter
from pathlib import Path
import p20_transport as p20
import p21_boundary as p21
STAGE="C3X 0.7.0-G9.4-P23";FAMILIES=p21.CORE_FAMILIES
HEADER=["sha","family","side","square","sf_main","sf_q","sf_qshare","berserk_main","berserk_q","berserk_qshare","ethereal_main","ethereal_q","ethereal_qshare","inanis_tt_main","inanis_pawn_q"]
def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def h(o):return hashlib.sha256(canon(o)).hexdigest()
def census(a):
 pool=json.loads(Path(a.pool).read_text())
 if pool.get("schema")!="c3x-p23-core-pool-v1" or pool.get("scientific_stage")!=STAGE or pool.get("engine_outcomes_consulted") is not False:raise SystemExit("P23_POOL_AUTHORITY")
 eng=p20.parse_engines(a.engine);src=[c for c in pool["candidates"] if c["material_seed_name"]==a.family]
 if len(src)!=48:raise SystemExit("P23_CENSUS_COUNT")
 rows=[]
 for i,c in enumerate(src,1):
  sh={t:p20.run_search(eng[t],c["fen"],"SHAM",a.nodes) for t in p21.P20_TARGETS};ina=p21.run_inanis(a.inanis,c["fen"],"SHAM",a.nodes);z=p21.feature_map(sh)
  rows.append({"candidate_sha256":c["candidate_sha256"],"material_seed_name":a.family,"side_to_move":c["side_to_move"],"square":c["square"],"vertex":c["vertex"],"fen":c["fen"],"world":c["world"],"sham":sh,"features":z,"inanis_sham":ina});print("P23_CENSUS",a.family,i,flush=True)
 out={"schema":"c3x-p23-core-census-v1","scientific_stage":STAGE,"family":a.family,"pool_sha256":pool["pool_sha256"],"selective_outcomes_consulted":False,"nodes":a.nodes,"p20_binaries":{t:{"protocol":eng[t]["protocol"],"sha256":p21.sha_file(eng[t]["path"])} for t in p21.P20_TARGETS},"inanis_binary_sha256":p21.sha_file(a.inanis),"rows":rows};out["receipt_sha256"]=h(out);Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
def collect(path):
 rows=[];seen=set();pb=None;ib=None;pool=None
 for p in sorted(Path(path).rglob("*.json")):
  x=json.loads(p.read_text())
  if x.get("schema")!="c3x-p23-core-census-v1" or x.get("scientific_stage")!=STAGE:continue
  if x.get("selective_outcomes_consulted") is not False or x["family"] in seen:raise SystemExit("P23_CENSUS_AUTHORITY")
  seen.add(x["family"]);rows.extend(x["rows"])
  if pb is None:pb=x["p20_binaries"];ib=x["inanis_binary_sha256"];pool=x["pool_sha256"]
  elif pb!=x["p20_binaries"] or ib!=x["inanis_binary_sha256"] or pool!=x["pool_sha256"]:raise SystemExit("P23_CENSUS_IDENTITY")
 if seen!=set(FAMILIES) or len(rows)!=384:raise SystemExit("P23_CENSUS_SET")
 return rows,pb,ib,pool
def export(a):
 rows,_,_,_=collect(a.census_dir);lines=["\t".join(HEADER)]
 for r in sorted(rows,key=lambda q:q["candidate_sha256"]):
  z=r["features"];hh=r["inanis_sham"]["engagement"]
  vals=[r["candidate_sha256"],r["material_seed_name"],r["side_to_move"],r["square"],*[format(float(z[k]),".17g") for k in p21.FEATURES],str(int(hh.get("TT_MAIN",0))),str(int(hh.get("PAWN_Q",0)))];lines.append("\t".join(vals))
 Path(a.out).write_text("\n".join(lines)+"\n");print("P23_TSV",len(rows),p21.sha_file(a.out))
def qindex(r):return statistics.median(float(r["features"][k]) for k in ("stockfish_19:Q_SHARE","berserk:Q_SHARE","ethereal:Q_SHARE"))
def seal(a):
 rows,pb,ib,pool=collect(a.census_dir);by={r["candidate_sha256"]:r for r in rows};sel=[x.strip() for x in Path(a.selected).read_text().splitlines() if x.strip()]
 if len(sel)!=96 or len(set(sel))!=96 or any(x not in by for x in sel):raise SystemExit("P23_SELECTION")
 rr=json.loads(Path(a.rust_report).read_text());cc=json.loads(Path(a.cpp_cert).read_text());ra=json.loads(Path(a.r_audit).read_text());xs=json.loads(Path(a.cross_seal).read_text())
 if not all(x.get("gate_pass") is True and x.get("selected_count")==96 for x in (rr,cc,ra)) or xs.get("authorization")!="P22-SELECTIVE-INTERVENTION-AUTHORIZED":raise SystemExit("P23_BALANCE_CERT")
 chosen=[by[x] for x in sel];q=Counter((r["material_seed_name"],r["side_to_move"]) for r in chosen)
 if len(q)!=16 or any(v!=6 for v in q.values()):raise SystemExit("P23_QUOTA")
 reg={};thr={}
 for key in sorted(q):
  z=sorted((r for r in chosen if (r["material_seed_name"],r["side_to_move"])==key),key=lambda r:(qindex(r),r["candidate_sha256"]))
  for r in z[:3]:reg[r["candidate_sha256"]]="Q_LOW"
  for r in z[3:]:reg[r["candidate_sha256"]]="Q_HIGH"
  thr["|".join(key)]={"low_max":qindex(z[2]),"high_min":qindex(z[3])}
 rq=Counter((r["material_seed_name"],r["side_to_move"],reg[r["candidate_sha256"]]) for r in chosen)
 if len(rq)!=32 or any(v!=3 for v in rq.values()):raise SystemExit("P23_REGIME_QUOTA")
 cells=[]
 for r in chosen:
  cells.append({"candidate_sha256":r["candidate_sha256"],"material_seed_name":r["material_seed_name"],"side_to_move":r["side_to_move"],"square":r["square"],"vertex":r["vertex"],"fen":r["fen"],"world":r["world"],"search_state":{"consensus_qshare":qindex(r),"features":r["features"],"inanis_engagement":r["inanis_sham"]["engagement"]},"regime":reg[r["candidate_sha256"]]})
 out={"schema":"c3x-p23-core-precommit-v1","scientific_stage":STAGE,"selective_outcomes_consulted":False,"p22_cells_reused":False,"fresh_world_pool_sha256":pool,"p20_binaries":pb,"inanis_binary_sha256":ib,"design_repair":{"failed_unused_p22_holdout_run":36129712883,"failed_best_max_abs_smd":1.769760886,"selective_outcomes_opened_before_repair":False,"repair":"fresh exact-world namespace; frozen 0.50 balance gate retained"},"selection":{"algorithm":"P22_RUST_64START_QUOTA_BEST_IMPROVEMENT_V1_ON_FRESH_P23_POOL","selected_count":96,"per_family_side":6,"balance_gate":0.50,"rust":rr,"cpp":cc,"r":ra,"cross_language":xs},"quotient":{"coordinate":"median_cross_engine_qshare","regimes":["Q_LOW","Q_HIGH"],"within_family_side_rank":True,"per_family_side_regime":3,"thresholds":thr},"cells":sorted(cells,key=lambda z:z["candidate_sha256"])};out["receipt_sha256"]=h(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P23_FRESH_PRECOMMIT_PASS",out["receipt_sha256"],rr["max_abs_smd"])
def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 p=sp.add_parser("census");p.add_argument("--pool",required=True);p.add_argument("--engine",action="append",required=True);p.add_argument("--inanis",required=True);p.add_argument("--family",choices=FAMILIES,required=True);p.add_argument("--nodes",type=int,default=80000);p.add_argument("--out",required=True);p.set_defaults(fn=census)
 p=sp.add_parser("export");p.add_argument("--census-dir",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=export)
 p=sp.add_parser("seal");
 for k in ("census_dir","selected","rust_report","cpp_cert","r_audit","cross_seal","out"):p.add_argument("--"+k.replace("_","-"),required=True)
 p.set_defaults(fn=seal);a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
