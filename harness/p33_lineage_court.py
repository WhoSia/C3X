#!/usr/bin/env python3
import argparse,hashlib,json,subprocess,tempfile
from pathlib import Path
from collections import Counter
import p32_event_court as p32

STAGE="C3X 0.7.0-G9.4-P33"
MAX_ROUNDS=8
MAX_ADDRESSES=2048
MAX_REPLAYS=160
MAX_FINAL_LOO=32

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load_json(p):return json.loads(Path(p).read_text())
def sha_file(p):return p32.sha_file(p)

def load_support(p):
 x=load_json(p)
 if x.get("schema")!="c3x-p33-parent-support-v1" or x.get("primary_case_count")!=3 or x.get("repeat_control_count")!=3:raise SystemExit("P33_SUPPORT")
 if x.get("p33_selective_outcomes_consulted") is not False:raise SystemExit("P33_SUPPORT_LEAK")
 return x
def load_constitution(p):
 x=load_json(p);c=x.get("constitution",{})
 if c.get("schema")!="c3x-lawgen-constitution-v9" or c.get("p33_selective_results_consulted") is not False:raise SystemExit("P33_CONSTITUTION")
 return x
def load_parent_final(p):
 x=load_json(p)
 if x.get("schema")!="c3x-p32-adjudication-v1" or x.get("scientific_stage")!="C3X 0.7.0-G9.4-P32":raise SystemExit("P33_PARENT_FINAL")
 return x
def load_pre(p):
 x=load_json(p)
 if x.get("schema")!="c3x-p33-precommit-v1" or x.get("p33_selective_results_consulted") is not False:raise SystemExit("P33_PRE")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P33_PRE_HASH")
 return x

def p32_final_cases(x):return {z["case"]["case_id"]:z["case"] for z in x["certificates"]}
def p32_pre_cases(x):return {z["case_id"]:z for z in x["cases"]}

def sem(s):return {k:s.get(k) for k in ("bestmove","score","wdl","depth","seldepth","nodes","pv")}
def event_doc(trace):
 rows=[]
 for i,e0 in enumerate(trace["events"]):
  e=dict(e0);e["ordinal"]=i;rows.append(e)
 return {"events":rows}
def write_lineage(lineager,base,cf,root,label):
 root=Path(root);root.mkdir(parents=True,exist_ok=True)
 bp=root/(label+"-base.json");cp=root/(label+"-cf.json");op=root/(label+"-lineage.json")
 bp.write_text(json.dumps(event_doc(base),sort_keys=True)+"\n");cp.write_text(json.dumps(event_doc(cf),sort_keys=True)+"\n")
 subprocess.run([lineager,str(bp),str(cp),str(op)],check=True)
 return load_json(op)
def cf_classes(lineage):
 out={}
 for z in lineage["pairs"]:out[z["counterfactual_address_id"]]=z["class"]
 for z in lineage["emergent"]:out[z["counterfactual_address_id"]]="EMERGENT"
 return out
def frontier_addresses(trace,frontier):
 out=[]
 for e in trace["events"]:
  if e["ply"]<=frontier:
   z=dict(e["address"]);z["address_id"]=e["address_id"];out.append(z)
 return out

