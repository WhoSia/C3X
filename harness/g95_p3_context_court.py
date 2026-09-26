#!/usr/bin/env python3
import argparse,hashlib,json,subprocess,sys
from collections import defaultdict,Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import c3x_context_v2 as ctx
sys.path.insert(0,str(ROOT/"harness"))
import p32_event_court as p32, p33_lineage_court as p33, g95_p1_fiber_court as p1

STAGE="C3X 0.7.0-G9.5-P3"; ENGINES=("stockfish_19","berserk","ethereal"); MAX_CAND=8
def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load(p):return json.loads(Path(p).read_text())
def gap(x):return x

def precommit(a):
 sup=load(a.support);law=load(a.constitution);corp=load(a.corpus);p2=load(a.p2_precommit)
 if sup.get("schema")!="c3x-g95-p3-support-v1" or sup.get("p3_selective_results_consulted") is not False:raise SystemExit("P3_SUPPORT")
 if law.get("constitution",{}).get("schema")!="c3x-lawgen-constitution-v13":raise SystemExit("P3_LAW")
 if corp.get("schema")!="c3x-g95-p3-corpus-v1":raise SystemExit("P3_CORPUS")
 if p2.get("schema")!="c3x-g95-p2-precommit-v1":raise SystemExit("P3_P2_PRE")
 cases=[]
 for role,key,tag in (("FRESH_RECONSTITUTION","discovery_positions","disc"),("HELDOUT_REGIME_TRANSPORT","heldout_positions","hold")):
  for i,pos in enumerate(corp[key]):
   for e in ENGINES:cases.append({"case_id":f"p3:{tag}:{i}:{e}","role":role,"engine":e,"position_id":pos["position_id"],"candidate_sha256":pos["candidate_sha256"],"cell":pos["cell"],"family":pos["family"],"frontier":pos["frontier"]})
 out={"schema":"c3x-g95-p3-precommit-v1","scientific_stage":STAGE,"p3_selective_results_consulted":False,
  "support_sha256":digest(sup),"constitution_sha256":law["constitution_sha256"],"corpus_sha256":digest(corp),
  "p2_precommit_receipt_sha256":p2["receipt_sha256"],"variants":p2["variants"],"architecture_descriptors":p2["architecture_descriptors"],
  "execution":p2["execution"],"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P3_PRECOMMIT",out["receipt_sha256"],"cases",len(cases))

def verify_binary(pre,case,path):
 v=pre["variants"][case["engine"]]
 if p32.sha_file(path)!=v["sha256"]:raise SystemExit("P3_BINARY_ID")
 return v["protocol"]

def candidates(trace,frontier,n=MAX_CAND):
 by=defaultdict(list);seen=set()
 for i,e in enumerate(trace["events"]):
  if e["ply"]>frontier or e["address_id"] in seen:continue
  seen.add(e["address_id"]);z=dict(e);z["ordinal"]=i;by[(e["scope"],e["class"],p1.ply_bucket(e["ply"]))].append(z)
 for k in by:by[k].sort(key=lambda z:z["address_id"])
 out=[];r=0;keys=sorted(by)
 while len(out)<n:
  add=False
  for k in keys:
   if r<len(by[k]):out.append(by[k][r]);add=True
   if len(out)>=n:break
  if not add:break
  r+=1
 return out

