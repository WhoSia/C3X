#!/usr/bin/env python3
import argparse,hashlib,json,math,subprocess,sys
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import c3x_context_v2 as ctx
sys.path.insert(0,str(ROOT/"harness"))
import p32_event_court as p32
import p33_lineage_court as p33
import g95_p1_fiber_court as p1

STAGE="C3X 0.7.0-G9.5-P4"
ENGINES=("stockfish_19","berserk","ethereal")

def canon(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o): return hashlib.sha256(canon(o)).hexdigest()
def seal(o):
 o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load(p): return json.loads(Path(p).read_text())

def precommit(a):
 lawx=load(a.constitution);corp=load(a.corpus);p3pre=load(a.p3_precommit)
 if lawx.get("schema")!="c3x-lawgen-constitution-v14": raise SystemExit("P4_LAW")
 law=lawx["constitution"]
 if law.get("scientific_stage")!=STAGE: raise SystemExit("P4_STAGE")
 if corp.get("schema")!="c3x-g95-p4-corpus-v1": raise SystemExit("P4_CORPUS")
 if p3pre.get("schema")!="c3x-g95-p3-precommit-v1": raise SystemExit("P4_P3_PRE")
 if law["selective_firewall"]["p2_p3_root_change_labels_used_to_choose_sampling_strata"] is not False: raise SystemExit("P4_FIREWALL")
 cases=[]
 for role,key,tag in (("FRESH_DISCOVERY","discovery_positions","disc"),("HELDOUT_TRANSPORT","heldout_positions","hold")):
  for i,pos in enumerate(corp[key]):
   for e in ENGINES:
    cases.append({"case_id":f"p4:{tag}:{i}:{e}","role":role,"engine":e,
      "position_id":pos["position_id"],"candidate_sha256":pos["candidate_sha256"],
      "source_stratum":pos["source_stratum"],"source_logical":pos["source_logical"],
      "cell":pos["cell"],"family":pos["family"],"frontier":pos["frontier"]})
 out={"schema":"c3x-g95-p4-precommit-v1","scientific_stage":STAGE,
  "selective_results_consulted":False,"p2_p3_target_labels_consulted_for_design":False,
  "constitution_sha256":digest(lawx),"corpus_sha256":digest(corp),
  "p3_precommit_receipt_sha256":p3pre["receipt_sha256"],
  "variants":p3pre["variants"],"architecture_descriptors":p3pre["architecture_descriptors"],
  "execution":law["execution"],"sampling":law["sampling"],"power_gate":law["power_gate"],
  "context_field":law["context_field"],"heldout_firewall":law["heldout_firewall"],
  "positive_control_lane":law["positive_control_lane"],"public_explanation_harness":law["public_explanation_harness"],
  "verdict_ladder":law["verdict_ladder"],"claim_ceiling":law["claim_ceiling"],"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P4_PRECOMMIT",out["receipt_sha256"],"cases",len(cases))

def verify_binary(pre,case,path):
 v=pre["variants"][case["engine"]]
 if p32.sha_file(path)!=v["sha256"]: raise SystemExit("P4_BINARY_ID")
 return v["protocol"]

