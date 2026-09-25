#!/usr/bin/env python3
import argparse,hashlib,json,math,os,re,subprocess,tempfile
from collections import defaultdict
from pathlib import Path
import p27_age_morphism as p27

STAGE="C3X 0.7.0-G9.4-P32"
ENGINES=("stockfish_19","berserk","ethereal")
FRONTIERS=(0,1,2,4,8)
CLS={"CUTOFF":0,"MOVE_ORDER_SEED":1,"EVAL_REUSE":2,"TT_VALUE_AS_EVAL":3}
MODE_FOR_FAMILY={"CUTOFF":"NO_CUTOFF","MOVE_ORDER":"NO_MOVE","EVAL":"NO_EVAL","MOVE_ORDER+EVAL":"NO_MOVE_EVAL"}
HASH=1;PRIME=20000;DECOY=20000;ANCHOR=80000
MAX_CANDIDATES=512;MAX_REPLAYS=96;MAX_FINAL_LOO=24

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def protocol_for(e):return "stockfish_uci" if e=="stockfish_19" else "env"

def load_json(p):return json.loads(Path(p).read_text())
def load_parent_final(p):
 x=load_json(p)
 if x.get("schema")!="c3x-p31-adjudication-v1" or x.get("scientific_stage")!="C3X 0.7.0-G9.4-P31":raise SystemExit("P32_PARENT_FINAL")
 return x
def load_parent_pre(p):
 x=load_json(p)
 if x.get("schema")!="c3x-p31-precommit-v1" or x.get("selective_results_consulted") is not False:raise SystemExit("P32_PARENT_PRE")
 return x
def load_support(p):
 x=load_json(p)
 if x.get("schema")!="c3x-p32-parent-support-v1" or x.get("selected_engine_worlds")!=14:raise SystemExit("P32_SUPPORT")
 return x
def load_constitution(p):
 x=load_json(p);c=x.get("constitution",{})
 if c.get("schema")!="c3x-lawgen-constitution-v8" or c.get("p32_event_results_consulted") is not False:raise SystemExit("P32_CONSTITUTION")
 return x
def load_pre(p):
 x=load_json(p)
 if x.get("schema")!="c3x-p32-precommit-v1" or x.get("event_results_consulted") is not False:raise SystemExit("P32_PRE")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P32_PRE_HASH")
 return x