def case_run(a):
 pre=load(a.precommit);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if not case:raise SystemExit("P3_CASE")
 protocol=verify_binary(pre,case,a.binary);work=Path(a.case_out).parent/"runs";work.mkdir(parents=True,exist_ok=True)
 parent=p32.run_history(a.binary,protocol,case["cell"],"CATALOG",case["family"],case["frontier"],None,work/"000-parent")
 cand=candidates(parent["trace"],case["frontier"]);pmap={e["address_id"]:(i,e) for i,e in enumerate(parent["trace"]["events"])}
 profiles=[];targets=[];frecs=[];miss=[]
 for j,e in enumerate(cand):
  addr=dict(e["address"]);addr["address_id"]=e["address_id"]
  cf=p32.run_history(a.binary,protocol,case["cell"],"REMOVE_SET",case["family"],case["frontier"],[addr],work/f"{j+1:03d}-single")
  fired=bool(cf["trace"]["targets"] and cf["trace"]["targets"][0]["fired"])
  if not fired:miss.append(e["address_id"]);continue
  lin=p33.write_lineage(a.lineager,parent["trace"],cf["trace"],work/"lineage",f"event-{j}")
  d=p1.diagnostic(parent["trace"],cf["trace"],lin);rec0={"source_scope":e["scope"],"source_class":e["class"],"source_ply":e["ply"],"diagnostic":d};fid=p1.fiber_id(rec0,0)
  ordinal,pe=pmap[e["address_id"]];cv,av=ctx.build_context(case["cell"]["fen"],parent["semantic"],parent["trace"],pe,ordinal,pre["architecture_descriptors"][case["engine"]])
  rid=f'{case["case_id"]}:{e["address_id"][:16]}'
  profiles.append({"record_id":rid,"engine":case["engine"],"position_id":case["position_id"],"event_id":e["address_id"],"fiber_id":fid,"context":cv,"architecture_context":av,"causal_availability":"EVENT_PREFIX_ONLY"})
  targets.append({"record_id":rid,"root_change":cf["semantic"]["bestmove"]!=parent["semantic"]["bestmove"],"parent_bestmove":parent["semantic"]["bestmove"],"counterfactual_bestmove":cf["semantic"]["bestmove"],"parent_score":parent["semantic"].get("score"),"counterfactual_score":cf["semantic"].get("score"),"parent_wdl":parent["semantic"].get("wdl"),"counterfactual_wdl":cf["semantic"].get("wdl"),"parent_pv":parent["semantic"].get("pv"),"counterfactual_pv":cf["semantic"].get("pv")})
  frecs.append({"event_id":e["address_id"],"source_scope":e["scope"],"source_class":e["class"],"source_ply":e["ply"],"diagnostic":d,"declared_fiber_id":fid})
 fi=work/"fiber-input.json";fo=work/"fiber-verify.json";fi.write_text(json.dumps({"level":"F0","records":frecs},sort_keys=True)+"\n");subprocess.run([a.fiber_verifier,str(fi),str(fo)],check=True)
 fv=load(fo)
 if fv.get("mismatches") or fv.get("target_fields_consulted") is not False:raise SystemExit("P3_FIBER_VERIFY")
 pd={"schema":"c3x-context-profile-batch-v2","schema_version":"c3x-context-v2","scientific_stage":STAGE,"case_id":case["case_id"],"role":case["role"],"records":profiles,"causal_availability":"EVENT_PREFIX_ONLY","target_fields_consulted":False,"raw_full_key_emitted":False}
 td={"schema":"c3x-context-target-batch-v1","scientific_stage":STAGE,"case_id":case["case_id"],"role":case["role"],"records":targets}
 Path(a.profile_out).write_text(json.dumps(pd,indent=2,sort_keys=True)+"\n");Path(a.target_out).write_text(json.dumps(td,indent=2,sort_keys=True)+"\n")
 man={"schema":"c3x-g95-p3-case-v1","scientific_stage":STAGE,"case_id":case["case_id"],"role":case["role"],"engine":case["engine"],"position_id":case["position_id"],"candidate_count":len(cand),"fired_records":len(profiles),"missed_target_ids":miss,"profile_sha256":digest(pd),"target_sha256":digest(td),"fiber_verification":fv,"status":"PASS" if profiles and not miss else "PARTIAL_TARGET_FIRE_HOLD"}
 seal(man);Path(a.case_out).write_text(json.dumps(man,indent=2,sort_keys=True)+"\n");print("G95_P3_CASE",case["case_id"],man["status"],len(profiles))

def batches(root,schema,role=None):
 out=[]
 for p in Path(root).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")==schema and (role is None or x.get("role")==role):out.append(x)
 return out
def merge_discovery(a):
 ps=batches(a.root,"c3x-context-profile-batch-v2","FRESH_RECONSTITUTION");ts=batches(a.root,"c3x-context-target-batch-v1","FRESH_RECONSTITUTION")
 if len(ps)!=24 or len(ts)!=24:raise SystemExit(f"P3_DISC_BATCH {len(ps)} {len(ts)}")
 pm={r["record_id"]:r for b in ps for r in b["records"]};tm={r["record_id"]:r for b in ts for r in b["records"]}
 if set(pm)!=set(tm):raise SystemExit("P3_DISC_JOIN")
 if any(r.get("causal_availability")!="EVENT_PREFIX_ONLY" for r in pm.values()):raise SystemExit("P3_DISC_CAUSAL_AVAILABILITY")
 rows=[{"record_id":rid,"engine":pm[rid]["engine"],"position_id":pm[rid]["position_id"],"event_id":pm[rid]["event_id"],"fiber_id":pm[rid]["fiber_id"],"context":pm[rid]["context"],"architecture_context":pm[rid]["architecture_context"],"target":bool(tm[rid]["root_change"])} for rid in sorted(pm)]
 Path(a.out).write_text(json.dumps({"schema":"c3x-field-p3-discovery-input-v1","scientific_stage":STAGE,"records":rows},indent=2,sort_keys=True)+"\n");print("P3_DISC_MERGE",len(rows))