def case_run(a):
 pre=load(a.precommit);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if not case: raise SystemExit("P4_CASE")
 protocol=verify_binary(pre,case,a.binary)
 work=Path(a.case_out).parent/"runs";work.mkdir(parents=True,exist_ok=True)
 parent=p32.run_history(a.binary,protocol,case["cell"],"CATALOG",case["family"],case["frontier"],None,work/"000-parent")
 trace_path=work/"parent-trace.json";trace_path.write_text(json.dumps(parent["trace"],sort_keys=True)+"\n")
 sample_path=work/"sampling.json"
 subprocess.run([a.sampler,"sample","--trace",str(trace_path),"--plan",a.sampling_plan,
                 "--max-events",str(pre["execution"]["candidate_events_per_world"]),"--out",str(sample_path)],check=True)
 samp=load(sample_path)
 if samp.get("target_fields_consulted") is not False or samp.get("raw_full_key_emitted") is not False:
  raise SystemExit("P4_SAMPLER_FIREWALL")
 byid={e["address_id"]:(i,e) for i,e in enumerate(parent["trace"]["events"])}
 profiles=[];targets=[];frecs=[];miss=[]
 for j,s in enumerate(samp["selected"]):
  aid=s["event_id"]
  if aid not in byid: raise SystemExit("P4_SAMPLE_EVENT")
  ordinal,e=byid[aid];addr=dict(e["address"]);addr["address_id"]=aid
  cf=p32.run_history(a.binary,protocol,case["cell"],"REMOVE_SET",case["family"],case["frontier"],[addr],work/f"{j+1:03d}-single")
  fired=bool(cf["trace"]["targets"] and cf["trace"]["targets"][0]["fired"])
  if not fired:
   miss.append({"event_id":aid,"sampling_stratum":s["sampling_stratum"]});continue
  lin=p33.write_lineage(a.lineager,parent["trace"],cf["trace"],work/"lineage",f"event-{j}")
  d=p1.diagnostic(parent["trace"],cf["trace"],lin)
  rec0={"source_scope":e["scope"],"source_class":e["class"],"source_ply":e["ply"],"diagnostic":d}
  fid=p1.fiber_id(rec0,0)
  cv,av=ctx.build_context(case["cell"]["fen"],parent["semantic"],parent["trace"],e,ordinal,pre["architecture_descriptors"][case["engine"]])
  rid=f'{case["case_id"]}:{aid[:16]}'
  profiles.append({"record_id":rid,"engine":case["engine"],"position_id":case["position_id"],
    "source_stratum":case["source_stratum"],"source_logical":case["source_logical"],
    "event_id":aid,"fiber_id":fid,"sampling_stratum":s["sampling_stratum"],
    "context":cv,"architecture_context":av,"causal_availability":"EVENT_PREFIX_ONLY"})
  targets.append({"record_id":rid,"root_change":cf["semantic"]["bestmove"]!=parent["semantic"]["bestmove"],
    "parent_bestmove":parent["semantic"]["bestmove"],"counterfactual_bestmove":cf["semantic"]["bestmove"],
    "parent_score":parent["semantic"].get("score"),"counterfactual_score":cf["semantic"].get("score"),
    "parent_wdl":parent["semantic"].get("wdl"),"counterfactual_wdl":cf["semantic"].get("wdl"),
    "parent_pv":parent["semantic"].get("pv"),"counterfactual_pv":cf["semantic"].get("pv")})
  frecs.append({"event_id":aid,"source_scope":e["scope"],"source_class":e["class"],"source_ply":e["ply"],
    "diagnostic":d,"declared_fiber_id":fid})
 fi=work/"fiber-input.json";fo=work/"fiber-verify.json"
 fi.write_text(json.dumps({"level":"F0","records":frecs},sort_keys=True)+"\n")
 subprocess.run([a.fiber_verifier,str(fi),str(fo)],check=True)
 fv=load(fo)
 if fv.get("mismatches") or fv.get("target_fields_consulted") is not False: raise SystemExit("P4_FIBER_VERIFY")
 pd={"schema":"c3x-context-profile-batch-p4-v1","schema_version":"c3x-context-v2","scientific_stage":STAGE,
   "case_id":case["case_id"],"role":case["role"],"source_stratum":case["source_stratum"],"records":profiles,
   "causal_availability":"EVENT_PREFIX_ONLY","target_fields_consulted":False,"raw_full_key_emitted":False}
 td={"schema":"c3x-context-target-batch-p4-v1","scientific_stage":STAGE,"case_id":case["case_id"],
   "role":case["role"],"source_stratum":case["source_stratum"],"records":targets}
 Path(a.profile_out).write_text(json.dumps(pd,indent=2,sort_keys=True)+"\n")
 Path(a.target_out).write_text(json.dumps(td,indent=2,sort_keys=True)+"\n")
 man={"schema":"c3x-g95-p4-case-v1","scientific_stage":STAGE,"case_id":case["case_id"],"role":case["role"],
   "engine":case["engine"],"position_id":case["position_id"],"source_stratum":case["source_stratum"],
   "selected_records":samp["selected_count"],"fired_records":len(profiles),"missed_targets":miss,
   "sampling_census":samp["stratum_census"],"sampling_target_fields_consulted":False,
   "profile_sha256":digest(pd),"target_sha256":digest(td),"fiber_verification":fv,
   "status":"PASS" if profiles else "NO_FIRED_EVENT_HOLD"}
 seal(man);Path(a.case_out).write_text(json.dumps(man,indent=2,sort_keys=True)+"\n")
 print("G95_P4_CASE",case["case_id"],man["status"],"selected",samp["selected_count"],"fired",len(profiles))

