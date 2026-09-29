#!/usr/bin/env python3
import argparse,hashlib,json,subprocess,sys
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"harness"))
import p32_event_court as p32
import p33_lineage_court as p33
sys.path.insert(0,str(ROOT/"tools"))
import c3x_cseg_input_v1 as chessphen

STAGE="C3X 0.7.0-G9.5-P10"
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
  "counterfactual_next":b[i] if i<len(b) else None}
def depth_band(d):
 d=int(d)
 if d<=4:return "LE4"
 if d<=8:return "D5_8"
 if d<=12:return "D9_12"
 return "D13_PLUS"
def bound_bucket(v):
 return {0:"NONE",1:"UPPER",2:"LOWER",3:"EXACT"}.get(int(v),"OTHER")
def count_bucket(n):
 if n<=1:return str(n)
 if n==2:return "2"
 return "3_PLUS"
def gap_bucket(g):
 if g is None:return "NONE"
 if g==1:return "1"
 if g<=4:return "2_4"
 if g<=16:return "5_16"
 return "17_PLUS"
def delta(a,b):
 if a is None or b is None:return "NONE"
 a=int(a);b=int(b)
 return "UP" if a>b else "DOWN" if a<b else "SAME"
def public_address(e):
 return {k:e["address"].get(k) for k in ("scope","class","class_id","ply","depth","tt_move","bound","payload","occ")}
def lineage_atoms(events,i):
 e=events[i];past=events[:i];same=[(j,z) for j,z in enumerate(past) if z.get("key")==e.get("key")]
 prev_same=same[-1] if same else None
 prev_class=next(((j,z) for j,z in reversed(list(enumerate(past))) if z.get("class")==e.get("class")),None)
 prev=events[i-1] if i>0 else None
 key_history="REPEAT_KEY" if same else "FIRST_KEY"
 if not same:move_rel="FIRST_KEY"
 else:move_rel="SAME_MOVE" if int(prev_same[1].get("tt_move",0))==int(e.get("tt_move",0)) else "DIFF_MOVE"
 a0={
  "scope":str(e["scope"]),"ply_bucket":"PLY0" if int(e["ply"])==0 else "PLY1",
  "depth_band":depth_band(e["depth"]),"bound_bucket":bound_bucket(e.get("bound",0)),
  "key_history":key_history,"same_key_move_relation":move_rel}
 a1=dict(a0)
 a1.update({
  "same_key_count_bucket":count_bucket(len(same)),
  "same_key_prev_gap_bucket":gap_bucket(None if prev_same is None else i-prev_same[0]),
  "same_key_depth_delta":"NONE" if prev_same is None else delta(e["depth"],prev_same[1]["depth"]),
  "same_class_prev_gap_bucket":gap_bucket(None if prev_class is None else i-prev_class[0]),
  "previous_semantic_class":"START" if prev is None else str(prev["class"]),
  "previous_scope":"START" if prev is None else str(prev["scope"])})
 def aid(z):return "|".join(str(z[k]) for k in sorted(z))
 return a0,a1,aid(a0),aid(a1)

def select_events(trace,max_events=24):
 es=trace["events"];eligible=[]
 for i,e in enumerate(es):
  if e.get("class")!="MOVE_ORDER_SEED" or int(e.get("ply",99))>1 or int(e.get("tt_move",0))==0:continue
  prior=any(z.get("key")==e.get("key") for z in es[:i])
  eligible.append((e["address_id"],i,"REPEAT_KEY" if prior else "FIRST_KEY"))
 eligible.sort()
 selected=[];used=set()
 for sid,quota in (("FIRST_KEY",8),("REPEAT_KEY",12)):
  n=0
  for aid,i,s in eligible:
   if n>=quota or len(selected)>=max_events:break
   if s==sid and aid not in used:
    used.add(aid);selected.append((aid,i,sid));n+=1
 for aid,i,_ in eligible:
  if len(selected)>=max_events:break
  if aid not in used:
   used.add(aid);selected.append((aid,i,"QUOTA_FILL"))
 return selected,{"eligible":len(eligible),"selected":len(selected),
   "FIRST_KEY":sum(z[2]=="FIRST_KEY" for z in selected),"REPEAT_KEY":sum(z[2]=="REPEAT_KEY" for z in selected),
   "QUOTA_FILL":sum(z[2]=="QUOTA_FILL" for z in selected)}

