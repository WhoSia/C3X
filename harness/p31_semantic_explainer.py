#!/usr/bin/env python3
import argparse,hashlib,json,os,re,subprocess
from collections import Counter,defaultdict
from pathlib import Path
import p27_age_morphism as p27
import p30_pressure_explanation as p30

STAGE="C3X 0.7.0-G9.4-P31"
ENGINES=("stockfish_19","berserk","ethereal")
MODES=("BASE","NO_CUTOFF","NO_MOVE","NO_EVAL","NO_CUTOFF_MOVE","NO_CUTOFF_EVAL","NO_MOVE_EVAL","NO_ALL")
SINGLES={"CUTOFF":"NO_CUTOFF","MOVE_ORDER":"NO_MOVE","EVAL":"NO_EVAL"}
COMPOUNDS={
 "CUTOFF+MOVE_ORDER":"NO_CUTOFF_MOVE",
 "CUTOFF+EVAL":"NO_CUTOFF_EVAL",
 "MOVE_ORDER+EVAL":"NO_MOVE_EVAL",
 "CUTOFF+MOVE_ORDER+EVAL":"NO_ALL",
}
HASH=1; PRIME=20000; DECOY=20000; ANCHOR=80000

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()

def load_constitution(p):
 x=json.loads(Path(p).read_text());c=x.get("constitution",{})
 if c.get("schema")!="c3x-lawgen-constitution-v7" or c.get("scientific_stage")!=STAGE or c.get("selective_results_consulted") is not False:raise SystemExit("P31_CONSTITUTION")
 return x

def load_p30_pre(p):
 x=json.loads(Path(p).read_text())
 if x.get("schema")!="c3x-p30-precommit-v1" or x.get("heldout_selective_consulted") is not False:raise SystemExit("P31_PARENT")
 return x

def protocol_for(e):return "stockfish_uci" if e=="stockfish_19" else "env"

