#!/usr/bin/env python3
import argparse,hashlib,json,math,subprocess,sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import c3x_relational_v1 as ctx
sys.path.insert(0,str(ROOT/"harness"))
import p32_event_court as p32
import p33_lineage_court as p33
import g95_p1_fiber_court as p1

STAGE="C3X 0.7.0-G9.5-P6"
ENGINES=("stockfish_19","berserk","ethereal")
ROLES=("RELATIONAL_TRAIN","RELATIONAL_SELECTION","UNTOUCHED_TRANSPORT")

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):
 o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load(p):return json.loads(Path(p).read_text())
def binom_ge(n,p,k):return 1-sum(math.comb(n,i)*(p**i)*((1-p)**(n-i)) for i in range(k))

def support_summary(rows,g,require_engine_positive=False):
 n=len(rows);pos=sum(bool(r["target"]) for r in rows);neg=n-pos
 byeng={e:{"records":sum(r["engine"]==e for r in rows),"positive":sum(r["engine"]==e and r["target"] for r in rows)} for e in ENGINES}
 bysrc={s:{"records":sum(r["source_stratum"]==s for r in rows),"positive":sum(r["source_stratum"]==s and r["target"] for r in rows)} for s in sorted({r["source_stratum"] for r in rows})}
 power=binom_ge(n,float(g["sensitivity_prevalence"]),int(g["min_positive_records"])) if n else 0.0
 reasons=[]
 if n<g["min_fired_records"]:reasons.append("FIRED_RECORDS")
 if pos<g["min_positive_records"]:reasons.append("POSITIVE_RECORDS")
 if neg<g["min_negative_records"]:reasons.append("NEGATIVE_RECORDS")
 if power+1e-12<g["min_detection_probability_at_sensitivity"]:reasons.append("EFFECTIVE_POWER")
 if any(z["records"]<g["min_records_per_engine"] for z in byeng.values()):reasons.append("ENGINE_RECORDS")
 if require_engine_positive and any(z["positive"]<g["min_positive_per_engine"] for z in byeng.values()):reasons.append("ENGINE_POSITIVES")
 if sum(z["positive"]>0 for z in bysrc.values())<g["min_positive_source_regimes"]:reasons.append("SOURCE_POSITIVE_BREADTH")
 return {"records":n,"positive_records":pos,"negative_records":neg,"pass":not reasons,"failure_reasons":reasons,
  "effective_detection_probability_at_sensitivity":power,"by_engine":byeng,"by_source_regime":bysrc}

def precommit(a):
 lawx=load(a.constitution);corp=load(a.corpus);p4pre=load(a.p4_precommit);p5close=load(a.p5_closure)
 if lawx.get("schema")!="c3x-lawgen-constitution-v16":raise SystemExit("P6_LAW")
 law=lawx["constitution"]
 if law.get("scientific_stage")!=STAGE or corp.get("schema")!="c3x-g95-p6-corpus-v1":raise SystemExit("P6_STAGE_CORPUS")
 if p4pre.get("schema")!="c3x-g95-p4-precommit-v1" or p5close.get("schema")!="c3x-g95-p5-closure-v1":raise SystemExit("P6_PARENT")
 ce=p5close["selection"]["shared_counterexample"]
 if ce.get("authority")!=law["counterexample_sequestration"]["p5_shared_counterexample_authority_required"]:raise SystemExit("P6_COUNTEREXAMPLE_AUTHORITY")
 if law["counterexample_sequestration"]["p5_selection_labels_confirmatory_vote"] is not False:raise SystemExit("P6_P5_LABEL_FIREWALL")
 if law["counterexample_sequestration"]["p5_selection_target_artifacts_may_be_downloaded"] is not False:raise SystemExit("P6_P5_ARTIFACT_FIREWALL")
 cases=[]
 for role,key,tag in (
   ("RELATIONAL_TRAIN","relational_train_positions","train"),
   ("RELATIONAL_SELECTION","relational_selection_positions","select"),
   ("UNTOUCHED_TRANSPORT","untouched_transport_positions","transport")):
  for i,pos in enumerate(corp[key]):
   for e in ENGINES:
    cases.append({"case_id":f"p6:{tag}:{i}:{e}","role":role,"engine":e,
      "position_id":pos["position_id"],"candidate_sha256":pos["candidate_sha256"],
      "source_stratum":pos["source_stratum"],"source_logical":pos["source_logical"],
      "cell":pos["cell"],"family":pos["family"],"frontier":pos["frontier"]})
 out={"schema":"c3x-g95-p6-precommit-v1","scientific_stage":STAGE,
   "constitution_sha256":digest(lawx),"corpus_sha256":digest(corp),
   "parent_p5_closure_receipt_sha256":p5close["receipt_sha256"],
   "p5_selection_labels_consulted":False,"p5_shared_counterexample_confirmatory_vote":False,
   "variants":p4pre["variants"],"architecture_descriptors":p4pre["architecture_descriptors"],
   "execution":law["execution"],"temporal_firewall":law["temporal_firewall"],
   "train_support_gate":law["train_support_gate"],"selection_support_gate":law["selection_support_gate"],
   "representation_grammar":law["representation_grammar"],"selection_gate":law["selection_gate"],
   "transport_gate":law["transport_gate"],"public_explanation_harness":law["public_explanation_harness"],
   "claim_ceiling":law["claim_ceiling"],"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P6_PRECOMMIT",out["receipt_sha256"],"cases",len(cases))

