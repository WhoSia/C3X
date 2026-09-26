#!/usr/bin/env python3
import argparse,hashlib,json,subprocess,tempfile
from collections import Counter,defaultdict
from pathlib import Path

import p32_event_court as p32
import p33_lineage_court as p33

STAGE="C3X 0.7.0-G9.5-P1"
LEVELS=("F0","F1","F2","F3")
CLASSES=("CUTOFF","MOVE_ORDER_SEED","EVAL_REUSE","TT_VALUE_AS_EVAL")
MAX_CAND=8
MAX_WORLD_REPLAYS=12

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load_json(p):return json.loads(Path(p).read_text())
def sem(s):return {k:s.get(k) for k in ("bestmove","score","wdl","depth","seldepth","nodes","pv")}

def load_support(p):
 x=load_json(p)
 if x.get("schema")!="c3x-g95-p1-support-v1" or x.get("g95_p1_selective_results_consulted") is not False:raise SystemExit("G95_SUPPORT")
 return x
def load_constitution(p):
 x=load_json(p);c=x.get("constitution",{})
 if c.get("schema")!="c3x-lawgen-constitution-v11" or c.get("g95_p1_selective_results_consulted") is not False:raise SystemExit("G95_CONSTITUTION")
 return x
def load_p34_pre(p):
 x=load_json(p)
 if x.get("schema")!="c3x-p34-precommit-v1" or x.get("p34_selective_results_consulted") is not False:raise SystemExit("G95_P34_PRE")
 return x
def load_p32_final(p):
 x=load_json(p)
 if x.get("schema")!="c3x-p32-adjudication-v1" or x.get("scientific_stage")!="C3X 0.7.0-G9.4-P32":raise SystemExit("G95_P32_FINAL")
 return x
def load_fresh(p):
 x=load_json(p)
 if x.get("schema")!="c3x-g95-p1-fresh-corpus-v1" or x.get("selection",{}).get("engine_outcomes_consulted") is not False:raise SystemExit("G95_CORPUS")
 return x
def load_pre(p):
 x=load_json(p)
 if x.get("schema")!="c3x-g95-p1-precommit-v1" or x.get("g95_p1_selective_results_consulted") is not False:raise SystemExit("G95_PRE")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("G95_PRE_HASH")
 return x
def p32_final_cases(x):return {z["case"]["case_id"]:z["case"] for z in x["certificates"]}
def p32_pre_cases(x):return {z["case_id"]:z for z in x["cases"]}
def p34_pre_cases(x):return {z["case_id"]:z for z in x["cases"]}

def precommit(a):
 sup=load_support(a.support);law=load_constitution(a.constitution)
 pp=p32.load_pre(a.p32_pre);pf=load_p32_final(a.p32_final);q34=load_p34_pre(a.p34_pre);fresh=load_fresh(a.fresh)
 pc=p32_pre_cases(pp);fc=p32_final_cases(pf);qc=p34_pre_cases(q34)
 cases=[]
 roles={}
 for z in sup["discovery_cases"]+sup["binding_holdout"]+sup["historical_transport_cases"]:roles[z["case_id"]]=z
 for z in sup["discovery_cases"]+sup["binding_holdout"]:
  cid=z["case_id"]
  if cid not in qc:raise SystemExit("G95_P34_CASE "+cid)
  q=qc[cid]
  cases.append({"case_id":cid,"engine":q["engine"],"family":q["family"],"role":z["role"],"context_kind":"P33_PARENT_SEED",
    "cell":q["cell"],"frontier":q["frontier"],"expected_parent":q["parent_seed_removal"],"expected_baseline":q["baseline"],
    "required_address_id":z.get("required_address_id")})
 for z in sup["historical_transport_cases"]:
  cid=z["case_id"]
  if cid not in pc or cid not in fc:raise SystemExit("G95_P32_CASE "+cid)
  q=pc[cid];f=fc[cid];fr=f.get("selected_frontier")
  if fr is None:raise SystemExit("G95_P32_NO_FRONTIER "+cid)
  cases.append({"case_id":cid,"engine":q["engine"],"family":q["family"],"role":z["role"],"context_kind":"BASELINE",
    "cell":q["cell"],"frontier":fr,"expected_parent":f["baseline"],"expected_baseline":f["baseline"],"required_address_id":None})
 for i,pos in enumerate(fresh["positions"]):
  for e in sup["fresh_corpus"]["engines"]:
   cases.append({"case_id":f"fresh:{i}:{e}","engine":e,"family":pos["family"],"role":"FRESH_CROSS_ENGINE_TRANSPORT",
    "context_kind":"BASELINE","cell":pos["cell"],"frontier":pos["frontier"],"expected_parent":None,"expected_baseline":None,
    "required_address_id":None,"fresh_position_id":pos["position_id"],"fresh_candidate_sha256":pos["candidate_sha256"]})
 if len([x for x in cases if x["role"]=="DISCOVERY_SPLIT_WORLD"])!=2:raise SystemExit("G95_DISCOVERY_COUNT")
 if len([x for x in cases if x["role"]=="BINDING_WITNESS_HOLDOUT"])!=1:raise SystemExit("G95_HOLDOUT_COUNT")
 if len([x for x in cases if x["role"]=="FRESH_CROSS_ENGINE_TRANSPORT"])!=6:raise SystemExit("G95_FRESH_COUNT")
 out={"schema":"c3x-g95-p1-precommit-v1","scientific_stage":STAGE,"g95_p1_selective_results_consulted":False,
  "support_sha256":digest(sup),"lawgen_constitution_sha256":law["constitution_sha256"],
  "p32_precommit_receipt_sha256":pp["receipt_sha256"],"p32_final_receipt_sha256":pf["receipt_sha256"],
  "p34_precommit_receipt_sha256":q34["receipt_sha256"],"fresh_corpus_sha256":digest(fresh),
  "variants":q34["variants"],"cases":cases,
  "execution":{"max_candidates_per_world":MAX_CAND,"max_world_replays":MAX_WORLD_REPLAYS,
    "hash_mib":1,"threads":1,"prime_nodes":20000,"decoy_nodes":20000,"decoy_count":3,"measurement_nodes":80000,
    "levels":list(LEVELS),"lineager":"HARD_ANCHOR_ORDER_PRESERVING_RANK_MATCH_V1"}}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P1_PRECOMMIT",out["receipt_sha256"],"cases",len(cases))

