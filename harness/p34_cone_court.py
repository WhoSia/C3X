#!/usr/bin/env python3
import argparse,hashlib,json,os,subprocess
from collections import Counter,defaultdict
from pathlib import Path
import p27_age_morphism as p27
import p32_event_court as p32

STAGE="C3X 0.7.0-G9.4-P34"
LEVELS=(0,1,2,3)
MAX_ROUNDS=6
MAX_CONES=256
MAX_REPLAYS=128
MAX_FINAL_LOO=24
MAX_DRILL=12

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load_json(p):return json.loads(Path(p).read_text())
def sem(s):return {k:s.get(k) for k in ("bestmove","score","wdl","depth","seldepth","nodes","pv")}

def load_support(p):
 x=load_json(p)
 if x.get("schema")!="c3x-p34-parent-support-v1" or x.get("primary_case_count")!=3 or x.get("p34_selective_outcomes_consulted") is not False:raise SystemExit("P34_SUPPORT")
 return x
def load_constitution(p):
 x=load_json(p);c=x.get("constitution",{})
 if c.get("schema")!="c3x-lawgen-constitution-v10" or c.get("p34_selective_results_consulted") is not False:raise SystemExit("P34_CONSTITUTION")
 return x
def load_p33_final(p):
 x=load_json(p)
 if x.get("schema")!="c3x-p33-adjudication-v1" or x.get("scientific_stage")!="C3X 0.7.0-G9.4-P33":raise SystemExit("P34_PARENT_FINAL")
 return x
def load_p33_pre(p):
 x=load_json(p)
 if x.get("schema")!="c3x-p33-precommit-v1" or x.get("p33_selective_results_consulted") is not False:raise SystemExit("P34_PARENT_PRE")
 return x
def load_pre(p):
 x=load_json(p)
 if x.get("schema")!="c3x-p34-precommit-v1" or x.get("p34_selective_results_consulted") is not False:raise SystemExit("P34_PRE")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P34_PRE_HASH")
 return x

def p33_cases(x):return {z["case"]["case_id"]:z["case"] for z in x["certificates"]}

def precommit(a):
 sup=load_support(a.support);pf=load_p33_final(a.parent_final);pp=load_p33_pre(a.parent_pre);law=load_constitution(a.constitution)
 fc=p33_cases(pf);pc={x["case_id"]:x for x in pp["cases"]};variants={}
 for e in ("stockfish_19","berserk","ethereal"):
  fs=list(Path(a.build_dir).rglob(f"c3x-p34-{e}"));ids=list(Path(a.build_dir).rglob(f"p34-transparency-{e}.json"))
  if len(fs)!=1 or len(ids)!=1:raise SystemExit(f"P34_BUILD_SET {e}")
  ix=load_json(ids[0])
  if ix.get("verdict")!="PASS":raise SystemExit("P34_TRANSPARENCY_FAIL "+e)
  variants[e]={"sha256":p32.sha_file(fs[0]),"protocol":p32.protocol_for(e),"transparency_receipt":ix["receipt_sha256"]}
 cases=[]
 for z in sup["primary_cases"]:
  cid=z["case_id"]
  if cid not in fc or cid not in pc:raise SystemExit("P34_CASESET "+cid)
  f=fc[cid];q=pc[cid]
  if f["status"]!=z["parent_status"]:raise SystemExit("P34_PARENT_STATUS "+cid)
  cases.append({"case_id":cid,"engine":q["engine"],"family":q["family"],"role":z["role"],"candidate_sha256":q["candidate_sha256"],
    "cell":q["cell"],"frontier":f["frontier"],"baseline":f["baseline"],"parent_seed_removal":f["parent_seed_removal"],
    "parent_status":f["status"],"parent_universe":f.get("universe",{})})
 out={"schema":"c3x-p34-precommit-v1","scientific_stage":STAGE,"p34_selective_results_consulted":False,
  "parent_p33_run":36192022350,"parent_final_receipt_sha256":pf["receipt_sha256"],"parent_precommit_receipt_sha256":pp["receipt_sha256"],
  "lawgen_constitution_sha256":law["constitution_sha256"],"support_sha256":digest(sup),"variants":variants,"cases":cases,
  "execution":{"levels":["Q0","Q1","Q2","Q3"],"max_refinement_rounds_per_level":MAX_ROUNDS,"max_observed_cones_per_level":MAX_CONES,
   "max_replays_per_case_level":MAX_REPLAYS,"max_final_cone_set_for_leave_one_out":MAX_FINAL_LOO,
   "max_exact_members_per_selected_cone":MAX_DRILL,"hash_mib":1,"threads":1,"prime_nodes":20000,"decoy_nodes":20000,"decoy_count":3,"measurement_nodes":80000}}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P34_PRECOMMIT",out["receipt_sha256"],len(cases))