def verify_binary(pre,case,path):
 v=pre["variants"][case["engine"]]
 if p32.sha_file(path)!=v["sha256"]:raise SystemExit("P6_BINARY_ID")
 return v["protocol"]

def case_run(a):
 pre=load(a.precommit);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if not case:raise SystemExit("P6_CASE")
 protocol=verify_binary(pre,case,a.binary)
 work=Path(a.case_out).parent/"runs";work.mkdir(parents=True,exist_ok=True)
 parent=p32.run_history(a.binary,protocol,case["cell"],"CATALOG",case["family"],case["frontier"],None,work/"000-parent")
 trace_path=work/"parent-trace.json";trace_path.write_text(json.dumps(parent["trace"],sort_keys=True)+"\n")
 sample_path=work/"sampling.json"
 subprocess.run([a.sampler,"sample","--trace",str(trace_path),"--plan",a.sampling_plan,
   "--max-events",str(pre["execution"]["candidate_events_per_world"]),"--out",str(sample_path)],check=True)
 samp=load(sample_path)
 if samp.get("target_fields_consulted") is not False or samp.get("raw_full_key_emitted") is not False:raise SystemExit("P6_SAMPLER_FIREWALL")
 byid={e["address_id"]:(i,e) for i,e in enumerate(parent["trace"]["events"])}
 profiles=[];targets=[];frecs=[];miss=[]
 for j,s in enumerate(samp["selected"]):
  aid=s["event_id"]
  if aid not in byid:raise SystemExit("P6_SAMPLE_EVENT")
  ordinal,e=byid[aid];addr=dict(e["address"]);addr["address_id"]=aid
  cf=p32.run_history(a.binary,protocol,case["cell"],"REMOVE_SET",case["family"],case["frontier"],[addr],work/f"{j+1:03d}-single")
  fired=bool(cf["trace"]["targets"] and cf["trace"]["targets"][0]["fired"])
  if not fired:
   miss.append({"event_id":aid,"sampling_stratum":s["sampling_stratum"]});continue
  lin=p33.write_lineage(a.lineager,parent["trace"],cf["trace"],work/"lineage",f"event-{j}")
  d=p1.diagnostic(parent["trace"],cf["trace"],lin)
  rec0={"source_scope":e["scope"],"source_class":e["class"],"source_ply":e["ply"],"diagnostic":d}
  fid=p1.fiber_id(rec0,0)
  cv,rv,av=ctx.build_context(case["cell"]["fen"],parent["trace"],ordinal,pre["architecture_descriptors"][case["engine"]])
  rid=f'{case["case_id"]}:{aid[:16]}'
  profiles.append({"record_id":rid,"engine":case["engine"],"position_id":case["position_id"],
    "source_stratum":case["source_stratum"],"source_logical":case["source_logical"],
    "event_id":aid,"fiber_id":fid,"sampling_stratum":s["sampling_stratum"],
    "context":cv,"relations":rv,"architecture_context":av,"causal_availability":"STRICT_EVENT_PREFIX_ONLY",
    "future_parent_trace_consulted":False,"parent_terminal_semantic_consulted":False,"raw_full_key_emitted":False})
  targets.append({"record_id":rid,"root_change":cf["semantic"]["bestmove"]!=parent["semantic"]["bestmove"],
    "parent_bestmove":parent["semantic"]["bestmove"],"counterfactual_bestmove":cf["semantic"]["bestmove"],
    "parent_score":parent["semantic"].get("score"),"counterfactual_score":cf["semantic"].get("score"),
    "parent_pv":parent["semantic"].get("pv"),"counterfactual_pv":cf["semantic"].get("pv")})
  frecs.append({"event_id":aid,"source_scope":e["scope"],"source_class":e["class"],"source_ply":e["ply"],
    "diagnostic":d,"declared_fiber_id":fid})
 fi=work/"fiber-input.json";fo=work/"fiber-verify.json"
 fi.write_text(json.dumps({"level":"F0","records":frecs},sort_keys=True)+"\n")
 subprocess.run([a.fiber_verifier,str(fi),str(fo)],check=True)
 fv=load(fo)
 if fv.get("mismatches") or fv.get("target_fields_consulted") is not False:raise SystemExit("P6_FIBER_VERIFY")
 pd={"schema":"c3x-context-profile-batch-p6-v1","schema_version":"c3x-context-v4-relational","scientific_stage":STAGE,
   "case_id":case["case_id"],"role":case["role"],"source_stratum":case["source_stratum"],"records":profiles,
   "causal_availability":"STRICT_EVENT_PREFIX_ONLY","target_fields_consulted":False,"p5_selection_labels_consulted":False,
   "raw_full_key_emitted":False,"future_parent_trace_consulted":False,"parent_terminal_semantic_consulted":False}
 td={"schema":"c3x-context-target-batch-p6-v1","scientific_stage":STAGE,"case_id":case["case_id"],
   "role":case["role"],"source_stratum":case["source_stratum"],"records":targets}
 Path(a.profile_out).write_text(json.dumps(pd,indent=2,sort_keys=True)+"\n")
 Path(a.target_out).write_text(json.dumps(td,indent=2,sort_keys=True)+"\n")
 man={"schema":"c3x-g95-p6-case-v1","scientific_stage":STAGE,"case_id":case["case_id"],"role":case["role"],
   "engine":case["engine"],"position_id":case["position_id"],"source_stratum":case["source_stratum"],
   "selected_records":samp["selected_count"],"fired_records":len(profiles),"missed_targets":miss,
   "sampling_census":samp["stratum_census"],"profile_sha256":digest(pd),"target_sha256":digest(td),
   "fiber_verification":fv,"status":"PASS" if profiles else "NO_FIRED_EVENT_HOLD"}
 seal(man);Path(a.case_out).write_text(json.dumps(man,indent=2,sort_keys=True)+"\n")
 print("G95_P6_CASE",case["case_id"],man["status"],"selected",samp["selected_count"],"fired",len(profiles))