def verify_binary(pre,case,path):
 v=pre["variants"][case["engine"]]
 if p32.sha_file(path)!=v["sha256"]:raise SystemExit("G95_BINARY "+case["engine"])
 return v["protocol"]

def frontier_addresses(trace,frontier,include_blocked=True):
 out=[];seen=set()
 for e in trace["events"]:
  if e["ply"]<=frontier and (include_blocked or not e.get("blocked")) and e["address_id"] not in seen:
   z=dict(e["address"]);z["address_id"]=e["address_id"];out.append(z);seen.add(e["address_id"])
 return out

def sign(x):return -1 if x<0 else 1 if x>0 else 0
def count_bucket(x):
 x=max(0,int(x))
 return 0 if x==0 else 1 if x==1 else 2 if x<=3 else 3 if x<=7 else 4 if x<=15 else 5
def ply_bucket(x):return 0 if x<=0 else 1 if x==1 else 2 if x==2 else 3 if x<=4 else 4 if x<=8 else 5
def div_bucket(x):return 0 if x is None else 1 if x<=3 else 2 if x<=15 else 3 if x<=63 else 4
def cap(x):return max(-255,min(255,int(x)))

def fiber_tuple(rec,level):
 d=rec["diagnostic"]
 v=[rec["source_scope"],rec["source_class"],str(ply_bucket(rec["source_ply"])),str(sign(d["emergent"]-d["vanished"])),str(div_bucket(d["first_divergence_ordinal"]))]
 if level>=1:v += [str(count_bucket(d["emergent"])),str(count_bucket(d["vanished"])),str(count_bucket(d["drifted_continuations"]))]
 if level>=2:
  for key in ("emergent_by_class","vanished_by_class","drifted_by_class","count_delta_by_class"):
   v += [str(sign(x)) for x in d[key]]
 if level>=3:
  v += [str(cap(d[k])) for k in ("exact_continuations","drifted_continuations","emergent","vanished")]
  for key in ("emergent_by_class","vanished_by_class","drifted_by_class","count_delta_by_class"):v += [str(cap(x)) for x in d[key]]
  v += [str(-1 if d["first_divergence_ordinal"] is None else cap(d["first_divergence_ordinal"]))]
 return v
def fiber_id(rec,level):return f"F{level}|"+ "|".join(fiber_tuple(rec,level))

def event_map(trace):return {e["address_id"]:e for e in trace["events"]}
def class_counts(trace):
 c=Counter(e["class"] for e in trace["events"])
 return [c[k] for k in CLASSES]