def setup(path,protocol,mode,sem_path,tt_path):
 env=os.environ.copy()
 env["C3X_TT_USE_MODE"]=mode;env["C3X_TT_USE_TRACE"]=str(sem_path)
 env["C3X_TT_TRACE"]=str(tt_path);env["C3X_TT_GRAPH_SEQ"]="0"
 if protocol=="env":env["C3X_PSM_MODE"]="SHAM"
 else:env.pop("C3X_PSM_MODE",None)
 p=subprocess.Popen([path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,env=env)
 p.stdin.write("uci\n");p.stdin.flush();pre=p27.read_until(p,lambda x:x.strip()=="uciok")
 if not any(x.strip()=="uciok" for x in pre):raise RuntimeError("P31_UCI")
 opts="\n".join(pre);cmd=[]
 if protocol=="stockfish_uci":
  if not p27.has_option(opts,"C3X_TTReadMode") or not p27.has_option(opts,"C3X_Telemetry"):raise RuntimeError("P31_SF_SURFACE")
  cmd += ["setoption name C3X_TTReadMode value SHAM","setoption name C3X_Telemetry value true"]
 if p27.has_option(opts,"Threads"):cmd.append("setoption name Threads value 1")
 if p27.has_option(opts,"Hash"):cmd.append(f"setoption name Hash value {HASH}")
 if p27.has_option(opts,"SyzygyProbeLimit"):cmd.append("setoption name SyzygyProbeLimit value 0")
 if p27.has_option(opts,"UCI_ShowWDL"):cmd.append("setoption name UCI_ShowWDL value true")
 if p27.has_option(opts,"Clear Hash"):cmd.append("setoption name Clear Hash")
 cmd.append("isready")
 for c in cmd:p.stdin.write(c+"\n")
 p.stdin.flush();ready=p27.read_until(p,lambda x:x.strip()=="readyok")
 if not any(x.strip()=="readyok" for x in ready):raise RuntimeError("P31_READY")
 return p

def parse_semantic_trace(path):
 z=None;w=[]
 for line in Path(path).read_text().splitlines():
  x=line.split(",")
  if not x:continue
  if x[0]=="Z":
   if len(x)!=6:raise RuntimeError("P31_Z_WIDTH")
   z={"CUTOFF":int(x[1]),"MOVE_ORDER_SEED":int(x[2]),"EVAL_REUSE":int(x[3]),"TT_VALUE_AS_EVAL":int(x[4]),"PV_PROMOTION":int(x[5])}
  elif x[0]=="U":
   if len(x)!=13:raise RuntimeError(f"P31_U_WIDTH {len(x)}")
   _,scope,cls,key,ply,depth,alpha,beta,ttval,tteval,bound,move,payload=x
   w.append({"scope":scope,"class":cls,"key":key,"ply":int(ply),"depth":int(depth),"alpha":int(alpha),"beta":int(beta),
             "tt_value":int(ttval),"tt_eval":int(tteval),"bound":int(bound),"tt_move_raw":move,"payload":int(payload)})
 if z is None:raise RuntimeError("P31_SUMMARY_MISSING")
 if len(w)>128:raise RuntimeError("P31_WITNESS_OVERFLOW")
 return z,w

def run_history(path,protocol,cell,mode,work):
 sem=Path(work)/f"{mode}.semantic.csv";tt=Path(work)/f"{mode}.tt.csv";sem.parent.mkdir(parents=True,exist_ok=True)
 p=setup(path,protocol,mode,sem,tt)
 try:
  prev={}
  _,prev=p27.go(p,cell["fen"],PRIME,protocol)
  for d in cell["history"]["decoys"]:_,prev=p27.go(p,d["fen"],DECOY,protocol)
  semantic,tel=p27.go(p,cell["fen"],ANCHOR,protocol)
  if protocol=="env":tel=p27.tdelta(tel,prev)
  p.stdin.write("quit\n");p.stdin.flush()
  try:p.communicate(timeout=8)
  except subprocess.TimeoutExpired:p.kill();p.communicate()
 finally:
  if p.poll() is None:p.kill()
 counts,witness=parse_semantic_trace(sem)
 sem.unlink(missing_ok=True);tt.unlink(missing_ok=True)
 return {"semantic":semantic,"psm_telemetry":tel,"event_counts":counts,"low_ply_witnesses":witness}

def readout_delta(base,alt):
 b=base["semantic"];a=alt["semantic"]
 return {
  "bestmove_changed":a.get("bestmove")!=b.get("bestmove"),
  "pv_changed":a.get("pv")!=b.get("pv"),
  "score_changed":a.get("score")!=b.get("score"),
  "wdl_changed":a.get("wdl")!=b.get("wdl"),
  "depth_changed":a.get("depth")!=b.get("depth"),
  "nodes_changed":a.get("nodes")!=b.get("nodes"),
  "nodes_delta":int(a.get("nodes") or 0)-int(b.get("nodes") or 0),
  "alternative":{"bestmove":a.get("bestmove"),"score":a.get("score"),"wdl":a.get("wdl"),"depth":a.get("depth"),"seldepth":a.get("seldepth"),"nodes":a.get("nodes"),"pv":a.get("pv")}
 }

def transparent(a):
 parent=load_p30_pre(a.parent);cells=[c for c in parent["cells"] if c.get("graph_probe")]
 c=sorted(cells,key=lambda z:z["candidate_sha256"])[0];protocol=protocol_for(a.engine)
 d=Path(a.out).parent/"identity";r1=run_history(a.binary,protocol,c,"BASE",d/"a");r2=run_history(a.binary,protocol,c,"BASE",d/"b")
 keys=("bestmove","score","wdl","depth","pv")
 ok=all(r1["semantic"].get(k)==r2["semantic"].get(k) for k in keys)
 out={"schema":"c3x-p31-transparency-v1","scientific_stage":STAGE,"engine":a.engine,
      "candidate_sha256":c["candidate_sha256"],"semantic_a":{k:r1["semantic"].get(k) for k in keys},
      "semantic_b":{k:r2["semantic"].get(k) for k in keys},"event_counts_a":r1["event_counts"],"event_counts_b":r2["event_counts"],
      "verdict":"PASS" if ok else "FAIL"}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P31_TRANSPARENCY",a.engine,out["verdict"])

def precommit(a):
 par=load_p30_pre(a.parent);law=load_constitution(a.constitution);b=Path(a.build_dir)
 cells=sorted([c for c in par["cells"] if c.get("graph_probe")],key=lambda z:z["candidate_sha256"])
 if len(cells)!=16:raise SystemExit("P31_SUPPORT")
 variants={};identity={}
 for e in ENGINES:
  fs=list(b.rglob(f"c3x-p31-{e}"))
  ids=list(b.rglob(f"p31-transparency-{e}.json"))
  if len(fs)!=1 or len(ids)!=1:raise SystemExit(f"P31_BUILD_SET {e}")
  ix=json.loads(ids[0].read_text())
  if ix.get("verdict")!="PASS":raise SystemExit("P31_TRANSPARENCY_FAIL "+e)
  variants[e]={"sha256":sha_file(fs[0]),"protocol":protocol_for(e)}
  identity[e]={"receipt_sha256":ix["receipt_sha256"],"verdict":"PASS"}
 out={"schema":"c3x-p31-precommit-v1","scientific_stage":STAGE,"selective_results_consulted":False,
      "p30_precommit_receipt_sha256":par["receipt_sha256"],"lawgen_constitution_sha256":law["constitution_sha256"],
      "support":{"worlds":16,"hash_mib":HASH,"prime_nodes":PRIME,"decoy_nodes":DECOY,"decoy_count":3,"measurement_nodes":ANCHOR},
      "modes":list(MODES),"variants":variants,"transparency":identity,"cells":cells}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P31_PRECOMMIT",out["receipt_sha256"],len(cells))

def load_pre(p):
 x=json.loads(Path(p).read_text())
 if x.get("schema")!="c3x-p31-precommit-v1" or x.get("selective_results_consulted") is not False:raise SystemExit("P31_PRE")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P31_PRE_HASH")
 return x

def shard(a):
 pre=load_pre(a.precommit);e=a.engine
 if sha_file(a.binary)!=pre["variants"][e]["sha256"]:raise SystemExit("P31_BINARY")
 cells=[c for i,c in enumerate(pre["cells"]) if i%int(a.shards)==int(a.shard)]
 rows=[];root=Path(a.out).parent/"runs"
 for ci,c in enumerate(cells,1):
  rec={k:c[k] for k in ("candidate_sha256","material_seed_name","side_to_move","square","vertex","fen","states_by_budget")}
  rec["mode"]={}
  for mode in MODES:
   rec["mode"][mode]=run_history(a.binary,pre["variants"][e]["protocol"],c,mode,root/c["candidate_sha256"][:16]/mode)
  rows.append(rec);print("P31_SHARD",e,a.shard,ci,len(cells),flush=True)
 out={"schema":"c3x-p31-shard-v1","scientific_stage":STAGE,"engine":e,"shard":int(a.shard),"shards":int(a.shards),
      "precommit_receipt_sha256":pre["receipt_sha256"],"rows":rows};seal(out)
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

def collect(path):
 out={}
 for p in Path(path).rglob("*.json"):
  try:x=json.loads(p.read_text())
  except:continue
  if x.get("schema")!="c3x-p31-shard-v1":continue
  k=(x["engine"],x["shard"])
  if k in out:raise SystemExit("P31_DUP")
  out[k]=x
 exp={(e,s) for e in ENGINES for s in range(4)}
 if set(out)!=exp:raise SystemExit(f"P31_RESULT_SET {len(out)}/12")
 return out

def interaction_effect(single_a,single_b,compound,field):
 return (not single_a[field]) and (not single_b[field]) and compound[field]

def compile_certificate(e,r):
 base=r["mode"]["BASE"];deltas={m:readout_delta(base,r["mode"][m]) for m in MODES if m!="BASE"}
 single={
  "CUTOFF":deltas["NO_CUTOFF"],
  "MOVE_ORDER":deltas["NO_MOVE"],
  "EVAL":deltas["NO_EVAL"],
 }
 inter={}
 pairs=[("CUTOFF","MOVE_ORDER","NO_CUTOFF_MOVE"),("CUTOFF","EVAL","NO_CUTOFF_EVAL"),("MOVE_ORDER","EVAL","NO_MOVE_EVAL")]
 for a,b,m in pairs:
  inter[f"{a}+{b}"]={f:interaction_effect(single[a],single[b],deltas[m],f) for f in ("bestmove_changed","pv_changed","score_changed","nodes_changed")}
 triple=deltas["NO_ALL"]
 inter["CUTOFF+MOVE_ORDER+EVAL"]={f:triple[f] and not any(single[k][f] for k in single) for f in ("bestmove_changed","pv_changed","score_changed","nodes_changed")}
 deps={
  "root_move":[k for k,v in single.items() if v["bestmove_changed"]],
  "pv":[k for k,v in single.items() if v["pv_changed"]],
  "score":[k for k,v in single.items() if v["score_changed"]],
  "search_path":[k for k,v in single.items() if v["nodes_changed"] or v["depth_changed"]],
  "interaction_root_move":[k for k,v in inter.items() if v["bestmove_changed"]],
  "interaction_pv":[k for k,v in inter.items() if v["pv_changed"]],
 }
 counts=base["event_counts"]
 observed={
  "CUTOFF":counts["CUTOFF"]>0,
  "MOVE_ORDER":counts["MOVE_ORDER_SEED"]>0,
  "EVAL":counts["EVAL_REUSE"]>0 or counts["TT_VALUE_AS_EVAL"]>0,
  "PV_PROMOTION":counts["PV_PROMOTION"]>0
 }
 bm=base["semantic"].get("bestmove")
 clauses=[]
 clauses.append(f"{e} chose {bm} at the frozen 1 MiB, 80k-node measurement search.")
 clauses.append(f"Observed TT semantic uses: {counts['CUTOFF']} cutoff gates, {counts['MOVE_ORDER_SEED']} move-order seeds, {counts['EVAL_REUSE']} stored-eval reuses, {counts['TT_VALUE_AS_EVAL']} TT-value-as-eval uses, and {counts['PV_PROMOTION']} TT-move PV promotions.")
 if deps["root_move"]:
  clauses.append("Removing "+", ".join(deps["root_move"])+" individually changed the root best move; these classes are root-move dependencies in this replay.")
 elif deps["interaction_root_move"]:
  clauses.append("No single semantic class changed the root move, but the compound mask "+", ".join(deps["interaction_root_move"])+" did; the root dependence is interaction-only at this resolution.")
 elif deps["pv"]:
  clauses.append("The root move stayed stable under every single-class mask, while "+", ".join(deps["pv"])+" changed the principal variation; these uses affect the reported continuation, not the chosen move.")
 elif deps["search_path"]:
  clauses.append("The root move and principal causal claim stayed stable, but "+", ".join(deps["search_path"])+" changed the search path under the fixed node budget.")
 else:
  clauses.append("No single TT semantic class changed the frozen root move, PV, or scored search path enough to earn a causal-dependence claim at this resolution.")
 return {
  "schema":"c3x-p31-explanation-certificate-v1","engine":e,"candidate_sha256":r["candidate_sha256"],
  "material_seed_name":r["material_seed_name"],"state":r["states_by_budget"]["80000"]["mapped"],"square":r["square"],
  "baseline":{"semantic":base["semantic"],"event_counts":counts,"low_ply_witnesses":base["low_ply_witnesses"]},
  "counterfactual_deltas":deltas,"observed_classes":observed,"dependencies":deps,"interactions":inter,
  "explanation":" ".join(clauses),
  "authority":"semantic-class dependence under frozen measurement-only replay; not unique-event causation or human strategic intent"
 }

def adjudicate(a):
 pre=load_pre(a.precommit);by=collect(a.results);certs=[];seen=set()
 for e in ENGINES:
  rows=[]
  for s in range(4):rows.extend(by[(e,s)]["rows"])
  if len(rows)!=16:raise SystemExit(f"P31_ROWS {e}")
  for r in rows:
   k=(e,r["candidate_sha256"])
   if k in seen:raise SystemExit("P31_ROW_DUP")
   seen.add(k);certs.append(compile_certificate(e,r))
 summary={}
 for e in ENGINES:
  xs=[c for c in certs if c["engine"]==e]
  summary[e]={
   "certificates":len(xs),
   "root_move_dependency":{"CUTOFF":sum("CUTOFF" in c["dependencies"]["root_move"] for c in xs),
                           "MOVE_ORDER":sum("MOVE_ORDER" in c["dependencies"]["root_move"] for c in xs),
                           "EVAL":sum("EVAL" in c["dependencies"]["root_move"] for c in xs)},
   "pv_dependency":{"CUTOFF":sum("CUTOFF" in c["dependencies"]["pv"] for c in xs),
                    "MOVE_ORDER":sum("MOVE_ORDER" in c["dependencies"]["pv"] for c in xs),
                    "EVAL":sum("EVAL" in c["dependencies"]["pv"] for c in xs)},
   "interaction_root_move":sum(bool(c["dependencies"]["interaction_root_move"]) for c in xs),
   "all_single_root_stable":sum(not c["dependencies"]["root_move"] for c in xs),
   "baseline_event_totals":{k:sum(c["baseline"]["event_counts"][k] for c in xs) for k in ("CUTOFF","MOVE_ORDER_SEED","EVAL_REUSE","TT_VALUE_AS_EVAL","PV_PROMOTION")}
  }
 move_dep=sum(bool(c["dependencies"]["root_move"]) for c in certs)
 pv_dep=sum(bool(c["dependencies"]["pv"]) for c in certs)
 inter_dep=sum(bool(c["dependencies"]["interaction_root_move"]) for c in certs)
 verdict="FAITHFUL_TT_SEMANTIC_EXPLANATION_COMPILER_MATERIALIZED"
 if move_dep:verdict+="_WITH_ROOT_MOVE_DEPENDENCIES"
 elif inter_dep:verdict+="_WITH_INTERACTION_ONLY_ROOT_DEPENDENCIES"
 elif pv_dep:verdict+="_WITH_PV_LEVEL_DEPENDENCIES"
 else:verdict+="_ROOT_MOVE_STABLE_ON_FROZEN_SUPPORT"
 graph={"schema":"c3x-p31-attribution-graph-v1","nodes":[],"edges":[]}
 for c in certs:
  cid=f"{c['engine']}:{c['candidate_sha256'][:16]}"
  graph["nodes"].append({"id":cid,"kind":"ROOT_DECISION","bestmove":c["baseline"]["semantic"].get("bestmove")})
  for cls,obs in c["observed_classes"].items():
   if not obs:continue
   nid=f"{cid}:{cls}";graph["nodes"].append({"id":nid,"kind":"TT_SEMANTIC_CLASS","class":cls})
   graph["edges"].append({"source":nid,"target":cid,"kind":"OBSERVED_USE"})
   if cls in c["dependencies"]["root_move"]:graph["edges"].append({"source":nid,"target":cid,"kind":"SINGLE_CLASS_ROOT_MOVE_EFFECT"})
   elif cls in c["dependencies"]["pv"]:graph["edges"].append({"source":nid,"target":cid,"kind":"SINGLE_CLASS_PV_EFFECT"})
 out={"schema":"c3x-p31-adjudication-v1","scientific_stage":STAGE,"precommit_receipt_sha256":pre["receipt_sha256"],
      "summary":summary,"certificates":certs,"attribution_graph":graph,"verdict":verdict,
      "authority_ceiling":"16 inherited pressure-probe worlds; native age policy; 1 MiB; identical prime/decoy history; measurement-only class masks; class-level not unique-event causation"}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 md=["# P31 Faithful Move-Level Engine Explanations","",f"Verdict: \`{verdict}\`",""]
 for c in certs:
  md += [f"## {c['engine']} · {c['candidate_sha256'][:12]} · {c['state']} / {c['square']}",c["explanation"],""]
 Path(a.markdown).write_text("\n".join(md)+"\n")
 Path(a.graph).write_text(json.dumps(graph,indent=2,sort_keys=True)+"\n")
 print("P31_ADJ",verdict,"root_move",move_dep,"pv",pv_dep,"interaction",inter_dep)

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("transparency");q.add_argument("--engine",choices=ENGINES,required=True);q.add_argument("--binary",required=True);q.add_argument("--parent",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=transparent)
 q=sp.add_parser("precommit");q.add_argument("--parent",required=True);q.add_argument("--constitution",required=True);q.add_argument("--build-dir",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=precommit)
 q=sp.add_parser("shard");q.add_argument("--precommit",required=True);q.add_argument("--engine",choices=ENGINES,required=True);q.add_argument("--binary",required=True);q.add_argument("--shard",required=True);q.add_argument("--shards",default="4");q.add_argument("--out",required=True);q.set_defaults(fn=shard)
 q=sp.add_parser("adjudicate");q.add_argument("--precommit",required=True);q.add_argument("--results",required=True);q.add_argument("--out",required=True);q.add_argument("--markdown",required=True);q.add_argument("--graph",required=True);q.set_defaults(fn=adjudicate)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
