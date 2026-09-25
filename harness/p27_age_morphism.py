#!/usr/bin/env python3
"""C3X G9.4-P27: history-conditioned age-on-hit causal morphism court."""
import argparse,hashlib,json,os,re,subprocess
from collections import defaultdict
from pathlib import Path
import p20_transport as p20
import p26_product_field as p26

STAGE="C3X 0.7.0-G9.4-P27"
ENGINES=("stockfish_19","berserk","ethereal")
DONORS=("stockfish_19","berserk")
HELDOUT="ethereal"
POLICIES=("OFF","ON")
MODES=("SHAM","MASK_MAIN","MASK_QSEARCH","MASK_MAIN_QSEARCH","MASK_ALL")
ANCHOR=80000
PRIME=20000
DECOY=20000
NDECOY=3

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()

def read_until(p,pred,limit=200000):
 out=[]
 while len(out)<limit:
  x=p.stdout.readline()
  if x=="":break
  x=x.rstrip("\n");out.append(x)
  if pred(x):break
 return out

def has_option(text,name):
 return re.search(r"^option name "+re.escape(name)+r"(?: |$)",text,re.M) is not None

def setup(path,protocol,mode):
 env=os.environ.copy()
 if protocol=="env":env["C3X_PSM_MODE"]=mode
 else:env.pop("C3X_PSM_MODE",None)
 p=subprocess.Popen([path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,env=env)
 p.stdin.write("uci\n");p.stdin.flush()
 pre=read_until(p,lambda x:x.strip()=="uciok")
 if not any(x.strip()=="uciok" for x in pre):raise RuntimeError("UCI_OK")
 opts="\n".join(pre);cmd=[]
 if protocol=="stockfish_uci":
  if not has_option(opts,"C3X_TTReadMode") or not has_option(opts,"C3X_Telemetry"):raise RuntimeError("C3X_SURFACE")
  cmd += [f"setoption name C3X_TTReadMode value {mode}","setoption name C3X_Telemetry value true"]
 if has_option(opts,"Threads"):cmd.append("setoption name Threads value 1")
 if has_option(opts,"Hash"):cmd.append("setoption name Hash value 64")
 if has_option(opts,"SyzygyProbeLimit"):cmd.append("setoption name SyzygyProbeLimit value 0")
 if has_option(opts,"UCI_ShowWDL"):cmd.append("setoption name UCI_ShowWDL value true")
 if has_option(opts,"Clear Hash"):cmd.append("setoption name Clear Hash")
 cmd.append("isready")
 for c in cmd:p.stdin.write(c+"\n")
 p.stdin.flush();ready=read_until(p,lambda x:x.strip()=="readyok")
 if not any(x.strip()=="readyok" for x in ready):raise RuntimeError("READY_OK")
 return p,opts

def parse_tel(lines,protocol):
 prefix="info string c3x_psm_v1 " if protocol=="env" else "info string c3x_ttread_v1 "
 s=next((x for x in reversed(lines) if x.startswith(prefix)),None)
 if not s:raise RuntimeError("TELEMETRY")
 d={}
 for z in s.split()[3:]:
  if "=" in z:
   k,v=z.split("=",1)
   try:d[k]=int(v)
   except:d[k]=v
 return d

def parse_sem(lines):
 best=next((x for x in reversed(lines) if x.startswith("bestmove ")),None)
 infos=[x for x in lines if x.startswith("info ") and " score " in x and " pv " in x]
 if not best or not infos:raise RuntimeError("SEARCH_RECEIPT")
 final=infos[-1]
 def g(pat):
  m=re.search(pat,final);return m.group(1) if m else None
 bt=best.split()
 return {"bestmove":bt[1] if len(bt)>1 else None,"score":g(r"\bscore ((?:cp|mate) -?\d+)"),
  "wdl":g(r"\bwdl (\d+ \d+ \d+)"),"depth":int(g(r"\bdepth (\d+)") or 0),
  "seldepth":int(g(r"\bseldepth (\d+)") or 0),"nodes":int(g(r"\bnodes (\d+)") or 0),"pv":g(r"\bpv (.+)$")}

def go(p,fen,nodes,protocol):
 p.stdin.write(f"position fen {fen}\ngo nodes {nodes}\n");p.stdin.flush()
 lines=read_until(p,lambda x:x.startswith("bestmove "))
 return parse_sem(lines),parse_tel(lines,protocol)

def tdelta(now,prev):
 out={}
 for k,v in now.items():
  if isinstance(v,int) and isinstance(prev.get(k),int):out[k]=v-prev[k]
  else:out[k]=v
 return out

def history_search(path,protocol,mode,target,decoys):
 p,_=setup(path,protocol,mode)
 try:
  prev={}
  _,prev=go(p,target,PRIME,protocol)
  for fen in decoys:_,prev=go(p,fen,DECOY,protocol)
  sem,tel=go(p,target,ANCHOR,protocol)
  if protocol=="env":tel=tdelta(tel,prev)
  main=int(tel.get("hits_main",0) if protocol=="env" else tel.get("raw_hits_main",0))
  q=int(tel.get("hits_qsearch",0) if protocol=="env" else tel.get("raw_hits_qsearch",0))
  return {"semantic":sem,"engagement":{"MAIN":main,"QSEARCH":q,"floor":min(main,q),"passed":main>0 and q>0},"telemetry":tel}
 finally:
  p.terminate()
  try:p.communicate(timeout=3)
  except subprocess.TimeoutExpired:p.kill();p.communicate()

def simple_search(path,fen,nodes):
 p=subprocess.Popen([path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
 try:
  p.stdin.write("uci\n");p.stdin.flush();pre=read_until(p,lambda x:x.strip()=="uciok")
  if not any(x.strip()=="uciok" for x in pre):raise RuntimeError("BASE_UCI")
  opts="\n".join(pre);cmd=[]
  if has_option(opts,"Threads"):cmd.append("setoption name Threads value 1")
  if has_option(opts,"Hash"):cmd.append("setoption name Hash value 64")
  if has_option(opts,"SyzygyProbeLimit"):cmd.append("setoption name SyzygyProbeLimit value 0")
  if has_option(opts,"UCI_ShowWDL"):cmd.append("setoption name UCI_ShowWDL value true")
  if has_option(opts,"Clear Hash"):cmd.append("setoption name Clear Hash")
  cmd += ["isready",f"position fen {fen}",f"go nodes {nodes}"]
  for c in cmd:p.stdin.write(c+"\n")
  p.stdin.flush();lines=pre+read_until(p,lambda x:x.startswith("bestmove "))
  if not any(x.strip()=="readyok" for x in lines):raise RuntimeError("BASE_READY")
  return parse_sem(lines)
 finally:
  p.terminate()
  try:p.communicate(timeout=3)
  except subprocess.TimeoutExpired:p.kill();p.communicate()

def identity(a):
 parent=p26.load_pre(a.parent)
 cells=sorted(parent["cells"],key=lambda x:x["candidate_sha256"])[:8]
 bad=[];rows=[]
 spec={"protocol":a.protocol,"path":a.native}
 for c in cells:
  base=simple_search(a.baseline,c["fen"],30000)
  inst=p20.run_search(spec,c["fen"],"SHAM",30000)["semantic"]
  keys=("bestmove","score","depth","pv")
  ok=all(base.get(k)==inst.get(k) for k in keys)
  rows.append({"candidate_sha256":c["candidate_sha256"],"match":ok,"baseline":{k:base.get(k) for k in keys},"native_variant":{k:inst.get(k) for k in keys}})
  if not ok:bad.append(c["candidate_sha256"])
 out={"schema":"c3x-p27-native-equivalence-v1","scientific_stage":STAGE,"engine":a.engine,
  "native_policy":{"stockfish_19":"OFF","berserk":"OFF","ethereal":"ON"}[a.engine],
  "nodes":30000,"cells":len(cells),"mismatches":bad,"verdict":"PASS" if not bad else "FAIL","rows":rows}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P27_IDENTITY",a.engine,out["verdict"],len(bad))

def load_lawgen(p):
 x=json.loads(Path(p).read_text());c=x.get("constitution",{})
 if c.get("schema")!="c3x-lawgen-constitution-v3" or c.get("scientific_stage")!=STAGE or c.get("selective_outcomes_consulted") is not False:raise SystemExit("P27_LAWGEN")
 return x

def pick_cells(parent):
 groups=defaultdict(list)
 for c in parent["cells"]:
  s=c["states_by_budget"][str(ANCHOR)]["mapped"]
  groups[(c["material_seed_name"],c["side_to_move"],s)].append(c)
 chosen=[]
 for k,v in groups.items():
  v=sorted(v,key=lambda x:x["candidate_sha256"])
  if len(v)<1:raise SystemExit("P27_SUPPORT")
  chosen.append(v[0])
 if len(chosen)!=128:raise SystemExit(f"P27_CELL_N {len(chosen)}")
 return sorted(chosen,key=lambda x:x["candidate_sha256"])

def attach_history(chosen,parent):
 universe=sorted(parent["cells"],key=lambda x:x["candidate_sha256"]);n=len(universe);out=[]
 for c in chosen:
  start=int(c["candidate_sha256"][:8],16)%n;ds=[]
  j=1
  while len(ds)<NDECOY and j<n+1:
   d=universe[(start+j)%n];j+=1
   if d["candidate_sha256"]==c["candidate_sha256"] or d["material_seed_name"]==c["material_seed_name"]:continue
   ds.append({"candidate_sha256":d["candidate_sha256"],"fen":d["fen"],"family":d["material_seed_name"]})
  if len(ds)!=NDECOY:raise SystemExit("P27_DECOY")
  z={k:c[k] for k in ("candidate_sha256","material_seed_name","side_to_move","square","vertex","fen","world","states_by_budget")}
  z["history"]={"prime_fen":c["fen"],"decoys":ds}
  out.append(z)
 return out

def precommit(a):
 parent=p26.load_pre(a.parent);law=load_lawgen(a.constitution)
 builds=Path(a.build_dir);variants={};identity={}
 protocol={"stockfish_19":"stockfish_uci","berserk":"env","ethereal":"env"}
 for e in ENGINES:
  idfiles=list(builds.rglob(f"p27-identity-{e}.json"))
  if len(idfiles)!=1:raise SystemExit("P27_ID_FILE "+e)
  ix=json.loads(idfiles[0].read_text())
  if ix.get("verdict")!="PASS":raise SystemExit("P27_ID_FAIL "+e)
  identity[e]={"receipt_sha256":ix["receipt_sha256"],"verdict":"PASS"}
  variants[e]={}
  for pol in POLICIES:
   fs=list(builds.rglob(f"c3x-p27-{e}-{pol.lower()}"))
   if len(fs)!=1:raise SystemExit(f"P27_BIN {e} {pol} {len(fs)}")
   variants[e][pol]={"sha256":sha_file(fs[0]),"protocol":protocol[e]}
 cells=attach_history(pick_cells(parent),parent)
 out={"schema":"c3x-p27-precommit-v1","scientific_stage":STAGE,"selective_outcomes_consulted":False,
  "parent_p26_receipt_sha256":parent["receipt_sha256"],"lawgen_constitution_sha256":law["constitution_sha256"],
  "anchor_budget":ANCHOR,"history":{"prime_nodes":PRIME,"decoy_nodes":DECOY,"decoy_count":NDECOY,"measurement_nodes":ANCHOR,
   "threads":1,"hash_mib":64,"psm_policy_applies_throughout_history":True},
  "selection":{"rule":"lexicographically first inherited P26 cell within every family×side×mapped-K8-state stratum","cells":len(cells)},
  "variants":variants,"native_equivalence":identity,
  "heldout":{"donors":list(DONORS),"target":HELDOUT,"prediction_frozen_before_target":True},
  "indexing_lane":{"authorization":"HOLD_MISSING_DYNAMIC_COLLISION_GRAPH_WITNESS","selective_outcomes_consulted":False},
  "cells":cells}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P27_PRECOMMIT_PASS",out["receipt_sha256"],len(cells))

def load_pre(p):
 x=json.loads(Path(p).read_text())
 if x.get("schema")!="c3x-p27-precommit-v1" or x.get("scientific_stage")!=STAGE or x.get("selective_outcomes_consulted") is not False:raise SystemExit("P27_PRE_AUTH")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P27_PRE_HASH")
 return x

def arm(c,base,run):
 w=p20.world_value(c,run["semantic"]["bestmove"])
 if w is None:raise SystemExit("P27_WORLD_JOIN")
 bw=base["world"]
 return {"receipt":run,"world":w,"action_changed":run["semantic"]["bestmove"]!=base["receipt"]["semantic"]["bestmove"],
  "fine_changed":(w["wdl"],w["precise_dtz"])!=(bw["wdl"],bw["precise_dtz"]),"coarse_changed":w["wdl"]!=bw["wdl"]}

def vertex(a):
 pre=load_pre(a.precommit)
 if a.engine not in ENGINES:raise SystemExit("P27_ENGINE")
 paths={"OFF":a.off,"ON":a.on}
 for pol in POLICIES:
  if sha_file(paths[pol])!=pre["variants"][a.engine][pol]["sha256"]:raise SystemExit("P27_BINARY_ID")
 protocol=pre["variants"][a.engine]["OFF"]["protocol"]
 src=[c for c in pre["cells"] if c["material_seed_name"]==a.family]
 if len(src)!=16:raise SystemExit(f"P27_VERTEX_N {len(src)}")
 rows=[]
 for i,c in enumerate(src,1):
  rec={k:c[k] for k in ("candidate_sha256","material_seed_name","side_to_move","square","vertex","fen","states_by_budget")};rec["age"]={}
  decoys=[x["fen"] for x in c["history"]["decoys"]]
  for pol in POLICIES:
   runs={}
   for mode in MODES:runs[mode]=history_search(paths[pol],protocol,mode,c["fen"],decoys)
   bw=p20.world_value(c,runs["SHAM"]["semantic"]["bestmove"])
   if bw is None:raise SystemExit("P27_SHAM_WORLD")
   base={"receipt":runs["SHAM"],"world":bw,"action_changed":False,"fine_changed":False,"coarse_changed":False}
   arms={"00":base}
   for bits,mode in (("10","MASK_MAIN"),("01","MASK_QSEARCH"),("11","MASK_MAIN_QSEARCH"),("ALL","MASK_ALL")):
    arms[bits]=arm(c,base,runs[mode])
   rec["age"][pol]={"targets":{a.engine:{"arms":arms}}}
  rows.append(rec);print("P27_VERTEX",a.engine,a.family,i,len(src),flush=True)
 out={"schema":"c3x-p27-vertex-v1","scientific_stage":STAGE,"engine":a.engine,"family":a.family,
  "precommit_receipt_sha256":pre["receipt_sha256"],"rows":rows};seal(out)
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

def collect(path,engines):
 by={}
 for p in Path(path).rglob("*.json"):
  try:x=json.loads(p.read_text())
  except:continue
  if x.get("schema")!="c3x-p27-vertex-v1":continue
  if x["engine"] not in engines:continue
  k=(x["engine"],x["family"])
  if k in by:raise SystemExit("P27_DUP_RESULT")
  by[k]=x
 exp={(e,f) for e in engines for f in p26.FAMILIES}
 if set(by)!=exp:raise SystemExit(f"P27_RESULT_SET {len(by)}/{len(exp)}")
 return by

def fp(z):
 c=z["curvature"];return [c["class"],c["dominant_coordinate"],c["dominant_sign"]]

def field(by,engine,pre):
 states=sorted({c["states_by_budget"][str(ANCHOR)]["mapped"] for c in pre["cells"]})
 out={pol:{} for pol in POLICIES}
 for pol in POLICIES:
  for s in states:
   out[pol][s]={}
   for sq,mp in p26.SQUARES.items():
    vres={}
    for bit,fam in mp.items():
     rr=[]
     for r in by[(engine,fam)]["rows"]:
      if r["states_by_budget"][str(ANCHOR)]["mapped"]==s:
       rr.append({"targets":{engine:r["age"][pol]["targets"][engine]}})
     if len(rr)!=2:raise SystemExit(f"P27_SUPPORT {engine} {pol} {s} {fam} {len(rr)}")
     vres[bit]={"rows":rr}
    out[pol][s][sq]=fp(p20.square_analysis(vres,engine))
 return out

def mask(off,on):return [off[i]!=on[i] for i in range(3)]

def predict(a):
 pre=load_pre(a.precommit);by=collect(a.results,DONORS)
 fs={e:field(by,e,pre) for e in DONORS};pred={};resolved=0
 states=sorted(fs[DONORS[0]]["OFF"])
 for s in states:
  pred[s]={}
  for sq in p26.SQUARES:
   dm={e:mask(fs[e]["OFF"][s][sq],fs[e]["ON"][s][sq]) for e in DONORS}
   ok=dm[DONORS[0]]==dm[DONORS[1]]
   if ok:resolved+=1
   pred[s][sq]={"donor_masks":dm,"status":"RESOLVED" if ok else "UNRESOLVED",
                "predicted_heldout_mask":dm[DONORS[0]] if ok else None}
 out={"schema":"c3x-p27-heldout-prediction-v1","scientific_stage":STAGE,"precommit_receipt_sha256":pre["receipt_sha256"],
  "heldout_outcomes_consulted":False,"donor_fields":fs,"predictions":pred,"resolved_cells":resolved,"total_cells":16,
  "prediction_capacity":"3-bit fingerprint component-change mask; exact donor consensus only"}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P27_PREDICTION_SEALED",out["receipt_sha256"],resolved,16)

def adjudicate(a):
 pre=load_pre(a.precommit);pr=json.loads(Path(a.prediction).read_text())
 if pr.get("schema")!="c3x-p27-heldout-prediction-v1" or pr.get("heldout_outcomes_consulted") is not False:raise SystemExit("P27_PRED_AUTH")
 by=collect(a.results,ENGINES);fs={e:field(by,e,pre) for e in ENGINES}
 transitions={};effects={}
 for e in ENGINES:
  transitions[e]={};changed=0
  for s in fs[e]["OFF"]:
   transitions[e][s]={}
   for sq in p26.SQUARES:
    m=mask(fs[e]["OFF"][s][sq],fs[e]["ON"][s][sq]);transitions[e][s][sq]=m
    changed+=int(any(m))
  effects[e]={"changed_state_square_cells":changed,"total":16,"nonzero_law_fingerprint_effect":changed>0}
 resolved=agree=0;held={}
 for s,pq in pr["predictions"].items():
  held[s]={}
  for sq,z in pq.items():
   obs=transitions[HELDOUT][s][sq]
   if z["status"]=="RESOLVED":
    resolved+=1;ok=obs==z["predicted_heldout_mask"];agree+=int(ok)
   else:ok=None
   held[s][sq]={"observed_mask":obs,"prediction_status":z["status"],"match":ok}
 universal=resolved==16 and agree==16
 anyeff=any(z["nonzero_law_fingerprint_effect"] for z in effects.values())
 if universal:verdict="AGE_ON_HIT_CAUSAL_MORPHISM_HELDOUT_SUPPORTED_AT_HISTORY_80K"
 elif not anyeff:verdict="NO_DETECTABLE_LAW_FINGERPRINT_EFFECT_UNDER_P27_HISTORY"
 elif resolved==0:verdict="AGE_EFFECT_OBSERVED_BUT_NO_DONOR_CONSENSUS_FOR_HELDOUT_MORPHISM"
 else:verdict="AGE_ON_HIT_EFFECT_ARCHITECTURE_CONDITIONED_NO_UNIVERSAL_HELDOUT_MORPHISM"
 out={"schema":"c3x-p27-adjudication-v1","scientific_stage":STAGE,"precommit_receipt_sha256":pre["receipt_sha256"],
  "prediction_receipt_sha256":pr["receipt_sha256"],"fields":fs,"transition_masks":transitions,"within_architecture_effects":effects,
  "heldout":{"resolved_cells":resolved,"agreement_cells":agree,"total_cells":16,"universal_morphism":universal,"details":held},
  "indexing_lane":pre["indexing_lane"],"verdict":verdict,
  "authority_ceiling":"P26-inherited frozen support; mapped K8 anchor state; 80k measurement; deterministic persistent-TT history; age policy applies through history; no 40k/160k/300k transport claim; indexing lane held without topology witness"}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P27_ADJUDICATION",verdict,"heldout",agree,resolved)

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 p=sp.add_parser("identity");p.add_argument("--engine",choices=ENGINES,required=True);p.add_argument("--baseline",required=True);p.add_argument("--native",required=True);p.add_argument("--protocol",choices=["env","stockfish_uci"],required=True);p.add_argument("--parent",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=identity)
 p=sp.add_parser("precommit");p.add_argument("--parent",required=True);p.add_argument("--constitution",required=True);p.add_argument("--build-dir",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=precommit)
 p=sp.add_parser("vertex");p.add_argument("--precommit",required=True);p.add_argument("--engine",choices=ENGINES,required=True);p.add_argument("--off",required=True);p.add_argument("--on",required=True);p.add_argument("--family",choices=p26.FAMILIES,required=True);p.add_argument("--out",required=True);p.set_defaults(fn=vertex)
 p=sp.add_parser("predict");p.add_argument("--precommit",required=True);p.add_argument("--results",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=predict)
 p=sp.add_parser("adjudicate");p.add_argument("--precommit",required=True);p.add_argument("--prediction",required=True);p.add_argument("--results",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=adjudicate)
 a=ap.parse_args();a.fn(a)

if __name__=="__main__":main()