def batches(root,schema,role=None):
 out=[]
 for p in Path(root).rglob("*.json"):
  try:x=load(p)
  except Exception:continue
  if x.get("schema")==schema and (role is None or x.get("role")==role):out.append(x)
 return out

def merge_controls(a):
 bs=batches(a.root,"c3x-g95-p4-positive-control-v1")
 if len(bs)!=3: raise SystemExit(f"P4_CONTROL_COUNT {len(bs)}")
 if {z["engine"] for z in bs}!=set(ENGINES): raise SystemExit("P4_CONTROL_ENGINES")
 passed=all(z["status"]=="PASS" and z["fresh_support_vote"] is False for z in bs)
 out={"schema":"c3x-g95-p4-control-gate-v1","scientific_stage":STAGE,
  "authority":"INSTRUMENT_CALIBRATION_ONLY_NO_FRESH_SUPPORT_VOTE",
  "controls":sorted(bs,key=lambda z:z["engine"]),"passed":passed,"fresh_support_records":0}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P4_CONTROL_GATE","PASS" if passed else "FAIL")
 if not passed: raise SystemExit("P4_CONTROL_GATE_FAIL")

def merge_discovery(a):
 ps=batches(a.root,"c3x-context-profile-batch-p4-v1","FRESH_DISCOVERY")
 ts=batches(a.root,"c3x-context-target-batch-p4-v1","FRESH_DISCOVERY")
 if len(ps)!=36 or len(ts)!=36: raise SystemExit(f"P4_DISC_BATCH {len(ps)} {len(ts)}")
 pm={r["record_id"]:r for b in ps for r in b["records"]}
 tm={r["record_id"]:r for b in ts for r in b["records"]}
 if set(pm)!=set(tm): raise SystemExit("P4_DISC_JOIN")
 if any(r.get("causal_availability")!="EVENT_PREFIX_ONLY" for r in pm.values()): raise SystemExit("P4_CAUSAL_AVAILABILITY")
 rows=[{"record_id":rid,"engine":pm[rid]["engine"],"position_id":pm[rid]["position_id"],
   "source_stratum":pm[rid]["source_stratum"],"sampling_stratum":pm[rid]["sampling_stratum"],
   "event_id":pm[rid]["event_id"],"fiber_id":pm[rid]["fiber_id"],"context":pm[rid]["context"],
   "architecture_context":pm[rid]["architecture_context"],"target":bool(tm[rid]["root_change"])}
   for rid in sorted(pm)]
 out={"schema":"c3x-field-p4-discovery-input-v1","scientific_stage":STAGE,"records":rows,
   "fresh_support_only":True,"positive_controls_included":False}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P4_DISC_MERGE",len(rows),"positive",sum(r["target"] for r in rows))

def cell(r,cs):
 return "||".join([r["fiber_id"]]+[f"{c}={r['context'][c]}" for c in cs])