def batches(root,schema,role=None):
 out=[]
 for p in Path(root).rglob("*.json"):
  try:x=load(p)
  except Exception:continue
  if x.get("schema")==schema and (role is None or x.get("role")==role):out.append(x)
 return out

def merge_profiles(a):
 bs=batches(a.root,"c3x-context-profile-batch-p6-v1",a.role)
 expected={"RELATIONAL_TRAIN":36,"RELATIONAL_SELECTION":36,"UNTOUCHED_TRANSPORT":36}[a.role]
 if len(bs)!=expected:raise SystemExit(f"P6_PROFILE_BATCH {a.role} {len(bs)} {expected}")
 rows=sorted([r for b in bs for r in b["records"]],key=lambda z:z["record_id"])
 for r in rows:
  if r.get("causal_availability")!="STRICT_EVENT_PREFIX_ONLY" or r.get("future_parent_trace_consulted") is not False or r.get("parent_terminal_semantic_consulted") is not False or r.get("raw_full_key_emitted") is not False:
   raise SystemExit("P6_PROFILE_TEMPORAL_FIREWALL")
 out={"schema":"c3x-context-profile-merged-p6-v1","schema_version":"c3x-context-v4-relational","scientific_stage":STAGE,
   "role":a.role,"records":rows,"target_fields_consulted":False,"p5_selection_labels_consulted":False}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P6_PROFILES",a.role,len(rows))