def verify_binary(pre,case,path):
 v=pre["variants"][case["engine"]]
 if p32.sha_file(path)!=v["sha256"]:raise SystemExit("P34_BINARY")
 return v["protocol"]

def transparency(a):
 sup=load_support(a.support);load_p33_final(a.parent_final);pp=load_p33_pre(a.parent_pre)
 pc={x["case_id"]:x for x in pp["cases"]};rows=[];bad=[]
 requested=[z["case_id"] for z in sup["primary_cases"] if z["engine"]==a.engine]
 if not requested:
  fallbacks=sorted(x["case_id"] for x in pp["cases"] if x["engine"]==a.engine)
  if not fallbacks:raise SystemExit("P34_TRANSPARENCY_NO_CASE "+a.engine)
  requested=[fallbacks[0]]
 for cid in requested[:1]:
  if cid not in pc:raise SystemExit("P34_TRANSPARENCY_CASE "+cid)
  q=pc[cid];frontier=q.get("selected_frontier")
  if frontier is None:frontier=8
  r=run34(a.binary,p32.protocol_for(a.engine),q["cell"],q["family"],frontier,None,"CATALOG",3,None,
    Path(a.out).parent/"identity"/cid.replace(":","_"))
  got=sem(r["semantic"]);exp=q["baseline"];keys=("bestmove","score","depth","pv")
  ok=all(got.get(k)==exp.get(k) for k in keys)
  rows.append({"case_id":cid,"match":ok,"expected":{k:exp.get(k) for k in keys},"got":{k:got.get(k) for k in keys},
    "catalog_events":r["cone"]["summary"]["events"]})
  if not ok:bad.append(cid)
 out={"schema":"c3x-p34-transparency-v1","scientific_stage":STAGE,"engine":a.engine,"rows":rows,"mismatches":bad,
  "verdict":"PASS" if not bad else "FAIL","p34_selective_results_consulted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P34_TRANSPARENCY",a.engine,out["verdict"],len(rows))

def write_cones(path,tuples):
 with open(path,"w") as f:
  for t in tuples:f.write("\t".join(str(x) for x in t)+"\n")