def metrics(rs,cs):
 g=defaultdict(list)
 for r in rs:g[cell(r,cs)].append(r)
 col=sum(len({z["target"] for z in v})>1 for v in g.values())
 xp=sum(len(v) for v in g.values() if len({z["position_id"] for z in v})>1)
 xe=sum(len(v) for v in g.values() if len({z["engine"] for z in v})>1)
 n=len(rs)
 return {"records":n,"distinct_cells":len(g),"target_collisions":col,
  "compression":1-len(g)/n if n else 0.0,"cross_position_records":xp,"cross_engine_records":xe,
  "positive_records":sum(r["target"] for r in rs),"negative_records":sum(not r["target"] for r in rs)}

def cells(rs,cs):
 g=defaultdict(list)
 for r in rs:g[cell(r,cs)].append(r)
 out={}
 for k,v in g.items():
  labs={z["target"] for z in v}
  if len(labs)==1:
   out[k]={"label":"ROOT_CHANGE" if next(iter(labs)) else "NO_ROOT_CHANGE","support":len(v),
    "engines":sorted({z["engine"] for z in v}),"positions":sorted({z["position_id"] for z in v}),
    "source_strata":sorted({z["source_stratum"] for z in v})}
 return out

def binom_ge(n,p,k):
 return 1-sum(math.comb(n,i)*(p**i)*((1-p)**(n-i)) for i in range(k))

def admissible(m,g):
 return m["target_collisions"]<=g["max_target_collisions"] and m["compression"]+1e-12>=g["min_compression"] and \
  m["cross_position_records"]>=g["min_records_in_cross_position_cells"] and m["cross_engine_records"]>=g["min_records_in_cross_engine_cells"] and \
  m["positive_records"]>0 and m["negative_records"]>0

def engine_admissible(m,g):
 return m["target_collisions"]==0 and m["compression"]+1e-12>=g["min_compression"] and \
  m["cross_position_records"]>=g["min_records_in_cross_position_cells"] and m["positive_records"]>0 and m["negative_records"]>0