def merge_targets(a):
 bs=batches(a.root,"c3x-context-target-batch-p6-v1",a.role)
 expected={"RELATIONAL_TRAIN":36,"RELATIONAL_SELECTION":36,"UNTOUCHED_TRANSPORT":36}[a.role]
 if len(bs)!=expected:raise SystemExit(f"P6_TARGET_BATCH {a.role} {len(bs)} {expected}")
 rows=sorted([r for b in bs for r in b["records"]],key=lambda z:z["record_id"])
 out={"schema":"c3x-context-target-merged-p6-v1","scientific_stage":STAGE,"role":a.role,"records":rows}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P6_TARGETS",a.role,len(rows))

def joined_rows(p,t):
 pm={r["record_id"]:r for r in p["records"]};tm={r["record_id"]:r for r in t["records"]}
 if set(pm)!=set(tm):raise SystemExit("P6_JOIN")
 return [{"record_id":rid,"engine":pm[rid]["engine"],"position_id":pm[rid]["position_id"],
   "source_stratum":pm[rid]["source_stratum"],"sampling_stratum":pm[rid]["sampling_stratum"],
   "event_id":pm[rid]["event_id"],"fiber_id":pm[rid]["fiber_id"],"context":pm[rid]["context"],
   "relations":pm[rid]["relations"],"architecture_context":pm[rid]["architecture_context"],"target":bool(tm[rid]["root_change"])}
   for rid in sorted(pm)]

def train_input(a):
 pre=load(a.precommit);p=load(a.profiles);t=load(a.targets)
 if p["role"]!="RELATIONAL_TRAIN" or t["role"]!="RELATIONAL_TRAIN":raise SystemExit("P6_TRAIN_ROLE")
 rows=joined_rows(p,t);sup=support_summary(rows,pre["train_support_gate"],True)
 out={"schema":"c3x-field-p6-train-input-v1","scientific_stage":STAGE,"records":rows,"support":sup,
   "train_targets_consulted":True,"p5_selection_labels_consulted":False,"selection_targets_consulted":False,"transport_targets_consulted":False}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P6_TRAIN_INPUT",len(rows),sup["positive_records"],"PASS" if sup["pass"] else sup["failure_reasons"])

def ref_value(r,rf):
 if rf.startswith("C."):return r["context"][rf[2:]]
 if rf.startswith("R."):return r["relations"][rf[2:]]
 raise SystemExit("P6_REF")

def term_value(r,t):
 typ=t["type"]
 if typ=="CONTEXT_ATOM":return r["context"][t["field"]]
 if typ=="RELATIONAL_ATOM":return r["relations"][t["field"]]
 if typ=="INTERACTION":return ref_value(r,t["left"])+"&"+ref_value(r,t["right"])
 raise SystemExit("P6_TERM")

def cell(r,terms):
 return "||".join([r["fiber_id"]]+[f'{t["id"]}={term_value(r,t)}' for t in terms])

def metrics(rows,terms):
 g=defaultdict(list)
 for r in rows:g[cell(r,terms)].append(r)
 col=sum(len({z["target"] for z in v})>1 for v in g.values())
 xp=sum(len(v) for v in g.values() if len({z["position_id"] for z in v})>1)
 xe=sum(len(v) for v in g.values() if len({z["engine"] for z in v})>1)
 rp=sum(len(v) for v in g.values() if len({z["target"] for z in v})==1 and bool(v[0]["target"]) and (len({z["position_id"] for z in v})>1 or len({z["engine"] for z in v})>1))
 rpc=sum(1 for v in g.values() if len({z["target"] for z in v})==1 and bool(v[0]["target"]) and (len({z["position_id"] for z in v})>1 or len({z["engine"] for z in v})>1))
 n=len(rows)
 return {"records":n,"distinct_cells":len(g),"target_collisions":col,"compression":1-len(g)/n if n else 0.0,
  "cross_position_records":xp,"cross_engine_records":xe,"reused_positive_records":rp,"reused_positive_cells":rpc,
  "positive_records":sum(r["target"] for r in rows),"negative_records":sum(not r["target"] for r in rows)}

