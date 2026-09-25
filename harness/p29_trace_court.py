#!/usr/bin/env python3
import argparse,gzip,hashlib,json,os,re,shutil,subprocess
from collections import Counter,defaultdict
from pathlib import Path
import p20_transport as p20
import p26_product_field as p26
import p27_age_morphism as p27

STAGE="C3X 0.7.0-G9.4-P29"
ENGINES=("stockfish_19","berserk","ethereal")
DONORS=("stockfish_19","berserk")
HELDOUT="ethereal"
POLICIES=("OFF","ON")
MODES=("SHAM","MASK_MAIN","MASK_QSEARCH","MASK_MAIN_QSEARCH","MASK_ALL")
ANCHOR=80000
PRIME=20000
DECOY=20000
NDECOY=3
GRAPH_FAMILIES=("KQQvKQ","KRBvKB")
TRACE_FIELDS=(
 "seq","probes","signature_hits","full_key_hits","signature_collisions",
 "empty_signature_matches","shadow_unknown_occupied","cross_search_full_hits",
 "origin_delta_1","origin_delta_2","origin_delta_3","origin_delta_4","origin_delta_5plus",
 "store_attempts","store_commits","initial_stores","same_full_key_updates",
 "full_key_replacements","store_rejects","age_write_attempts","age_write_effective_changes",
 "age_write_true_key","age_write_signature_collision"
)

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def sign(x):return -1 if x<0 else 1 if x>0 else 0
def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()

def load_lawgen(p):
 x=json.loads(Path(p).read_text());c=x.get("constitution",{})
 if c.get("schema")!="c3x-lawgen-constitution-v5" or c.get("scientific_stage")!=STAGE or c.get("selective_outcomes_consulted") is not False:raise SystemExit("P29_LAWGEN")
 return x

def pick_cells(parent):
 groups=defaultdict(list)
 for c in parent["cells"]:
  s=c["states_by_budget"][str(ANCHOR)]["mapped"]
  groups[(c["material_seed_name"],c["side_to_move"],s)].append(c)
 out=[]
 for k,v in groups.items():
  v=sorted(v,key=lambda z:z["candidate_sha256"])
  if len(v)<2:raise SystemExit(f"P29_FRESH_SUPPORT_SHORT {k} {len(v)}")
  c=dict(v[1])
  c["p28_first_candidate_sha256"]=v[0]["candidate_sha256"]
  out.append(c)
 if len(out)!=128:raise SystemExit(f"P29_CELL_N {len(out)}/128")
 if any(c["candidate_sha256"]==c["p28_first_candidate_sha256"] for c in out):raise SystemExit("P29_P28_OVERLAP")
 return sorted(out,key=lambda z:z["candidate_sha256"])

def attach_history(chosen,parent):
 universe=sorted(parent["cells"],key=lambda x:x["candidate_sha256"]);n=len(universe);out=[]
 for c in chosen:
  start=int(c["candidate_sha256"][:8],16)%n;ds=[];j=1
  while len(ds)<NDECOY and j<n+1:
   d=universe[(start+j)%n];j+=1
   if d["candidate_sha256"]==c["candidate_sha256"] or d["material_seed_name"]==c["material_seed_name"]:continue
   ds.append({"candidate_sha256":d["candidate_sha256"],"fen":d["fen"],"family":d["material_seed_name"]})
  if len(ds)!=NDECOY:raise SystemExit("P29_DECOY")
  z={k:c[k] for k in ("candidate_sha256","material_seed_name","side_to_move","square","vertex","fen","world","states_by_budget","p28_first_candidate_sha256")}
  z["history"]={"prime_fen":c["fen"],"decoys":ds}
  z["graph_probe"]=c["material_seed_name"] in GRAPH_FAMILIES and c["side_to_move"]=="WHITE"
  out.append(z)
 if sum(c["graph_probe"] for c in out)!=16:raise SystemExit("P29_GRAPH_PROBE_N")
 return out