def select_field(a):
 law=load(a.constitution)["constitution"];inp=load(a.input);rust=load(a.rust_assessment);rs=inp["records"];pg=law["power_gate"]
 n=len(rs);pos=sum(r["target"] for r in rs);neg=n-pos
 by_engine={e:{"records":sum(r["engine"]==e for r in rs),"positive":sum(r["engine"]==e and r["target"] for r in rs)} for e in ENGINES}
 by_source={s:{"records":sum(r["source_stratum"]==s for r in rs),"positive":sum(r["source_stratum"]==s and r["target"] for r in rs)} for s in sorted({r["source_stratum"] for r in rs})}
 det=binom_ge(n,float(pg["sensitivity_prevalence"]),int(pg["min_positive_records"])) if n else 0.0
 reasons=[]
 if n<pg["min_fired_records"]:reasons.append("FIRED_RECORDS")
 if pos<pg["min_positive_records"]:reasons.append("POSITIVE_RECORDS")
 if neg<pg["min_negative_records"]:reasons.append("NEGATIVE_RECORDS")
 if det+1e-12<pg["min_detection_probability_at_sensitivity"]:reasons.append("EFFECTIVE_POWER")
 if any(z["records"]<pg["min_records_per_engine"] for z in by_engine.values()):reasons.append("ENGINE_RECORDS")
 if any(z["positive"]<pg["min_positive_per_engine"] for z in by_engine.values()):reasons.append("ENGINE_POSITIVES")
 if sum(z["positive"]>0 for z in by_source.values())<pg["min_positive_source_regimes"]:reasons.append("SOURCE_POSITIVE_BREADTH")
 support=not reasons
 fam=law["context_field"]["schema_families"];rc={z["schema_id"]:z for z in rust["census"]};census=[];good=[]
 for f in fam:
  m=metrics(rs,f["coordinates"]);r=rc[f["id"]]
  for k in ("records","distinct_cells","target_collisions","cross_position_records","cross_engine_records","positive_records","negative_records"):
   if m[k]!=r[k]: raise SystemExit("P4_RUST_METRIC_"+k)
  if abs(m["compression"]-r["compression"])>1e-12: raise SystemExit("P4_RUST_COMPRESSION")
  ok=support and admissible(m,law["context_field"]["admissibility"])
  z={**f,"metrics":m,"admissible":ok,"cells":cells(rs,f["coordinates"]) if ok else {}}
  census.append(z)
  if ok:good.append(z)
 good.sort(key=lambda z:(len(z["added_coordinates"]),z["rank"],z["id"]));sel=good[0] if good else None
 eg=law["context_field"]["engine_specific"];eng={}
 for e in ENGINES:
  rr=[r for r in rs if r["engine"]==e]
  ep=len(rr)>=eg["min_fired_records"] and sum(r["target"] for r in rr)>=eg["min_positive_records"] and sum(not r["target"] for r in rr)>=eg["min_negative_records"]
  gg=[]
  for f in fam:
   m=metrics(rr,f["coordinates"]);ok=ep and engine_admissible(m,eg)
   if ok:gg.append({**f,"metrics":m,"admissible":True,"cells":cells(rr,f["coordinates"])})
  gg.sort(key=lambda z:(len(z["added_coordinates"]),z["rank"],z["id"]))
  eng[e]={"support_pass":ep,"records":len(rr),"positive_records":sum(r["target"] for r in rr),
    "negative_records":sum(not r["target"] for r in rr),"selected_schema":gg[0] if gg else None,"admissible_schemas":gg}
 status="RARE_EVENT_SUPPORT_POWER_HOLD" if not support else "NO_ADMISSIBLE_GLOBAL_SCHEMA" if sel is None else "GLOBAL_SCHEMA_RECONSTITUTED"
 out={"schema":"c3x-field-p4-discovery-v1","scientific_stage":STAGE,"status":status,
  "support":{"records":n,"positive_records":pos,"negative_records":neg,"pass":support,"failure_reasons":reasons,
    "effective_detection_probability_at_sensitivity":det,"by_engine":by_engine,"by_source_regime":by_source,
    "by_sampling_stratum":dict(Counter(r["sampling_stratum"] for r in rs)),
    "positive_by_sampling_stratum":dict(Counter(r["sampling_stratum"] for r in rs if r["target"]))},
  "context_schema_version":"c3x-context-v2","schema_census":census,"selected_global_schema":sel,"engine_specific":eng,
  "scope_gate":law["heldout_firewall"]["global_scope_gate"],"engine_scope_gate":law["heldout_firewall"]["engine_scope_gate"],
  "target_fields_consulted":True,"feature_expansion_performed":False}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P4_FIELD",status,"positive",pos,"n",n,"schema",None if sel is None else sel["id"])

def merge_profiles(a):
 bs=batches(a.root,"c3x-context-profile-batch-p4-v1","HELDOUT_TRANSPORT")
 if len(bs)!=24: raise SystemExit(f"P4_HOLD_PROFILES {len(bs)}")
 rows=sorted([r for b in bs for r in b["records"]],key=lambda z:z["record_id"])
 if any(r.get("causal_availability")!="EVENT_PREFIX_ONLY" for r in rows): raise SystemExit("P4_PROFILE_CAUSAL_AVAILABILITY")
 out={"schema":"c3x-context-profile-batch-p4-v1","schema_version":"c3x-context-v2","scientific_stage":STAGE,
   "records":rows,"causal_availability":"EVENT_PREFIX_ONLY","target_fields_consulted":False,"raw_full_key_emitted":False}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P4_PROFILES",len(rows))

