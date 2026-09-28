#!/usr/bin/env python3
import argparse,hashlib,json,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"harness"))
import p32_event_court as p32
sys.path.insert(0,str(ROOT/"tools"))
import c3x_cseg_input_v1 as chessphen

STAGE="C3X 0.7.0-G9.5-P9"
ENGINES=("stockfish_19","berserk","ethereal")

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load(p):return json.loads(Path(p).read_text())
def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def pv_list(x):
 if x is None:return []
 if isinstance(x,list):return [str(v) for v in x]
 if isinstance(x,str):return [z for z in x.split() if z]
 return []
def first_div(a,b):
 a=pv_list(a);b=pv_list(b);i=0
 while i<min(len(a),len(b)) and a[i]==b[i]:i+=1
 if i==len(a)==len(b):return None
 return {"ply_index":i,"common_prefix":a[:i],"baseline_next":a[i] if i<len(a) else None,
  "counterfactual_next":b[i] if i<len(b) else None,"baseline_remaining":a[i:],"counterfactual_remaining":b[i:]}

def precommit(a):
 lawx=load(a.constitution);corp=load(a.corpus);p4=load(a.p4_precommit);p8=load(a.p8_closure)
 if lawx.get("schema")!="c3x-lawgen-constitution-v19":raise SystemExit("P9_LAW")
 law=lawx["constitution"]
 if law.get("scientific_stage")!=STAGE or corp.get("schema")!="c3x-g95-p9-corpus-v1":raise SystemExit("P9_STAGE")
 if p8.get("schema")!="c3x-g95-p8-closure-v1" or p8.get("receipt_sha256")!=law["parent"]["closure_receipt_sha256"]:raise SystemExit("P9_PARENT")
 fw=law["p8_firewall"]
 for k in ("p8_target_labels_confirmatory_vote","p8_positive_source_locations_confirmatory_vote","p8_prototype_ids_allowed","p8_descriptor_allowed_as_primary_estimand"):
  if fw[k] is not False:raise SystemExit("P9_FIREWALL_"+k)
 if corp["selection"].get("engine_outcomes_consulted") is not False or corp["selection"].get("historical_target_labels_consulted") is not False or corp["selection"].get("p8_target_labels_consulted") is not False:
  raise SystemExit("P9_CORPUS_FIREWALL")
 cases=[]
 for i,pos in enumerate(corp["positions"]):
  for e in ENGINES:
   cases.append({"case_id":f"p9:{i}:{e}","engine":e,"position_id":pos["position_id"],"trajectory_id":pos["trajectory_id"],
    "phase":pos["phase"],"source_id":pos["source_id"],"source_logical":pos["source_logical"],"source_ply":pos["source_ply"],
    "candidate_sha256":pos["candidate_sha256"],"complexity":pos["complexity"],"cell":pos["cell"],"family":pos["family"],"frontier":pos["frontier"]})
 if len(cases)!=72:raise SystemExit(f"P9_CASE_COUNT {len(cases)}")
 out={"schema":"c3x-g95-p9-precommit-v1","scientific_stage":STAGE,"constitution_sha256":digest(lawx),"corpus_sha256":digest(corp),
  "parent_p8_closure_receipt_sha256":p8["receipt_sha256"],"p8_target_labels_consulted":False,"p8_source_positive_locations_consulted":False,
  "variants":p4["variants"],"execution":law["execution"],"support_gate":law["support_gate"],"hotspot_rule":law["hotspot_rule"],
  "regression_suite":law["regression_suite"],"developer_diagnostic":law["developer_diagnostic"],"claim_ceiling":law["claim_ceiling"],"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P9_PRECOMMIT",out["receipt_sha256"],"cases",len(cases))

def verify_binary(pre,case,path):
 v=pre["variants"][case["engine"]]
 if sha_file(path)!=v["sha256"]:raise SystemExit("P9_BINARY_ID")
 return v["protocol"],v["sha256"]