def precommit(a):
 parent=p26.load_pre(a.parent);law=load_lawgen(a.constitution);b=Path(a.build_dir)
 protocol={"stockfish_19":"stockfish_uci","berserk":"env","ethereal":"env"}
 variants={};identity={}
 for e in ENGINES:
  ids=list(b.rglob(f"p29-identity-{e}.json"))
  if len(ids)!=1:raise SystemExit("P29_ID_FILE "+e)
  ix=json.loads(ids[0].read_text())
  if ix.get("verdict")!="PASS":raise SystemExit("P29_ID_FAIL "+e)
  identity[e]={"receipt_sha256":ix["receipt_sha256"],"verdict":"PASS"}
  variants[e]={}
  for pol in POLICIES:
   fs=list(b.rglob(f"c3x-p29-{e}-{pol.lower()}"))
   if len(fs)!=1:raise SystemExit(f"P29_BIN {e} {pol} {len(fs)}")
   variants[e][pol]={"sha256":sha_file(fs[0]),"protocol":protocol[e]}
 cells=attach_history(pick_cells(parent),parent)
 out={"schema":"c3x-p29-precommit-v1","scientific_stage":STAGE,"selective_outcomes_consulted":False,
  "parent_p26_receipt_sha256":parent["receipt_sha256"],"parent_p28_closure_commit":"9f7decbaf84029c86a3113a241be59b76fb257e9",
  "lawgen_constitution_sha256":law["constitution_sha256"],
  "history":{"prime_nodes":PRIME,"decoy_nodes":DECOY,"decoy_count":NDECOY,"measurement_nodes":ANCHOR,"threads":1,"hash_mib":64},
  "selection":{"rule":"second candidate_sha256 in every family×side×mapped-state stratum","worlds":128,"graph_probe_worlds":16},
  "variants":variants,"trace_identity":identity,
  "heldout":{"donors":list(DONORS),"target":HELDOUT,"heldout_trace_before_prediction":True,"selective_after_prediction":True},
  "cells":cells}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P29_PRECOMMIT",out["receipt_sha256"],len(cells))

def load_pre(p):
 x=json.loads(Path(p).read_text())
 if x.get("schema")!="c3x-p29-precommit-v1" or x.get("selective_outcomes_consulted") is not False:raise SystemExit("P29_PRE")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P29_PRE_HASH")
 return x