def precommit(a):
 sup=load_support(a.support);pf=load_parent_final(a.parent_final);pp=p32.load_pre(a.parent_pre);law=load_constitution(a.constitution)
 fc=p32_final_cases(pf);pc=p32_pre_cases(pp)
 requested=[z["case_id"] for z in sup["primary_cases"]+sup["repeat_controls"]]
 if len(set(requested))!=6 or any(x not in fc or x not in pc for x in requested):raise SystemExit("P33_CASESET")
 cases=[]
 roles={z["case_id"]:z["role"] for z in sup["primary_cases"]+sup["repeat_controls"]}
 for cid in requested:
  f=fc[cid];q=pc[cid]
  cases.append({"case_id":cid,"engine":q["engine"],"family":q["family"],"role":roles[cid],"primary":roles[cid]=="ADDRESS_INCOMPLETENESS_PRIMARY",
   "candidate_sha256":q["candidate_sha256"],"cell":q["cell"],"baseline":f["baseline"],"selected_frontier":f.get("selected_frontier"),
   "p32_status":f["status"],"p32_all_addressed":f.get("removal",{}).get("all_addressed_comprehensiveness"),
   "p32_parent_kind":f.get("parent_kind")})
 for c in cases:
  if c["primary"] and c["selected_frontier"] is None:raise SystemExit("P33_PRIMARY_NO_FRONTIER")
 out={"schema":"c3x-p33-precommit-v1","scientific_stage":STAGE,"p33_selective_results_consulted":False,
  "parent_p32_run":36188807920,"parent_final_receipt_sha256":pf["receipt_sha256"],"parent_precommit_receipt_sha256":pp["receipt_sha256"],
  "lawgen_constitution_sha256":law["constitution_sha256"],"support_sha256":digest(sup),
  "execution":{"hash_mib":1,"threads":1,"prime_nodes":20000,"decoy_nodes":20000,"decoy_count":3,"measurement_nodes":80000,
   "max_refinement_rounds":MAX_ROUNDS,"max_addresses":MAX_ADDRESSES,"max_replays_per_case":MAX_REPLAYS,"max_final_leave_one_out":MAX_FINAL_LOO},
  "variants":pp["variants"],"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P33_PRECOMMIT",out["receipt_sha256"],len(cases))

def verify_binary(pre,case,path):
 v=pre["variants"][case["engine"]]
 if sha_file(path)!=v["sha256"]:raise SystemExit("P33_BINARY")
 return v["protocol"]

def control(a):
 pre=load_pre(a.precommit);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id and not x["primary"]),None)
 if case is None:raise SystemExit("P33_CONTROL_CASE")
 protocol=verify_binary(pre,case,a.binary);frontier=case["selected_frontier"] if case["selected_frontier"] is not None else 8
 root=Path(a.out).parent/"runs";root.mkdir(parents=True,exist_ok=True)
 r1=p32.run_history(a.binary,protocol,case["cell"],"CATALOG",case["family"],frontier,None,root/"repeat-a")
 r2=p32.run_history(a.binary,protocol,case["cell"],"CATALOG",case["family"],frontier,None,root/"repeat-b")
 lin=write_lineage(a.lineager,r1["trace"],r2["trace"],root,"repeat")
 stable=all(sem(r1["semantic"]).get(k)==sem(r2["semantic"]).get(k) for k in ("bestmove","score","depth","pv"))
 no_birth=lin["summary"]["emergent"]==0 and lin["summary"]["vanished"]==0
 out={"schema":"c3x-p33-repeat-control-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],
  "frontier":frontier,"semantic_repeat_stable":stable,"lineage":lin,"status":"PASS" if stable and no_birth else "HOLD_REPEAT_IDENTITY",
  "semantics":[sem(r1["semantic"]),sem(r2["semantic"])]}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P33_CONTROL",case["case_id"],out["status"])

class Refine(Exception):pass
class Budget(Exception):pass

