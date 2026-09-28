#!/usr/bin/env python3
import argparse,hashlib,json,math,subprocess,sys,tempfile
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import c3x_cseg_input_v1 as cseg
sys.path.insert(0,str(ROOT/"harness"))
import p32_event_court as p32

STAGE="C3X 0.7.0-G9.5-P7"
ENGINES=("stockfish_19","berserk","ethereal")
ROLES=("STRUCTURAL_TRAIN","STRUCTURAL_SELECTION","UNTOUCHED_TRANSPORT")
QLEVELS=("Q0","Q1","Q2","Q3")

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):
 o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load(p):return json.loads(Path(p).read_text())
def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def binom_ge(n,p,k):return 1-sum(math.comb(n,i)*(p**i)*((1-p)**(n-i)) for i in range(k))

def support_summary(rows,g,engine_positive=False):
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
 if engine_positive and any(z["positive"]<g["min_positive_per_engine"] for z in byeng.values()):reasons.append("ENGINE_POSITIVES")
 if sum(z["positive"]>0 for z in bysrc.values())<g["min_positive_source_regimes"]:reasons.append("SOURCE_POSITIVE_BREADTH")
 return {"records":n,"positive_records":pos,"negative_records":neg,"pass":not reasons,"failure_reasons":reasons,
  "effective_detection_probability_at_sensitivity":power,"by_engine":byeng,"by_source_regime":bysrc}

def precommit(a):
 lawx=load(a.constitution);corp=load(a.corpus);p4pre=load(a.p4_precommit);p6=load(a.p6_closure)
 if lawx.get("schema")!="c3x-lawgen-constitution-v17":raise SystemExit("P7_LAW")
 law=lawx["constitution"]
 if law.get("scientific_stage")!=STAGE or corp.get("schema")!="c3x-g95-p7-corpus-v1":raise SystemExit("P7_STAGE_CORPUS")
 if p6.get("schema")!="c3x-g95-p6-closure-v1" or p6.get("receipt_sha256")!=law["parent"]["closure_receipt_sha256"]:raise SystemExit("P7_PARENT")
 fw=law["label_firewall"]
 for k in ("p6_target_labels_confirmatory_vote","p6_near_miss_diagnostics_confirmatory_vote","p6_target_artifacts_may_be_downloaded_for_p7_state_construction","fiber_id_allowed_in_p7_state","counterfactual_trace_allowed_in_p7_state","root_change_allowed_in_p7_state"):
  if fw[k] is not False:raise SystemExit("P7_FIREWALL_"+k)
 cases=[]
 for role,key,tag in (
  ("STRUCTURAL_TRAIN","structural_train_positions","train"),
  ("STRUCTURAL_SELECTION","structural_selection_positions","select"),
  ("UNTOUCHED_TRANSPORT","untouched_transport_positions","transport")):
  for i,pos in enumerate(corp[key]):
   for e in ENGINES:
    cases.append({"case_id":f"p7:{tag}:{i}:{e}","role":role,"engine":e,"position_id":pos["position_id"],
      "candidate_sha256":pos["candidate_sha256"],"source_stratum":pos["source_stratum"],"source_kind":pos["source_kind"],
      "source_logical":pos.get("source_logical"),"cell":pos["cell"],"family":pos["family"],"frontier":pos["frontier"]})
 if len(cases)!=135:raise SystemExit(f"P7_CASE_COUNT {len(cases)}")
 out={"schema":"c3x-g95-p7-precommit-v1","scientific_stage":STAGE,"constitution_sha256":digest(lawx),"corpus_sha256":digest(corp),
  "parent_p6_closure_receipt_sha256":p6["receipt_sha256"],"p6_target_labels_consulted":False,"p6_near_miss_diagnostics_consulted":False,
  "variants":p4pre["variants"],"execution":law["execution"],"cseg":law["cseg"],"quotient_ladder":law["quotient_ladder"],
  "train_support_gate":law["train_support_gate"],"state_gate":law["state_gate"],"selection_support_gate":law["selection_support_gate"],
  "selection_gate":law["selection_gate"],"transport_gate":law["transport_gate"],"chess_phenotype_lane":law["chess_phenotype_lane"],
  "claim_ceiling":law["claim_ceiling"],"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P7_PRECOMMIT",out["receipt_sha256"],"cases",len(cases))

