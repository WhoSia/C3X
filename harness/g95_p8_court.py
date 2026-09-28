#!/usr/bin/env python3
import argparse,hashlib,json,math,subprocess,sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import c3x_prototype_v1 as proto
import c3x_cseg_input_v1 as chessphen
sys.path.insert(0,str(ROOT/"harness"))
import p32_event_court as p32

STAGE="C3X 0.7.0-G9.5-P8"
ENGINES=("stockfish_19","berserk","ethereal")
ROLES=("PROTOTYPE_TRAIN","RETRIEVAL_SELECTION","UNTOUCHED_TRANSPORT")

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load(p):return json.loads(Path(p).read_text())
def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def binom_ge(n,p,k):return 1-sum(math.comb(n,i)*(p**i)*((1-p)**(n-i)) for i in range(k))
def support(rows,g,engine_positive=False):
 n=len(rows);pos=sum(bool(r["root_change"]) for r in rows);neg=n-pos
 byeng={e:{"records":sum(r["engine"]==e for r in rows),"positive":sum(r["engine"]==e and r["root_change"] for r in rows)} for e in ENGINES}
 bysrc={s:{"records":sum(r["source_stratum"]==s for r in rows),"positive":sum(r["source_stratum"]==s and r["root_change"] for r in rows)} for s in sorted({r["source_stratum"] for r in rows})}
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
 lawx=load(a.constitution);corp=load(a.corpus);p4=load(a.p4_precommit);p7=load(a.p7_closure)
 if lawx.get("schema")!="c3x-lawgen-constitution-v18":raise SystemExit("P8_LAW")
 law=lawx["constitution"]
 if law.get("scientific_stage")!=STAGE or corp.get("schema")!="c3x-g95-p8-corpus-v1":raise SystemExit("P8_STAGE")
 if p7.get("schema")!="c3x-g95-p7-closure-v1" or p7.get("receipt_sha256")!=law["parent"]["closure_receipt_sha256"]:raise SystemExit("P8_PARENT")
 fw=law["label_firewall"]
 for k in ("p7_q_state_ids_allowed_in_p8_descriptor","p7_target_labels_confirmatory_vote","p7_reuse_diagnostics_confirmatory_vote",
           "engine_identity_allowed_in_primary_descriptor","source_identity_allowed_in_primary_descriptor","sampling_stratum_allowed_in_primary_descriptor",
           "raw_tt_key_emitted","raw_tt_key_allowed_as_feature","counterfactual_information_allowed_before_train_prototype_freeze",
           "root_change_allowed_before_train_prototype_freeze","post_selection_metric_refit"):
  if fw[k] is not False:raise SystemExit("P8_FIREWALL_"+k)
 cases=[]
 for role,key,tag in (("PROTOTYPE_TRAIN","prototype_train_positions","train"),("RETRIEVAL_SELECTION","retrieval_selection_positions","select"),("UNTOUCHED_TRANSPORT","untouched_transport_positions","transport")):
  for i,pos in enumerate(corp[key]):
   for e in ENGINES:
    cases.append({"case_id":f"p8:{tag}:{i}:{e}","role":role,"engine":e,"position_id":pos["position_id"],"candidate_sha256":pos["candidate_sha256"],
     "source_stratum":pos["source_stratum"],"source_kind":pos["source_kind"],"source_logical":pos.get("source_logical"),
     "cell":pos["cell"],"family":pos["family"],"frontier":pos["frontier"]})
 if len(cases)!=108:raise SystemExit(f"P8_CASE_COUNT {len(cases)}")
 out={"schema":"c3x-g95-p8-precommit-v1","scientific_stage":STAGE,"constitution_sha256":digest(lawx),"corpus_sha256":digest(corp),
  "parent_p7_closure_receipt_sha256":p7["receipt_sha256"],"p7_target_labels_consulted":False,"p7_q_state_ids_consulted":False,
  "p7_reuse_diagnostics_confirmatory_vote":False,"variants":p4["variants"],"execution":law["execution"],"descriptor":law["descriptor"],
  "prototype_cover":law["prototype_cover"],"train_support_gate":law["train_support_gate"],"selection_support_gate":law["selection_support_gate"],
  "retrieval_gate":law["retrieval_gate"],"transport_gate":law["transport_gate"],"developer_diagnostic":law["developer_diagnostic"],
  "claim_ceiling":law["claim_ceiling"],"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P8_PRECOMMIT",out["receipt_sha256"],"cases",len(cases))