def cell(r,cs):return "||".join([r["fiber_id"]]+[f"{c}={r['context'][c]}" for c in cs])
def metrics(rs,cs):
 g=defaultdict(list)
 for r in rs:g[cell(r,cs)].append(r)
 col=sum(len({z["target"] for z in v})>1 for v in g.values());xp=sum(len(v) for v in g.values() if len({z["position_id"] for z in v})>1);xe=sum(len(v) for v in g.values() if len({z["engine"] for z in v})>1)
 n=len(rs);return {"records":n,"distinct_cells":len(g),"target_collisions":col,"compression":1-len(g)/n if n else 0,"cross_position_records":xp,"cross_engine_records":xe,"positive_records":sum(r["target"] for r in rs),"negative_records":sum(not r["target"] for r in rs)}
def cells(rs,cs):
 g=defaultdict(list)
 for r in rs:g[cell(r,cs)].append(r)
 return {k:{"label":"ROOT_CHANGE" if next(iter({z["target"] for z in v})) else "NO_ROOT_CHANGE","support":len(v),"engines":sorted({z["engine"] for z in v}),"positions":sorted({z["position_id"] for z in v})} for k,v in g.items() if len({z["target"] for z in v})==1}
def adm(m,g):return m["target_collisions"]==0 and m["compression"]+1e-12>=g["min_compression"] and m["cross_position_records"]>=g["min_records_in_cross_position_cells"] and m["cross_engine_records"]>=g["min_records_in_cross_engine_cells"] and m["positive_records"]>0 and m["negative_records"]>0
def eadm(m,g):return m["target_collisions"]==0 and m["compression"]+1e-12>=g["min_compression"] and m["cross_position_records"]>=g["min_records_in_cross_position_cells"] and m["positive_records"]>0 and m["negative_records"]>0
def select_field(a):
 law=load(a.constitution)["constitution"];inp=load(a.input);rust=load(a.rust_assessment);rs=inp["records"];sup=law["discovery_court"]["support_gate"];support=len(rs)>=sup["min_fired_records"] and sum(r["target"] for r in rs)>=sup["min_positive_records"] and sum(not r["target"] for r in rs)>=sup["min_negative_records"]
 fam=law["schema_families"];rivals=law.get("development_derived_rivals",[]);rc={z["schema_id"]:z for z in rust["census"]};census=[];good=[];rival_census=[]
 for f in fam:
  m=metrics(rs,f["coordinates"]);r=rc[f["id"]]
  for k in ("records","distinct_cells","target_collisions","cross_position_records","cross_engine_records"):
   if m[k]!=r[k]:raise SystemExit("P3_RUST_METRIC_"+k)
  if abs(m["compression"]-r["compression"])>1e-12:raise SystemExit("P3_RUST_COMPRESSION")
  ok=support and adm(m,law["discovery_court"]["admissibility"]);z={**f,"metrics":m,"admissible":ok,"cells":cells(rs,f["coordinates"]) if ok else {}}
  census.append(z)
  if ok:good.append(z)
 for f in rivals:
  m=metrics(rs,f["coordinates"]);r=rc[f["id"]]
  for k in ("records","distinct_cells","target_collisions","cross_position_records","cross_engine_records"):
   if m[k]!=r[k]:raise SystemExit("P3_RUST_RIVAL_METRIC_"+k)
  if abs(m["compression"]-r["compression"])>1e-12:raise SystemExit("P3_RUST_RIVAL_COMPRESSION")
  rival_census.append({**f,"metrics":m,"primary_eligible":False,"fresh_admissible_under_primary_metrics":support and adm(m,law["discovery_court"]["admissibility"])})
 good.sort(key=lambda z:(len(z["added_coordinates"]),z["rank"],z["id"]));sel=good[0] if good else None
 eng={}
 eg=law["discovery_court"]["engine_specific"];es=eg["support_gate"]
 for e in ENGINES:
  rr=[r for r in rs if r["engine"]==e];esp=len(rr)>=es["min_fired_records"] and sum(r["target"] for r in rr)>=es["min_positive_records"] and sum(not r["target"] for r in rr)>=es["min_negative_records"];gg=[]
  for f in fam:
   m=metrics(rr,f["coordinates"]);ok=esp and eadm(m,eg)
   if ok:gg.append({**f,"metrics":m,"admissible":True,"cells":cells(rr,f["coordinates"])})
  gg.sort(key=lambda z:(len(z["added_coordinates"]),z["rank"],z["id"]));eng[e]={"support_pass":esp,"selected_schema":gg[0] if gg else None,"admissible_schemas":gg}
 status="FRESH_DISCOVERY_SUPPORT_LIMITED" if not support else "NO_ADMISSIBLE_GLOBAL_SCHEMA" if sel is None else "GLOBAL_SCHEMA_RECONSTITUTED"
 out={"schema":"c3x-field-p3-discovery-v1","scientific_stage":STAGE,"status":status,"support":{"records":len(rs),"positive_records":sum(r["target"] for r in rs),"negative_records":sum(not r["target"] for r in rs),"pass":support},"context_schema_version":law["context_schema_version"],"causal_availability":law["context_measurement"]["causal_availability"],"schema_census":census,"development_rival_census":rival_census,"selected_global_schema":sel,"engine_specific":eng,"scope_gate":law["heldout_firewall"]["pre_target_scope_gate"],"engine_scope_gate":law["heldout_firewall"]["engine_specific_scope_gate"],"target_fields_consulted":True,"primary_selection_consulted_development_rivals":False}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P3_FIELD",status,sel["id"] if sel else None)