def verify_binary(pre,case,path):
 v=pre["variants"][case["engine"]]
 if sha_file(path)!=v["sha256"]:raise SystemExit("P7_BINARY_ID")
 return v["protocol"]

def case_run(a):
 pre=load(a.precommit);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if not case:raise SystemExit("P7_CASE")
 protocol=verify_binary(pre,case,a.binary);work=Path(a.case_out).parent/"private";work.mkdir(parents=True,exist_ok=True)
 parent=p32.run_history(a.binary,protocol,case["cell"],"CATALOG",case["family"],case["frontier"],None,work/"000-parent")
 trace_path=work/"parent-trace.json";trace_path.write_text(json.dumps(parent["trace"],sort_keys=True)+"\n")
 sample_path=work/"sampling.json"
 subprocess.run([a.sampler,"sample","--trace",str(trace_path),"--plan",a.sampling_plan,"--max-events",
  str(pre["execution"]["candidate_events_per_world"]),"--out",str(sample_path)],check=True)
 samp=load(sample_path)
 if samp.get("target_fields_consulted") is not False or samp.get("raw_full_key_emitted") is not False:raise SystemExit("P7_SAMPLER_FIREWALL")
 internal=cseg.prepare_batch(case["cell"]["fen"],parent["trace"],samp["selected"])
 internal_path=work/"cseg-internal.json";internal_path.write_text(json.dumps(internal,sort_keys=True)+"\n")
 states_path=work/"cseg-states.json";go_path=work/"go-parity.json"
 subprocess.run([a.cseg_kernel,"materialize","--input",str(internal_path),"--out",str(states_path)],check=True)
 subprocess.run([a.go_verifier,str(internal_path),str(states_path),str(go_path)],check=True)
 states=load(states_path);go=load(go_path)
 if go.get("pass") is not True or states.get("raw_tt_key_emitted") is not False or states.get("counterfactual_information_consulted") is not False or states.get("fiber_id_consulted") is not False:
  raise SystemExit("P7_CSEG_FIREWALL")
 state_by={r["event_id"]:r for r in states["records"]}
 byid={e["address_id"]:(i,e) for i,e in enumerate(parent["trace"]["events"])}
 profiles=[];targets=[];miss=[]
 for j,s in enumerate(samp["selected"]):
  aid=s["event_id"]
  if aid not in byid or aid not in state_by:raise SystemExit("P7_EVENT_STATE")
  _,e=byid[aid];addr=dict(e["address"]);addr["address_id"]=aid
  cf=p32.run_history(a.binary,protocol,case["cell"],"REMOVE_SET",case["family"],case["frontier"],[addr],work/f"{j+1:03d}-single")
  fired=bool(cf["trace"]["targets"] and cf["trace"]["targets"][0]["fired"])
  if not fired:miss.append({"event_id":aid,"sampling_stratum":s["sampling_stratum"]});continue
  rid=f'{case["case_id"]}:{aid[:16]}';st=state_by[aid]
  profiles.append({"record_id":rid,"engine":case["engine"],"position_id":case["position_id"],"source_stratum":case["source_stratum"],
    "source_kind":case["source_kind"],"event_id":aid,"sampling_stratum":s["sampling_stratum"],"state_ids":st["state_ids"],
    "graph_census":st["graph_census"],"current_event":st["current_event"],"board_atoms":st["board_atoms"],
    "causal_availability":"BASELINE_PREFIX_ONLY","target_fields_consulted":False,"raw_tt_key_emitted":False,
    "counterfactual_information_consulted":False,"fiber_id_consulted":False})
  targets.append({"record_id":rid,"root_change":cf["semantic"]["bestmove"]!=parent["semantic"]["bestmove"],
    "baseline":{k:parent["semantic"].get(k) for k in ("bestmove","score","wdl","depth","seldepth","nodes","pv")},
    "counterfactual":{k:cf["semantic"].get(k) for k in ("bestmove","score","wdl","depth","seldepth","nodes","pv")},
    "chess_phenotype":cseg.root_move_phenotype(case["cell"]["fen"],parent["semantic"].get("bestmove"),cf["semantic"].get("bestmove"))})
 pd={"schema":"c3x-cseg-profile-batch-p7-v1","scientific_stage":STAGE,"case_id":case["case_id"],"role":case["role"],
  "source_stratum":case["source_stratum"],"records":profiles,"target_fields_consulted":False,"raw_tt_key_emitted":False,
  "counterfactual_information_consulted":False,"fiber_id_consulted":False}
 td={"schema":"c3x-cseg-target-batch-p7-v1","scientific_stage":STAGE,"case_id":case["case_id"],"role":case["role"],
  "source_stratum":case["source_stratum"],"records":targets}
 Path(a.profile_out).write_text(json.dumps(pd,indent=2,sort_keys=True)+"\n");Path(a.target_out).write_text(json.dumps(td,indent=2,sort_keys=True)+"\n")
 man={"schema":"c3x-g95-p7-case-v1","scientific_stage":STAGE,"case_id":case["case_id"],"role":case["role"],"engine":case["engine"],
  "position_id":case["position_id"],"source_stratum":case["source_stratum"],"selected_records":samp["selected_count"],"fired_records":len(profiles),
  "missed_targets":miss,"sampling_census":samp["stratum_census"],"profile_sha256":digest(pd),"target_sha256":digest(td),
  "go_cseg_parity":{"pass":go["pass"],"records_checked":go["records_checked"],"q_levels_checked":go["q_levels_checked"]},
  "private_raw_graph_uploaded":False,"status":"PASS" if profiles else "NO_FIRED_EVENT_HOLD"}
 seal(man);Path(a.case_out).write_text(json.dumps(man,indent=2,sort_keys=True)+"\n")
 print("G95_P7_CASE",case["case_id"],man["status"],"selected",samp["selected_count"],"fired",len(profiles))