def predict(schema,rs):
 if not schema:return []
 cs=schema["coordinates"];cc=schema["cells"];out=[]
 for r in rs:
  k=cell(r,cs);c=cc.get(k)
  out.append({"record_id":r["record_id"],"engine":r["engine"],"position_id":r["position_id"],
    "source_stratum":r["source_stratum"],"sampling_stratum":r["sampling_stratum"],"event_id":r["event_id"],"fiber_id":r["fiber_id"],
    "cell_key":k,"status":"ABSTAIN_UNSEEN_CONTEXT" if not c else "CERTIFIED_ROOT_CHANGE" if c["label"]=="ROOT_CHANGE" else "CERTIFIED_NO_ROOT_CHANGE",
    "predicted_root_change":None if not c else c["label"]=="ROOT_CHANGE","discovery_support":0 if not c else c["support"]})
 return out

def coverage(pr,n):
 seen=[p for p in pr if p["status"]!="ABSTAIN_UNSEEN_CONTEXT"]
 return {"profiles":n,"seen":len(seen),"seen_fraction":len(seen)/n if n else 0.0,
  "covered_engines":sorted({p["engine"] for p in seen}),"covered_positions":sorted({p["position_id"] for p in seen}),
  "covered_source_regimes":sorted({p["source_stratum"] for p in seen}),
  "discovery_predicted_positive_profiles":sum(p["predicted_root_change"] is True for p in seen)}

def scope_run(a):
 f=load(a.field);p=load(a.profiles);rs=p["records"];gp=predict(f["selected_global_schema"],rs);gc=coverage(gp,len(rs));g=f["scope_gate"]
 gc["gate_pass"]=gc["seen_fraction"]>=g["min_seen_fraction"] and len(gc["covered_engines"])>=g["required_engines"] and \
  len(gc["covered_positions"])>=g["min_positions"] and len(gc["covered_source_regimes"])>=g["min_source_regimes"] and \
  gc["discovery_predicted_positive_profiles"]>=g["min_discovery_predicted_positive_profiles"]
 eng={}
 for e in ENGINES:
  rr=[r for r in rs if r["engine"]==e];s=f["engine_specific"][e]["selected_schema"];pr=predict(s,rr);cc=coverage(pr,len(rr));eg=f["engine_scope_gate"]
  cc["gate_pass"]=cc["seen_fraction"]>=eg["min_seen_fraction"] and len(cc["covered_positions"])>=eg["min_positions"] and len(cc["covered_source_regimes"])>=eg["min_source_regimes"]
  eng[e]={"selected_schema_id":None if not s else s["id"],"predictions":pr,"coverage":cc}
 out={"schema":"c3x-field-p4-scope-v1","scientific_stage":STAGE,"field_status":f["status"],"discovery_support":f["support"],
  "selected_global_schema_id":None if not f["selected_global_schema"] else f["selected_global_schema"]["id"],
  "global_predictions":gp,"global_coverage":gc,"engine_specific":eng,"target_fields_consulted":False}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P4_SCOPE",gc["seen"],len(rs),gc["gate_pass"])

def merge_targets(a):
 bs=batches(a.root,"c3x-context-target-batch-p4-v1","HELDOUT_TRANSPORT")
 if len(bs)!=24: raise SystemExit(f"P4_HOLD_TARGETS {len(bs)}")
 rows=sorted([r for b in bs for r in b["records"]],key=lambda z:z["record_id"])
 Path(a.out).write_text(json.dumps({"schema":"c3x-context-target-batch-p4-v1","scientific_stage":STAGE,"records":rows},indent=2,sort_keys=True)+"\n")
 print("P4_TARGETS",len(rows))