def merge_profiles(a):
 bs=batches(a.root,"c3x-context-profile-batch-v2","HELDOUT_REGIME_TRANSPORT")
 if len(bs)!=24:raise SystemExit("P3_HOLD_PROFILES")
 rows=sorted([r for b in bs for r in b["records"]],key=lambda z:z["record_id"])
 if any(r.get("causal_availability")!="EVENT_PREFIX_ONLY" for r in rows):raise SystemExit("P3_PROFILE_CAUSAL_AVAILABILITY")
 Path(a.out).write_text(json.dumps({"schema":"c3x-context-profile-batch-v2","schema_version":"c3x-context-v2","scientific_stage":STAGE,"records":rows,"causal_availability":"EVENT_PREFIX_ONLY","target_fields_consulted":False,"raw_full_key_emitted":False},indent=2,sort_keys=True)+"\n")
 print("P3_PROFILES",len(rows))
def predict(schema,rs):
 if not schema:return []
 cs=schema["coordinates"];cc=schema["cells"];out=[]
 for r in rs:
  k=cell(r,cs);c=cc.get(k)
  out.append({"record_id":r["record_id"],"engine":r["engine"],"position_id":r["position_id"],"event_id":r["event_id"],"fiber_id":r["fiber_id"],"cell_key":k,"status":"ABSTAIN_UNSEEN_CONTEXT" if not c else "CERTIFIED_ROOT_CHANGE" if c["label"]=="ROOT_CHANGE" else "CERTIFIED_NO_ROOT_CHANGE","predicted_root_change":None if not c else c["label"]=="ROOT_CHANGE","discovery_support":0 if not c else c["support"]})
 return out
def cov(pr,n):
 seen=[p for p in pr if p["status"]!="ABSTAIN_UNSEEN_CONTEXT"];return {"profiles":n,"seen":len(seen),"seen_fraction":len(seen)/n if n else 0,"covered_engines":sorted({p["engine"] for p in seen}),"covered_positions":sorted({p["position_id"] for p in seen}),"discovery_predicted_positive_profiles":sum(p["predicted_root_change"] is True for p in seen)}
def scope_run(a):
 f=load(a.field);p=load(a.profiles);rs=p["records"];gp=predict(f["selected_global_schema"],rs);gc=cov(gp,len(rs));g=f["scope_gate"];gc["gate_pass"]=gc["seen_fraction"]>=g["min_seen_fraction"] and len(gc["covered_engines"])>=g["required_engines"] and len(gc["covered_positions"])>=g["min_positions"] and gc["discovery_predicted_positive_profiles"]>=g["min_discovery_predicted_positive_profiles"]
 eng={}
 for e in ENGINES:
  rr=[r for r in rs if r["engine"]==e];s=f["engine_specific"][e]["selected_schema"];pr=predict(s,rr);cc=cov(pr,len(rr));eg=f["engine_scope_gate"];cc["gate_pass"]=cc["seen_fraction"]>=eg["min_seen_fraction"] and len(cc["covered_positions"])>=eg["min_positions"];eng[e]={"selected_schema_id":None if not s else s["id"],"predictions":pr,"coverage":cc}
 out={"schema":"c3x-field-p3-scope-v1","scientific_stage":STAGE,"field_status":f["status"],"discovery_support":f["support"],"selected_global_schema_id":None if not f["selected_global_schema"] else f["selected_global_schema"]["id"],"global_predictions":gp,"global_coverage":gc,"engine_specific":eng,"target_fields_consulted":False}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P3_SCOPE",gc["seen"],len(rs),gc["gate_pass"])