def setup(path,protocol,mode,family,frontier,target_file,trace_file,tt_file):
 env=os.environ.copy()
 env["C3X_TT_USE_MODE"]="BASE"
 env["C3X_P32_MODE"]=mode
 env["C3X_P32_FAMILY"]=family
 env["C3X_P32_FRONTIER"]=str(frontier)
 env["C3X_P32_TRACE"]=str(trace_file)
 env["C3X_TT_TRACE"]=str(tt_file);env["C3X_TT_GRAPH_SEQ"]="0"
 if target_file:env["C3X_P32_TARGET_FILE"]=str(target_file)
 else:env.pop("C3X_P32_TARGET_FILE",None)
 if protocol=="env":env["C3X_PSM_MODE"]="SHAM"
 else:env.pop("C3X_PSM_MODE",None)
 p=subprocess.Popen([path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,env=env)
 p.stdin.write("uci\n");p.stdin.flush();pre=p27.read_until(p,lambda x:x.strip()=="uciok")
 if not any(x.strip()=="uciok" for x in pre):raise RuntimeError("P32_UCI")
 opts="\n".join(pre);cmd=[]
 if protocol=="stockfish_uci":
  if not p27.has_option(opts,"C3X_TTReadMode") or not p27.has_option(opts,"C3X_Telemetry"):raise RuntimeError("P32_SF_SURFACE")
  cmd += ["setoption name C3X_TTReadMode value SHAM","setoption name C3X_Telemetry value true"]
 if p27.has_option(opts,"Threads"):cmd.append("setoption name Threads value 1")
 if p27.has_option(opts,"Hash"):cmd.append(f"setoption name Hash value {HASH}")
 if p27.has_option(opts,"SyzygyProbeLimit"):cmd.append("setoption name SyzygyProbeLimit value 0")
 if p27.has_option(opts,"UCI_ShowWDL"):cmd.append("setoption name UCI_ShowWDL value true")
 if p27.has_option(opts,"Clear Hash"):cmd.append("setoption name Clear Hash")
 cmd.append("isready")
 for c in cmd:p.stdin.write(c+"\n")
 p.stdin.flush();ready=p27.read_until(p,lambda x:x.strip()=="readyok")
 if not any(x.strip()=="readyok" for x in ready):raise RuntimeError("P32_READY")
 return p

def addr_signature(e):
 return (e["scope"],e["class"],e["key"],e["ply"],e["depth"],e["tt_move"],e["bound"],e["payload"])

def parse_trace(path):
 events=[];summary=None;targets=[]
 for line in Path(path).read_text().splitlines():
  z=line.split(",")
  if not z:continue
  if z[0]=="E":
   if len(z)!=15:raise RuntimeError(f"P32_E_WIDTH {len(z)}")
   _,scope,cl,key,ply,depth,alpha,beta,ttval,tteval,bound,move,payload,selected,blocked=z
   if cl not in CLS:raise RuntimeError("P32_CLASS "+cl)
   events.append({"scope":scope,"class":cl,"class_id":CLS[cl],"key":key,"ply":int(ply),"depth":int(depth),
    "alpha":int(alpha),"beta":int(beta),"tt_value":int(ttval),"tt_eval":int(tteval),"bound":int(bound),
    "tt_move":int(move),"payload":int(payload),"selected":int(selected),"blocked":int(blocked)})
  elif z[0]=="S":
   if len(z)!=6:raise RuntimeError("P32_S_WIDTH")
   summary={"events":int(z[1]),"catalogued":int(z[2]),"blocked":int(z[3]),"targets":int(z[4]),"targets_fired":int(z[5])}
  elif z[0]=="T":
   if len(z)!=5:raise RuntimeError("P32_T_WIDTH")
   targets.append({"index":int(z[1]),"occ":int(z[2]),"seen":int(z[3]),"fired":int(z[4])})
 if summary is None:raise RuntimeError("P32_TRACE_SUMMARY")
 counts=defaultdict(int)
 for e in events:
  sig=addr_signature(e);counts[sig]+=1;e["occ"]=counts[sig]
  a={"scope":e["scope"],"class":e["class"],"class_id":e["class_id"],"key":e["key"],"ply":e["ply"],"depth":e["depth"],
     "tt_move":e["tt_move"],"bound":e["bound"],"payload":e["payload"],"occ":e["occ"]}
  e["address"]=a;e["address_id"]=digest(a)
 return {"events":events,"summary":summary,"targets":targets}

def write_targets(path,addresses):
 with open(path,"w") as f:
  for a in addresses:
   f.write(f'{a["scope"]}\t{a["class_id"]}\t{a["key"]}\t{a["ply"]}\t{a["depth"]}\t{a["tt_move"]}\t{a["bound"]}\t{a["payload"]}\t{a["occ"]}\n')

def run_history(path,protocol,cell,mode,family,frontier,addresses,work):
 work=Path(work);work.mkdir(parents=True,exist_ok=True)
 trace=work/"p32.csv";tt=work/"tt.csv";target=work/"targets.tsv"
 if addresses is not None:write_targets(target,addresses)
 p=setup(path,protocol,mode,family,frontier,target if addresses is not None else None,trace,tt)
 try:
  p27.go(p,cell["fen"],PRIME,protocol)
  for d in cell["history"]["decoys"]:p27.go(p,d["fen"],DECOY,protocol)
  sem,_=p27.go(p,cell["fen"],ANCHOR,protocol)
  try:p.stdin.write("quit\n");p.stdin.flush()
  except:pass
  try:p.communicate(timeout=8)
  except subprocess.TimeoutExpired:p.kill();p.communicate()
 finally:
  if p.poll() is None:p.kill()
 tr=parse_trace(trace)
 trace.unlink(missing_ok=True);tt.unlink(missing_ok=True);target.unlink(missing_ok=True)
 return {"semantic":sem,"trace":tr}

def sem_view(s):
 return {k:s.get(k) for k in ("bestmove","score","wdl","depth","seldepth","nodes","pv")}

def cert_map(final):
 return {(c["engine"],c["candidate_sha256"]):c for c in final["certificates"]}

def cell_map(pre):return {c["candidate_sha256"]:c for c in pre["cells"]}

def transparency(a):
 sup=load_support(a.support);final=load_parent_final(a.parent_final);pre=load_parent_pre(a.parent_pre)
 cm=cert_map(final);cells=cell_map(pre);rows=[];bad=[]
 units=[u for u in sup["units"] if u["engine"]==a.engine]
 for i,u in enumerate(units):
  c=cm[(a.engine,u["candidate_sha256"])];cell=cells[u["candidate_sha256"]]
  fam=(u["single_families"]+u["interaction_families"])[0]
  r=run_history(a.binary,protocol_for(a.engine),cell,"BASE",fam,8,None,Path(a.out).parent/"identity"/str(i))
  got=sem_view(r["semantic"]);exp=sem_view(c["baseline"]["semantic"])
  keys=("bestmove","score","depth","pv")
  ok=all(got.get(k)==exp.get(k) for k in keys)
  rows.append({"candidate_sha256":u["candidate_sha256"],"family_probe":fam,"match":ok,"expected":exp,"got":got})
  if not ok:bad.append(u["candidate_sha256"])
 out={"schema":"c3x-p32-transparency-v1","scientific_stage":STAGE,"engine":a.engine,"rows":rows,"mismatches":bad,"verdict":"PASS" if not bad else "FAIL"}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P32_TRANSPARENCY",a.engine,out["verdict"],len(rows))

def precommit(a):
 sup=load_support(a.support);final=load_parent_final(a.parent_final);pp=load_parent_pre(a.parent_pre);law=load_constitution(a.constitution)
 cm=cert_map(final);cells=cell_map(pp);builds=Path(a.build_dir);variants={};identity={}
 for e in ENGINES:
  fs=list(builds.rglob(f"c3x-p32-{e}"));ids=list(builds.rglob(f"p32-transparency-{e}.json"))
  if len(fs)!=1 or len(ids)!=1:raise SystemExit(f"P32_BUILD_SET {e}")
  ix=load_json(ids[0])
  if ix.get("verdict")!="PASS":raise SystemExit("P32_TRANSPARENCY_FAIL "+e)
  variants[e]={"sha256":sha_file(fs[0]),"protocol":protocol_for(e)}
  identity[e]={"receipt_sha256":ix["receipt_sha256"],"verdict":"PASS","units":len(ix["rows"])}
 cases=[]
 for u in sup["units"]:
  pc=cm[(u["engine"],u["candidate_sha256"])]
  cell=cells[u["candidate_sha256"]]
  if pc["baseline"]["semantic"]["bestmove"]!=u["baseline_bestmove"]:raise SystemExit("P32_SUPPORT_PARENT_MISMATCH")
  for fam in u["single_families"]:
   mode=MODE_FOR_FAMILY[fam];alt=pc["counterfactual_deltas"][mode]["alternative"]
   if alt["bestmove"]==u["baseline_bestmove"]:raise SystemExit("P32_PARENT_SINGLE_NULL")
   cases.append({"case_id":f'{u["engine"]}:{u["candidate_sha256"][:12]}:{fam}',"engine":u["engine"],"candidate_sha256":u["candidate_sha256"],
    "family":fam,"primary":True,"parent_kind":"SINGLE_CLASS","baseline":sem_view(pc["baseline"]["semantic"]),"parent_counterfactual":sem_view(alt),
    "cell":cell})
  for fam in u["interaction_families"]:
   mode=MODE_FOR_FAMILY[fam];alt=pc["counterfactual_deltas"][mode]["alternative"]
   pure=bool(u["pure_interaction_only"])
   cases.append({"case_id":f'{u["engine"]}:{u["candidate_sha256"][:12]}:{fam}',"engine":u["engine"],"candidate_sha256":u["candidate_sha256"],
    "family":fam,"primary":pure,"parent_kind":"PURE_INTERACTION" if pure else "INTERACTION_DIAGNOSTIC","baseline":sem_view(pc["baseline"]["semantic"]),
    "parent_counterfactual":sem_view(alt),"cell":cell})
 if sum(c["primary"] for c in cases)!=18 or len(cases)!=19:raise SystemExit(f"P32_CASE_COUNT {sum(c['primary'] for c in cases)} {len(cases)}")
 out={"schema":"c3x-p32-precommit-v1","scientific_stage":STAGE,"event_results_consulted":False,
  "lawgen_constitution_sha256":law["constitution_sha256"],"support_sha256":digest(sup),
  "parent_final_receipt_sha256":final["receipt_sha256"],"parent_precommit_receipt_sha256":pp["receipt_sha256"],
  "execution":{"hash_mib":HASH,"threads":1,"prime_nodes":PRIME,"decoy_nodes":DECOY,"decoy_count":3,"measurement_nodes":ANCHOR,
    "frontiers":list(FRONTIERS),"max_candidates":MAX_CANDIDATES,"max_replays_per_case":MAX_REPLAYS,"max_final_leave_one_out":MAX_FINAL_LOO},
  "variants":variants,"transparency":identity,"cases":cases}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P32_PRECOMMIT",out["receipt_sha256"],len(cases),sum(c["primary"] for c in cases))

class BudgetExceeded(Exception):pass

def chunks(seq,n):
 n=max(1,min(n,len(seq)));q,r=divmod(len(seq),n);out=[];i=0
 for k in range(n):
  z=q+(1 if k<r else 0);out.append(seq[i:i+z]);i+=z
 return [x for x in out if x]

def ddmin(items,pred):
 cur=list(items);n=2
 while len(cur)>=2:
  subs=chunks(cur,n);reduced=False
  for s in subs:
   if pred(s):cur=s;n=max(n-1,2);reduced=True;break
  if reduced:continue
  for s in subs:
   ss=set(s);comp=[x for x in cur if x not in ss]
   if comp and pred(comp):cur=comp;n=max(n-1,2);reduced=True;break
  if reduced:continue
  if n>=len(cur):break
  n=min(len(cur),n*2)
 return cur

def stabilize_minimal(items,pred,max_size):
 cur=list(items)
 if len(cur)>max_size:return cur,False,{"reason":"FINAL_SET_TOO_LARGE_FOR_LOO","size":len(cur)}
 changed=True
 while changed:
  changed=False
  for x in list(cur):
   trial=[y for y in cur if y!=x]
   if trial and pred(trial):cur=trial;changed=True;break
 if len(cur)>max_size:return cur,False,{"reason":"FINAL_SET_TOO_LARGE_FOR_LOO","size":len(cur)}
 checks=[]
 for x in cur:
  trial=[y for y in cur if y!=x]
  remains=pred(trial) if trial else False
  checks.append({"address_id":x,"predicate_after_deletion":remains})
 if any(z["predicate_after_deletion"] for z in checks):return cur,False,{"reason":"LEAVE_ONE_OUT_FAILED","checks":checks}
 return cur,True,{"checks":checks}

def case_run(a):
 pre=load_pre(a.precommit);case=next((c for c in pre["cases"] if c["case_id"]==a.case_id),None)
 if not case:raise SystemExit("P32_CASE_ID")
 e=case["engine"];v=pre["variants"][e]
 if sha_file(a.binary)!=v["sha256"]:raise SystemExit("P32_BINARY")
 cell=case["cell"];family=case["family"];root=Path(a.out).parent/"runs";root.mkdir(parents=True,exist_ok=True)
 replay_count=0;cache={}
 def replay(mode,frontier,addresses,label):
  nonlocal replay_count
  ids=tuple(sorted(x["address_id"] for x in addresses)) if addresses is not None else ()
  key=(mode,frontier,ids)
  if key in cache:return cache[key]
  if replay_count>=MAX_REPLAYS:raise BudgetExceeded()
  replay_count+=1
  r=run_history(a.binary,v["protocol"],cell,mode,family,frontier,addresses,root/f"{replay_count:03d}-{label}")
  cache[key]=r;return r
 base=replay("CATALOG",8,None,"catalog")
 if base["semantic"]["bestmove"]!=case["baseline"]["bestmove"]:raise SystemExit("P32_BASE_DRIFT")
 frontier_rows=[];chosen=None;frontier_cf=None
 try:
  for f in FRONTIERS:
   r=replay("FRONTIER_NULL",f,None,f"frontier-{f}")
   changed=r["semantic"]["bestmove"]!=base["semantic"]["bestmove"]
   frontier_rows.append({"frontier":f,"changed":changed,"semantic":sem_view(r["semantic"]),"trace_summary":r["trace"]["summary"]})
   if changed and chosen is None:chosen=f;frontier_cf=r
 except BudgetExceeded:pass
 out={"schema":"c3x-p32-case-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":e,"candidate_sha256":case["candidate_sha256"],
  "family":family,"primary":case["primary"],"parent_kind":case["parent_kind"],"baseline":sem_view(base["semantic"]),
  "parent_counterfactual":case["parent_counterfactual"],"frontier_ladder":frontier_rows,"selected_frontier":chosen,"replays_used":replay_count,
  "status":None,"catalogue":{},"removal":{},"retaining":{}}
 if chosen is None:
  out["status"]="DEEPER_OR_NONADDRESSABLE";seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P32_CASE",a.case_id,out["status"]);return
 events=[q for q in base["trace"]["events"] if q["ply"]<=chosen]
 addrs=[];seen=set()
 for q in events:
  aid=q["address_id"]
  if aid in seen:raise SystemExit("P32_ADDRESS_DUP")
  seen.add(aid);z=dict(q["address"]);z["address_id"]=aid;addrs.append(z)
 out["catalogue"]={"events_in_frontier":len(addrs),"event_types":dict((k,sum(q["class"]==k for q in events)) for k in CLS),
                   "catalog_trace_summary":base["trace"]["summary"]}
 if len(addrs)>MAX_CANDIDATES:
  out["status"]="EVENT_UNIVERSE_BUDGET_HOLD";seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P32_CASE",a.case_id,out["status"],len(addrs));return
 byid={z["address_id"]:z for z in addrs}
 def rr(mode,ids,label):
  return replay(mode,chosen,[byid[i] for i in ids],label)
 try:
  all_ids=[z["address_id"] for z in addrs]
  full_remove=rr("REMOVE_SET",all_ids,"remove-all-addresses")
  comp=full_remove["semantic"]["bestmove"]!=base["semantic"]["bestmove"]
  out["removal"]["all_addressed_comprehensiveness"]={"changed":comp,"semantic":sem_view(full_remove["semantic"]),"trace_summary":full_remove["trace"]["summary"]}
  rem_cert=False;rem_ids=[];rem_res=None
  if comp:
   def pred_rem(ids):return rr("REMOVE_SET",ids,"dd-rem")["semantic"]["bestmove"]!=base["semantic"]["bestmove"]
   rem_ids=ddmin(all_ids,pred_rem)
   rem_ids,rem_cert,rem_loo=stabilize_minimal(rem_ids,pred_rem,MAX_FINAL_LOO)
   rem_res=rr("REMOVE_SET",rem_ids,"minimal-removal")
   singles=[]
   if rem_cert:
    for i in rem_ids:
     z=rr("REMOVE_SET",[i],"singleton-rem")
     singles.append({"address_id":i,"changes_root":z["semantic"]["bestmove"]!=base["semantic"]["bestmove"],"semantic":sem_view(z["semantic"])})
   out["removal"].update({"status":"CERTIFIED" if rem_cert else "MINIMALITY_HOLD","address_ids":rem_ids,
     "addresses":[byid[i] for i in rem_ids],"semantic":sem_view(rem_res["semantic"]),"minimality":rem_loo,"singleton_effects":singles,
     "interaction_only":bool(rem_cert and len(rem_ids)>1 and not any(s["changes_root"] for s in singles))})
  else:out["removal"]["status"]="ADDRESS_SET_NOT_COMPREHENSIVE"

  empty_keep=rr("KEEP_SET",[],"keep-empty")
  all_keep=rr("KEEP_SET",all_ids,"keep-all")
  out["retaining"]["boundary"]={"empty":sem_view(empty_keep["semantic"]),"all":sem_view(all_keep["semantic"]),
    "empty_changes_root":empty_keep["semantic"]["bestmove"]!=base["semantic"]["bestmove"],
    "all_restores_root":all_keep["semantic"]["bestmove"]==base["semantic"]["bestmove"]}
  if out["retaining"]["boundary"]["empty_changes_root"] and out["retaining"]["boundary"]["all_restores_root"]:
   def pred_keep(ids):return rr("KEEP_SET",ids,"dd-keep")["semantic"]["bestmove"]==base["semantic"]["bestmove"]
   keep_ids=ddmin(all_ids,pred_keep)
   keep_ids,keep_cert,keep_loo=stabilize_minimal(keep_ids,pred_keep,MAX_FINAL_LOO)
   keep_res=rr("KEEP_SET",keep_ids,"minimal-retain")
   out["retaining"].update({"status":"CERTIFIED" if keep_cert else "SUFFICIENCY_MINIMALITY_HOLD","address_ids":keep_ids,
     "addresses":[byid[i] for i in keep_ids],"semantic":sem_view(keep_res["semantic"]),"minimality":keep_loo})
  else:out["retaining"]["status"]="ADDRESS_REPLAY_BOUNDARY_FAIL"
  if out["removal"].get("status")=="CERTIFIED" and out["retaining"].get("status")=="CERTIFIED":out["status"]="EVENT_LEVEL_NECESSITY_AND_SUFFICIENCY_CERTIFIED"
  elif out["removal"].get("status")=="CERTIFIED":out["status"]="EVENT_LEVEL_NECESSITY_CERTIFIED_SUFFICIENCY_HOLD"
  elif out["retaining"].get("status")=="CERTIFIED":out["status"]="EVENT_LEVEL_SUFFICIENCY_CERTIFIED_NECESSITY_HOLD"
  else:out["status"]="EVENT_LEVEL_LOCALIZATION_HOLD"
 except BudgetExceeded:
  out["status"]="REPLAY_BUDGET_HOLD"
 out["replays_used"]=replay_count
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P32_CASE",a.case_id,out["status"],"frontier",chosen,"cand",len(addrs),"replays",replay_count)

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("transparency");q.add_argument("--engine",choices=ENGINES,required=True);q.add_argument("--binary",required=True);q.add_argument("--support",required=True);q.add_argument("--parent-final",required=True);q.add_argument("--parent-pre",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=transparency)
 q=sp.add_parser("precommit");q.add_argument("--support",required=True);q.add_argument("--parent-final",required=True);q.add_argument("--parent-pre",required=True);q.add_argument("--constitution",required=True);q.add_argument("--build-dir",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=precommit)
 q=sp.add_parser("case");q.add_argument("--precommit",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=case_run)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