def batches(root,schema,role=None):
 out=[]
 for p in Path(root).rglob("*.json"):
  try:x=load(p)
  except Exception:continue
  if x.get("schema")==schema and (role is None or x.get("role")==role):out.append(x)
 return out

def merge_profiles(a):
 bs=batches(a.root,"c3x-cseg-profile-batch-p7-v1",a.role)
 if len(bs)!=45:raise SystemExit(f"P7_PROFILE_BATCH {a.role} {len(bs)}")
 rows=sorted([r for b in bs for r in b["records"]],key=lambda z:z["record_id"])
 for r in rows:
  if r.get("target_fields_consulted") is not False or r.get("raw_tt_key_emitted") is not False or r.get("counterfactual_information_consulted") is not False or r.get("fiber_id_consulted") is not False:
   raise SystemExit("P7_PROFILE_FIREWALL")
 out={"schema":"c3x-cseg-profile-merged-p7-v1","scientific_stage":STAGE,"role":a.role,"records":rows,
  "target_fields_consulted":False,"raw_tt_key_emitted":False,"counterfactual_information_consulted":False,"fiber_id_consulted":False}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P7_PROFILES",a.role,len(rows))

def merge_targets(a):
 bs=batches(a.root,"c3x-cseg-target-batch-p7-v1",a.role)
 if len(bs)!=45:raise SystemExit(f"P7_TARGET_BATCH {a.role} {len(bs)}")
 rows=sorted([r for b in bs for r in b["records"]],key=lambda z:z["record_id"])
 out={"schema":"c3x-cseg-target-merged-p7-v1","scientific_stage":STAGE,"role":a.role,"records":rows}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P7_TARGETS",a.role,len(rows))