def setup34(path,protocol,p32_mode,p34_mode,family,frontier,seed_file,set_file,level,p32_trace,p34_trace,tt_file):
 env=os.environ.copy();env["C3X_TT_USE_MODE"]="BASE";env["C3X_P32_MODE"]=p32_mode;env["C3X_P32_FAMILY"]=family
 env["C3X_P32_FRONTIER"]=str(frontier);env["C3X_P32_TRACE"]=str(p32_trace)
 env["C3X_P34_MODE"]=p34_mode;env["C3X_P34_LEVEL"]=str(level);env["C3X_P34_TRACE"]=str(p34_trace)
 env["C3X_TT_TRACE"]=str(tt_file);env["C3X_TT_GRAPH_SEQ"]="0"
 if seed_file:env["C3X_P32_TARGET_FILE"]=str(seed_file)
 else:env.pop("C3X_P32_TARGET_FILE",None)
 if set_file:env["C3X_P34_SET_FILE"]=str(set_file)
 else:env.pop("C3X_P34_SET_FILE",None)
 if protocol=="env":env["C3X_PSM_MODE"]="SHAM"
 else:env.pop("C3X_PSM_MODE",None)
 p=subprocess.Popen([path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,env=env)
 p.stdin.write("uci\n");p.stdin.flush();pre=p27.read_until(p,lambda x:x.strip()=="uciok")
 if not any(x.strip()=="uciok" for x in pre):raise RuntimeError("P34_UCI")
 opts="\n".join(pre);cmd=[]
 if protocol=="stockfish_uci":
  if not p27.has_option(opts,"C3X_TTReadMode") or not p27.has_option(opts,"C3X_Telemetry"):raise RuntimeError("P34_SF_SURFACE")
  cmd += ["setoption name C3X_TTReadMode value SHAM","setoption name C3X_Telemetry value true"]
 if p27.has_option(opts,"Threads"):cmd.append("setoption name Threads value 1")
 if p27.has_option(opts,"Hash"):cmd.append("setoption name Hash value 1")
 if p27.has_option(opts,"SyzygyProbeLimit"):cmd.append("setoption name SyzygyProbeLimit value 0")
 if p27.has_option(opts,"UCI_ShowWDL"):cmd.append("setoption name UCI_ShowWDL value true")
 if p27.has_option(opts,"Clear Hash"):cmd.append("setoption name Clear Hash")
 cmd.append("isready")
 for c in cmd:p.stdin.write(c+"\n")
 p.stdin.flush();ready=p27.read_until(p,lambda x:x.strip()=="readyok")
 if not any(x.strip()=="readyok" for x in ready):raise RuntimeError("P34_READY")
 return p

def parse34(path,p32trace):
 rows=[];summary=None
 for line in Path(path).read_text().splitlines():
  z=line.split(",")
  if z[0]=="C":
   if len(z)!=23:raise RuntimeError(f"P34_C_WIDTH {len(z)}")
   _,level,scope,cls,pb,bound,payloadb,db,moveb,rel,selected,seed,extra,key,ply,depth,move,payload,alpha,beta,ttval,tteval,bound2=z
   if int(bound)!=int(bound2):raise RuntimeError("P34_BOUND_MISMATCH")
   rows.append({"level":int(level),"scope_code":int(scope),"class_id":int(cls),"ply_bucket":int(pb),"bound":int(bound),
    "payload_bucket":int(payloadb),"depth_bucket":int(db),"move_presence":int(moveb),"window_relation":int(rel),
    "selected":int(selected),"seed_blocked":int(seed),"extra_blocked":int(extra),"key":key,"ply":int(ply),"depth":int(depth),
    "tt_move":int(move),"payload":int(payload),"alpha":int(alpha),"beta":int(beta),"tt_value":int(ttval),"tt_eval":int(tteval)})
  elif z[0]=="S34":
   if len(z)!=6:raise RuntimeError("P34_S_WIDTH")
   summary={"events":int(z[1]),"seed_blocked":int(z[2]),"extra_blocked":int(z[3]),"level":int(z[4]),"selected_cones":int(z[5])}
 if summary is None:raise RuntimeError("P34_TRACE_SUMMARY")
 pe=p32trace["events"]
 if len(rows)!=len(pe):raise RuntimeError(f"P34_TRACE_ALIGNMENT {len(rows)} {len(pe)}")
 for i,(a,b) in enumerate(zip(rows,pe)):
  if a["class_id"]!=b["class_id"] or a["ply"]!=b["ply"] or a["depth"]!=b["depth"] or a["bound"]!=b["bound"] or a["tt_move"]!=b["tt_move"] or a["payload"]!=b["payload"]:
   raise RuntimeError(f"P34_TRACE_RAW_ALIGNMENT {i}")
  a["ordinal"]=i;a["scope"]=b["scope"];a["class"]=b["class"];a["address_id"]=b["address_id"];a["address"]=b["address"]
 return {"events":rows,"summary":summary}

def cone_tuple(e):
 return (e["scope_code"],e["class_id"],e["ply_bucket"],e["bound"],e["payload_bucket"],e["depth_bucket"],e["move_presence"],e["window_relation"])
def qid_from_tuple(t,level):return "Q%d:%s"%(level,":".join(str(x) for x in t[:(3 if level==0 else 5 if level==1 else 7 if level==2 else 8)]))
def qid(e,level):return qid_from_tuple(cone_tuple(e),level)
def qtuple_for_id(events,level,target):
 for e in events:
  if qid(e,level)==target:return cone_tuple(e)
 raise KeyError(target)

def verify_cones(coner,trace,level,root,label):
 root=Path(root);root.mkdir(parents=True,exist_ok=True);ip=root/(label+"-cone-in.json");op=root/(label+"-cone-out.json")
 ev=[]
 for e in trace["events"]:
  ev.append({"scope":e["scope"],"class_id":e["class_id"],"ply":e["ply"],"depth":e["depth"],"bound":e["bound"],"payload":e["payload"],
   "tt_move":e["tt_move"],"alpha":e["alpha"],"beta":e["beta"],"tt_value":e["tt_value"],
   "declared":list(cone_tuple(e)),"address_id":e["address_id"],"ordinal":e["ordinal"]})
 ip.write_text(json.dumps({"level":level,"events":ev},sort_keys=True)+"\n")
 subprocess.run([coner,str(ip),str(op)],check=True)
 return load_json(op)

def run34(binary,protocol,cell,family,frontier,seed_addresses,p34_mode,level,cone_tuples,work):
 work=Path(work);work.mkdir(parents=True,exist_ok=True)
 p32tr=work/"p32.csv";p34tr=work/"p34.csv";tt=work/"tt.csv";seed=work/"seed.tsv";sets=work/"cones.tsv"
 if seed_addresses is not None:p32.write_targets(seed,seed_addresses)
 if cone_tuples is not None:write_cones(sets,cone_tuples)
 p32mode="REMOVE_SET" if seed_addresses is not None else "CATALOG"
 p=setup34(binary,protocol,p32mode,p34_mode,family,frontier,seed if seed_addresses is not None else None,sets if cone_tuples is not None else None,
   level,p32tr,p34tr,tt)
 try:
  p27.go(p,cell["fen"],20000,protocol)
  for d in cell["history"]["decoys"]:p27.go(p,d["fen"],20000,protocol)
  sm,_=p27.go(p,cell["fen"],80000,protocol)
  try:p.stdin.write("quit\n");p.stdin.flush()
  except:pass
  try:p.communicate(timeout=8)
  except subprocess.TimeoutExpired:p.kill();p.communicate()
 finally:
  if p.poll() is None:p.kill()
 pt=p32.parse_trace(p32tr);ct=parse34(p34tr,pt)
 for x in (p32tr,p34tr,tt,seed,sets):x.unlink(missing_ok=True)
 return {"semantic":sm,"p32":pt,"cone":ct}

def frontier_addresses(trace,frontier):
 out=[]
 for e in trace["events"]:
  if e["ply"]<=frontier:
   z=dict(e["address"]);z["address_id"]=e["address_id"];out.append(z)
 return out

class Refine(Exception):pass
class Budget(Exception):pass

def case_run(a):
 pre=load_pre(a.precommit);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if case is None:raise SystemExit("P34_CASE")
 protocol=verify_binary(pre,case,a.binary);frontier=case["frontier"];root=Path(a.out).parent/"runs";root.mkdir(parents=True,exist_ok=True)
 base=run34(a.binary,protocol,case["cell"],case["family"],frontier,None,"CATALOG",3,None,root/"000-base")
 if base["semantic"]["bestmove"]!=case["baseline"]["bestmove"]:raise SystemExit("P34_BASE_DRIFT")
 seed=frontier_addresses(base["p32"],frontier)
 if len({x["address_id"] for x in seed})!=len(seed):raise SystemExit("P34_SEED_DUP")
 parent=run34(a.binary,protocol,case["cell"],case["family"],frontier,seed,"SEED_ONLY",3,None,root/"001-parent")
 if parent["semantic"]["bestmove"]!=case["parent_seed_removal"]["bestmove"]:raise SystemExit("P34_PARENT_DRIFT")
 base_verify=verify_cones(a.coner,base["cone"],3,root/"verify","base")
 parent_verify=verify_cones(a.coner,parent["cone"],3,root/"verify","parent")
 levels=[];selected=None
 for level in LEVELS:
  replay_count=0;rounds=0;universe={}
  parent_events=[e for e in parent["cone"]["events"] if e["ply"]<=frontier and not e["seed_blocked"]]
  for e in parent_events:universe[qid(e,level)]=cone_tuple(e)
  cache={}
  def replay(mode,ids,label,allow_refine=True,seed_override=None):
   nonlocal replay_count
   ids=tuple(sorted(ids));key=(mode,ids,tuple(x["address_id"] for x in (seed_override if seed_override is not None else seed)))
   if key in cache:return cache[key]
   if replay_count>=MAX_REPLAYS:raise Budget()
   replay_count+=1
   tuples=[universe[i] for i in ids] if ids else []
   r=run34(a.binary,protocol,case["cell"],case["family"],frontier,seed_override if seed_override is not None else seed,mode,level,tuples,
     root/f"Q{level}"/f"{replay_count:03d}-{label}")
   cache[key]=r
   new=[]
   for e in r["cone"]["events"]:
    if e["ply"]<=frontier and not e["seed_blocked"]:
     k=qid(e,level)
     if k not in universe:universe[k]=cone_tuple(e);new.append(k)
   if len(universe)>MAX_CONES:raise Budget()
   if new and allow_refine:raise Refine()
   return r
  status=None;rem_ids=[];keep_ids=[];rem_cert=False;keep_cert=False;full=None;rem=None;keep=None;loo_rem={};loo_keep={};failure=[]
  try:
   while rounds<MAX_ROUNDS:
    rounds+=1
    try:
     full=replay("REMOVE_SET",list(universe),f"closure-{rounds}")
     all_dynamic=replay("REMOVE_ALL",[],f"all-{rounds}")
     if full["semantic"]["bestmove"]!=all_dynamic["semantic"]["bestmove"]:
      status="DYNAMIC_ALL_PARITY_FAIL";failure.append(status);break
     if full["semantic"]["bestmove"]==parent["semantic"]["bestmove"]:
      status="NO_CONDITIONAL_ROOT_EFFECT";failure.append(status);break
     def pred_rem(ids):return replay("REMOVE_SET",ids,"dd-rem")["semantic"]["bestmove"]!=parent["semantic"]["bestmove"]
     rem_ids=p32.ddmin(list(universe),pred_rem);rem_ids,rem_cert,loo_rem=p32.stabilize_minimal(rem_ids,pred_rem,MAX_FINAL_LOO)
     rem=replay("REMOVE_SET",rem_ids,"minimal-rem")
     def pred_keep(ids):return replay("KEEP_SET",ids,"dd-keep")["semantic"]["bestmove"]==parent["semantic"]["bestmove"]
     if pred_keep(list(universe)):
      keep_ids=p32.ddmin(list(universe),pred_keep);keep_ids,keep_cert,loo_keep=p32.stabilize_minimal(keep_ids,pred_keep,MAX_FINAL_LOO)
      keep=replay("KEEP_SET",keep_ids,"minimal-keep")
     else:failure.append("KEEP_ALL_BOUNDARY_FAIL")
     status="CAUSAL_SETS_CERTIFIED" if rem_cert and keep_cert else "CAUSAL_SET_MINIMALITY_HOLD"
     break
    except Refine:
     if rounds>=MAX_ROUNDS:status="QUOTIENT_REFINEMENT_LIMIT_HOLD";failure.append(status);break
     continue
  except Budget:
   status="QUOTIENT_BUDGET_HOLD";failure.append(status)

  drill={"status":"NOT_RUN","cones":{},"collision":False,"large_class_hold":False,"exact_expansion_parity":False}
  if rem_cert:
   parent_by_q=defaultdict(list)
   for pe,ce in zip(parent["p32"]["events"],parent["cone"]["events"]):
    if pe["ply"]<=frontier and not ce["seed_blocked"]:parent_by_q[qid(ce,level)].append(pe)
   singleton_bestmoves=set();large=False;collision=False
   union_members=[]
   for q in rem_ids:
    members=parent_by_q.get(q,[]);info={"parent_trace_members":len(members),"singleton_probes":[]}
    union_members.extend(members)
    if len(members)>MAX_DRILL:
     large=True;info["status"]="DRILLDOWN_SIZE_HOLD"
    else:
     sig=set()
     for j,m in enumerate(members):
      extra=dict(m["address"]);extra["address_id"]=m["address_id"]
      rr=run34(a.binary,protocol,case["cell"],case["family"],frontier,seed+[extra],"SEED_ONLY",level,None,
        root/f"Q{level}"/"drill"/f"{q.replace(':','_')}-{j}")
      bm=rr["semantic"]["bestmove"];sig.add(bm);singleton_bestmoves.add(bm)
      info["singleton_probes"].append({"address_id":m["address_id"],"bestmove":bm,"changes_parent":bm!=parent["semantic"]["bestmove"]})
     info["singleton_signature_count"]=len(sig);info["status"]="COLLISION" if len(sig)>1 else "NO_SINGLETON_COLLISION"
     if len(sig)>1:collision=True
    drill["cones"][q]=info
   uniq=[];seen=set()
   for m in union_members:
    if m["address_id"] not in seen:
     seen.add(m["address_id"]);z=dict(m["address"]);z["address_id"]=m["address_id"];uniq.append(z)
   expansion=run34(a.binary,protocol,case["cell"],case["family"],frontier,seed+uniq,"SEED_ONLY",level,None,root/f"Q{level}"/"drill"/"exact-expansion")
   parity=bool(rem and expansion["semantic"]["bestmove"]==rem["semantic"]["bestmove"])
   drill.update({"status":"PASS" if (not collision and not large and parity) else "HOLD","collision":collision,"large_class_hold":large,
     "exact_expansion_member_count":len(uniq),"exact_expansion_bestmove":expansion["semantic"]["bestmove"],
     "dynamic_quotient_bestmove":rem["semantic"]["bestmove"] if rem else None,"exact_expansion_parity":parity})
   if collision:failure.append("QUOTIENT_COLLISION")
   if large:failure.append("DRILLDOWN_SIZE_HOLD")
   if not parity:failure.append("LOCAL_EXACT_EXPANSION_PARITY_FAIL")

  fullv=verify_cones(a.coner,full["cone"],level,root/"verify",f"Q{level}-full") if full else None
  remv=verify_cones(a.coner,rem["cone"],level,root/"verify",f"Q{level}-rem") if rem else None
  keepv=verify_cones(a.coner,keep["cone"],level,root/"verify",f"Q{level}-keep") if keep else None
  pass_all=bool(status=="CAUSAL_SETS_CERTIFIED" and drill["status"]=="PASS")
  lr={"level":f"Q{level}","status":"QUOTIENT_CAUSAL_CLOSURE_EXACT_DRILLDOWN_PRESERVED" if pass_all else status,
    "closure_rounds":rounds,"replays_used":replay_count,"closed_cones":len(universe),"cone_ids":sorted(universe),
    "full_remove":sem(full["semantic"]) if full else None,
    "minimal_remove":{"certified":rem_cert,"cone_ids":rem_ids,"minimality":loo_rem,"semantic":sem(rem["semantic"]) if rem else None},
    "minimal_keep":{"certified":keep_cert,"cone_ids":keep_ids,"minimality":loo_keep,"semantic":sem(keep["semantic"]) if keep else None},
    "drilldown":drill,"failures":failure,
    "independent_verification":{"full":fullv,"minimal_remove":remv,"minimal_keep":keepv}}
  levels.append(lr)
  if pass_all:
   selected=f"Q{level}";break

 out={"schema":"c3x-p34-case-v1","scientific_stage":STAGE,"case_id":case["case_id"],"engine":case["engine"],"family":case["family"],"role":case["role"],
  "frontier":frontier,"baseline":sem(base["semantic"]),"parent_seed_removal":sem(parent["semantic"]),"seed_exact_addresses":len(seed),
  "base_cone_verification":base_verify,"parent_cone_verification":parent_verify,"levels":levels,"selected_level":selected,
  "status":"QUOTIENT_CAUSAL_CLOSURE_EXACT_DRILLDOWN_PRESERVED" if selected else "BOUNDED_QUOTIENT_LATTICE_DIVERGENCE",
  "authority_ceiling":"first passing level in frozen Q0→Q3 lattice only; exact-member collision probes are parent-trace-local; no universal causal abstraction claim"}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P34_CASE",a.case_id,out["status"],"selected",selected,"levels",len(levels))

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("transparency");q.add_argument("--engine",choices=("stockfish_19","berserk","ethereal"),required=True);q.add_argument("--binary",required=True);q.add_argument("--support",required=True);q.add_argument("--parent-final",required=True);q.add_argument("--parent-pre",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=transparency)
 q=sp.add_parser("precommit");q.add_argument("--support",required=True);q.add_argument("--parent-final",required=True);q.add_argument("--parent-pre",required=True);q.add_argument("--constitution",required=True);q.add_argument("--build-dir",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=precommit)
 q=sp.add_parser("case");q.add_argument("--precommit",required=True);q.add_argument("--case-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--coner",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=case_run)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
