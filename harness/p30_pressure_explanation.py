#!/usr/bin/env python3
import argparse,hashlib,json,os,re,shutil,subprocess
from collections import Counter,defaultdict
from pathlib import Path
import p20_transport as p20
import p26_product_field as p26
import p27_age_morphism as p27
import p29_trace_court as p29

STAGE="C3X 0.7.0-G9.4-P30"
ENGINES=("stockfish_19","berserk","ethereal")
DONORS=("stockfish_19","berserk")
HELDOUT="ethereal"
POLICIES=("OFF","ON")
CAPS=(1,4,16,64)
LAW_CAP=1
ANCHOR=80000
PRIME=20000
DECOY=20000

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
 if c.get("schema")!="c3x-lawgen-constitution-v6" or c.get("scientific_stage")!=STAGE or c.get("heldout_selective_consulted") is not False:raise SystemExit("P30_LAWGEN")
 return x

def setup_hash(path,protocol,mode,hash_mib,trace_path=None,graph_seq=0):
 env=os.environ.copy()
 if protocol=="env":env["C3X_PSM_MODE"]=mode
 else:env.pop("C3X_PSM_MODE",None)
 if trace_path is not None:
  env["C3X_TT_TRACE"]=str(trace_path);env["C3X_TT_GRAPH_SEQ"]=str(graph_seq)
 else:
  env.pop("C3X_TT_TRACE",None);env.pop("C3X_TT_GRAPH_SEQ",None)
 p=subprocess.Popen([path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,env=env)
 p.stdin.write("uci\n");p.stdin.flush();pre=p27.read_until(p,lambda x:x.strip()=="uciok")
 if not any(x.strip()=="uciok" for x in pre):raise RuntimeError("P30_UCI")
 opts="\n".join(pre);cmd=[]
 if protocol=="stockfish_uci":
  if not p27.has_option(opts,"C3X_TTReadMode") or not p27.has_option(opts,"C3X_Telemetry"):raise RuntimeError("P30_C3X_SURFACE")
  cmd += [f"setoption name C3X_TTReadMode value {mode}","setoption name C3X_Telemetry value true"]
 if p27.has_option(opts,"Threads"):cmd.append("setoption name Threads value 1")
 if p27.has_option(opts,"Hash"):cmd.append(f"setoption name Hash value {hash_mib}")
 if p27.has_option(opts,"SyzygyProbeLimit"):cmd.append("setoption name SyzygyProbeLimit value 0")
 if p27.has_option(opts,"UCI_ShowWDL"):cmd.append("setoption name UCI_ShowWDL value true")
 if p27.has_option(opts,"Clear Hash"):cmd.append("setoption name Clear Hash")
 cmd.append("isready")
 for c in cmd:p.stdin.write(c+"\n")
 p.stdin.flush();ready=p27.read_until(p,lambda x:x.strip()=="readyok")
 if not any(x.strip()=="readyok" for x in ready):raise RuntimeError("P30_READY")
 return p

def history_search_hash(path,protocol,mode,cell,hash_mib):
 p=setup_hash(path,protocol,mode,hash_mib)
 try:
  prev={}
  _,prev=p27.go(p,cell["fen"],PRIME,protocol)
  for d in cell["history"]["decoys"]:_,prev=p27.go(p,d["fen"],DECOY,protocol)
  sem,tel=p27.go(p,cell["fen"],ANCHOR,protocol)
  if protocol=="env":tel=p27.tdelta(tel,prev)
  main=int(tel.get("hits_main",0) if protocol=="env" else tel.get("raw_hits_main",0))
  q=int(tel.get("hits_qsearch",0) if protocol=="env" else tel.get("raw_hits_qsearch",0))
  return {"semantic":sem,"engagement":{"MAIN":main,"QSEARCH":q,"floor":min(main,q),"passed":main>0 and q>0},"telemetry":tel}
 finally:
  p.terminate()
  try:p.communicate(timeout=3)
  except subprocess.TimeoutExpired:p.kill();p.communicate()

def parse_victim(path,seq=5):
 lines=Path(path).read_text().splitlines();V=[];H=[]
 for idx,line in enumerate(lines):
  z=line.split(",")
  if not z:continue
  if z[0]=="V" and int(z[1])==seq:
   if len(z)!=11:raise RuntimeError(f"P30_V_WIDTH {len(z)}")
   _,_,bucket,req,aslot,akey,dslot,dkey,ascore,dscore,known=z
   q={"pos":idx,"bucket":int(bucket),"requested":req,"actual_slot":int(aslot),"actual_key":akey,
      "depth_slot":int(dslot),"depth_key":dkey,"actual_score":int(ascore),"depth_only_score":int(dscore),"all_known":int(known)}
   if q["all_known"]!=1 or q["actual_key"]=="0000000000000000" or q["depth_key"]=="0000000000000000":raise RuntimeError("P30_V_SHADOW")
   V.append(q)
  elif z[0]=="H" and int(z[1])==seq:
   if len(z)!=6:raise RuntimeError(f"P30_H_WIDTH {len(z)}")
   _,_,bucket,slot,key,storeseq=z;H.append({"pos":idx,"bucket":int(bucket),"slot":int(slot),"key":key,"store_seq":int(storeseq)})
 hp=defaultdict(list)
 for h in H:hp[h["key"]].append(h["pos"])
 sensitive=[v for v in V if v["actual_slot"]!=v["depth_slot"]]
 protected=[v for v in sensitive if any(p>v["pos"] for p in hp.get(v["depth_key"],[]))]
 unique=set(v["depth_key"] for v in protected)
 packed_v=[[v[k] for k in ("bucket","requested","actual_slot","actual_key","depth_slot","depth_key","actual_score","depth_only_score")] for v in V]
 return {"victim_competitions":len(V),"age_sensitive_victim_choices":len(sensitive),
         "protected_then_reused_events":len(protected),"protected_then_reused_unique_keys":len(unique),
         "full_key_hit_events":len(H),"victim_event_sha256":digest(packed_v)}

def trace_history_hash(path,protocol,cell,hash_mib,trace_path,graph=True):
 trace_path=Path(trace_path);trace_path.parent.mkdir(parents=True,exist_ok=True)
 p=setup_hash(path,protocol,"SHAM",hash_mib,trace_path,5 if graph else 0)
 try:
  prev={}
  _,prev=p27.go(p,cell["fen"],PRIME,protocol)
  for d in cell["history"]["decoys"]:_,prev=p27.go(p,d["fen"],DECOY,protocol)
  sem,tel=p27.go(p,cell["fen"],ANCHOR,protocol)
  if protocol=="env":tel=p27.tdelta(tel,prev)
  p.stdin.write(f"position fen {cell['fen']}\ngo nodes 1\n");p.stdin.flush()
  flush=p27.read_until(p,lambda x:x.startswith("bestmove "))
  if not any(x.startswith("bestmove ") for x in flush):raise RuntimeError("P30_FLUSH")
 finally:
  try:p.stdin.write("quit\n");p.stdin.flush()
  except:pass
  try:p.communicate(timeout=5)
  except subprocess.TimeoutExpired:p.kill();p.communicate()
 tt,g=p29.parse_trace(trace_path,5);victim=parse_victim(trace_path,5) if graph else None
 if not graph:Path(trace_path).unlink(missing_ok=True)
 return {"semantic":sem,"psm_telemetry":tel,"tt":tt,"graph":g if graph else None,"victim":victim}

def precommit(a):
 parent=p29.load_pre(a.parent);law=load_lawgen(a.constitution);b=Path(a.build_dir)
 variants={};identity={}
 protocol={"stockfish_19":"stockfish_uci","berserk":"env","ethereal":"env"}
 for e in ENGINES:
  ids=list(b.rglob(f"p30-identity-{e}.json"))
  if len(ids)!=1:raise SystemExit("P30_ID_FILE "+e)
  ix=json.loads(ids[0].read_text())
  if ix.get("verdict")!="PASS":raise SystemExit("P30_ID_FAIL "+e)
  identity[e]={"receipt_sha256":ix["receipt_sha256"],"verdict":"PASS"}
  variants[e]={}
  for pol in POLICIES:
   fs=list(b.rglob(f"c3x-p30-{e}-{pol.lower()}"))
   if len(fs)!=1:raise SystemExit(f"P30_BIN {e} {pol}")
   variants[e][pol]={"sha256":sha_file(fs[0]),"protocol":protocol[e]}
 cells=parent["cells"];probe=[c for c in cells if c.get("graph_probe")]
 if len(cells)!=128 or len(probe)!=16:raise SystemExit("P30_SUPPORT")
 out={"schema":"c3x-p30-precommit-v1","scientific_stage":STAGE,"heldout_selective_consulted":False,
      "p29_precommit_receipt_sha256":parent["receipt_sha256"],"lawgen_constitution_sha256":law["constitution_sha256"],
      "capacities_mib":list(CAPS),"law_capacity_mib":LAW_CAP,"history":parent["history"],
      "selection":{"worlds":128,"pressure_probe_worlds":16,"rule":"exact P29 frozen support; graph_probe marks pressure lane"},
      "variants":variants,"trace_identity":identity,
      "heldout":{"donors":list(DONORS),"target":"ethereal_1mib_law","trace_all_capacities_before_prediction":True},
      "cells":cells}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P30_PRECOMMIT",out["receipt_sha256"])

def load_pre(p):
 x=json.loads(Path(p).read_text())
 if x.get("schema")!="c3x-p30-precommit-v1" or x.get("heldout_selective_consulted") is not False:raise SystemExit("P30_PRE")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P30_PRE_HASH")
 return x

def pressure(a):
 pre=load_pre(a.precommit);e=a.engine;paths={"OFF":a.off,"ON":a.on};protocol=pre["variants"][e]["OFF"]["protocol"]
 for pol in POLICIES:
  if sha_file(paths[pol])!=pre["variants"][e][pol]["sha256"]:raise SystemExit("P30_BINARY")
 cells=[c for c in pre["cells"] if c["graph_probe"]];rows=[];od=Path(a.out).parent
 for ci,c in enumerate(cells,1):
  z={k:c[k] for k in ("candidate_sha256","material_seed_name","side_to_move","square","vertex","fen","states_by_budget")};z["capacity"]={}
  for cap in CAPS:
   z["capacity"][str(cap)]={}
   for pol in POLICIES:
    tp=od/"traces"/f"{e}-{c['candidate_sha256'][:16]}-{cap}m-{pol}.csv"
    tr=trace_history_hash(paths[pol],protocol,c,cap,tp,True)
    z["capacity"][str(cap)][pol]=tr
  rows.append(z);print("P30_PRESSURE",e,ci,len(cells),flush=True)
 out={"schema":"c3x-p30-pressure-v1","scientific_stage":STAGE,"engine":e,"precommit_receipt_sha256":pre["receipt_sha256"],"rows":rows}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

def arm(c,base,run):
 w=p20.world_value(c,run["semantic"]["bestmove"])
 if w is None:raise SystemExit("P30_WORLD_JOIN")
 bw=base["world"]
 return {"receipt":run,"world":w,"action_changed":run["semantic"]["bestmove"]!=base["receipt"]["semantic"]["bestmove"],
   "fine_changed":(w["wdl"],w["precise_dtz"])!=(bw["wdl"],bw["precise_dtz"]),"coarse_changed":w["wdl"]!=bw["wdl"]}

def law_arms(path,protocol,c,base_trace):
 bw=p20.world_value(c,base_trace["semantic"]["bestmove"])
 if bw is None:raise SystemExit("P30_SHAM_WORLD")
 base={"receipt":{"semantic":base_trace["semantic"],"telemetry":base_trace["psm_telemetry"]},"world":bw,"action_changed":False,"fine_changed":False,"coarse_changed":False}
 arms={"00":base}
 for bits,mode in (("10","MASK_MAIN"),("01","MASK_QSEARCH"),("11","MASK_MAIN_QSEARCH"),("ALL","MASK_ALL")):
  run=history_search_hash(path,protocol,mode,c,LAW_CAP);arms[bits]=arm(c,base,run)
 return arms

def law_family(a):
 pre=load_pre(a.precommit);e=a.engine;paths={"OFF":a.off,"ON":a.on};protocol=pre["variants"][e]["OFF"]["protocol"]
 for pol in POLICIES:
  if sha_file(paths[pol])!=pre["variants"][e][pol]["sha256"]:raise SystemExit("P30_LAW_BINARY")
 src=[c for c in pre["cells"] if c["material_seed_name"]==a.family];rows=[];od=Path(a.out).parent
 if len(src)!=16:raise SystemExit("P30_FAMILY_N")
 for i,c in enumerate(src,1):
  rec={k:c[k] for k in ("candidate_sha256","material_seed_name","side_to_move","square","vertex","fen","world","states_by_budget")};rec["policy"]={}
  for pol in POLICIES:
   tp=od/"traces"/f"{e}-{c['candidate_sha256'][:16]}-1m-{pol}.csv"
   tr=trace_history_hash(paths[pol],protocol,c,LAW_CAP,tp,False)
   rec["policy"][pol]={"trace":tr,"targets":{e:{"arms":law_arms(paths[pol],protocol,c,tr)}}}
  rows.append(rec);print("P30_LAW",e,a.family,i,16,flush=True)
 out={"schema":"c3x-p30-law-family-v1","scientific_stage":STAGE,"engine":e,"family":a.family,
      "capacity_mib":LAW_CAP,"precommit_receipt_sha256":pre["receipt_sha256"],"rows":rows};seal(out)
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

def collect_pressure(path,engines=ENGINES):
 by={}
 for p in Path(path).rglob("*.json"):
  try:x=json.loads(p.read_text())
  except:continue
  if x.get("schema")!="c3x-p30-pressure-v1" or x.get("engine") not in engines:continue
  by[x["engine"]]=x
 if set(by)!=set(engines):raise SystemExit(f"P30_PRESSURE_SET {set(by)}")
 return by

def collect_law(path,engines):
 by={}
 for p in Path(path).rglob("*.json"):
  try:x=json.loads(p.read_text())
  except:continue
  if x.get("schema")!="c3x-p30-law-family-v1" or x.get("engine") not in engines:continue
  by[(x["engine"],x["family"])]=x
 exp={(e,f) for e in engines for f in p26.FAMILIES}
 if set(by)!=exp:raise SystemExit(f"P30_LAW_SET {len(by)}/{len(exp)}")
 return by

def pressure_maps(px):
 out={}
 for r in px["rows"]:
  s=r["states_by_budget"][str(ANCHOR)]["mapped"];sq=r["square"];out.setdefault(s,{})
  doses={}
  for cap in CAPS:
   off=r["capacity"][str(cap)]["OFF"];on=r["capacity"][str(cap)]["ON"]
   doses[str(cap)]={
    "victim_delta":on["victim"]["age_sensitive_victim_choices"]-off["victim"]["age_sensitive_victim_choices"],
    "replacement_delta":on["tt"]["full_key_replacements"]-off["tt"]["full_key_replacements"],
    "protected_reuse_delta":on["victim"]["protected_then_reused_events"]-off["victim"]["protected_then_reused_events"],
    "prime_survival_delta":on["tt"]["origin_delta_4"]-off["tt"]["origin_delta_4"],
    "full_hit_delta":on["tt"]["full_key_hits"]-off["tt"]["full_key_hits"],
    "signature_collision_delta":on["tt"]["signature_collisions"]-off["tt"]["signature_collisions"],
    "action_changed":on["semantic"]["bestmove"]!=off["semantic"]["bestmove"],
    "off_bestmove":off["semantic"]["bestmove"],"on_bestmove":on["semantic"]["bestmove"]
   }
  out[s][sq]={"doses":doses}
 return out

def signature(z):
 d=z["doses"]["1"]
 profile=[sign(z["doses"][str(c)]["replacement_delta"]) for c in CAPS]
 return [sign(d["victim_delta"]),sign(d["replacement_delta"]),sign(d["protected_reuse_delta"]),
         sign(d["prime_survival_delta"]),sign(d["full_hit_delta"])]+profile

def law_field(by,e,pre):
 states=sorted({c["states_by_budget"][str(ANCHOR)]["mapped"] for c in pre["cells"]});out={p:{} for p in POLICIES}
 for pol in POLICIES:
  for s in states:
   out[pol][s]={}
   for sq,mp in p26.SQUARES.items():
    v={}
    for bit,fam in mp.items():
     rr=[]
     for r in by[(e,fam)]["rows"]:
      if r["states_by_budget"][str(ANCHOR)]["mapped"]==s:rr.append({"targets":{e:r["policy"][pol]["targets"][e]}})
     if len(rr)!=2:raise SystemExit(f"P30_LAW_SUPPORT {e} {s} {fam} {len(rr)}")
     v[bit]={"rows":rr}
    ca=p20.square_analysis(v,e)["curvature"];out[pol][s][sq]=[ca["class"],ca["dominant_coordinate"],ca["dominant_sign"]]
 return out

def mask(a,b):return [a[i]!=b[i] for i in range(3)]

def donor_rule(a):
 pre=load_pre(a.precommit);press=collect_pressure(a.pressure,DONORS);laws=collect_law(a.law,DONORS)
 obs=[];rules=defaultdict(list)
 for e in DONORS:
  pm=pressure_maps(press[e]);lf=law_field(laws,e,pre)
  for s in pm:
   for sq,z in pm[s].items():
    sig=signature(z);lm=mask(lf["OFF"][s][sq],lf["ON"][s][sq])
    o={"engine":e,"state":s,"square":sq,"signature":sig,"law_mask":lm};obs.append(o);rules[",".join(map(str,sig))].append(o)
 ro={}
 for k,v in rules.items():
  es={q["engine"] for q in v};ms={tuple(q["law_mask"]) for q in v};ok=es==set(DONORS) and len(ms)==1
  ro[k]={"status":"RESOLVED" if ok else "UNRESOLVED","mask":list(next(iter(ms))) if ok else None,"n":len(v)}
 out={"schema":"c3x-p30-donor-rule-v1","scientific_stage":STAGE,"heldout_selective_consulted":False,
      "precommit_receipt_sha256":pre["receipt_sha256"],"rules":ro,"donor_observations":obs}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P30_RULE",sum(v["status"]=="RESOLVED" for v in ro.values()),len(ro))

def predict(a):
 pre=load_pre(a.precommit);rule=json.loads(Path(a.rule).read_text());press=collect_pressure(a.pressure,[HELDOUT])[HELDOUT]
 if rule.get("heldout_selective_consulted") is not False:raise SystemExit("P30_RULE_AUTH")
 pm=pressure_maps(press);pred={};resolved=0
 for s in pm:
  pred[s]={}
  for sq,z in pm[s].items():
   sig=signature(z);k=",".join(map(str,sig));r=rule["rules"].get(k,{"status":"UNRESOLVED"});ok=r["status"]=="RESOLVED";resolved+=int(ok)
   pred[s][sq]={"signature":sig,"rule_key":k,"status":"RESOLVED" if ok else "UNRESOLVED","predicted_mask":r.get("mask") if ok else None}
 out={"schema":"c3x-p30-heldout-prediction-v1","scientific_stage":STAGE,"heldout_selective_consulted":False,
      "precommit_receipt_sha256":pre["receipt_sha256"],"rule_receipt_sha256":rule["receipt_sha256"],
      "target":"ethereal_1mib_law","resolved":resolved,"total":16,"predictions":pred};seal(out)
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P30_PRED",resolved,16)

def label(d,law_mask):
 if any(law_mask):return "LAW_EFFECT"
 if d["full_hit_delta"]!=0 or d["action_changed"]:return "SEARCH_EFFECT"
 if d["protected_reuse_delta"]!=0:return "REUSE_EDGE"
 if d["replacement_delta"]!=0:return "REPLACEMENT_EDGE"
 if d["victim_delta"]!=0:return "VICTIM_ONLY"
 return "NULL_BEFORE_VICTIM"

def adjudicate(a):
 pre=load_pre(a.precommit);pr=json.loads(Path(a.prediction).read_text());press=collect_pressure(a.pressure);laws=collect_law(a.law,ENGINES)
 fields={e:law_field(laws,e,pre) for e in ENGINES};pm={e:pressure_maps(press[e]) for e in ENGINES}
 effects={};trans={}
 for e in ENGINES:
  changed=0;trans[e]={}
  for s in fields[e]["OFF"]:
   trans[e][s]={}
   for sq in p26.SQUARES:
    m=mask(fields[e]["OFF"][s][sq],fields[e]["ON"][s][sq]);trans[e][s][sq]=m;changed+=int(any(m))
  effects[e]={"changed_law_cells":changed,"total":16}
 dose={}
 for e in ENGINES:
  dose[e]={}
  for cap in CAPS:
   ds=[pm[e][s][sq]["doses"][str(cap)] for s in pm[e] for sq in pm[e][s]]
   dose[e][str(cap)]={
    "victim_shift_cells":sum(q["victim_delta"]!=0 for q in ds),
    "replacement_shift_cells":sum(q["replacement_delta"]!=0 for q in ds),
    "protected_reuse_shift_cells":sum(q["protected_reuse_delta"]!=0 for q in ds),
    "prime_survival_shift_cells":sum(q["prime_survival_delta"]!=0 for q in ds),
    "full_hit_shift_cells":sum(q["full_hit_delta"]!=0 for q in ds),
    "action_changed_cells":sum(q["action_changed"] for q in ds),"total":len(ds)}
 reopened=[c for c in CAPS if dose[HELDOUT][str(c)]["replacement_shift_cells"]>0]
 resolved=agree=0
 for s,q in pr["predictions"].items():
  for sq,z in q.items():
   if z["status"]=="RESOLVED":
    resolved+=1;agree+=int(trans[HELDOUT][s][sq]==z["predicted_mask"])
 cert={}
 for e in ENGINES:
  cert[e]={}
  for s in pm[e]:
   cert[e][s]={}
   for sq,z in pm[e][s].items():
    d=z["doses"]["1"];lm=trans[e][s][sq];lab=label(d,lm)
    cert[e][s][sq]={"label":lab,"hash_mib":1,"dose_response":z["doses"],"law_mask":lm,
      "sentence":f"At 1 MiB, age-on-hit changed victim eligibility by {d['victim_delta']}; committed replacements by {d['replacement_delta']}; protected-then-reused events by {d['protected_reuse_delta']}; full-key hits by {d['full_hit_delta']}; law mask={lm}."}
 universal=resolved==16 and agree==16
 if reopened:
  verdict="ETHEREAL_AGE_REPLACEMENT_EDGE_REOPENED_UNDER_PRESSURE"
  if universal:verdict+="_AND_CONDITIONAL_MORPHISM_RECOVERED"
  else:verdict+="_MEDIATOR_NOT_UNIVERSALLY_SUFFICIENT"
 else:verdict="ETHEREAL_REPLACEMENT_EDGE_REMAINS_NULL_UNDER_TESTED_PRESSURE"
 out={"schema":"c3x-p30-adjudication-v1","scientific_stage":STAGE,"precommit_receipt_sha256":pre["receipt_sha256"],
      "prediction_receipt_sha256":pr["receipt_sha256"],"law_effects_1mib":effects,"capacity_dose_response":dose,
      "ethereal_replacement_edge":{"reopened_capacities_mib":reopened,"highest_capacity_reopened_mib":max(reopened) if reopened else None},
      "conditional_morphism":{"resolved":resolved,"agreement":agree,"total":16,"universal":universal},
      "explanation_certificates":cert,"verdict":verdict,
      "authority_ceiling":"P29 fixed support; 1/4/16/64 MiB pressure trace; 1 MiB selective law; observer-only victim/full-hit witness; engine-computation explanation only"}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P30_ADJ",verdict,reopened,agree,resolved)

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("precommit");q.add_argument("--parent",required=True);q.add_argument("--constitution",required=True);q.add_argument("--build-dir",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=precommit)
 q=sp.add_parser("pressure");q.add_argument("--precommit",required=True);q.add_argument("--engine",choices=ENGINES,required=True);q.add_argument("--off",required=True);q.add_argument("--on",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=pressure)
 q=sp.add_parser("law");q.add_argument("--precommit",required=True);q.add_argument("--engine",choices=ENGINES,required=True);q.add_argument("--family",choices=p26.FAMILIES,required=True);q.add_argument("--off",required=True);q.add_argument("--on",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=law_family)
 q=sp.add_parser("rule");q.add_argument("--precommit",required=True);q.add_argument("--pressure",required=True);q.add_argument("--law",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=donor_rule)
 q=sp.add_parser("predict");q.add_argument("--precommit",required=True);q.add_argument("--rule",required=True);q.add_argument("--pressure",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=predict)
 q=sp.add_parser("adjudicate");q.add_argument("--precommit",required=True);q.add_argument("--prediction",required=True);q.add_argument("--pressure",required=True);q.add_argument("--law",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=adjudicate)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