def joined(p,t):
 pm={r["record_id"]:r for r in p["records"]};tm={r["record_id"]:r for r in t["records"]}
 if set(pm)!=set(tm):raise SystemExit("P7_JOIN")
 return [{"record_id":rid,"engine":pm[rid]["engine"],"position_id":pm[rid]["position_id"],"source_stratum":pm[rid]["source_stratum"],
  "source_kind":pm[rid]["source_kind"],"sampling_stratum":pm[rid]["sampling_stratum"],"state_ids":pm[rid]["state_ids"],
  "graph_census":pm[rid]["graph_census"],"current_event":pm[rid]["current_event"],"board_atoms":pm[rid]["board_atoms"],
  "target":bool(tm[rid]["root_change"]),"chess_phenotype":tm[rid]["chess_phenotype"]}
  for rid in sorted(pm)]

def q_metrics(rows,q):
 g=defaultdict(list)
 for r in rows:g[r["state_ids"][q]].append(r)
 col=0;xp=0;xe=0;rp=0;mixed=[]
 for sid,v in g.items():
  labs={z["target"] for z in v};poss={z["position_id"] for z in v};engs={z["engine"] for z in v}
  if len(labs)>1:col+=1;mixed.append({"state_id":sid,"records":len(v),"engines":sorted(engs),"positions":len(poss),"labels":sorted(labs)})
  if len(poss)>1:xp+=len(v)
  if len(engs)>1:xe+=len(v)
  if labs=={True} and (len(poss)>1 or len(engs)>1):rp+=len(v)
 n=len(rows)
 return {"records":n,"distinct_states":len(g),"target_collisions":col,"compression":1-len(g)/n if n else 0.0,
  "cross_position_records":xp,"cross_engine_records":xe,"reused_positive_records":rp,
  "positive_records":sum(r["target"] for r in rows),"negative_records":sum(not r["target"] for r in rows),"mixed_state_sample":mixed[:20]}