def verify_binary(pre,case,path):
 v=pre["variants"][case["engine"]]
 if sha_file(path)!=v["sha256"]:raise SystemExit("P8_BINARY_ID")
 return v["protocol"]

def profile_case(a):
 pre=load(a.precommit);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if not case:raise SystemExit("P8_CASE")
 protocol=verify_binary(pre,case,a.binary)
 work=Path(a.profile_out).parent.parent/".p8-private"/case["case_id"].replace(":","_");work.mkdir(parents=True,exist_ok=True)
 parent=p32.run_history(a.binary,protocol,case["cell"],"CATALOG",case["family"],case["frontier"],None,work/"000-parent")
 trace_path=work/"parent-trace.json";trace_path.write_text(json.dumps(parent["trace"],sort_keys=True)+"\n")
 sample_path=work/"sampling.json"
 subprocess.run([a.sampler,"sample","--trace",str(trace_path),"--plan",a.sampling_plan,"--max-events",str(pre["execution"]["candidate_events_per_world"]),"--out",str(sample_path)],check=True)
 samp=load(sample_path)
 if samp.get("target_fields_consulted") is not False or samp.get("raw_full_key_emitted") is not False:raise SystemExit("P8_SAMPLER_FIREWALL")
 batch=proto.prepare_batch(case["cell"]["fen"],parent["trace"],samp["selected"])
 profiles=[]
 for z in batch["records"]:
  rid=f'{case["case_id"]}:{z["event_id"][:16]}'
  profiles.append({"record_id":rid,"engine":case["engine"],"position_id":case["position_id"],"source_stratum":case["source_stratum"],"source_kind":case["source_kind"],
   "event_id":z["event_id"],"sampling_stratum":z["sampling_stratum"],"descriptor":z["descriptor"],"target_fields_consulted":False,
   "counterfactual_information_consulted":False,"raw_tt_key_emitted":False,"p7_q_state_consulted":False})
 pd={"schema":"c3x-prototype-profile-batch-p8-v1","scientific_stage":STAGE,"case_id":case["case_id"],"role":case["role"],"records":profiles,
  "target_fields_consulted":False,"counterfactual_information_consulted":False,"raw_tt_key_emitted":False,"p7_q_state_consulted":False}
 Path(a.profile_out).write_text(json.dumps(pd,indent=2,sort_keys=True)+"\n")
 man={"schema":"c3x-g95-p8-profile-case-v1","scientific_stage":STAGE,"case_id":case["case_id"],"role":case["role"],"engine":case["engine"],
  "position_id":case["position_id"],"source_stratum":case["source_stratum"],"selected_profiles":len(profiles),"profile_sha256":digest(pd),
  "counterfactual_replay_executed":False,"target_fields_consulted":False,"status":"PASS"}
 seal(man);Path(a.case_out).write_text(json.dumps(man,indent=2,sort_keys=True)+"\n")
 print("G95_P8_PROFILE_CASE",case["case_id"],"profiles",len(profiles))

