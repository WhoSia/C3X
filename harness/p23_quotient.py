#!/usr/bin/env python3
"""C3X G9.4-P23 prospective holdout search-state quotient court.
Design commands cannot read P22 selective outcomes. Selective execution uses only the sealed P23 holdout precommit.
"""
import argparse,csv,hashlib,itertools,json,statistics
from collections import Counter,defaultdict
from pathlib import Path
import p20_transport as p20
import p21_boundary as p21

STAGE="C3X 0.7.0-G9.4-P23"
REGIMES=("Q_LOW","Q_HIGH")
FAMILIES=p21.CORE_FAMILIES
SQUARES=p21.CORE_SQUARES
TARGETS=p21.P20_TARGETS
LEVELS=("EFFECT_SUPPORT","CURVATURE_CLASS","DOMINANT_COORDINATE","SIGNED_COORDINATE","FULL_FINGERPRINT")

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def seal(o):
 o.pop("receipt_sha256",None);o["receipt_sha256"]=hashlib.sha256(canon(o)).hexdigest();return o

def read_tsv(path):
 with open(path,newline="") as f:return list(csv.DictReader(f,delimiter="\t"))
def write_tsv(path,rows,fieldnames):
 with open(path,"w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fieldnames,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)

def filter_holdout(a):
 rows=read_tsv(a.census);old={x.strip() for x in Path(a.p22_selected).read_text().splitlines() if x.strip()}
 if len(rows)!=384 or len(old)!=96:raise SystemExit(f"P23_PARENT_CARDINALITY rows={len(rows)} old={len(old)}")
 out=[r for r in rows if r["sha"] not in old]
 if len(out)!=288:raise SystemExit(f"P23_HOLDOUT_CARDINALITY {len(out)}/288")
 q=Counter((r["family"],r["side"]) for r in out)
 if len(q)!=16 or any(v!=18 for v in q.values()):raise SystemExit("P23_HOLDOUT_STRATA")
 write_tsv(a.out,out,list(rows[0].keys()));print("P23_HOLDOUT_FILTER_PASS",len(out))

def load_parent_pre(path):
 x=json.loads(Path(path).read_text())
 if x.get("schema")!="c3x-p22-core-precommit-v1" or x.get("scientific_stage")!="C3X 0.7.0-G9.4-P22":raise SystemExit("P23_PARENT_PRECOMMIT")
 if x.get("selective_outcomes_consulted") is not False:raise SystemExit("P23_PARENT_DESIGN_LEAK")
 return x

def qindex(r):return statistics.median(float(r[k]) for k in ("sf_qshare","berserk_qshare","ethereal_qshare"))
def preseal(a):
 rows=read_tsv(a.holdout);by={r["sha"]:r for r in rows};sel=[x.strip() for x in Path(a.selected).read_text().splitlines() if x.strip()]
 parent=load_parent_pre(a.p22_precommit);old={r["candidate_sha256"] for r in parent["cells"]}
 if len(rows)!=288 or len(sel)!=96 or len(set(sel))!=96 or any(x not in by for x in sel):raise SystemExit("P23_SELECTION_AUTHORITY")
 if old & set(sel):raise SystemExit("P23_P22_CELL_REUSE")
 rr=json.loads(Path(a.rust_report).read_text());cc=json.loads(Path(a.cpp_cert).read_text());ra=json.loads(Path(a.r_audit).read_text());xs=json.loads(Path(a.cross_seal).read_text())
 if not all(x.get("gate_pass") is True and x.get("selected_count")==96 for x in (rr,cc,ra)):raise SystemExit("P23_BALANCE_CERT_FAIL")
 if xs.get("authorization")!="P22-SELECTIVE-INTERVENTION-AUTHORIZED":raise SystemExit("P23_CROSS_LANGUAGE_FAIL")
 chosen=[by[x] for x in sel];quota=Counter((r["family"],r["side"]) for r in chosen)
 if len(quota)!=16 or any(v!=6 for v in quota.values()):raise SystemExit("P23_QUOTA_FAIL")
 regime={};thresholds={}
 for key in sorted(quota):
  z=sorted((r for r in chosen if (r["family"],r["side"])==key),key=lambda r:(qindex(r),r["sha"]))
  if len(z)!=6:raise SystemExit("P23_REGIME_STRATUM")
  for r in z[:3]:regime[r["sha"]]="Q_LOW"
  for r in z[3:]:regime[r["sha"]]="Q_HIGH"
  thresholds["|".join(key)]={"low_max":qindex(z[2]),"high_min":qindex(z[3])}
 rq=Counter((r["family"],r["side"],regime[r["sha"]]) for r in chosen)
 if len(rq)!=32 or any(v!=3 for v in rq.values()):raise SystemExit("P23_REGIME_QUOTA_FAIL")
 pool=json.loads(Path(a.pool).read_text())
 if pool.get("schema")!="c3x-p22-core-pool-v1" or pool.get("engine_outcomes_consulted") is not False:raise SystemExit("P23_POOL_AUTHORITY")
 cand={c["candidate_sha256"]:c for c in pool["candidates"]}
 cells=[]
 for r in chosen:
  c=cand.get(r["sha"])
  if c is None:raise SystemExit("P23_POOL_JOIN "+r["sha"])
  cells.append({"candidate_sha256":r["sha"],"material_seed_name":r["family"],"side_to_move":r["side"],"square":r["square"],"vertex":c["vertex"],"fen":c["fen"],"world":c["world"],"search_state":{"consensus_qshare":qindex(r),"features":{k:float(r[k]) for k in ("sf_main","sf_q","sf_qshare","berserk_main","berserk_q","berserk_qshare","ethereal_main","ethereal_q","ethereal_qshare")},"inanis_tt_main":int(r["inanis_tt_main"]),"inanis_pawn_q":int(r["inanis_pawn_q"])},"regime":regime[r["sha"]]})
 out={"schema":"c3x-p23-core-precommit-v1","scientific_stage":STAGE,"selective_outcomes_consulted":False,"p22_selective_results_available":False,"p22_cells_reused":False,"parent_p22_precommit_receipt":parent["receipt_sha256"],"p20_binaries":parent["p20_binaries"],"inanis_binary_sha256":parent["inanis_binary_sha256"],"selection":{"algorithm":"P22_RUST_64START_QUOTA_BEST_IMPROVEMENT_V1_ON_P22_UNUSED_HOLDOUT","selected_count":96,"per_family_side":6,"balance_gate":0.50,"rust":rr,"cpp":cc,"r":ra,"cross_language":xs},"quotient":{"coordinate":"median_cross_engine_qshare","within_family_side_rank":True,"regimes":list(REGIMES),"per_family_side_regime":3,"thresholds":thresholds},"cells":sorted(cells,key=lambda z:z["candidate_sha256"])};seal(out)
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P23_PRECOMMIT_PASS",out["receipt_sha256"],max(float(rr["max_abs_smd"]),float(cc["max_abs_smd"]),float(ra["max_abs_smd"])))

def baseline(c,run):
 w=p20.world_value(c,run["semantic"]["bestmove"])
 if w is None:raise SystemExit("P23_WORLD_JOIN_SHAM "+c["candidate_sha256"])
 return {"receipt":run,"world":w,"action_changed":False,"fine_changed":False,"coarse_changed":False}
def arm(c,base_run,base_world,run):
 w=p20.world_value(c,run["semantic"]["bestmove"])
 if w is None:raise SystemExit("P23_WORLD_JOIN "+c["candidate_sha256"])
 return {"receipt":run,"world":w,"action_changed":run["semantic"]["bestmove"]!=base_run["semantic"]["bestmove"],"fine_changed":(w["wdl"],w["precise_dtz"])!=(base_world["wdl"],base_world["precise_dtz"]),"coarse_changed":w["wdl"]!=base_world["wdl"]}

def load_pre(path):
 x=json.loads(Path(path).read_text())
 if x.get("schema")!="c3x-p23-core-precommit-v1" or x.get("scientific_stage")!=STAGE or x.get("selective_outcomes_consulted") is not False:raise SystemExit("P23_PRECOMMIT_AUTHORITY")
 return x

def vertex(a):
 pre=load_pre(a.precommit);eng=p20.parse_engines(a.engine)
 for t in TARGETS:
  if p21.sha_file(eng[t]["path"])!=pre["p20_binaries"][t]["sha256"] or eng[t]["protocol"]!=pre["p20_binaries"][t]["protocol"]:raise SystemExit("P23_ENGINE_IDENTITY "+t)
 if p21.sha_file(a.inanis)!=pre["inanis_binary_sha256"]:raise SystemExit("P23_INANIS_IDENTITY")
 src=[r for r in pre["cells"] if r["material_seed_name"]==a.family]
 if len(src)!=12 or Counter(r["regime"] for r in src)!=Counter({"Q_LOW":6,"Q_HIGH":6}):raise SystemExit("P23_VERTEX_SUPPORT")
 rows=[]
 for i,c in enumerate(src,1):
  rec={k:c[k] for k in ("candidate_sha256","material_seed_name","side_to_move","square","vertex","fen","regime")};rec["targets"]={}
  for t in TARGETS:
   br=p20.run_search(eng[t],c["fen"],"SHAM",a.nodes);b=baseline(c,br);arms={"00":b}
   for bits,mode in (("10","MASK_MAIN"),("01","MASK_QSEARCH"),("11","MASK_MAIN_QSEARCH"),("ALL","MASK_ALL")):
    arms[bits]=arm(c,br,b["world"],p20.run_search(eng[t],c["fen"],mode,a.nodes))
   rec["targets"][t]={"arms":arms}
  ibr=p21.run_inanis(a.inanis,c["fen"],"SHAM",a.nodes);ib=baseline(c,ibr);ia={"SHAM":ib}
  for name,mode in (("TT_MAIN","MASK_TT_MAIN"),("PAWN_Q","MASK_PAWN_Q")):
   ia[name]=arm(c,ibr,ib["world"],p21.run_inanis(a.inanis,c["fen"],mode,a.nodes))
  rec["inanis"]={"arms":ia};rows.append(rec);print("P23_VERTEX",a.family,c["regime"],i,flush=True)
 out={"schema":"c3x-p23-core-vertex-v1","scientific_stage":STAGE,"family":a.family,"precommit_receipt_sha256":pre["receipt_sha256"],"rows":rows};seal(out);Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P23_VERTEX_PASS",a.family,out["receipt_sha256"])

def fp(z):
 c=z["curvature"];return [c["class"],c["dominant_coordinate"],c["dominant_sign"]]
def effect_support(z):
 return any(v["counts"]["MAIN"]+v["counts"]["QSEARCH"]+v["counts"]["MAIN_QSEARCH"]>0 for v in z["vertices"].values())
def abstract(z,level):
 c=z["curvature"]
 if level=="EFFECT_SUPPORT":return "EFFECT" if effect_support(z) else "NULL"
 if level=="CURVATURE_CLASS":return c["class"]
 if level=="DOMINANT_COORDINATE":return c["dominant_coordinate"] if c["class"]=="CURVED" else c["class"]
 if level=="SIGNED_COORDINATE":return [c["dominant_coordinate"],c["dominant_sign"]] if c["class"]=="CURVED" else [c["class"],0]
 if level=="FULL_FINGERPRINT":return [c["class"],c["dominant_coordinate"],c["dominant_sign"]]
 raise ValueError(level)
def same(vals):return len({json.dumps(v,sort_keys=True) for v in vals})==1

def adjudicate(a):
 pre=load_pre(a.precommit);files=sorted(Path(a.results).rglob("p23-core-*.json"));by={}
 for p in files:
  x=json.loads(p.read_text())
  if x.get("schema")!="c3x-p23-core-vertex-v1" or x.get("scientific_stage")!=STAGE or x.get("precommit_receipt_sha256")!=pre["receipt_sha256"]:continue
  if x["family"] in by:raise SystemExit("P23_RESULT_DUP")
  by[x["family"]]=x
 if set(by)!=set(FAMILIES):raise SystemExit(f"P23_RESULT_SET {sorted(by)}")
 analyses={};fingerprints={};compatibility={}
 for reg in REGIMES:
  analyses[reg]={};fingerprints[reg]={};compatibility[reg]={}
  for t in TARGETS:
   analyses[reg][t]={};fingerprints[reg][t]={}
   for sq,mp in SQUARES.items():
    vres={bit:{"rows":[r for r in by[fam]["rows"] if r["regime"]==reg]} for bit,fam in mp.items()}
    if any(len(vres[b]["rows"])!=6 for b in vres):raise SystemExit("P23_REGIME_SUPPORT")
    z=p20.square_analysis(vres,t);analyses[reg][t][sq]=z;fingerprints[reg][t][sq]=fp(z)
  for sq in SQUARES:
   compatibility[reg][sq]={}
   for x,y in itertools.combinations(TARGETS,2):compatibility[reg][sq][x+"_VS_"+y]=p20.compatible(analyses[reg][x][sq],analyses[reg][y][sq])
 recovered=[];strict=[]
 for reg in REGIMES:
  heavy=[fingerprints[reg][t]["HEAVY_HEAVY"] for t in TARGETS];minor=[fingerprints[reg][t]["MINOR_MINOR"] for t in TARGETS]
  if all(tuple(x)==("CURVED","QSEARCH",-1) for x in heavy) and not (same(minor) and minor[0][0]=="CURVED"):recovered.append(reg)
  if all(z["compatible"] for sq in SQUARES for z in compatibility[reg][sq].values()):strict.append(reg)
 lattice={};minimal=None
 for level in LEVELS:
  cells={};all_inv=True;vals=[]
  for reg in REGIMES:
   cells[reg]={}
   for sq in SQUARES:
    v=[abstract(analyses[reg][t][sq],level) for t in TARGETS];inv=same(v);all_inv=all_inv and inv
    cells[reg][sq]={"invariant":inv,"values":dict(zip(TARGETS,v))};
    if inv:vals.append(v[0])
  nontrivial=all_inv and len({json.dumps(v,sort_keys=True) for v in vals})>=2
  lattice[level]={"all_regime_square_cells_architecture_invariant":all_inv,"nontrivial":nontrivial,"cells":cells}
  if minimal is None and nontrivial:minimal=level
 full_convergence=[];disagreement=[]
 for reg in REGIMES:
  for sq in SQUARES:
   (full_convergence if lattice["FULL_FINGERPRINT"]["cells"][reg][sq]["invariant"] else disagreement).append(reg+"|"+sq)
 regime_changes={t:{sq:fingerprints["Q_LOW"][t][sq]!=fingerprints["Q_HIGH"][t][sq] for sq in SQUARES} for t in TARGETS}
 any_change=any(v for t in TARGETS for v in regime_changes[t].values())
 if recovered:localization="SEARCH_STATE_LOCALIZED_P20_RECOVERY"
 elif full_convergence and any_change:localization="SEARCH_STATE_MODULATED_PARTIAL_CONVERGENCE"
 elif not full_convergence and not any_change:localization="ARCHITECTURE_DOMINANT_NOT_SEARCH_STATE_LOCALIZED"
 else:localization="MIXED_SEARCH_STATE_BY_ARCHITECTURE_FAILURE_GEOMETRY"
 pawnq=sum(r["inanis"]["arms"]["PAWN_Q"]["fine_changed"] for x in by.values() for r in x["rows"])
 coarse=any(r["targets"][t]["arms"][b]["coarse_changed"] for x in by.values() for r in x["rows"] for t in TARGETS for b in ("10","01","11","ALL"))
 if recovered:verdict="SEARCH_STATE_CONDITIONAL_P20_RELATION_LAW_RECOVERED"
 elif strict:verdict="SEARCH_STATE_CONDITIONAL_RELATION_NATURALITY_WITHOUT_P20_FINGERPRINT"
 elif minimal:verdict="P20_LAW_NOT_RECOVERED_BUT_MINIMAL_ARCHITECTURE_INVARIANT_CAUSAL_OBJECT_RECONSTITUTED"
 else:verdict="TRANSPORT_FAILURE_PERSISTS_AFTER_PREINTERVENTION_QUOTIENTING"
 out={"schema":"c3x-p23-adjudication-v1","scientific_stage":STAGE,"precommit_receipt_sha256":pre["receipt_sha256"],"fresh_holdout_cells":96,"p22_cells_reused":False,"quotient":pre["quotient"],"fingerprints":fingerprints,"pairwise_compatibility":compatibility,"p20_conditional_recovery_regimes":recovered,"strict_conditional_naturality_regimes":strict,"abstraction_lattice":lattice,"minimal_architecture_invariant_causal_object":minimal,"failure_localization":localization,"full_fingerprint_convergence_cells":full_convergence,"full_fingerprint_disagreement_cells":disagreement,"regime_changes_by_engine_square":regime_changes,"inanis_pawn_q_negative_control":{"fine_changes":pawnq,"pass":pawnq==0},"robust_wdl_changed_any_arm":coarse,"verdict":verdict,"authority_ceiling":"fresh P22-unused pawnless-core cells; frozen Q-share rank quotient; three admitted PSM_READ engines; Inanis negative control; 300k nodes; fine-value relation geometry only"};seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P23_ADJUDICATION",verdict,localization,"minimal=",minimal,"recovered=",recovered,"strict=",strict,"pawnq=",pawnq)

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 p=sp.add_parser("filter");p.add_argument("--census",required=True);p.add_argument("--p22-selected",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=filter_holdout)
 p=sp.add_parser("preseal");
 for k in ("holdout","selected","rust_report","cpp_cert","r_audit","cross_seal","pool","p22_precommit","out"):p.add_argument("--"+k.replace("_","-"),required=True)
 p.set_defaults(fn=preseal)
 p=sp.add_parser("vertex");p.add_argument("--precommit",required=True);p.add_argument("--engine",action="append",required=True);p.add_argument("--inanis",required=True);p.add_argument("--family",choices=FAMILIES,required=True);p.add_argument("--nodes",type=int,default=300000);p.add_argument("--out",required=True);p.set_defaults(fn=vertex)
 p=sp.add_parser("adjudicate");p.add_argument("--precommit",required=True);p.add_argument("--results",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=adjudicate)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