def audit_shortlist(a):
 tr=load(a.train);sl=load(a.shortlist);grammar=load(a.grammar)
 if sl.get("schema")!="c3x-p6-train-shortlist-v1":raise SystemExit("P6_SHORTLIST")
 rows=tr["records"];allowed={t["id"]:t for t in grammar["terms"]};audits=[]
 for c in sl["shortlist"]:
  terms=c["basis_terms"];ids=[t["id"] for t in terms]
  if any(i not in allowed for i in ids) or len(terms)>grammar["max_terms"]:raise SystemExit("P6_GRAMMAR_ESCAPE")
  ints=sum(t["type"]=="INTERACTION" for t in terms)
  if ints>grammar["max_interaction_terms"]:raise SystemExit("P6_INTERACTION_ESCAPE")
  desc=sum(float(t["cost_bits"]) for t in terms)
  if desc>grammar["max_description_bits"]+1e-12 or abs(desc-float(c["description_bits"]))>1e-12:raise SystemExit("P6_DESCRIPTION_ESCAPE")
  m=metrics(rows,terms);rm=c["metrics"]
  for k in ("records","distinct_cells","target_collisions","cross_position_records","cross_engine_records","reused_positive_records","reused_positive_cells","positive_records","negative_records"):
   if m[k]!=rm[k]:raise SystemExit("P6_RUST_PY_METRIC_"+k)
  if abs(m["compression"]-rm["compression"])>1e-12:raise SystemExit("P6_RUST_PY_COMPRESSION")
  audits.append({"id":c["id"],"term_ids":ids,"metrics":m,"description_bits":desc,"mdl_bits":c["mdl_bits"]})
 out={"schema":"c3x-g95-p6-train-audit-v1","scientific_stage":STAGE,"support":tr["support"],
   "shortlist_count":len(audits),"audit_pass":True,"p5_selection_labels_consulted":False,"candidates":audits}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P6_TRAIN_AUDIT","PASS",len(audits))

def compare_predictions(preds,tm):
 seen=[];bad=[];labels=defaultdict(set)
 for p in preds:
  if p["status"]=="ABSTAIN_UNSEEN_CONTEXT":continue
  seen.append(p);y=bool(tm[p["record_id"]]["root_change"]);labels[p["cell_key"]].add(y)
  if bool(p["predicted_root_change"])!=y:
   bad.append({"record_id":p["record_id"],"engine":p["engine"],"position_id":p["position_id"],
     "source_stratum":p["source_stratum"],"cell_key":p["cell_key"],
     "predicted_root_change":p["predicted_root_change"],"observed_root_change":y})
 return seen,bad,[{"cell_key":k,"labels":sorted(v)} for k,v in labels.items() if len(v)>1]