def case_run(a):
 pre=load_pre(a.precommit);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id and x["primary"]),None)
 if case is None:raise SystemExit("P33_PRIMARY_CASE")
 protocol=verify_binary(pre,case,a.binary);frontier=case["selected_frontier"];work=Path(a.out).parent/"runs";work.mkdir(parents=True,exist_ok=True)
 replay_count=0;cache={}
 def raw(addresses,label):
  nonlocal replay_count
  ids=tuple(sorted(z["address_id"] for z in addresses))
  if ids in cache:return cache[ids]
  if replay_count>=MAX_REPLAYS:raise Budget()
  replay_count+=1
  r=p32.run_history(a.binary,protocol,case["cell"],"REMOVE_SET",case["family"],frontier,addresses,work/f"{replay_count:03d}-{label}")
  cache[ids]=r;return r

 base=p32.run_history(a.binary,protocol,case["cell"],"CATALOG",case["family"],frontier,None,work/"000-baseline")
 if base["semantic"]["bestmove"]!=case["baseline"]["bestmove"]:raise SystemExit("P33_BASE_DRIFT")
 base_addrs=frontier_addresses(base["trace"],frontier);base_ids={z["address_id"] for z in base_addrs}
 if len(base_ids)!=len(base_addrs):raise SystemExit("P33_BASE_ADDR_DUP")
 universe={z["address_id"]:z for z in base_addrs};first_seen={};class_by_id={}
 parent=raw(base_addrs,"parent-seed-removal")
 expected=(case.get("p32_all_addressed") or {}).get("semantic",{}).get("bestmove")
 if expected and parent["semantic"]["bestmove"]!=expected:
  out={"schema":"c3x-p33-case-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],"family":case["family"],
   "status":"PARENT_REPLAY_DRIFT_HOLD","expected_parent_bestmove":expected,"got_parent":sem(parent["semantic"]),"replays_used":replay_count}
  seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P33_CASE",a.case_id,out["status"]);return
 parent_sem=sem(parent["semantic"])
 lineage_records=[]

 def observe(r,label,allow_refine=True):
  lin=write_lineage(a.lineager,base["trace"],r["trace"],work/"lineage",label)
  lineage_records.append({"label":label,"summary":lin["summary"],"first_trace_divergence":lin["first_trace_divergence"]})
  cmap=cf_classes(lin);new=[]
  for z in frontier_addresses(r["trace"],frontier):
   aid=z["address_id"]
   if aid not in universe:
    universe[aid]=z;class_by_id[aid]=cmap.get(aid,"EMERGENT");first_seen[aid]=label;new.append(aid)
  if len(universe)>MAX_ADDRESSES:raise Budget()
  if new and allow_refine:raise Refine()
  return lin,new

 parent_lin,parent_new=observe(parent,"parent-seed-removal",allow_refine=False)
 closure_rounds=0;refinement_restarts=0;status=None;full=None;full_lin=None;rem_ids=[];keep_ids=[];rem_cert=False;keep_cert=False;rem_loo={};keep_loo={};rem_res=None;keep_res=None
 productive=False;productive_detail={}
 try:
  while closure_rounds<MAX_ROUNDS:
   closure_rounds+=1
   try:
    full=raw([universe[k] for k in sorted(universe)],f"closure-{closure_rounds}")
    full_lin,_=observe(full,f"closure-{closure_rounds}")
    novel=[k for k in universe if k not in base_ids]
    if full["semantic"]["bestmove"]==parent["semantic"]["bestmove"]:
     status="LINEAGE_CLOSURE_NO_CONDITIONAL_ROOT_EFFECT";break
    if not novel:
     status="LINEAGE_CLOSURE_EMPTY_NOVEL_SET_HOLD";break

    def rr_remove(ids,label):
     r=raw([universe[k] for k in sorted(base_ids|set(ids))],label);observe(r,label);return r
    def pred_rem(ids):return rr_remove(ids,"dd-rem")["semantic"]["bestmove"]!=parent["semantic"]["bestmove"]
    rem_ids=p32.ddmin(novel,pred_rem)
    rem_ids,rem_cert,rem_loo=p32.stabilize_minimal(rem_ids,pred_rem,MAX_FINAL_LOO)
    rem_res=rr_remove(rem_ids,"minimal-branch-novel-removal")

    frozen_novel=[k for k in universe if k not in base_ids]
    def rr_keep(keep,label):
     targets=base_ids | (set(frozen_novel)-set(keep))
     r=raw([universe[k] for k in sorted(targets)],label);observe(r,label);return r
    def pred_keep(keep):return rr_keep(keep,"dd-keep")["semantic"]["bestmove"]==parent["semantic"]["bestmove"]
    if pred_keep(frozen_novel):
     keep_ids=p32.ddmin(frozen_novel,pred_keep)
     keep_ids,keep_cert,keep_loo=p32.stabilize_minimal(keep_ids,pred_keep,MAX_FINAL_LOO)
     keep_res=rr_keep(keep_ids,"minimal-branch-novel-retain")
    else:keep_res=None
    if rem_cert and keep_cert:status="LINEAGE_CLOSURE_NECESSITY_AND_SUFFICIENCY_CERTIFIED"
    elif rem_cert:status="LINEAGE_CLOSURE_NECESSITY_CERTIFIED_SUFFICIENCY_HOLD"
    else:status="LINEAGE_CLOSURE_MINIMALITY_HOLD"

    parent_events=event_doc(parent["trace"])["events"]
    first_blocked=min((e["ordinal"] for e in parent_events if e.get("blocked")==1),default=None)
    causal_parent_ord=[e["ordinal"] for e in parent_events if e["address_id"] in set(rem_ids)]
    first_causal=min(causal_parent_ord) if causal_parent_ord else None
    productive=bool(rem_cert and first_blocked is not None and first_causal is not None and first_causal>first_blocked)
    productive_detail={"first_fired_parent_target_ordinal":first_blocked,"first_minimal_branch_novel_ordinal":first_causal,
      "minimal_set_lineage_classes":{i:class_by_id.get(i,"UNCLASSIFIED") for i in rem_ids},
      "operational_witness":productive}
    break
   except Refine:
    refinement_restarts+=1
    if refinement_restarts>=MAX_ROUNDS:status="LINEAGE_CLOSURE_REFINEMENT_LIMIT_HOLD";break
    continue
 except Budget:
  status="LINEAGE_CLOSURE_BUDGET_HOLD"

 novel_ids=[k for k in universe if k not in base_ids]
 counts=Counter(class_by_id.get(k,"UNCLASSIFIED") for k in novel_ids)
 out={"schema":"c3x-p33-case-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],"family":case["family"],
  "primary":True,"frontier":frontier,"status":status,"baseline":sem(base["semantic"]),"parent_seed_removal":parent_sem,
  "parent_lineage":parent_lin,"closure_lineage":full_lin,"closure_semantic":sem(full["semantic"]) if full else None,
  "universe":{"baseline_exact_addresses":len(base_ids),"closed_exact_addresses":len(universe),"branch_novel_exact_addresses":len(novel_ids),
   "branch_novel_lineage_classes":dict(counts),"first_seen":first_seen},
  "minimal_branch_novel_removal":{"status":"CERTIFIED" if rem_cert else "HOLD","address_ids":rem_ids,
    "lineage_classes":{i:class_by_id.get(i,"UNCLASSIFIED") for i in rem_ids},"minimality":rem_loo,"semantic":sem(rem_res["semantic"]) if rem_res else None},
  "minimal_branch_novel_retaining":{"status":"CERTIFIED" if keep_cert else "HOLD","address_ids":keep_ids,
    "lineage_classes":{i:class_by_id.get(i,"UNCLASSIFIED") for i in keep_ids},"minimality":keep_loo,"semantic":sem(keep_res["semantic"]) if keep_res else None},
  "productive_search_trace":productive_detail,"productive_search_trace_witness":productive,
  "closure_rounds":closure_rounds,"refinement_restarts":refinement_restarts,"replays_used":replay_count,
  "lineage_records":lineage_records,
  "authority_ceiling":"replay-discovered closure over the prospective visited replay path; conditional on baseline-seed removal; operational lineage is not metaphysical identity or general SCM actual causation"}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P33_CASE",a.case_id,status,"base",len(base_ids),"closed",len(universe),"novel",len(novel_ids),"replays",replay_count)

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("precommit");q.add_argument("--support",required=True);q.add_argument("--parent-final",required=True);q.add_argument("--parent-pre",required=True);q.add_argument("--constitution",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=precommit)
 q=sp.add_parser("control");q.add_argument("--precommit",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--lineager",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=control)
 q=sp.add_parser("case");q.add_argument("--precommit",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--lineager",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=case_run)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
