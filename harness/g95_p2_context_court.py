#!/usr/bin/env python3
import argparse,hashlib,json,subprocess,sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import c3x_context as ctx
import p32_event_court as p32
import p33_lineage_court as p33
import g95_p1_fiber_court as p1

STAGE="C3X 0.7.0-G9.5-P2"
ENGINES=("stockfish_19","berserk","ethereal")
MAX_CAND=8

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load(p):return json.loads(Path(p).read_text())
def sha_file(p):return p32.sha_file(p)

def load_support(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p2-support-v1" or x.get("p2_selective_results_consulted") is not False:raise SystemExit("P2_SUPPORT")
 return x
def load_constitution(p):
 x=load(p);c=x.get("constitution",{})
 if c.get("schema")!="c3x-lawgen-constitution-v12" or c.get("p2_selective_results_consulted") is not False:raise SystemExit("P2_CONSTITUTION")
 return x
def load_corpus(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p2-corpus-v1" or x.get("selection",{}).get("p2_selective_results_consulted") is not False:raise SystemExit("P2_CORPUS")
 return x
def load_p34(p):
 x=load(p)
 if x.get("schema")!="c3x-p34-precommit-v1" or x.get("p34_selective_results_consulted") is not False:raise SystemExit("P2_P34")
 return x
def load_p25(p):
 x=load(p)
 if x.get("scientific_stage")!="C3X 0.7.0-G9.4-P25":raise SystemExit("P2_P25")
 return x
def load_pre(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p2-precommit-v1" or x.get("p2_selective_results_consulted") is not False:raise SystemExit("P2_PRE")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P2_PRE_HASH")
 return x

def precommit(a):
 sup=load_support(a.support);law=load_constitution(a.constitution);corp=load_corpus(a.corpus);p34=load_p34(a.p34_pre);p25=load_p25(a.p25_spec)
 c=law["constitution"]
 portable=[z["name"] for z in c["context_vocabulary"]["portable"]]
 arch=list(c["context_vocabulary"]["architecture_secondary"])
 desc={z["id"]:z["descriptor"] for z in p25["engines"]}
 if set(desc)!=set(ENGINES):raise SystemExit("P2_ARCH_ENGINE_SET")
 cases=[]
 for role,key in (("DISCOVERY_CONTEXT_BASIS","discovery_positions"),("HELDOUT_CONTEXT_TRANSPORT","heldout_positions")):
  for i,pos in enumerate(corp[key]):
   for e in ENGINES:
    cases.append({"case_id":f"p2:{'disc' if role.startswith('DISCOVERY') else 'hold'}:{i}:{e}",
      "role":role,"engine":e,"position_id":pos["position_id"],"candidate_sha256":pos["candidate_sha256"],
      "cell":pos["cell"],"family":pos["family"],"frontier":pos["frontier"]})
 if len(cases)!=48:raise SystemExit(f"P2_CASE_COUNT {len(cases)}")
 out={"schema":"c3x-g95-p2-precommit-v1","scientific_stage":STAGE,"p2_selective_results_consulted":False,
   "support_sha256":digest(sup),"lawgen_constitution_sha256":law["constitution_sha256"],"corpus_sha256":digest(corp),
   "p34_precommit_receipt_sha256":p34["receipt_sha256"],"variants":p34["variants"],
   "architecture_descriptors":desc,"portable_coordinates":portable,"architecture_coordinates":arch,
   "execution":{"hash_mib":1,"threads":1,"prime_nodes":20000,"decoy_nodes":20000,"decoy_count":3,
                "measurement_nodes":80000,"candidate_events_per_world":MAX_CAND,"family":"MOVE_ORDER+EVAL","frontier":1},
   "cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P2_PRECOMMIT",out["receipt_sha256"],"cases",len(cases))

def verify_binary(pre,case,path):
 v=pre["variants"][case["engine"]]
 if sha_file(path)!=v["sha256"]:raise SystemExit("P2_BINARY_ID "+case["engine"])
 return v["protocol"]

def parent_event_rows(trace,frontier):
 rows=[]
 for i,e in enumerate(trace["events"]):
  if e["ply"]<=frontier:
   z=dict(e);z["ordinal"]=i;rows.append(z)
 return rows

def stratified_candidates(trace,frontier,n=MAX_CAND):
 rows=parent_event_rows(trace,frontier);by=defaultdict(list);seen=set()
 for e in rows:
  aid=e["address_id"]
  if aid in seen:continue
  seen.add(aid);key=(e["scope"],e["class"],p1.ply_bucket(e["ply"]))
  by[key].append(e)
 for k in by:by[k].sort(key=lambda z:z["address_id"])
 keys=sorted(by);out=[];round_i=0
 while len(out)<n:
  added=False
  for k in keys:
   if round_i<len(by[k]):
    out.append(by[k][round_i]);added=True
    if len(out)>=n:break
  if not added:break
  round_i+=1
 return out

def address_from_event(e):
 z=dict(e["address"]);z["address_id"]=e["address_id"];return z

def case_run(a):
 pre=load_pre(a.precommit);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if case is None:raise SystemExit("P2_CASE_ID")
 protocol=verify_binary(pre,case,a.binary);work=Path(a.case_out).parent/"runs";work.mkdir(parents=True,exist_ok=True)
 parent=p32.run_history(a.binary,protocol,case["cell"],"CATALOG",case["family"],case["frontier"],None,work/"000-parent")
 candidates=stratified_candidates(parent["trace"],case["frontier"],MAX_CAND)
 pmap={e["address_id"]:(i,e) for i,e in enumerate(parent["trace"]["events"])}
 profiles=[];targets=[];missed=[];fiber_records=[]
 for j,e in enumerate(candidates):
  addr=address_from_event(e)
  cf=p32.run_history(a.binary,protocol,case["cell"],"REMOVE_SET",case["family"],case["frontier"],[addr],work/f"{j+1:03d}-single")
  fired=bool(cf["trace"]["targets"] and cf["trace"]["targets"][0]["fired"])
  if not fired:missed.append(e["address_id"]);continue
  lin=p33.write_lineage(a.lineager,parent["trace"],cf["trace"],work/"lineage",f"event-{j}")
  d=p1.diagnostic(parent["trace"],cf["trace"],lin)
  rec0={"source_scope":e["scope"],"source_class":e["class"],"source_ply":e["ply"],"diagnostic":d}
  fid=p1.fiber_id(rec0,0)
  ordinal,pe=pmap[e["address_id"]]
  cvals,avals=ctx.build_context(case["cell"]["fen"],parent["semantic"],parent["trace"],pe,ordinal,pre["architecture_descriptors"][case["engine"]])
  rid=f'{case["case_id"]}:{e["address_id"][:16]}'
  profile={"record_id":rid,"engine":case["engine"],"position_id":case["position_id"],"event_id":e["address_id"],
    "fiber_id":fid,"context":cvals,"architecture_context":avals}
  target={"record_id":rid,"root_change":cf["semantic"]["bestmove"]!=parent["semantic"]["bestmove"],
    "parent_bestmove":parent["semantic"]["bestmove"],"counterfactual_bestmove":cf["semantic"]["bestmove"],
    "parent_score":parent["semantic"].get("score"),"counterfactual_score":cf["semantic"].get("score"),
    "parent_wdl":parent["semantic"].get("wdl"),"counterfactual_wdl":cf["semantic"].get("wdl"),
    "parent_pv":parent["semantic"].get("pv"),"counterfactual_pv":cf["semantic"].get("pv")}
  profiles.append(profile);targets.append(target)
  fiber_records.append({"event_id":e["address_id"],"source_scope":e["scope"],"source_class":e["class"],"source_ply":e["ply"],
    "diagnostic":d,"declared_fiber_id":fid})
 # independent F0 recomputation
 fdoc={"level":"F0","records":fiber_records};fi=work/"fiber-input.json";fo=work/"fiber-verify.json"
 fi.write_text(json.dumps(fdoc,sort_keys=True)+"\n");subprocess.run([a.fiber_verifier,str(fi),str(fo)],check=True)
 fv=load(fo)
 if fv.get("mismatches") or fv.get("target_fields_consulted") is not False:raise SystemExit("P2_FIBER_VERIFY")
 profile_doc={"schema":"c3x-context-profile-batch-v1","scientific_stage":STAGE,"case_id":case["case_id"],
   "role":case["role"],"records":profiles,"target_fields_consulted":False}
 target_doc={"schema":"c3x-context-target-batch-v1","scientific_stage":STAGE,"case_id":case["case_id"],
   "role":case["role"],"records":targets}
 Path(a.profile_out).write_text(json.dumps(profile_doc,indent=2,sort_keys=True)+"\n")
 Path(a.target_out).write_text(json.dumps(target_doc,indent=2,sort_keys=True)+"\n")
 manifest={"schema":"c3x-g95-p2-case-v1","scientific_stage":STAGE,"case_id":case["case_id"],"role":case["role"],
  "engine":case["engine"],"position_id":case["position_id"],"parent_semantic":parent["semantic"],
  "candidate_count":len(candidates),"fired_records":len(profiles),"missed_target_ids":missed,
  "profile_sha256":digest(profile_doc),"target_sha256":digest(target_doc),"fiber_verification":fv,
  "status":"PASS" if profiles and not missed else "PARTIAL_TARGET_FIRE_HOLD" if profiles else "NO_FIRED_TARGETS_HOLD"}
 seal(manifest);Path(a.case_out).write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
 print("G95_P2_CASE",case["case_id"],manifest["status"],"fired",len(profiles),"/",len(candidates))

def collect_batches(root,schema):
 out=[]
 for p in Path(root).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")==schema:out.append(x)
 return out

def merge_discovery(a):
 pre=load_pre(a.precommit);profiles=collect_batches(a.root,"c3x-context-profile-batch-v1");targets=collect_batches(a.root,"c3x-context-target-batch-v1")
 profiles=[x for x in profiles if x.get("role")=="DISCOVERY_CONTEXT_BASIS"];targets=[x for x in targets if x.get("role")=="DISCOVERY_CONTEXT_BASIS"]
 if len(profiles)!=24 or len(targets)!=24:raise SystemExit(f"P2_DISC_BATCHES {len(profiles)} {len(targets)}")
 ps={r["record_id"]:r for b in profiles for r in b["records"]};ts={r["record_id"]:r for b in targets for r in b["records"]}
 if set(ps)!=set(ts):raise SystemExit("P2_DISC_JOIN")
 rows=[]
 for rid in sorted(ps):
  p=ps[rid];t=ts[rid]
  rows.append({"record_id":rid,"engine":p["engine"],"position_id":p["position_id"],"event_id":p["event_id"],
    "fiber_id":p["fiber_id"],"context":p["context"],"architecture_context":p["architecture_context"],"target":bool(t["root_change"])})
 out={"schema":"c3x-field-discovery-input-v1","scientific_stage":STAGE,
   "portable_coordinates":pre["portable_coordinates"],"architecture_coordinates":pre["architecture_coordinates"],"records":rows}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P2_DISCOVERY_MERGE",len(rows))

def merge_profiles(a):
 batches=collect_batches(a.root,"c3x-context-profile-batch-v1")
 batches=[x for x in batches if x.get("role")=="HELDOUT_CONTEXT_TRANSPORT"]
 if len(batches)!=24:raise SystemExit(f"P2_HOLD_PROFILE_BATCHES {len(batches)}")
 rows=[r for b in batches for r in b["records"]]
 ids=[r["record_id"] for r in rows]
 if len(ids)!=len(set(ids)):raise SystemExit("P2_PROFILE_DUP")
 out={"schema":"c3x-context-profile-batch-v1","scientific_stage":STAGE,"records":sorted(rows,key=lambda z:z["record_id"])}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P2_PROFILE_MERGE",len(rows))

def merge_targets(a):
 batches=collect_batches(a.root,"c3x-context-target-batch-v1")
 batches=[x for x in batches if x.get("role")=="HELDOUT_CONTEXT_TRANSPORT"]
 if len(batches)!=24:raise SystemExit(f"P2_HOLD_TARGET_BATCHES {len(batches)}")
 rows=[r for b in batches for r in b["records"]]
 ids=[r["record_id"] for r in rows]
 if len(ids)!=len(set(ids)):raise SystemExit("P2_TARGET_DUP")
 out={"schema":"c3x-context-target-batch-v1","scientific_stage":STAGE,"records":sorted(rows,key=lambda z:z["record_id"])}
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P2_TARGET_MERGE",len(rows))

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("precommit");q.add_argument("--support",required=True);q.add_argument("--constitution",required=True);q.add_argument("--corpus",required=True)
 q.add_argument("--p34-pre",required=True);q.add_argument("--p25-spec",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=precommit)
 q=sp.add_parser("case");q.add_argument("--precommit",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True)
 q.add_argument("--lineager",required=True);q.add_argument("--fiber-verifier",required=True);q.add_argument("--profile-out",required=True)
 q.add_argument("--target-out",required=True);q.add_argument("--case-out",required=True);q.set_defaults(fn=case_run)
 q=sp.add_parser("merge-discovery");q.add_argument("--precommit",required=True);q.add_argument("--root",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=merge_discovery)
 q=sp.add_parser("merge-profiles");q.add_argument("--root",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=merge_profiles)
 q=sp.add_parser("merge-targets");q.add_argument("--root",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=merge_targets)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