def precommit(a):
 lawx=load(a.constitution);corp=load(a.corpus);p4=load(a.p4_precommit);p9=load(a.p9_closure)
 if lawx.get("schema")!="c3x-lawgen-constitution-v20":raise SystemExit("P10_LAW")
 law=lawx["constitution"]
 if law.get("scientific_stage")!=STAGE or corp.get("schema")!="c3x-g95-p10-corpus-v1":raise SystemExit("P10_STAGE")
 if p9.get("schema")!="c3x-g95-p9-closure-v1" or p9.get("receipt_sha256")!=law["parent"]["closure_receipt_sha256"]:raise SystemExit("P10_PARENT")
 fw=law["p9_firewall"]
 if fw["p9_target_labels_confirmatory_vote"] is not False or fw["p9_regression_witnesses_confirmatory_vote"] is not False:raise SystemExit("P10_FIREWALL")
 if corp["selection"]["engine_outcomes_consulted"] is not False or corp["selection"]["p9_target_labels_consulted"] is not False:raise SystemExit("P10_CORPUS_FIREWALL")
 cases=[]
 for i,pos in enumerate(corp["positions"]):
  for e in ENGINES:
   cases.append({"case_id":f"p10:{i}:{e}","engine":e,"position_id":pos["position_id"],"trajectory_id":pos["trajectory_id"],
    "source_id":pos["source_id"],"source_logical":pos["source_logical"],"source_ply":pos["source_ply"],
    "candidate_sha256":pos["candidate_sha256"],"complexity":pos["complexity"],"cell":pos["cell"],
    "family":"MOVE_ORDER","frontier":1})
 if len(cases)!=27:raise SystemExit("P10_CASE_COUNT")
 out={"schema":"c3x-g95-p10-precommit-v1","scientific_stage":STAGE,
  "constitution_sha256":digest(lawx),"corpus_sha256":digest(corp),"parent_p9_receipt_sha256":p9["receipt_sha256"],
  "p9_target_labels_consulted":False,"p9_regression_witnesses_confirmatory_vote":False,
  "variants":p4["variants"],"execution":law["execution"],"event_sampler":law["event_sampler"],
  "support_gate":law["support_gate"],"lineage":law["lineage"],"p9_regression_seed_lane":law["p9_regression_seed_lane"],
  "claim_ceiling":law["claim_ceiling"],"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P10_PRECOMMIT",out["receipt_sha256"],"cases",len(cases))

def verify_binary(pre,case,path):
 v=pre["variants"][case["engine"]]
 if sha_file(path)!=v["sha256"]:raise SystemExit("P10_BINARY_ID")
 return v["protocol"],v["sha256"]