def setup_trace(path,protocol,mode,trace_path,graph_seq):
 env=os.environ.copy()
 if protocol=="env":env["C3X_PSM_MODE"]=mode
 else:env.pop("C3X_PSM_MODE",None)
 env["C3X_TT_TRACE"]=str(trace_path)
 env["C3X_TT_GRAPH_SEQ"]=str(graph_seq)
 p=subprocess.Popen([path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,env=env)
 p.stdin.write("uci\n");p.stdin.flush()
 pre=p27.read_until(p,lambda x:x.strip()=="uciok")
 if not any(x.strip()=="uciok" for x in pre):raise RuntimeError("P29_UCI")
 opts="\n".join(pre);cmd=[]
 if protocol=="stockfish_uci":
  if not p27.has_option(opts,"C3X_TTReadMode") or not p27.has_option(opts,"C3X_Telemetry"):raise RuntimeError("P29_C3X_SURFACE")
  cmd += [f"setoption name C3X_TTReadMode value {mode}","setoption name C3X_Telemetry value true"]
 if p27.has_option(opts,"Threads"):cmd.append("setoption name Threads value 1")
 if p27.has_option(opts,"Hash"):cmd.append("setoption name Hash value 64")
 if p27.has_option(opts,"SyzygyProbeLimit"):cmd.append("setoption name SyzygyProbeLimit value 0")
 if p27.has_option(opts,"UCI_ShowWDL"):cmd.append("setoption name UCI_ShowWDL value true")
 if p27.has_option(opts,"Clear Hash"):cmd.append("setoption name Clear Hash")
 cmd.append("isready")
 for c in cmd:p.stdin.write(c+"\n")
 p.stdin.flush();ready=p27.read_until(p,lambda x:x.strip()=="readyok")
 if not any(x.strip()=="readyok" for x in ready):raise RuntimeError("P29_READY")
 return p

def parse_trace(path,measurement_seq=5):
 summaries={};edges=[];age_events=0
 for line in Path(path).read_text().splitlines():
  z=line.split(",")
  if not z:continue
  if z[0]=="S":
   if len(z)!=1+len(TRACE_FIELDS):raise RuntimeError(f"P29_TRACE_SUMMARY_WIDTH {len(z)}")
   d={k:int(v) for k,v in zip(TRACE_FIELDS,z[1:])};summaries[d["seq"]]=d
  elif z[0] in ("R","C") and int(z[1])==measurement_seq:
   if z[0]=="R":
    _,seq,bucket,slot,old,new,oldseq=z
    edges.append(("R",old,new,int(bucket),int(slot),int(oldseq)))
   else:
    _,seq,bucket,slot,req,resident,oldseq=z
    edges.append(("C",req,resident,int(bucket),int(slot),int(oldseq)))
  elif z[0]=="A" and int(z[1])==measurement_seq:
   age_events+=1
 if measurement_seq not in summaries:raise RuntimeError(f"P29_TRACE_SEQ {sorted(summaries)}")
 sm=summaries[measurement_seq]
 if sm["shadow_unknown_occupied"]!=0:raise RuntimeError(f"P29_SHADOW_UNKNOWN {sm['shadow_unknown_occupied']}")
 cnt=Counter(edges);vertices=set()
 for e in edges:vertices.update((e[1],e[2]))
 packed=[list(k)+[v] for k,v in sorted(cnt.items())]
 graph={"vertex_count":len(vertices),"replacement_edge_count":sum(v for k,v in cnt.items() if k[0]=="R"),
        "signature_collision_edge_count":sum(v for k,v in cnt.items() if k[0]=="C"),
        "unique_edge_count":len(cnt),"age_event_count":age_events,
        "edge_multiset_sha256":digest(packed)}
 return sm,graph

def trace_history(path,protocol,cell,trace_path,graph):
 trace_path=Path(trace_path);trace_path.parent.mkdir(parents=True,exist_ok=True)
 p=setup_trace(path,protocol,"SHAM",trace_path,5 if graph else 0)
 try:
  prev={}
  _,prev=p27.go(p,cell["fen"],PRIME,protocol)
  for d in cell["history"]["decoys"]:_,prev=p27.go(p,d["fen"],DECOY,protocol)
  sem,tel=p27.go(p,cell["fen"],ANCHOR,protocol)
  if protocol=="env":tel=p27.tdelta(tel,prev)
  p.stdin.write(f"position fen {cell['fen']}\ngo nodes 1\n");p.stdin.flush()
  flushed=p27.read_until(p,lambda x:x.startswith("bestmove "))
  if not any(x.startswith("bestmove ") for x in flushed):raise RuntimeError("P29_TRACE_FLUSH")
 finally:
  try:
   p.stdin.write("quit\n");p.stdin.flush()
  except:pass
  try:p.communicate(timeout=5)
  except subprocess.TimeoutExpired:p.kill();p.communicate()
 sm,g=parse_trace(trace_path,5)
 kept=None
 if graph:
  kept=str(trace_path)+".gz"
  with open(trace_path,"rb") as src,gzip.open(kept,"wb",compresslevel=9) as dst:shutil.copyfileobj(src,dst)
 Path(trace_path).unlink(missing_ok=True)
 return {"semantic":sem,"psm_telemetry":tel,"tt":sm,"graph":g if graph else None,"raw_graph_trace_gz":Path(kept).name if kept else None}

def trace_identity(a):
 parent=p26.load_pre(a.parent);chosen=attach_history(pick_cells(parent),parent)[0]
 tmp=Path(a.out).with_suffix(".trace.csv")
 traced=trace_history(a.binary,a.protocol,chosen,tmp,False)
 base=p27.history_search(a.binary,a.protocol,"SHAM",chosen["fen"],[x["fen"] for x in chosen["history"]["decoys"]])
 keys=("bestmove","score","depth","pv")
 ok=all(traced["semantic"].get(k)==base["semantic"].get(k) for k in keys) and traced["tt"]["shadow_unknown_occupied"]==0
 out={"schema":"c3x-p29-trace-identity-v1","scientific_stage":STAGE,"engine":a.engine,"policy":a.policy,
      "candidate_sha256":chosen["candidate_sha256"],"trace_enabled_semantic":{k:traced["semantic"].get(k) for k in keys},
      "trace_disabled_semantic":{k:base["semantic"].get(k) for k in keys},"trace_summary":traced["tt"],"verdict":"PASS" if ok else "FAIL"}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P29_IDENTITY",a.engine,out["verdict"])

def arm(c,base,run):
 w=p20.world_value(c,run["semantic"]["bestmove"])
 if w is None:raise SystemExit("P29_WORLD_JOIN")
 bw=base["world"]
 return {"receipt":run,"world":w,"action_changed":run["semantic"]["bestmove"]!=base["receipt"]["semantic"]["bestmove"],
  "fine_changed":(w["wdl"],w["precise_dtz"])!=(bw["wdl"],bw["precise_dtz"]),"coarse_changed":w["wdl"]!=bw["wdl"]}

def law_arms(path,protocol,c,baseline_trace):
 bw=p20.world_value(c,baseline_trace["semantic"])
 if bw is None:raise SystemExit("P29_SHAM_WORLD")
 base={"receipt":{"semantic":baseline_trace["semantic"],"telemetry":baseline_trace["psm_telemetry"]},"world":bw,
       "action_changed":False,"fine_changed":False,"coarse_changed":False}
 arms={"00":base};decoys=[x["fen"] for x in c["history"]["decoys"]]
 for bits,mode in (("10","MASK_MAIN"),("01","MASK_QSEARCH"),("11","MASK_MAIN_QSEARCH"),("ALL","MASK_ALL")):
  run=p27.history_search(path,protocol,mode,c["fen"],decoys);arms[bits]=arm(c,base,run)
 return arms

def donor_vertex(a):
 pre=load_pre(a.precommit);e=a.engine;paths={"OFF":a.off,"ON":a.on}
 protocol=pre["variants"][e]["OFF"]["protocol"]
 for pol in POLICIES:
  if sha_file(paths[pol])!=pre["variants"][e][pol]["sha256"]:raise SystemExit("P29_BINARY")
 src=[c for c in pre["cells"] if c["material_seed_name"]==a.family]
 if len(src)!=16:raise SystemExit("P29_FAMILY_N")
 rows=[];outdir=Path(a.out).parent
 for i,c in enumerate(src,1):
  rec={k:c[k] for k in ("candidate_sha256","material_seed_name","side_to_move","square","vertex","fen","world","states_by_budget","graph_probe")};rec["policy"]={}
  for pol in POLICIES:
   tp=outdir/"traces"/f"{e}-{c['candidate_sha256'][:16]}-{pol}.csv"
   tr=trace_history(paths[pol],protocol,c,tp,c["graph_probe"])
   arms=law_arms(paths[pol],protocol,c,tr)
   rec["policy"][pol]={"trace":tr,"targets":{e:{"arms":arms}}}
  rows.append(rec);print("P29_DONOR",e,a.family,i,16,flush=True)
 out={"schema":"c3x-p29-full-v1","scientific_stage":STAGE,"phase":"donor","engine":e,"family":a.family,
      "precommit_receipt_sha256":pre["receipt_sha256"],"rows":rows};seal(out)
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

def heldout_trace(a):
 pre=load_pre(a.precommit);e=HELDOUT;paths={"OFF":a.off,"ON":a.on};protocol=pre["variants"][e]["OFF"]["protocol"]
 for pol in POLICIES:
  if sha_file(paths[pol])!=pre["variants"][e][pol]["sha256"]:raise SystemExit("P29_HELDOUT_TRACE_BINARY")
 src=[c for c in pre["cells"] if c["material_seed_name"]==a.family]
 rows=[];outdir=Path(a.out).parent
 for i,c in enumerate(src,1):
  rec={k:c[k] for k in ("candidate_sha256","material_seed_name","side_to_move","square","vertex","fen","world","states_by_budget","graph_probe")};rec["policy"]={}
  for pol in POLICIES:
   tp=outdir/"traces"/f"{e}-{c['candidate_sha256'][:16]}-{pol}.csv"
   tr=trace_history(paths[pol],protocol,c,tp,c["graph_probe"])
   rec["policy"][pol]={"trace":tr}
  rows.append(rec);print("P29_HELDOUT_TRACE",a.family,i,16,flush=True)
 out={"schema":"c3x-p29-heldout-trace-v1","scientific_stage":STAGE,"heldout_selective_consulted":False,
      "engine":e,"family":a.family,"precommit_receipt_sha256":pre["receipt_sha256"],"rows":rows};seal(out)
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

def collect_trace(path):
 by={}
 for p in Path(path).rglob("*.json"):
  try:x=json.loads(p.read_text())
  except:continue
  if x.get("schema")!="c3x-p29-heldout-trace-v1":continue
  by[x["family"]]=x
 if set(by)!=set(p26.FAMILIES):raise SystemExit(f"P29_TRACE_SET {len(by)}/8")
 return by

def heldout_selective(a):
 pre=load_pre(a.precommit);e=HELDOUT;paths={"OFF":a.off,"ON":a.on};protocol=pre["variants"][e]["OFF"]["protocol"]
 pr=json.loads(Path(a.prediction).read_text())
 if pr.get("schema")!="c3x-p29-heldout-prediction-v1" or pr.get("heldout_selective_consulted") is not False:raise SystemExit("P29_PREDICTION_AUTH")
 if pr.get("precommit_receipt_sha256")!=pre["receipt_sha256"]:raise SystemExit("P29_PREDICTION_PARENT")
 for pol in POLICIES:
  if sha_file(paths[pol])!=pre["variants"][e][pol]["sha256"]:raise SystemExit("P29_HELDOUT_SELECTIVE_BINARY")
 tb=collect_trace(a.trace_results);src=tb[a.family]["rows"];rows=[]
 index={c["candidate_sha256"]:c for c in pre["cells"] if c["material_seed_name"]==a.family}
 for i,r in enumerate(src,1):
  c=index[r["candidate_sha256"]];rec=dict(r)
  for pol in POLICIES:
   tr=rec["policy"][pol]["trace"]
   rec["policy"][pol]["targets"]={e:{"arms":law_arms(paths[pol],protocol,c,tr)}}
  rows.append(rec);print("P29_HELDOUT_LAW",a.family,i,16,flush=True)
 out={"schema":"c3x-p29-full-v1","scientific_stage":STAGE,"phase":"heldout","engine":e,"family":a.family,
      "precommit_receipt_sha256":pre["receipt_sha256"],"rows":rows};seal(out)
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

def collect_full(path,engines):
 by={}
 for p in Path(path).rglob("*.json"):
  try:x=json.loads(p.read_text())
  except:continue
  if x.get("schema")!="c3x-p29-full-v1" or x.get("engine") not in engines:continue
  k=(x["engine"],x["family"])
  if k in by:raise SystemExit("P29_FULL_DUP")
  by[k]=x
 exp={(e,f) for e in engines for f in p26.FAMILIES}
 if set(by)!=exp:raise SystemExit(f"P29_FULL_SET {len(by)}/{len(exp)}")
 return by

def fp(z):
 c=z["curvature"];return [c["class"],c["dominant_coordinate"],c["dominant_sign"]]

def field(by,e,pre):
 states=sorted({c["states_by_budget"][str(ANCHOR)]["mapped"] for c in pre["cells"]});out={p:{} for p in POLICIES}
 for pol in POLICIES:
  for s in states:
   out[pol][s]={}
   for sq,mp in p26.SQUARES.items():
    v={}
    for bit,fam in mp.items():
     rr=[]
     for r in by[(e,fam)]["rows"]:
      if r["states_by_budget"][str(ANCHOR)]["mapped"]==s:
       rr.append({"targets":{e:r["policy"][pol]["targets"][e]}})
     if len(rr)!=2:raise SystemExit(f"P29_LAW_SUPPORT {e} {s} {fam} {len(rr)}")
     v[bit]={"rows":rr}
    out[pol][s][sq]=fp(p20.square_analysis(v,e))
 return out

def trace_maps_from_full(by,e,pre):
 states=sorted({c["states_by_budget"][str(ANCHOR)]["mapped"] for c in pre["cells"]});out={}
 famsq={sq:set(mp.values()) for sq,mp in p26.SQUARES.items()}
 for s in states:
  out[s]={}
  for sq,fams in famsq.items():
   agg={pol:defaultdict(int) for pol in POLICIES}
   for fam in fams:
    for r in by[(e,fam)]["rows"]:
     if r["states_by_budget"][str(ANCHOR)]["mapped"]!=s:continue
     for pol in POLICIES:
      for k,v in r["policy"][pol]["trace"]["tt"].items():
       if k!="seq":agg[pol][k]+=int(v)
   sig=[1 if agg["ON"]["age_write_effective_changes"]>0 else 0,
        sign(agg["ON"]["full_key_replacements"]-agg["OFF"]["full_key_replacements"]),
        sign(agg["ON"]["origin_delta_4"]-agg["OFF"]["origin_delta_4"]),
        sign(agg["ON"]["full_key_hits"]-agg["OFF"]["full_key_hits"]),
        sign(agg["ON"]["signature_collisions"]-agg["OFF"]["signature_collisions"])]
   out[s][sq]={"signature":sig,"OFF":dict(agg["OFF"]),"ON":dict(agg["ON"])}
 return out

def trace_maps_heldout(trace_by,pre):
 pseudo={}
 for fam,x in trace_by.items():
  pseudo[(HELDOUT,fam)]={"rows":[]}
  for r in x["rows"]:
   z=dict(r)
   for pol in POLICIES:z["policy"][pol]["targets"]={HELDOUT:{"arms":{}}}
   pseudo[(HELDOUT,fam)]["rows"].append(z)
 return trace_maps_from_full(pseudo,HELDOUT,pre)

def lawmask(a,b):return [a[i]!=b[i] for i in range(3)]

def donor_rule(a):
 pre=load_pre(a.precommit);by=collect_full(a.results,DONORS);obs=[];fields={};traces={}
 for e in DONORS:
  fields[e]=field(by,e,pre);traces[e]=trace_maps_from_full(by,e,pre)
  for s in traces[e]:
   for sq,z in traces[e][s].items():
    obs.append({"engine":e,"state":s,"square":sq,"signature":z["signature"],
                "law_mask":lawmask(fields[e]["OFF"][s][sq],fields[e]["ON"][s][sq])})
 groups=defaultdict(list)
 for z in obs:groups[",".join(map(str,z["signature"]))].append(z)
 rules={}
 for k,v in groups.items():
  engines={z["engine"] for z in v};masks={tuple(z["law_mask"]) for z in v}
  ok=engines==set(DONORS) and len(masks)==1
  rules[k]={"status":"RESOLVED" if ok else "UNRESOLVED","mask":list(next(iter(masks))) if ok else None,"n":len(v)}
 out={"schema":"c3x-p29-donor-rule-v1","scientific_stage":STAGE,"heldout_selective_consulted":False,
      "precommit_receipt_sha256":pre["receipt_sha256"],"signature":"age-engaged + exact signs of replacement/prime-survival/full-hit/signature-collision deltas",
      "rules":rules,"donor_observations":obs}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P29_RULE",sum(z["status"]=="RESOLVED" for z in rules.values()),len(rules))

def predict(a):
 pre=load_pre(a.precommit);rule=json.loads(Path(a.rule).read_text())
 if rule.get("heldout_selective_consulted") is not False:raise SystemExit("P29_RULE_AUTH")
 tb=collect_trace(a.trace_results);tm=trace_maps_heldout(tb,pre);pred={};resolved=0
 for s in tm:
  pred[s]={}
  for sq,z in tm[s].items():
   k=",".join(map(str,z["signature"]));r=rule["rules"].get(k,{"status":"UNRESOLVED"})
   ok=r["status"]=="RESOLVED";resolved+=int(ok)
   pred[s][sq]={"signature":z["signature"],"rule_key":k,"status":"RESOLVED" if ok else "UNRESOLVED",
                "predicted_mask":r.get("mask") if ok else None}
 out={"schema":"c3x-p29-heldout-prediction-v1","scientific_stage":STAGE,"heldout_selective_consulted":False,
      "precommit_receipt_sha256":pre["receipt_sha256"],"rule_receipt_sha256":rule["receipt_sha256"],
      "predictions":pred,"resolved":resolved,"total":16};seal(out)
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P29_PRED",resolved,16)

def graph_census(by,e):
 pairs=changed=0;details=[]
 for fam in p26.FAMILIES:
  for r in by[(e,fam)]["rows"]:
   if not r["graph_probe"]:continue
   pairs+=1
   a=r["policy"]["OFF"]["trace"]["graph"];b=r["policy"]["ON"]["trace"]["graph"]
   diff=a["edge_multiset_sha256"]!=b["edge_multiset_sha256"];changed+=int(diff)
   details.append({"candidate_sha256":r["candidate_sha256"],"family":fam,"state":r["states_by_budget"][str(ANCHOR)]["mapped"],
                   "off":a,"on":b,"edge_multiset_changed":diff})
 return {"pairs":pairs,"changed":changed,"details":details}

def localize(sig,law_changed):
 if law_changed:return "LAW_EFFECT_REOPENED"
 if sig[0]==0:return "AGE_WRITE_SEMANTIC_NOOP"
 if sig[1]==0:return "AGE_WRITE_ENGAGED_REPLACEMENT_CHANNEL_NULL"
 if sig[2]==0 and sig[3]==0:return "REPLACEMENT_SHIFT_REUSE_CHANNEL_NULL"
 return "REUSE_SHIFT_FROZEN_LAW_NULL"

def adjudicate(a):
 pre=load_pre(a.precommit);pr=json.loads(Path(a.prediction).read_text())
 donors=collect_full(a.donors,DONORS);held=collect_full(a.heldout,[HELDOUT]);by={**donors,**held}
 fields={e:field(by,e,pre) for e in ENGINES};traces={e:trace_maps_from_full(by,e,pre) for e in ENGINES}
 transitions={};effects={}
 for e in ENGINES:
  transitions[e]={};changed=0
  for s in fields[e]["OFF"]:
   transitions[e][s]={}
   for sq in p26.SQUARES:
    m=lawmask(fields[e]["OFF"][s][sq],fields[e]["ON"][s][sq]);transitions[e][s][sq]=m;changed+=int(any(m))
  effects[e]={"changed_law_cells":changed,"total":16}
 resolved=agree=0
 for s,q in pr["predictions"].items():
  for sq,z in q.items():
   if z["status"]=="RESOLVED":
    resolved+=1;agree+=int(transitions[HELDOUT][s][sq]==z["predicted_mask"])
 universal=resolved==16 and agree==16
 loc=Counter()
 for s in traces[HELDOUT]:
  for sq,z in traces[HELDOUT][s].items():loc[localize(z["signature"],any(transitions[HELDOUT][s][sq]))]+=1
 graphs={e:graph_census(by,e) for e in ENGINES}
 census={}
 for e in ENGINES:
  census[e]={k:0 for k in ("replacement_shift","prime_survival_shift","full_hit_shift","signature_collision_shift","age_engaged")}
  for s in traces[e]:
   for sq,z in traces[e][s].items():
    sig=z["signature"];census[e]["age_engaged"]+=int(sig[0]!=0);census[e]["replacement_shift"]+=int(sig[1]!=0)
    census[e]["prime_survival_shift"]+=int(sig[2]!=0);census[e]["full_hit_shift"]+=int(sig[3]!=0);census[e]["signature_collision_shift"]+=int(sig[4]!=0)
 verdict="ENTRY_LEVEL_MEDIATOR_CONDITIONAL_MORPHISM_RECOVERED" if universal else "ENTRY_LEVEL_PATHWAY_LOCALIZED_BUT_MEDIATOR_NOT_UNIVERSALLY_SUFFICIENT"
 out={"schema":"c3x-p29-adjudication-v1","scientific_stage":STAGE,"precommit_receipt_sha256":pre["receipt_sha256"],
      "prediction_receipt_sha256":pr["receipt_sha256"],"within_architecture_law_effects":effects,
      "replacement_event_causal_census":census,"ethereal_pathway_localization":dict(loc),
      "collision_graph_census":graphs,
      "conditional_morphism":{"resolved":resolved,"agreement":agree,"total":16,"universal":universal},
      "verdict":verdict,
      "authority_ceiling":"fresh second-rank 128-world support; single-thread full-key instrumentation witness; 80k law anchor; five-coordinate mediator only; no cross-budget or uninstrumented-production claim"}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P29_ADJ",verdict,dict(loc),agree,resolved)

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 p=sp.add_parser("identity");p.add_argument("--engine",choices=ENGINES,required=True);p.add_argument("--policy",choices=POLICIES,required=True);p.add_argument("--binary",required=True);p.add_argument("--protocol",choices=["env","stockfish_uci"],required=True);p.add_argument("--parent",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=trace_identity)
 p=sp.add_parser("precommit");p.add_argument("--parent",required=True);p.add_argument("--constitution",required=True);p.add_argument("--build-dir",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=precommit)
 p=sp.add_parser("donor");p.add_argument("--precommit",required=True);p.add_argument("--engine",choices=DONORS,required=True);p.add_argument("--family",choices=p26.FAMILIES,required=True);p.add_argument("--off",required=True);p.add_argument("--on",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=donor_vertex)
 p=sp.add_parser("heldout-trace");p.add_argument("--precommit",required=True);p.add_argument("--family",choices=p26.FAMILIES,required=True);p.add_argument("--off",required=True);p.add_argument("--on",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=heldout_trace)
 p=sp.add_parser("rule");p.add_argument("--precommit",required=True);p.add_argument("--results",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=donor_rule)
 p=sp.add_parser("predict");p.add_argument("--precommit",required=True);p.add_argument("--rule",required=True);p.add_argument("--trace-results",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=predict)
 p=sp.add_parser("heldout-selective");p.add_argument("--precommit",required=True);p.add_argument("--prediction",required=True);p.add_argument("--trace-results",required=True);p.add_argument("--family",choices=p26.FAMILIES,required=True);p.add_argument("--off",required=True);p.add_argument("--on",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=heldout_selective)
 p=sp.add_parser("adjudicate");p.add_argument("--precommit",required=True);p.add_argument("--prediction",required=True);p.add_argument("--donors",required=True);p.add_argument("--heldout",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=adjudicate)
 a=ap.parse_args();a.fn(a)

if __name__=="__main__":main()