def train_field(a):
 pre=load(a.precommit);p=load(a.profiles);t=load(a.targets)
 if p["role"]!="STRUCTURAL_TRAIN" or t["role"]!="STRUCTURAL_TRAIN":raise SystemExit("P7_TRAIN_ROLE")
 rows=joined(p,t);sup=support_summary(rows,pre["train_support_gate"],True);gate=pre["state_gate"];levels=[]
 selected=None
 for q in QLEVELS:
  m=q_metrics(rows,q)
  ok=(m["target_collisions"]<=gate["max_target_collisions"] and m["compression"]>=gate["min_compression"] and
      m["cross_position_records"]>=gate["min_cross_position_records"] and m["cross_engine_records"]>=gate["min_cross_engine_records"] and
      m["reused_positive_records"]>=gate["min_reused_positive_records"] and m["positive_records"]>0 and m["negative_records"]>0)
  levels.append({"q_level":q,"metrics":m,"pass":bool(ok)})
  if selected is None and sup["pass"] and ok:selected=q
 smap={}
 if selected:
  gg=defaultdict(list)
  for r in rows:gg[r["state_ids"][selected]].append(r)
  for sid,v in gg.items():
   labs={z["target"] for z in v}
   if len(labs)!=1:raise SystemExit("P7_SELECTED_MIXED")
   smap[sid]={"label":"ROOT_CHANGE" if next(iter(labs)) else "NO_ROOT_CHANGE","support":len(v),
    "engines":sorted({z["engine"] for z in v}),"positions":sorted({z["position_id"] for z in v}),
    "source_strata":sorted({z["source_stratum"] for z in v})}
 status="STRUCTURAL_STATE_SELECTED" if selected else ("TRAIN_SUPPORT_HOLD" if not sup["pass"] else "PREFIX_GRAPH_STATE_FAMILY_HOLD")
 out={"schema":"c3x-p7-train-field-v1","scientific_stage":STAGE,"status":status,"support":sup,"levels":levels,
  "selected_q_level":selected,"state_map":smap,"train_targets_consulted":True,"p6_target_labels_consulted":False,
  "post_target_graph_mutation":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P7_TRAIN_FIELD",status,selected,"states",len(smap),"support",sup["positive_records"])

def query_field(a):
 f=load(a.field);p=load(a.profiles);q=f.get("selected_q_level");mp=f.get("state_map",{});pred=[]
 for r in p["records"]:
  if not q:
   pred.append({"record_id":r["record_id"],"engine":r["engine"],"position_id":r["position_id"],"source_stratum":r["source_stratum"],
    "state_id":None,"status":"ABSTAIN_NO_TRAIN_STATE","predicted_root_change":None,"train_support":0});continue
  sid=r["state_ids"][q];z=mp.get(sid)
  if z is None:st="ABSTAIN_UNSEEN_STATE";y=None;su=0
  else:st="CERTIFIED_ROOT_CHANGE" if z["label"]=="ROOT_CHANGE" else "CERTIFIED_NO_ROOT_CHANGE";y=z["label"]=="ROOT_CHANGE";su=z["support"]
  pred.append({"record_id":r["record_id"],"engine":r["engine"],"position_id":r["position_id"],"source_stratum":r["source_stratum"],
    "state_id":sid,"status":st,"predicted_root_change":y,"train_support":su})
 out={"schema":"c3x-p7-state-query-v1","scientific_stage":STAGE,"selected_q_level":q,"predictions":pred,
  "target_fields_consulted":False,"p6_target_labels_consulted":False}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P7_QUERY",q,len(pred))

def compare(preds,tm):
 seen=[];bad=[];states=defaultdict(set)
 for p in preds:
  if p["predicted_root_change"] is None:continue
  seen.append(p);y=bool(tm[p["record_id"]]["root_change"]);states[p["state_id"]].add(y)
  if bool(p["predicted_root_change"])!=y:bad.append({"record_id":p["record_id"],"engine":p["engine"],"position_id":p["position_id"],
   "source_stratum":p["source_stratum"],"state_id":p["state_id"],"predicted_root_change":p["predicted_root_change"],"observed_root_change":y})
 mixed=[{"state_id":k,"labels":sorted(v)} for k,v in states.items() if len(v)>1]
 return seen,bad,mixed

def selection_field(a):
 pre=load(a.precommit);train=load(a.train);q=load(a.query);p=load(a.profiles);t=load(a.targets)
 rows=joined(p,t);sup=support_summary(rows,pre["selection_support_gate"],False)
 if not train.get("selected_q_level"):
  status="TRAIN_SUPPORT_HOLD" if train["status"]=="TRAIN_SUPPORT_HOLD" else "PREFIX_GRAPH_STATE_FAMILY_HOLD"
  out={"schema":"c3x-p7-selected-field-v1","scientific_stage":STAGE,"status":status,"selected_q_level":None,"state_map":{},
   "selection_support":sup,"selection_evaluation":None,"selection_targets_consulted":True,"transport_targets_consulted":False,"post_selection_refit":False}
  seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P7_SELECTION",status);return
 if not sup["pass"]:
  out={"schema":"c3x-p7-selected-field-v1","scientific_stage":STAGE,"status":"SELECTION_SUPPORT_HOLD","selected_q_level":None,"state_map":{},
   "selection_support":sup,"selection_evaluation":None,"selection_targets_consulted":True,"transport_targets_consulted":False,"post_selection_refit":False}
  seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P7_SELECTION","SELECTION_SUPPORT_HOLD");return
 tm={r["record_id"]:r for r in t["records"]};pred=q["predictions"];seen,bad,mixed=compare(pred,tm);g=pre["selection_gate"];n=len(pred)
 per={}
 for e in ENGINES:
  ee=[x for x in pred if x["engine"]==e];ss=[x for x in seen if x["engine"]==e];eb=[x for x in bad if x["engine"]==e]
  per[e]={"profiles":len(ee),"seen":len(ss),"seen_fraction":len(ss)/len(ee) if ee else 0.0,"contradictions":len(eb)}
 pos=[x for x in seen if bool(tm[x["record_id"]]["root_change"])]
 ev={"profiles":n,"seen":len(seen),"seen_fraction":len(seen)/n if n else 0.0,"covered_engines":sorted({x["engine"] for x in seen}),
  "covered_positions":sorted({x["position_id"] for x in seen}),"covered_source_regimes":sorted({x["source_stratum"] for x in seen}),
  "covered_positive":len(pos),"per_engine":per,"contradictions":bad,"mixed_states":mixed}
 ok=(ev["seen_fraction"]>=g["min_seen_fraction"] and len(ev["covered_engines"])>=g["required_engines"] and len(ev["covered_positions"])>=g["min_positions"] and
  len(ev["covered_source_regimes"])>=g["min_source_regimes"] and len(pos)>=g["min_covered_positive"] and len(bad)<=g["max_contradictions"] and
  len(mixed)<=g["max_mixed_cells"] and all(per[e]["seen_fraction"]>=g["min_seen_fraction_per_engine"] and per[e]["contradictions"]==0 for e in ENGINES))
 status="STRUCTURAL_STATE_SELECTION_PASS" if ok else "STRUCTURAL_STATE_SELECTION_FAIL"
 out={"schema":"c3x-p7-selected-field-v1","scientific_stage":STAGE,"status":status,
  "selected_q_level":train["selected_q_level"] if ok else None,"state_map":train["state_map"] if ok else {},
  "selection_support":sup,"selection_evaluation":ev,"selection_targets_consulted":True,"transport_targets_consulted":False,"post_selection_refit":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P7_SELECTION",status,"seen",len(seen),"bad",len(bad))

def scope_run(a):
 pre=load(a.precommit);f=load(a.field);q=load(a.query);p=load(a.profiles);pred=q["predictions"];g=pre["transport_gate"];n=len(pred)
 seen=[x for x in pred if x["predicted_root_change"] is not None];per={}
 for e in ENGINES:
  ee=[r for r in pred if r["engine"]==e];ss=[r for r in seen if r["engine"]==e]
  per[e]={"profiles":len(ee),"seen":len(ss),"seen_fraction":len(ss)/len(ee) if ee else 0.0}
 cov={"profiles":n,"seen":len(seen),"seen_fraction":len(seen)/n if n else 0.0,
  "covered_engines":sorted({x["engine"] for x in seen}),"covered_positions":sorted({x["position_id"] for x in seen}),
  "covered_source_regimes":sorted({x["source_stratum"] for x in seen}),"predicted_positive_profiles":sum(x["predicted_root_change"] is True for x in seen),"per_engine":per}
 cov["gate_pass"]=f.get("selected_q_level") is not None and cov["seen_fraction"]>=g["min_seen_fraction"] and len(cov["covered_engines"])>=g["required_engines"] and   len(cov["covered_positions"])>=g["min_positions"] and len(cov["covered_source_regimes"])>=g["min_source_regimes"] and   cov["predicted_positive_profiles"]>=g["min_predicted_positive_profiles"] and all(per[e]["seen_fraction"]>=g["min_seen_fraction_per_engine"] for e in ENGINES)
 out={"schema":"c3x-p7-transport-scope-v1","scientific_stage":STAGE,"selected_q_level":f.get("selected_q_level"),
  "predictions":pred,"coverage":cov,"target_fields_consulted":False,"transport_targets_open_authorized":bool(cov["gate_pass"])}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P7_TRANSPORT_SCOPE",len(seen),n,cov["gate_pass"])

def verify_transport(a):
 scope=load(a.scope);t=load(a.targets);tm={r["record_id"]:r for r in t["records"]};seen,bad,mixed=compare(scope["predictions"],tm)
 ok=bool(scope["coverage"]["gate_pass"]) and not bad and not mixed
 out={"schema":"c3x-p7-transport-verification-v1","scientific_stage":STAGE,
  "verdict":"P7_PREFIX_GRAPH_CAUSAL_STATE_HELDOUT_CERTIFIED" if ok else "P7_PREFIX_GRAPH_CAUSAL_STATE_HELDOUT_FALSIFIED",
  "target_opened_after_scope":True,"transport_targets_consulted":True,"covered_verified":len(seen),
  "abstained":len(scope["predictions"])-len(seen),"contradictions":bad,"mixed_states":mixed,"transport_certified":ok}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P7_TRANSPORT_VERIFY",out["verdict"],len(seen),len(bad),len(mixed))

def no_transport_open(a):
 scope=load(a.scope);f=load(a.field)
 if scope.get("transport_targets_open_authorized") is True:raise SystemExit("P7_NO_OPEN_AUTHORIZED")
 status=f.get("status")
 verdict={"TRAIN_SUPPORT_HOLD":"P7_TRAIN_SUPPORT_HOLD","PREFIX_GRAPH_STATE_FAMILY_HOLD":"P7_PREFIX_GRAPH_STATE_FAMILY_HOLD",
  "SELECTION_SUPPORT_HOLD":"P7_SELECTION_SUPPORT_HOLD","STRUCTURAL_STATE_SELECTION_FAIL":"P7_STRUCTURAL_STATE_SELECTION_FAIL_HOLD"}.get(status,"P7_TRANSPORT_SCOPE_INSUFFICIENT_HOLD")
 out={"schema":"c3x-p7-transport-verification-v1","scientific_stage":STAGE,"verdict":verdict,"target_opened_after_scope":False,
  "transport_targets_consulted":False,"covered_verified":0,"abstained":len(scope.get("predictions",[])),"contradictions":[],"mixed_states":[],"transport_certified":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P7_TRANSPORT_NOT_OPENED",verdict)

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("precommit");q.add_argument("--constitution",required=True);q.add_argument("--corpus",required=True);q.add_argument("--p4-precommit",required=True);q.add_argument("--p6-closure",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=precommit)
 q=sp.add_parser("case");q.add_argument("--precommit",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--sampler",required=True);q.add_argument("--sampling-plan",required=True);q.add_argument("--cseg-kernel",required=True);q.add_argument("--go-verifier",required=True);q.add_argument("--profile-out",required=True);q.add_argument("--target-out",required=True);q.add_argument("--case-out",required=True);q.set_defaults(fn=case_run)
 q=sp.add_parser("merge-profiles");q.add_argument("--root",required=True);q.add_argument("--role",choices=ROLES,required=True);q.add_argument("--out",required=True);q.set_defaults(fn=merge_profiles)
 q=sp.add_parser("merge-targets");q.add_argument("--root",required=True);q.add_argument("--role",choices=ROLES,required=True);q.add_argument("--out",required=True);q.set_defaults(fn=merge_targets)
 q=sp.add_parser("train-field");q.add_argument("--precommit",required=True);q.add_argument("--profiles",required=True);q.add_argument("--targets",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=train_field)
 q=sp.add_parser("query-field");q.add_argument("--field",required=True);q.add_argument("--profiles",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=query_field)
 q=sp.add_parser("selection-field");q.add_argument("--precommit",required=True);q.add_argument("--train",required=True);q.add_argument("--query",required=True);q.add_argument("--profiles",required=True);q.add_argument("--targets",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=selection_field)
 q=sp.add_parser("transport-scope");q.add_argument("--precommit",required=True);q.add_argument("--field",required=True);q.add_argument("--query",required=True);q.add_argument("--profiles",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=scope_run)
 q=sp.add_parser("verify-transport");q.add_argument("--scope",required=True);q.add_argument("--targets",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=verify_transport)
 q=sp.add_parser("no-transport-open");q.add_argument("--scope",required=True);q.add_argument("--field",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=no_transport_open)
 a=ap.parse_args();a.fn(a)

if __name__=="__main__":main()