def case_run(a):
 pre=load(a.precommit);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if not case:raise SystemExit("P10_CASE")
 protocol,bsha=verify_binary(pre,case,a.binary)
 work=Path(a.event_out).parent/".p10-private";work.mkdir(parents=True,exist_ok=True)
 base=p32.run_history(a.binary,protocol,case["cell"],"CATALOG","MOVE_ORDER",1,None,work/"000-base")
 selected,census=select_events(base["trace"],int(pre["execution"]["candidate_events_per_world"]))
 rows=[];miss=[]
 for j,(aid,ordinal,stratum) in enumerate(selected):
  e=base["trace"]["events"][ordinal];addr=dict(e["address"]);addr["address_id"]=aid
  a0,a1,a0id,a1id=lineage_atoms(base["trace"]["events"],ordinal)
  cf=p32.run_history(a.binary,protocol,case["cell"],"REMOVE_SET","MOVE_ORDER",1,[addr],work/f"{j+1:03d}-remove")
  fired=bool(cf["trace"]["targets"] and cf["trace"]["targets"][0]["fired"])
  if not fired:
   miss.append({"event_id":aid,"sampling_stratum":stratum});continue
  lin=p33.write_lineage(a.lineager,base["trace"],cf["trace"],work/"lineage",f"event-{j:03d}")
  baseline={k:base["semantic"].get(k) for k in ("bestmove","score","wdl","depth","seldepth","nodes","pv")}
  counter={k:cf["semantic"].get(k) for k in ("bestmove","score","wdl","depth","seldepth","nodes","pv")}
  rows.append({"record_id":f'{case["case_id"]}:{aid[:16]}',"engine":case["engine"],"engine_binary_sha256":bsha,
   "position_id":case["position_id"],"trajectory_id":case["trajectory_id"],"source_id":case["source_id"],"source_ply":case["source_ply"],
   "candidate_sha256":case["candidate_sha256"],"complexity":case["complexity"],"event_id":aid,
   "event_address_public":public_address(e),"sampling_stratum":stratum,"semantic_class":"MOVE_ORDER_SEED",
   "a0_archetype":a0,"a0_id":a0id,"a1_archetype":a1,"a1_id":a1id,
   "root_change":counter["bestmove"]!=baseline["bestmove"],"baseline":baseline,"counterfactual":counter,
   "first_pv_divergence":first_div(baseline.get("pv"),counter.get("pv")),
   "chess_phenotype":chessphen.root_move_phenotype(case["cell"]["fen"],baseline.get("bestmove"),counter.get("bestmove")),
   "trace_lineage":{"summary":lin["summary"],"first_trace_divergence":lin["first_trace_divergence"]},
   "raw_tt_key_emitted":False})
 out={"schema":"c3x-p10-event-batch-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
  "position_id":case["position_id"],"trajectory_id":case["trajectory_id"],"source_id":case["source_id"],
  "sampler_census":census,"records":rows,"p9_target_labels_consulted":False,"raw_tt_key_emitted":False}
 Path(a.event_out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 man={"schema":"c3x-g95-p10-case-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
  "position_id":case["position_id"],"source_id":case["source_id"],"eligible_events":census["eligible"],
  "sampled_events":census["selected"],"fired_events":len(rows),"root_change_events":sum(r["root_change"] for r in rows),
  "missed_targets":miss,"event_batch_sha256":digest(out),"status":"PASS"}
 seal(man);Path(a.case_out).write_text(json.dumps(man,indent=2,sort_keys=True)+"\n")
 print("G95_P10_CASE",case["case_id"],"fired",len(rows),"positive",man["root_change_events"],"repeat",census["REPEAT_KEY"])

def merge(a):
 bs=[]
 for p in Path(a.root).rglob("*.json"):
  try:x=load(p)
  except Exception:continue
  if x.get("schema")=="c3x-p10-event-batch-v1":bs.append(x)
 if len(bs)!=27:raise SystemExit(f"P10_BATCH_COUNT {len(bs)}")
 rows=sorted([r for b in bs for r in b["records"]],key=lambda z:z["record_id"])
 out={"schema":"c3x-p10-event-merged-v1","scientific_stage":STAGE,"case_batches":len(bs),"records":rows,
  "p9_target_labels_consulted":False,"raw_tt_key_emitted":False}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P10_MERGED","batches",len(bs),"records",len(rows),"positive",sum(r["root_change"] for r in rows))

def regression(a):
 p9map=load(a.p9_map);p9pre=load(a.p9_precommit)
 if p9map.get("schema")!="c3x-g95-p9-map-v1" or p9pre.get("schema")!="c3x-g95-p9-precommit-v1":raise SystemExit("P10_REG_PARENT")
 bins={"stockfish_19":a.stockfish_bin,"berserk":a.berserk_bin,"ethereal":a.ethereal_bin}
 cases={(z["engine"],z["position_id"]):z for z in p9pre["cases"]};rows=[];all_pass=True
 for i,pair in enumerate(p9map["regression_suite"]):
  pos=pair["positive"];eng=pos["engine"];case=cases[(eng,pos["position_id"])]
  path=bins[eng];protocol,bsha=verify_binary(p9pre,case,path)
  work=Path(a.out).parent/".p10-regression"/f"{i:02d}-{eng}";work.mkdir(parents=True,exist_ok=True)
  base=p32.run_history(path,protocol,case["cell"],"CATALOG",case["family"],case["frontier"],None,work/"base")
  addr=dict(pos["event_address"]);addr["address_id"]=pos["event_address_id"]
  cf=p32.run_history(path,protocol,case["cell"],"REMOVE_SET",case["family"],case["frontier"],[addr],work/"positive")
  fired=bool(cf["trace"]["targets"] and cf["trace"]["targets"][0]["fired"])
  base_ok=base["semantic"].get("bestmove")==pos["baseline"].get("bestmove")
  pos_ok=fired and cf["semantic"].get("bestmove")==pos["counterfactual"].get("bestmove")
  ctrl=pair.get("matched_control");ctrl_doc=None;ctrl_ok=True
  if ctrl:
   ca=dict(ctrl["event_address"]);ca["address_id"]=ctrl["event_address_id"]
   cr=p32.run_history(path,protocol,case["cell"],"REMOVE_SET",case["family"],case["frontier"],[ca],work/"control")
   cfired=bool(cr["trace"]["targets"] and cr["trace"]["targets"][0]["fired"])
   ctrl_ok=cfired and cr["semantic"].get("bestmove")==ctrl["counterfactual"].get("bestmove")==ctrl["baseline"].get("bestmove")
   ctrl_doc={"record_id":ctrl["record_id"],"event_address":ctrl["event_address"],"expected_bestmove":ctrl["baseline"].get("bestmove"),
    "observed_bestmove":cr["semantic"].get("bestmove"),"target_fired":cfired,"pass":ctrl_ok}
  ok=base_ok and pos_ok and ctrl_ok;all_pass=all_pass and ok
  rows.append({"case_index":i,"engine":eng,"engine_binary_sha256":bsha,"position_id":pos["position_id"],
   "fen":case["cell"]["fen"],"positive_record_id":pos["record_id"],"positive_event_address":pos["event_address"],
   "expected_baseline_bestmove":pos["baseline"].get("bestmove"),"observed_baseline_bestmove":base["semantic"].get("bestmove"),
   "expected_counterfactual_bestmove":pos["counterfactual"].get("bestmove"),"observed_counterfactual_bestmove":cf["semantic"].get("bestmove"),
   "positive_target_fired":fired,"baseline_pass":base_ok,"positive_pass":pos_ok,"matched_control":ctrl_doc,
   "baseline_pv":pos["baseline"].get("pv"),"counterfactual_pv":pos["counterfactual"].get("pv"),
   "first_pv_divergence":pos.get("first_pv_divergence"),"pass":ok})
 out={"schema":"c3x-g95-p10-p9-seed-replay-v1","scientific_stage":STAGE,"authority":"ENGINEERING_REPRODUCTION_ONLY",
  "fresh_confirmatory_vote":False,"cases":rows,"case_count":len(rows),"pass":all_pass}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P10_P9_SEED_REPLAY","PASS" if all_pass else "FAIL","cases",len(rows))
 if not all_pass:raise SystemExit(2)

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("precommit");q.add_argument("--constitution",required=True);q.add_argument("--corpus",required=True);q.add_argument("--p4-precommit",required=True);q.add_argument("--p9-closure",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=precommit)
 q=sp.add_parser("case");q.add_argument("--precommit",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--lineager",required=True);q.add_argument("--event-out",required=True);q.add_argument("--case-out",required=True);q.set_defaults(fn=case_run)
 q=sp.add_parser("merge");q.add_argument("--root",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=merge)
 q=sp.add_parser("regression");q.add_argument("--p9-map",required=True);q.add_argument("--p9-precommit",required=True);q.add_argument("--stockfish-bin",required=True);q.add_argument("--berserk-bin",required=True);q.add_argument("--ethereal-bin",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=regression)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