def merge_targets(a):
 bs=batches(a.root,"c3x-context-target-batch-v1","HELDOUT_REGIME_TRANSPORT")
 if len(bs)!=24:raise SystemExit("P3_HOLD_TARGETS")
 rows=sorted([r for b in bs for r in b["records"]],key=lambda z:z["record_id"]);Path(a.out).write_text(json.dumps({"schema":"c3x-context-target-batch-v1","scientific_stage":STAGE,"records":rows},indent=2,sort_keys=True)+"\n");print("P3_TARGETS",len(rows))
def compare(pr,tm):
 bad=[];ab=0;labels=defaultdict(set)
 for p in pr:
  if p["status"]=="ABSTAIN_UNSEEN_CONTEXT":ab+=1;continue
  t=tm[p["record_id"]];labels[p["cell_key"]].add(bool(t["root_change"]))
  if bool(p["predicted_root_change"])!=bool(t["root_change"]):bad.append({"record_id":p["record_id"],"engine":p["engine"],"position_id":p["position_id"],"cell_key":p["cell_key"],"predicted_root_change":p["predicted_root_change"],"observed_root_change":t["root_change"],"parent_bestmove":t.get("parent_bestmove"),"counterfactual_bestmove":t.get("counterfactual_bestmove")})
 return {"covered_verified":len(pr)-ab,"abstained":ab,"contradictions":bad,"mixed_cells":[{"cell_key":k,"labels":sorted(v)} for k,v in labels.items() if len(v)>1]}
def verify_run(a):
 s=load(a.scope);t=load(a.targets);tm={r["record_id"]:r for r in t["records"]};gr=compare(s["global_predictions"],tm);gpass=s["global_coverage"]["gate_pass"];gok=gpass and not gr["contradictions"] and not gr["mixed_cells"];eng={};allok=True
 for e in ENGINES:
  z=s["engine_specific"][e];r=compare(z["predictions"],tm);ok=z["coverage"]["gate_pass"] and not r["contradictions"] and not r["mixed_cells"];allok=allok and ok;eng[e]={"gate_pass":z["coverage"]["gate_pass"],"transport_certified":ok,"result":r}
 verdict="FRESH_RECONSTITUTION_SUPPORT_LIMITED_HOLD" if not s.get("discovery_support",{}).get("pass") else "ENGINE_CONDITIONAL_FIELDS_SUPPORTED_CROSS_ENGINE_GLUE_HOLD" if s.get("selected_global_schema_id") is None and allok else "NO_TOPOLOGY_AWARE_GLOBAL_FIELD_HOLD" if s.get("selected_global_schema_id") is None else "TOPOLOGY_FIELD_SCOPE_INSUFFICIENT_HOLD" if not gpass else "TOPOLOGY_CONTEXT_CAUSAL_FIELD_HELDOUT_CERTIFIED" if gok else "ENGINE_CONDITIONAL_FIELDS_SUPPORTED_CROSS_ENGINE_GLUE_HOLD" if allok else "TOPOLOGY_FIELD_HELDOUT_FALSIFIED"
 out={"schema":"c3x-field-p3-verification-v1","scientific_stage":STAGE,"verdict":verdict,"global_transport_certified":gok,"global":gr,"engine_specific":eng,"target_opened_after_scope":True}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P3_VERIFY",verdict)

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("precommit");q.add_argument("--support",required=True);q.add_argument("--constitution",required=True);q.add_argument("--corpus",required=True);q.add_argument("--p2-precommit",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=precommit)
 q=sp.add_parser("case");q.add_argument("--precommit",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--lineager",required=True);q.add_argument("--fiber-verifier",required=True);q.add_argument("--profile-out",required=True);q.add_argument("--target-out",required=True);q.add_argument("--case-out",required=True);q.set_defaults(fn=case_run)
 q=sp.add_parser("merge-discovery");q.add_argument("--root",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=merge_discovery)
 q=sp.add_parser("select-field");q.add_argument("--constitution",required=True);q.add_argument("--input",required=True);q.add_argument("--rust-assessment",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=select_field)
 q=sp.add_parser("merge-profiles");q.add_argument("--root",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=merge_profiles)
 q=sp.add_parser("scope");q.add_argument("--field",required=True);q.add_argument("--profiles",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=scope_run)
 q=sp.add_parser("merge-targets");q.add_argument("--root",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=merge_targets)
 q=sp.add_parser("verify");q.add_argument("--scope",required=True);q.add_argument("--targets",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=verify_run)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