def target_case(a):
 pre=load(a.precommit);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if not case:raise SystemExit("P8_CASE")
 profile=load(a.profile);protocol=verify_binary(pre,case,a.binary)
 if profile.get("case_id")!=case["case_id"] or profile.get("role")!=case["role"] or profile.get("target_fields_consulted") is not False:raise SystemExit("P8_TARGET_PROFILE_ID")
 work=Path(a.target_out).parent.parent/".p8-target-private"/case["case_id"].replace(":","_");work.mkdir(parents=True,exist_ok=True)
 parent=p32.run_history(a.binary,protocol,case["cell"],"CATALOG",case["family"],case["frontier"],None,work/"000-parent")
 trace_path=work/"parent-trace.json";trace_path.write_text(json.dumps(parent["trace"],sort_keys=True)+"\n")
 sample_path=work/"sampling.json"
 subprocess.run([a.sampler,"sample","--trace",str(trace_path),"--plan",a.sampling_plan,"--max-events",str(pre["execution"]["candidate_events_per_world"]),"--out",str(sample_path)],check=True)
 samp=load(sample_path)
 profile_ids=[r["event_id"] for r in profile["records"]];sample_ids=[r["event_id"] for r in samp["selected"]]
 if profile_ids!=sample_ids:raise SystemExit("P8_TARGET_PROFILE_SELECTION_DRIFT")
 byid={e["address_id"]:e for e in parent["trace"]["events"]};targets=[];miss=[]
 for j,s in enumerate(samp["selected"]):
  aid=s["event_id"];e=byid[aid];addr=dict(e["address"]);addr["address_id"]=aid
  cf=p32.run_history(a.binary,protocol,case["cell"],"REMOVE_SET",case["family"],case["frontier"],[addr],work/f"{j+1:03d}-single")
  fired=bool(cf["trace"]["targets"] and cf["trace"]["targets"][0]["fired"])
  if not fired:miss.append({"event_id":aid,"sampling_stratum":s["sampling_stratum"]});continue
  rid=f'{case["case_id"]}:{aid[:16]}'
  targets.append({"record_id":rid,"engine":case["engine"],"position_id":case["position_id"],"source_stratum":case["source_stratum"],"source_kind":case["source_kind"],
    "root_change":cf["semantic"]["bestmove"]!=parent["semantic"]["bestmove"],
    "baseline":{k:parent["semantic"].get(k) for k in ("bestmove","score","wdl","depth","seldepth","nodes","pv")},
    "counterfactual":{k:cf["semantic"].get(k) for k in ("bestmove","score","wdl","depth","seldepth","nodes","pv")},
    "chess_phenotype":chessphen.root_move_phenotype(case["cell"]["fen"],parent["semantic"].get("bestmove"),cf["semantic"].get("bestmove"))})
 td={"schema":"c3x-prototype-target-batch-p8-v1","scientific_stage":STAGE,"case_id":case["case_id"],"role":case["role"],"records":targets}
 Path(a.target_out).write_text(json.dumps(td,indent=2,sort_keys=True)+"\n")
 man={"schema":"c3x-g95-p8-target-case-v1","scientific_stage":STAGE,"case_id":case["case_id"],"role":case["role"],"engine":case["engine"],
  "position_id":case["position_id"],"source_stratum":case["source_stratum"],"selected_profiles":len(profile_ids),"fired_targets":len(targets),
  "missed_targets":miss,"profile_sha256":digest(profile),"target_sha256":digest(td),"target_open_authorized_upstream":True,"status":"PASS"}
 seal(man);Path(a.case_out).write_text(json.dumps(man,indent=2,sort_keys=True)+"\n")
 print("G95_P8_TARGET_CASE",case["case_id"],"fired",len(targets))

def batches(root,schema,role):
 out=[]
 for p in Path(root).rglob("*.json"):
  try:x=load(p)
  except Exception:continue
  if x.get("schema")==schema and x.get("role")==role:out.append(x)
 return out
def merge_profiles(a):
 bs=batches(a.root,"c3x-prototype-profile-batch-p8-v1",a.role)
 if len(bs)!=36:raise SystemExit(f"P8_PROFILE_BATCH {a.role} {len(bs)}")
 rows=sorted([r for b in bs for r in b["records"]],key=lambda z:z["record_id"])
 for r in rows:
  if r.get("target_fields_consulted") is not False or r.get("counterfactual_information_consulted") is not False or r.get("p7_q_state_consulted") is not False:raise SystemExit("P8_PROFILE_FIREWALL")
 out={"schema":"c3x-prototype-profile-merged-p8-v1","scientific_stage":STAGE,"role":a.role,"records":rows,"target_fields_consulted":False,
  "counterfactual_information_consulted":False,"raw_tt_key_emitted":False,"p7_q_state_consulted":False}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P8_PROFILES",a.role,len(rows))