def case_run(a):
 pre=load(a.precommit);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if not case:raise SystemExit("P9_CASE")
 protocol,bsha=verify_binary(pre,case,a.binary)
 work=Path(a.event_out).parent/".p9-private";work.mkdir(parents=True,exist_ok=True)
 parent=p32.run_history(a.binary,protocol,case["cell"],"CATALOG",case["family"],case["frontier"],None,work/"000-parent")
 trace_path=work/"parent-trace.json";trace_path.write_text(json.dumps(parent["trace"],sort_keys=True)+"\n")
 sample_path=work/"sampling.json"
 subprocess.run([a.sampler,"sample","--trace",str(trace_path),"--plan",a.sampling_plan,
  "--max-events",str(pre["execution"]["candidate_events_per_world"]),"--out",str(sample_path)],check=True)
 samp=load(sample_path)
 if samp.get("target_fields_consulted") is not False or samp.get("raw_full_key_emitted") is not False:raise SystemExit("P9_SAMPLER_FIREWALL")
 byid={e["address_id"]:e for e in parent["trace"]["events"]};rows=[];miss=[]
 for j,z in enumerate(samp["selected"]):
  aid=z["event_id"];e=byid[aid];addr=dict(e["address"]);addr["address_id"]=aid
  cf=p32.run_history(a.binary,protocol,case["cell"],"REMOVE_SET",case["family"],case["frontier"],[addr],work/f"{j+1:03d}-single")
  fired=bool(cf["trace"]["targets"] and cf["trace"]["targets"][0]["fired"])
  if not fired:
   miss.append({"event_id":aid,"sampling_stratum":z["sampling_stratum"]});continue
  rid=f'{case["case_id"]}:{aid[:16]}'
  baseline={k:parent["semantic"].get(k) for k in ("bestmove","score","wdl","depth","seldepth","nodes","pv")}
  counter={k:cf["semantic"].get(k) for k in ("bestmove","score","wdl","depth","seldepth","nodes","pv")}
  rows.append({"record_id":rid,"engine":case["engine"],"engine_binary_sha256":bsha,"position_id":case["position_id"],
   "trajectory_id":case["trajectory_id"],"phase":case["phase"],"source_id":case["source_id"],"source_logical":case["source_logical"],
   "source_ply":case["source_ply"],"candidate_sha256":case["candidate_sha256"],"complexity":case["complexity"],
   "event_id":aid,"event_address":addr,"sampling_stratum":z["sampling_stratum"],"semantic_class":e["class"],"scope":e["scope"],
   "ply":e["ply"],"depth":e["depth"],"root_change":counter["bestmove"]!=baseline["bestmove"],
   "baseline":baseline,"counterfactual":counter,"first_pv_divergence":first_div(baseline.get("pv"),counter.get("pv")),
   "chess_phenotype":chessphen.root_move_phenotype(case["cell"]["fen"],baseline.get("bestmove"),counter.get("bestmove"))})
 out={"schema":"c3x-p9-event-batch-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
  "position_id":case["position_id"],"trajectory_id":case["trajectory_id"],"phase":case["phase"],"source_id":case["source_id"],"records":rows}
 Path(a.event_out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 man={"schema":"c3x-g95-p9-case-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
  "position_id":case["position_id"],"trajectory_id":case["trajectory_id"],"phase":case["phase"],"source_id":case["source_id"],
  "sampled_events":len(samp["selected"]),"fired_events":len(rows),"root_change_events":sum(r["root_change"] for r in rows),
  "missed_targets":miss,"event_batch_sha256":digest(out),"status":"PASS"}
 seal(man);Path(a.case_out).write_text(json.dumps(man,indent=2,sort_keys=True)+"\n")
 print("G95_P9_CASE",case["case_id"],case["phase"],"fired",len(rows),"positive",man["root_change_events"])

def merge(a):
 bs=[]
 for p in Path(a.root).rglob("*.json"):
  try:x=load(p)
  except Exception:continue
  if x.get("schema")=="c3x-p9-event-batch-v1":bs.append(x)
 if len(bs)!=72:raise SystemExit(f"P9_EVENT_BATCH_COUNT {len(bs)}")
 rows=sorted([r for b in bs for r in b["records"]],key=lambda z:z["record_id"])
 out={"schema":"c3x-p9-event-merged-v1","scientific_stage":STAGE,"case_batches":len(bs),"records":rows,
  "target_fields_consulted":True,"p8_target_labels_consulted":False}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P9_MERGED","batches",len(bs),"records",len(rows),"positive",sum(r["root_change"] for r in rows))

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("precommit");q.add_argument("--constitution",required=True);q.add_argument("--corpus",required=True);q.add_argument("--p4-precommit",required=True);q.add_argument("--p8-closure",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=precommit)
 q=sp.add_parser("case");q.add_argument("--precommit",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--sampler",required=True);q.add_argument("--sampling-plan",required=True);q.add_argument("--event-out",required=True);q.add_argument("--case-out",required=True);q.set_defaults(fn=case_run)
 q=sp.add_parser("merge");q.add_argument("--root",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=merge)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