def selection_field(a):
 pre=load(a.precommit);tr=load(a.train);sl=load(a.shortlist);q=load(a.query);p=load(a.profiles);t=load(a.targets)
 if p["role"]!="RELATIONAL_SELECTION" or t["role"]!="RELATIONAL_SELECTION":raise SystemExit("P6_SELECT_ROLE")
 rows=joined_rows(p,t);ss=support_summary(rows,pre["selection_support_gate"],False)
 def write_hold(status):
  out={"schema":"c3x-p6-selected-field-v1","scientific_stage":STAGE,"status":status,
   "selected_candidate":None,"selected_candidate_id":None,"selection_evaluations":[],
   "selection_support":ss,"selection_targets_consulted":True,"p5_selection_labels_consulted":False,
   "transport_targets_consulted":False,"post_selection_representation_mutation":False}
  seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
  print("P6_SELECTION",status,None,"passing",0)
 if not tr.get("support",{}).get("pass"):return write_hold("TRAIN_SUPPORT_HOLD")
 if not sl.get("shortlist"):return write_hold("NO_ADMISSIBLE_RELATIONAL_TRAIN_REPRESENTATION")
 if not ss["pass"]:return write_hold("SELECTION_SUPPORT_HOLD")
 tm={r["record_id"]:r for r in t["records"]};n=len(p["records"]);g=pre["selection_gate"]
 bycand={z["candidate_id"]:z["predictions"] for z in q["queries"]};candmap={z["id"]:z for z in sl["shortlist"]}
 evals=[];passing=[]
 for cid,c in candmap.items():
  preds=bycand.get(cid,[]);seen,bad,mixed=compare_predictions(preds,tm)
  engines=sorted({x["engine"] for x in seen});positions=sorted({x["position_id"] for x in seen});sources=sorted({x["source_stratum"] for x in seen})
  per={}
  for e in ENGINES:
   ee=[x for x in preds if x["engine"]==e];ss0=[x for x in ee if x["status"]!="ABSTAIN_UNSEEN_CONTEXT"];eb=[x for x in bad if x["engine"]==e]
   per[e]={"profiles":len(ee),"seen":len(ss0),"seen_fraction":len(ss0)/len(ee) if ee else 0.0,"contradictions":len(eb)}
  covered_pos=[x for x in seen if bool(tm[x["record_id"]]["root_change"])]
  pos_sources=sorted({x["source_stratum"] for x in covered_pos});cov=len(seen)/n if n else 0.0
  ok=(cov>=g["min_seen_fraction"] and len(engines)>=g["required_engines"] and len(positions)>=g["min_positions"] and
      len(sources)>=g["min_source_regimes"] and len(covered_pos)>=g["min_covered_positive"] and
      len(pos_sources)>=g["min_covered_positive_source_regimes"] and len(bad)<=g["max_contradictions"] and len(mixed)<=g["max_mixed_cells"] and
      all(per[e]["seen_fraction"]>=g["min_seen_fraction_per_engine"] and per[e]["contradictions"]==0 for e in ENGINES))
  ev={"candidate_id":cid,"mdl_bits":c["mdl_bits"],"description_bits":c["description_bits"],"term_ids":c["term_ids"],
    "coverage":{"profiles":n,"seen":len(seen),"seen_fraction":cov,"covered_engines":engines,"covered_positions":positions,
      "covered_source_regimes":sources,"covered_positive":len(covered_pos),"covered_positive_source_regimes":pos_sources,"per_engine":per},
    "contradictions":bad,"mixed_cells":mixed,"pass":ok}
  evals.append(ev)
  if ok:passing.append((c,ev))
 passing.sort(key=lambda z:(z[0]["mdl_bits"],-z[1]["coverage"]["seen_fraction"],z[0]["description_bits"],z[0]["id"]))
 selected=passing[0][0] if passing else None
 status="RELATIONAL_REPRESENTATION_SELECTED" if selected else "RELATIONAL_SELECTION_FAIL"
 out={"schema":"c3x-p6-selected-field-v1","scientific_stage":STAGE,"status":status,
   "selected_candidate":selected,"selected_candidate_id":None if selected is None else selected["id"],
   "selection_evaluations":evals,"selection_support":ss,"selection_targets_consulted":True,
   "p5_selection_labels_consulted":False,"transport_targets_consulted":False,"post_selection_representation_mutation":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P6_SELECTION",status,None if selected is None else selected["id"],"passing",len(passing))

def scope_run(a):
 pre=load(a.precommit);field=load(a.field);p=load(a.profiles);q=load(a.query)
 n=len(p["records"]);preds=q.get("predictions",[]);g=pre["transport_gate"];seen=[x for x in preds if x["status"]!="ABSTAIN_UNSEEN_CONTEXT"]
 per={}
 for e in ENGINES:
  ee=[r for r in p["records"] if r["engine"]==e];ss=[x for x in seen if x["engine"]==e]
  per[e]={"profiles":len(ee),"seen":len(ss),"seen_fraction":len(ss)/len(ee) if ee else 0.0}
 cov={"profiles":n,"seen":len(seen),"seen_fraction":len(seen)/n if n else 0.0,
   "covered_engines":sorted({x["engine"] for x in seen}),"covered_positions":sorted({x["position_id"] for x in seen}),
   "covered_source_regimes":sorted({x["source_stratum"] for x in seen}),"per_engine":per,
   "predicted_positive_profiles":sum(x.get("predicted_root_change") is True for x in seen)}
 cov["gate_pass"]=field.get("selected_candidate") is not None and cov["seen_fraction"]>=g["min_seen_fraction"] and    len(cov["covered_engines"])>=g["required_engines"] and len(cov["covered_positions"])>=g["min_positions"] and    len(cov["covered_source_regimes"])>=g["min_source_regimes"] and cov["predicted_positive_profiles"]>=g["min_predicted_positive_profiles"] and    all(per[e]["seen_fraction"]>=g["min_seen_fraction_per_engine"] for e in ENGINES)
 out={"schema":"c3x-p6-transport-scope-v1","scientific_stage":STAGE,"selected_candidate_id":field.get("selected_candidate_id"),
   "predictions":preds,"coverage":cov,"target_fields_consulted":False,"p5_selection_labels_consulted":False,
   "transport_targets_open_authorized":bool(cov["gate_pass"])}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P6_TRANSPORT_SCOPE",len(seen),n,cov["gate_pass"])

def verify_transport(a):
 scope=load(a.scope);t=load(a.targets);tm={r["record_id"]:r for r in t["records"]}
 seen,bad,mixed=compare_predictions(scope["predictions"],tm)
 ok=bool(scope["coverage"]["gate_pass"]) and not bad and not mixed
 verdict="P6_RELATIONAL_REPRESENTATION_HELDOUT_CERTIFIED" if ok else "P6_RELATIONAL_REPRESENTATION_HELDOUT_FALSIFIED"
 out={"schema":"c3x-p6-transport-verification-v1","scientific_stage":STAGE,"verdict":verdict,
   "target_opened_after_scope":True,"transport_targets_consulted":True,"p5_selection_labels_consulted":False,
   "covered_verified":len(seen),"abstained":len(scope["predictions"])-len(seen),
   "contradictions":bad,"mixed_cells":mixed,"transport_certified":ok}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P6_TRANSPORT_VERIFY",verdict,len(seen),len(bad),len(mixed))

def no_transport_open(a):
 scope=load(a.scope);field=load(a.field);st=field.get("status")
 if scope.get("transport_targets_open_authorized") is True:raise SystemExit("P6_NO_OPEN_WHEN_AUTHORIZED")
 verdict={"TRAIN_SUPPORT_HOLD":"P6_TRAIN_SUPPORT_HOLD","NO_ADMISSIBLE_RELATIONAL_TRAIN_REPRESENTATION":"P6_NO_ADMISSIBLE_RELATIONAL_REPRESENTATION_HOLD",
  "SELECTION_SUPPORT_HOLD":"P6_SELECTION_SUPPORT_HOLD","RELATIONAL_SELECTION_FAIL":"P6_RELATIONAL_SELECTION_FAIL_HOLD"}.get(st,"P6_TRANSPORT_SCOPE_INSUFFICIENT_HOLD")
 out={"schema":"c3x-p6-transport-verification-v1","scientific_stage":STAGE,"verdict":verdict,
   "target_opened_after_scope":False,"transport_targets_consulted":False,"p5_selection_labels_consulted":False,
   "covered_verified":0,"abstained":len(scope.get("predictions",[])),"contradictions":[],"mixed_cells":[],"transport_certified":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P6_TRANSPORT_NOT_OPENED",verdict)

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("precommit");q.add_argument("--constitution",required=True);q.add_argument("--corpus",required=True);q.add_argument("--p4-precommit",required=True);q.add_argument("--p5-closure",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=precommit)
 q=sp.add_parser("case");q.add_argument("--precommit",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--sampler",required=True);q.add_argument("--sampling-plan",required=True);q.add_argument("--lineager",required=True);q.add_argument("--fiber-verifier",required=True);q.add_argument("--profile-out",required=True);q.add_argument("--target-out",required=True);q.add_argument("--case-out",required=True);q.set_defaults(fn=case_run)
 q=sp.add_parser("merge-profiles");q.add_argument("--root",required=True);q.add_argument("--role",choices=ROLES,required=True);q.add_argument("--out",required=True);q.set_defaults(fn=merge_profiles)
 q=sp.add_parser("merge-targets");q.add_argument("--root",required=True);q.add_argument("--role",choices=ROLES,required=True);q.add_argument("--out",required=True);q.set_defaults(fn=merge_targets)
 q=sp.add_parser("train-input");q.add_argument("--precommit",required=True);q.add_argument("--profiles",required=True);q.add_argument("--targets",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=train_input)
 q=sp.add_parser("audit-shortlist");q.add_argument("--train",required=True);q.add_argument("--shortlist",required=True);q.add_argument("--grammar",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=audit_shortlist)
 q=sp.add_parser("selection-field");q.add_argument("--precommit",required=True);q.add_argument("--train",required=True);q.add_argument("--shortlist",required=True);q.add_argument("--query",required=True);q.add_argument("--profiles",required=True);q.add_argument("--targets",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=selection_field)
 q=sp.add_parser("transport-scope");q.add_argument("--precommit",required=True);q.add_argument("--field",required=True);q.add_argument("--profiles",required=True);q.add_argument("--query",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=scope_run)
 q=sp.add_parser("verify-transport");q.add_argument("--scope",required=True);q.add_argument("--targets",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=verify_transport)
 q=sp.add_parser("no-transport-open");q.add_argument("--scope",required=True);q.add_argument("--field",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=no_transport_open)
 a=ap.parse_args();a.fn(a)

if __name__=="__main__":main()