def merge_targets(a):
 bs=batches(a.root,"c3x-prototype-target-batch-p8-v1",a.role)
 if len(bs)!=36:raise SystemExit(f"P8_TARGET_BATCH {a.role} {len(bs)}")
 rows=sorted([r for b in bs for r in b["records"]],key=lambda z:z["record_id"])
 out={"schema":"c3x-prototype-target-merged-p8-v1","scientific_stage":STAGE,"role":a.role,"records":rows}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P8_TARGETS",a.role,len(rows))

def annotate(a):
 pre=load(a.precommit);idx=load(a.index);p=load(a.profiles);t=load(a.targets)
 if idx.get("status")!="TARGET_BLIND_PROTOTYPE_COVER_SELECTED":raise SystemExit("P8_ANNOTATE_NO_INDEX")
 pm={r["record_id"]:r for r in p["records"]};tm={r["record_id"]:r for r in t["records"]};assign={r["record_id"]:r["prototype_id"] for r in idx["assignments"]}
 rows=[]
 for rid,z in tm.items():
  if rid not in pm or rid not in assign:raise SystemExit("P8_ANNOTATE_JOIN")
  q=pm[rid];rows.append({**z,"prototype_id":assign[rid],"engine":q["engine"],"position_id":q["position_id"],"source_stratum":q["source_stratum"]})
 sup=support(rows,pre["train_support_gate"],True)
 byp=defaultdict(list)
 for r in rows:byp[r["prototype_id"]].append(r)
 protos=[]
 for z in idx["prototypes"]:
  v=byp.get(z["prototype_id"],[]);pos=[r for r in v if r["root_change"]];neg=[r for r in v if not r["root_change"]]
  protos.append({**z,"labelled_support":len(v),"positive_count":len(pos),"negative_count":len(neg),"risk_score":(len(pos)+1)/(len(v)+2),
   "positive_exemplars":[{"record_id":r["record_id"],"engine":r["engine"],"position_id":r["position_id"],"source_stratum":r["source_stratum"],
     "baseline":r["baseline"],"counterfactual":r["counterfactual"],"chess_phenotype":r["chess_phenotype"]} for r in pos],
   "negative_exemplar_ids":[r["record_id"] for r in neg[:8]]})
 status="TRAIN_PROTOTYPE_ANNOTATED" if sup["pass"] else "TRAIN_SUPPORT_HOLD"
 out={"schema":"c3x-p8-annotated-index-v1","scientific_stage":STAGE,"status":status,"selected_radius":idx["selected_radius"],"support":sup,
  "prototypes":protos,"target_blind_index_sha256":digest(idx),"train_targets_consulted":True,"post_target_metric_refit":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P8_ANNOTATE",status,"positive",sup["positive_records"],"prototypes",len(protos))

def enrich(a):
 idx=load(a.annotated_index);q=load(a.query);p=load(a.profiles);pm={r["record_id"]:r for r in p["records"]};pro={z["prototype_id"]:z for z in idx["prototypes"]}
 rows=[]
 for z in q["queries"]:
  rid=z["record_id"];m=pm[rid]
  if z["status"]!="COVERED":
   rows.append({"record_id":rid,"engine":m["engine"],"position_id":m["position_id"],"source_stratum":m["source_stratum"],"status":z["status"],"prototype_id":None,"distance":z.get("distance"),"risk_score":None,"labelled_support":0,"positive_count":0});continue
  pr=pro[z["prototype_id"]]
  st="COVERED_LABELLED_PROTOTYPE" if pr["labelled_support"]>0 else "ABSTAIN_UNLABELLED_PROTOTYPE"
  rows.append({"record_id":rid,"engine":m["engine"],"position_id":m["position_id"],"source_stratum":m["source_stratum"],"status":st,
   "prototype_id":pr["prototype_id"],"distance":z["distance"],"risk_score":pr["risk_score"] if pr["labelled_support"]>0 else None,
   "labelled_support":pr["labelled_support"],"positive_count":pr["positive_count"],
   "positive_exemplars":pr["positive_exemplars"] if pr["labelled_support"]>0 else []})
 out={"schema":"c3x-p8-enriched-query-v1","scientific_stage":STAGE,"records":rows,"target_fields_consulted":False,"post_target_metric_refit":False}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P8_ENRICH",len(rows))

def scope_metrics(rows):
 covered=[r for r in rows if r["status"]=="COVERED_LABELLED_PROTOTYPE"];n=len(rows)
 byeng={e:{"records":sum(r["engine"]==e for r in rows),"covered":sum(r["engine"]==e and r["status"]=="COVERED_LABELLED_PROTOTYPE" for r in rows)} for e in ENGINES}
 return {"records":n,"covered":len(covered),"coverage":len(covered)/n if n else 0.0,
  "coverage_per_engine":{e:(z["covered"]/z["records"] if z["records"] else 0.0) for e,z in byeng.items()},
  "engines":sorted({r["engine"] for r in covered}),"positions":len({r["position_id"] for r in covered}),"source_regimes":len({r["source_stratum"] for r in covered})}
def scope_pass(m,g):
 return m["coverage"]>=g["min_coverage"] and all(m["coverage_per_engine"].get(e,0)>=g["min_coverage_per_engine"] for e in ENGINES) and len(m["engines"])>=g["required_engines"] and m["positions"]>=g["min_positions"] and m["source_regimes"]>=g["min_source_regimes"]
def scope_cmd(a):
 pre=load(a.precommit);q=load(a.query);m=scope_metrics(q["records"]);g=pre["retrieval_gate"] if a.role=="RETRIEVAL_SELECTION" else pre["transport_gate"]["scope_gate"];ok=scope_pass(m,g)
 out={"schema":"c3x-p8-scope-v1","scientific_stage":STAGE,"role":a.role,"status":a.role+"_SCOPE_PASS" if ok else a.role+"_SCOPE_HOLD",
  "metrics":m,"target_open_authorized":bool(ok),"target_fields_consulted":False,"post_target_metric_refit":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P8_SCOPE",a.role,ok,m["coverage"])

def auroc(scores,labels):
 pos=[s for s,y in zip(scores,labels) if y];neg=[s for s,y in zip(scores,labels) if not y]
 if not pos or not neg:return None
 win=0.0
 for a in pos:
  for b in neg:win+=1 if a>b else 0.5 if a==b else 0
 return win/(len(pos)*len(neg))
def average_precision(scores,labels):
 if not any(labels):return None
 groups=defaultdict(lambda:[0,0])
 for s,y in zip(scores,labels):groups[float(s)][1]+=1;groups[float(s)][0]+=int(bool(y))
 tp=0;seen=0;ap=0.0;P=sum(labels)
 for sc in sorted(groups,reverse=True):
  gp,gn=groups[sc];tp+=gp;seen+=gn;ap+=(gp/P)*(tp/seen)
 return ap
def verify(a):
 pre=load(a.precommit);idx=load(a.annotated_index);q=load(a.query);t=load(a.targets)
 tm={r["record_id"]:r for r in t["records"]};qm={r["record_id"]:r for r in q["records"]};evals=[]
 for rid,z in tm.items():
  if rid not in qm:raise SystemExit("P8_VERIFY_JOIN")
  x=qm[rid];score=0.0 if x["risk_score"] is None else float(x["risk_score"]);posx=x.get("positive_exemplars",[])
  evals.append({"record_id":rid,"engine":z["engine"],"position_id":z["position_id"],"source_stratum":z["source_stratum"],"root_change":bool(z["root_change"]),
    "score":score,"covered":x["status"]=="COVERED_LABELLED_PROTOTYPE","positive_analogue":bool(posx),
    "cross_engine_positive_analogue":any(e["engine"]!=z["engine"] for e in posx),"cross_position_positive_analogue":any(e["position_id"]!=z["position_id"] for e in posx)})
 gate=pre["selection_support_gate"];sup=support(list(tm.values()),gate,False);labels=[z["root_change"] for z in evals];scores=[z["score"] for z in evals]
 auc=auroc(scores,labels);ap=average_precision(scores,labels);base=sum(labels)/len(labels) if labels else 0
 pos=[z for z in evals if z["root_change"]]
 hit=sum(z["positive_analogue"] for z in pos)/len(pos) if pos else 0
 xeh=sum(z["cross_engine_positive_analogue"] for z in pos)/len(pos) if pos else 0
 xph=sum(z["cross_position_positive_analogue"] for z in pos)/len(pos) if pos else 0
 sm=scope_metrics(q["records"]);g=pre["retrieval_gate"]
 metrics={"scope":sm,"auroc":auc,"average_precision":ap,"base_rate":base,"average_precision_lift_over_base_rate":(ap/base if ap is not None and base>0 else None),
  "positive_analogue_hit_rate":hit,"cross_engine_positive_analogue_hit_rate":xeh,"cross_position_positive_analogue_hit_rate":xph}
 ok=sup["pass"] and scope_pass(sm,g) and auc is not None and auc>=g["min_auroc"] and metrics["average_precision_lift_over_base_rate"] is not None and metrics["average_precision_lift_over_base_rate"]>=g["min_average_precision_lift_over_base_rate"] and hit>=g["min_positive_analogue_hit_rate"] and xeh>=g["min_cross_engine_positive_analogue_hit_rate"] and xph>=g["min_cross_position_positive_analogue_hit_rate"]
 status=("RETRIEVAL_SELECTION_PASS" if a.role=="RETRIEVAL_SELECTION" else "TRANSPORT_RETRIEVAL_VALIDATED") if ok else (a.role+"_RETRIEVAL_HOLD")
 out={"schema":"c3x-p8-retrieval-verification-v1","scientific_stage":STAGE,"role":a.role,"status":status,"support":sup,"metrics":metrics,
  "pass":bool(ok),"evaluations":evals,"targets_consulted":True,"post_target_metric_refit":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P8_VERIFY",a.role,status,"auc",auc,"aplift",metrics["average_precision_lift_over_base_rate"])

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("precommit");q.add_argument("--constitution",required=True);q.add_argument("--corpus",required=True);q.add_argument("--p4-precommit",required=True);q.add_argument("--p7-closure",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=precommit)
 q=sp.add_parser("profile-case");q.add_argument("--precommit",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--sampler",required=True);q.add_argument("--sampling-plan",required=True);q.add_argument("--profile-out",required=True);q.add_argument("--case-out",required=True);q.set_defaults(fn=profile_case)
 q=sp.add_parser("target-case");q.add_argument("--precommit",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--sampler",required=True);q.add_argument("--sampling-plan",required=True);q.add_argument("--profile",required=True);q.add_argument("--target-out",required=True);q.add_argument("--case-out",required=True);q.set_defaults(fn=target_case)
 for name,fn in (("merge-profiles",merge_profiles),("merge-targets",merge_targets)):
  q=sp.add_parser(name);q.add_argument("--root",required=True);q.add_argument("--role",choices=ROLES,required=True);q.add_argument("--out",required=True);q.set_defaults(fn=fn)
 q=sp.add_parser("annotate");q.add_argument("--precommit",required=True);q.add_argument("--index",required=True);q.add_argument("--profiles",required=True);q.add_argument("--targets",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=annotate)
 q=sp.add_parser("enrich");q.add_argument("--annotated-index",required=True);q.add_argument("--query",required=True);q.add_argument("--profiles",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=enrich)
 q=sp.add_parser("scope");q.add_argument("--precommit",required=True);q.add_argument("--query",required=True);q.add_argument("--role",choices=("RETRIEVAL_SELECTION","UNTOUCHED_TRANSPORT"),required=True);q.add_argument("--out",required=True);q.set_defaults(fn=scope_cmd)
 q=sp.add_parser("verify");q.add_argument("--precommit",required=True);q.add_argument("--annotated-index",required=True);q.add_argument("--query",required=True);q.add_argument("--targets",required=True);q.add_argument("--role",choices=("RETRIEVAL_SELECTION","UNTOUCHED_TRANSPORT"),required=True);q.add_argument("--out",required=True);q.set_defaults(fn=verify)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