def diagnostic(parent,cf,lineage):
 pm=event_map(parent);cm=event_map(cf)
 em=[0]*4;va=[0]*4;dr=[0]*4
 ci={k:i for i,k in enumerate(CLASSES)}
 for z in lineage["emergent"]:
  e=cm.get(z["counterfactual_address_id"])
  if e and e["class"] in ci:em[ci[e["class"]]]+=1
 for z in lineage["vanished"]:
  e=pm.get(z["base_address_id"])
  if e and e["class"] in ci:va[ci[e["class"]]]+=1
 for z in lineage["pairs"]:
  if z["class"]!="DRIFTED_CONTINUATION":continue
  e=cm.get(z["counterfactual_address_id"]) or pm.get(z["base_address_id"])
  if e and e["class"] in ci:dr[ci[e["class"]]]+=1
 a=class_counts(parent);b=class_counts(cf)
 fd=lineage.get("first_trace_divergence")
 return {"exact_continuations":lineage["summary"]["exact_continuations"],"drifted_continuations":lineage["summary"]["drifted_continuations"],
   "emergent":lineage["summary"]["emergent"],"vanished":lineage["summary"]["vanished"],
   "first_divergence_ordinal":fd.get("ordinal") if fd else None,
   "emergent_by_class":em,"vanished_by_class":va,"drifted_by_class":dr,"count_delta_by_class":[y-x for x,y in zip(a,b)]}

def verify_fibers(fiber_bin,records,root):
 root=Path(root);root.mkdir(parents=True,exist_ok=True);outs={}
 for i,l in enumerate(LEVELS):
  inp=root/f"{l}-input.json";out=root/f"{l}-verify.json"
  doc={"level":l,"records":[{"event_id":r["event_id"],"source_scope":r["source_scope"],"source_class":r["source_class"],
    "source_ply":r["source_ply"],"diagnostic":r["diagnostic"],"declared_fiber_id":r["fibers"][l]} for r in records]}
  inp.write_text(json.dumps(doc,sort_keys=True)+"\n")
  subprocess.run([fiber_bin,str(inp),str(out)],check=True)
  outs[l]=load_json(out)
 return outs

def assess(records,level):
 groups=defaultdict(list)
 for r in records:
  if r.get("target_fired") and r.get("root_change") is not None:groups[r["fibers"][level]].append(r)
 collisions=[]
 for fid,rs in sorted(groups.items()):
  labels=sorted(set(bool(z["root_change"]) for z in rs))
  if len(labels)>1:collisions.append({"fiber_id":fid,"members":[z["event_id"] for z in rs],"labels":labels})
 return {"records":sum(len(v) for v in groups.values()),"distinct_fibers":len(groups),
  "non_singleton_fibers":sum(1 for v in groups.values() if len(v)>1),"collisions":collisions,
  "collision_count":len(collisions),"compression":(1-len(groups)/sum(len(v) for v in groups.values())) if groups else 0.0}