def compare(pr,tm):
 bad=[];ab=0;labels=defaultdict(set)
 for p in pr:
  if p["status"]=="ABSTAIN_UNSEEN_CONTEXT":ab+=1;continue
  t=tm[p["record_id"]];labels[p["cell_key"]].add(bool(t["root_change"]))
  if bool(p["predicted_root_change"])!=bool(t["root_change"]):
   bad.append({"record_id":p["record_id"],"engine":p["engine"],"position_id":p["position_id"],"source_stratum":p["source_stratum"],
    "cell_key":p["cell_key"],"predicted_root_change":p["predicted_root_change"],"observed_root_change":t["root_change"],
    "parent_bestmove":t.get("parent_bestmove"),"counterfactual_bestmove":t.get("counterfactual_bestmove")})
 return {"covered_verified":len(pr)-ab,"abstained":ab,"contradictions":bad,
  "mixed_cells":[{"cell_key":k,"labels":sorted(v)} for k,v in labels.items() if len(v)>1]}

def verify_run(a):
 s=load(a.scope);t=load(a.targets);tm={r["record_id"]:r for r in t["records"]};gr=compare(s["global_predictions"],tm)
 gpass=s["global_coverage"]["gate_pass"];gok=gpass and not gr["contradictions"] and not gr["mixed_cells"]
 eng={};allok=True
 for e in ENGINES:
  z=s["engine_specific"][e];r=compare(z["predictions"],tm)
  ok=z["selected_schema_id"] is not None and z["coverage"]["gate_pass"] and not r["contradictions"] and not r["mixed_cells"]
  allok=allok and ok;eng[e]={"gate_pass":z["coverage"]["gate_pass"],"transport_certified":ok,"result":r}
 if not s.get("discovery_support",{}).get("pass"):verdict="RARE_EVENT_SUPPORT_POWER_HOLD"
 elif s.get("selected_global_schema_id") is None:verdict="ENGINE_CONDITIONAL_RARE_EVENT_FIELDS_CROSS_ENGINE_GLUE_HOLD" if allok else "SUPPORT_RECOVERED_NO_ADMISSIBLE_GLOBAL_FIELD_HOLD"
 elif not gpass:verdict="RARE_EVENT_FIELD_SCOPE_INSUFFICIENT_HOLD"
 elif gok:verdict="RARE_EVENT_CAUSAL_FIELD_HELDOUT_CERTIFIED"
 elif allok:verdict="ENGINE_CONDITIONAL_RARE_EVENT_FIELDS_CROSS_ENGINE_GLUE_HOLD"
 else:verdict="RARE_EVENT_FIELD_HELDOUT_FALSIFIED"
 out={"schema":"c3x-field-p4-verification-v1","scientific_stage":STAGE,"verdict":verdict,
  "global_transport_certified":gok,"global":gr,"engine_specific":eng,"target_opened_after_scope":True}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P4_VERIFY",verdict)

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("precommit");q.add_argument("--constitution",required=True);q.add_argument("--corpus",required=True);q.add_argument("--p3-precommit",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=precommit)
 q=sp.add_parser("case");q.add_argument("--precommit",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--sampler",required=True);q.add_argument("--sampling-plan",required=True);q.add_argument("--lineager",required=True);q.add_argument("--fiber-verifier",required=True);q.add_argument("--profile-out",required=True);q.add_argument("--target-out",required=True);q.add_argument("--case-out",required=True);q.set_defaults(fn=case_run)
 q=sp.add_parser("merge-controls");q.add_argument("--root",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=merge_controls)
 q=sp.add_parser("merge-discovery");q.add_argument("--root",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=merge_discovery)
 q=sp.add_parser("select-field");q.add_argument("--constitution",required=True);q.add_argument("--input",required=True);q.add_argument("--rust-assessment",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=select_field)
 q=sp.add_parser("merge-profiles");q.add_argument("--root",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=merge_profiles)
 q=sp.add_parser("scope");q.add_argument("--field",required=True);q.add_argument("--profiles",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=scope_run)
 q=sp.add_parser("merge-targets");q.add_argument("--root",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=merge_targets)
 q=sp.add_parser("verify");q.add_argument("--scope",required=True);q.add_argument("--targets",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=verify_run)
 a=ap.parse_args();a.fn(a)

if __name__=="__main__": main()