def case_run(a):
 pre=load_pre(a.precommit);case=next((z for z in pre["cases"] if z["case_id"]==a.case_id),None)
 if case is None:raise SystemExit("G95_CASE "+a.case_id)
 protocol=verify_binary(pre,case,a.binary);work=Path(a.out).parent/"runs";work.mkdir(parents=True,exist_ok=True)
 replays=0
 base=p32.run_history(a.binary,protocol,case["cell"],"CATALOG",case["family"],case["frontier"],None,work/"000-base");replays+=1
 exp=case.get("expected_baseline")
 if exp and base["semantic"]["bestmove"]!=exp.get("bestmove"):raise SystemExit("G95_BASE_DRIFT "+case["case_id"])
 seed=[]
 if case["context_kind"]=="P33_PARENT_SEED":
  seed=frontier_addresses(base["trace"],case["frontier"],include_blocked=True)
  parent=p32.run_history(a.binary,protocol,case["cell"],"REMOVE_SET",case["family"],case["frontier"],seed,work/"001-parent");replays+=1
 else:parent=base
 exp=case.get("expected_parent")
 if exp and parent["semantic"]["bestmove"]!=exp.get("bestmove"):raise SystemExit("G95_PARENT_DRIFT "+case["case_id"])
 pe=event_map(parent["trace"])
 candidates=frontier_addresses(parent["trace"],case["frontier"],include_blocked=False)
 req=case.get("required_address_id")
 ordered=sorted(candidates,key=lambda z:z["address_id"])
 if req:
  hit=[z for z in ordered if z["address_id"]==req]
  if len(hit)!=1:raise SystemExit("G95_REQUIRED_WITNESS_MISSING "+case["case_id"])
  ordered=hit+[z for z in ordered if z["address_id"]!=req]
 candidates=ordered[:MAX_CAND]
 records=[]
 for j,cand in enumerate(candidates):
  if replays>=MAX_WORLD_REPLAYS:break
  targets=seed+[cand] if seed else [cand]
  cf=p32.run_history(a.binary,protocol,case["cell"],"REMOVE_SET",case["family"],case["frontier"],targets,work/f"{replays:03d}-single-{j}");replays+=1
  lin=p33.write_lineage(a.lineager,parent["trace"],cf["trace"],work/"lineage",f"event-{j}")
  e=pe[cand["address_id"]]
  ti=len(targets)-1
  fired=bool(cf["trace"]["targets"][ti]["fired"]) if ti<len(cf["trace"]["targets"]) else False
  d=diagnostic(parent["trace"],cf["trace"],lin)
  rec={"event_id":cand["address_id"],"address":cand,"source_scope":e["scope"],"source_class":e["class"],"source_ply":e["ply"],
    "source_depth":e["depth"],"target_fired":fired,"diagnostic":d,
    "root_change":bool(cf["semantic"]["bestmove"]!=parent["semantic"]["bestmove"]) if fired else None,
    "counterfactual":sem(cf["semantic"]) if fired else None}
  rec["fibers"]={l:fiber_id(rec,i) for i,l in enumerate(LEVELS)}
  records.append(rec)
 ver=verify_fibers(a.fiber_verifier,records,work/"fiber-verify") if records else {}
 selected=None;assessment=None;holdout_gate=None
 if a.selection:
  sx=load_json(a.selection);selected=sx.get("selected_level")
  if selected:
   assessment=assess(records,selected)
   if case["role"]=="BINDING_WITNESS_HOLDOUT":
    wr=next((z for z in records if z["event_id"]==req),None)
    peers=[z for z in records if wr and z["fibers"][selected]==wr["fibers"][selected] and z.get("target_fired")]
    collision=len(set(bool(z["root_change"]) for z in peers))>1 if peers else True
    holdout_gate={"witness_present":wr is not None,"witness_fired":bool(wr and wr["target_fired"]),
      "witness_root_change":bool(wr and wr["root_change"]),"fiber_id":wr["fibers"][selected] if wr else None,
      "fiber_members":[z["event_id"] for z in peers],"fiber_size":len(peers),"collision":collision,
      "pass":bool(wr and wr["target_fired"] and wr["root_change"] and not collision)}
 status="PASS" if records and all(z["target_fired"] for z in records) else "HOLD_TARGET_FIRE"
 if not records:status="HOLD_NO_CANDIDATES"
 if case["role"]=="BINDING_WITNESS_HOLDOUT" and holdout_gate and not holdout_gate["pass"]:status="WITNESS_FIBER_COLLISION_HOLD"
 out={"schema":"c3x-g95-p1-case-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],"family":case["family"],
  "role":case["role"],"context_kind":case["context_kind"],"frontier":case["frontier"],"status":status,
  "parent":sem(parent["semantic"]),"seed_exact_addresses":len(seed),"candidate_count":len(records),"replays_used":replays,
  "selected_level":selected,"selected_assessment":assessment,"holdout_gate":holdout_gate,
  "records":records,"fiber_verification":ver,
  "authority_ceiling":"Fiber identity uses lineage-response diagnostics only; root semantics remain target queries and never enter the diagnostic signature."}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P1_CASE",case["case_id"],status,"cand",len(records),"replays",replays)

def select_level(a):
 pre=load_pre(a.precommit)
 files=sorted(Path(a.results_dir).rglob("*.json"));cases=[]
 for p in files:
  try:x=load_json(p)
  except:continue
  if x.get("schema")=="c3x-g95-p1-case-v1" and x.get("role")=="DISCOVERY_SPLIT_WORLD":cases.append(x)
 if len(cases)!=2:raise SystemExit(f"G95_DISCOVERY_RESULTS {len(cases)}")
 rows=[r for c in cases for r in c["records"] if r.get("target_fired")]
 levels=[];selected=None
 for l in LEVELS:
  a0=assess(rows,l);passed=(a0["collision_count"]==0 and a0["distinct_fibers"]<a0["records"] and a0["non_singleton_fibers"]>0)
  levels.append({"level":l,**a0,"pass":passed})
  if selected is None and passed:selected=l
 out={"schema":"c3x-g95-p1-selection-v1","scientific_stage":STAGE,
  "status":"DISCOVERY_FIBER_LEVEL_FROZEN" if selected else "DISCOVERY_FIBER_CONSTITUTION_HOLD",
  "selected_level":selected,"levels":levels,"discovery_case_ids":sorted(c["case_id"] for c in cases),
  "discovery_receipts":sorted(c["receipt_sha256"] for c in cases),
  "holdout_consulted":False,"transport_consulted":False,
  "selection_rule":"first F0→F3 level with zero discovery ROOT_CHANGE collisions and nontrivial compression"}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P1_SELECTION",out["status"],selected)

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("precommit");q.add_argument("--support",required=True);q.add_argument("--constitution",required=True)
 q.add_argument("--p32-pre",required=True);q.add_argument("--p32-final",required=True);q.add_argument("--p34-pre",required=True)
 q.add_argument("--fresh",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=precommit)
 q=sp.add_parser("case");q.add_argument("--precommit",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True)
 q.add_argument("--lineager",required=True);q.add_argument("--fiber-verifier",required=True);q.add_argument("--selection");q.add_argument("--out",required=True);q.set_defaults(fn=case_run)
 q=sp.add_parser("select");q.add_argument("--precommit",required=True);q.add_argument("--results-dir",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=select_level)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
