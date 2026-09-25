#!/usr/bin/env python3
import argparse,hashlib,json
from collections import defaultdict
from pathlib import Path
import p20_transport as p20
import p26_product_field as p26
import p27_age_morphism as p27

STAGE="C3X 0.7.0-G9.4-P28"
ENGINES=("stockfish_19","berserk","ethereal")
DONORS=("stockfish_19","berserk")
HELDOUT="ethereal"
POLICIES=("OFF","ON")
DOSES=(0,1,3,7)
MODES=("SHAM","MASK_MAIN","MASK_QSEARCH","MASK_MAIN_QSEARCH","MASK_ALL")
ANCHOR=80000
PRIME=20000
DECOY=20000

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()

def load_lawgen(p):
 x=json.loads(Path(p).read_text());c=x.get("constitution",{})
 if c.get("schema")!="c3x-lawgen-constitution-v4" or c.get("scientific_stage")!=STAGE or c.get("selective_outcomes_consulted") is not False:raise SystemExit("P28_LAWGEN")
 return x

def pick_cells(parent):
 by=defaultdict(list)
 for c in parent["cells"]:
  s=c["states_by_budget"][str(ANCHOR)]["mapped"]
  by[(c["material_seed_name"],c["side_to_move"],s)].append(c)
 out=[]
 for k,v in by.items():out.append(sorted(v,key=lambda z:z["candidate_sha256"])[0])
 if len(out)!=128:raise SystemExit(f"P28_CELL_N {len(out)}")
 return sorted(out,key=lambda z:z["candidate_sha256"])

def histories(chosen,parent):
 universe=sorted(parent["cells"],key=lambda x:x["candidate_sha256"]);n=len(universe);out=[]
 for c in chosen:
  start=int(c["candidate_sha256"][:8],16)%n;ds=[];j=1
  while len(ds)<7 and j<n+1:
   d=universe[(start+j)%n];j+=1
   if d["candidate_sha256"]==c["candidate_sha256"] or d["material_seed_name"]==c["material_seed_name"]:continue
   ds.append({"candidate_sha256":d["candidate_sha256"],"fen":d["fen"],"family":d["material_seed_name"]})
  if len(ds)!=7:raise SystemExit("P28_DECOY")
  z={k:c[k] for k in ("candidate_sha256","material_seed_name","side_to_move","square","vertex","fen","world","states_by_budget")}
  z["decoys"]=ds;out.append(z)
 return out

def precommit(a):
 parent=p26.load_pre(a.parent);law=load_lawgen(a.constitution);b=Path(a.build_dir)
 variants={};protocol={"stockfish_19":"stockfish_uci","berserk":"env","ethereal":"env"}
 for e in ENGINES:
  variants[e]={}
  for pol in POLICIES:
   fs=list(b.rglob(f"c3x-p28-{e}-{pol.lower()}"))
   if len(fs)!=1:raise SystemExit(f"P28_BIN {e} {pol} {len(fs)}")
   variants[e][pol]={"sha256":sha_file(fs[0]),"protocol":protocol[e]}
 cells=histories(pick_cells(parent),parent)
 out={"schema":"c3x-p28-precommit-v1","scientific_stage":STAGE,"selective_outcomes_consulted":False,
  "lawgen_constitution_sha256":law["constitution_sha256"],"parent_p26_receipt_sha256":parent["receipt_sha256"],
  "parent_p27_closure":"09cf2eb8e943e49f74242d06a1370d4e81d5bb78",
  "doses":list(DOSES),"anchor_dose":3,"prime_nodes":PRIME,"decoy_nodes":DECOY,"measurement_nodes":ANCHOR,
  "threads":1,"hash_mib":64,"variants":variants,
  "selection":"lexicographically first inherited P26 cell per family×side×mapped-state","cells":cells,
  "collision_graph":{"status":"HOLD_NO_FULL_KEY_TRACE","reason":"aggregate PSM telemetry has no full 64-bit key trace"}}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P28_PRECOMMIT",out["receipt_sha256"],len(cells))

def load_pre(p):
 x=json.loads(Path(p).read_text())
 if x.get("schema")!="c3x-p28-precommit-v1" or x.get("selective_outcomes_consulted") is not False:raise SystemExit("P28_PRE")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P28_PRE_HASH")
 return x

def telnorm(t,protocol):
 if protocol=="env":return (int(t.get("probes_main",0)),int(t.get("hits_main",0)),int(t.get("probes_qsearch",0)),int(t.get("hits_qsearch",0)))
 return (int(t.get("probes_main",0)),int(t.get("raw_hits_main",0)),int(t.get("probes_qsearch",0)),int(t.get("raw_hits_qsearch",0)))

def history(path,protocol,mode,c,dose):
 p,_=p27.setup(path,protocol,mode)
 try:
  _,prev=p27.go(p,c["fen"],PRIME,protocol)
  for x in c["decoys"][:dose]:_,prev=p27.go(p,x["fen"],DECOY,protocol)
  sem,tel=p27.go(p,c["fen"],ANCHOR,protocol)
  if protocol=="env":tel=p27.tdelta(tel,prev)
  pm,hm,pq,hq=telnorm(tel,protocol)
  return {"semantic":sem,"telemetry":tel,"reuse":{"probes_main":pm,"hits_main":hm,"probes_qsearch":pq,"hits_qsearch":hq,"probes":pm+pq,"hits":hm+hq}}
 finally:
  p.terminate()
  try:p.communicate(timeout=3)
  except:p.kill();p.communicate()

def arm(c,base,run):
 w=p20.world_value(c,run["semantic"]["bestmove"])
 if w is None:raise SystemExit("P28_WORLD_JOIN")
 bw=base["world"]
 return {"receipt":run,"world":w,"action_changed":run["semantic"]["bestmove"]!=base["receipt"]["semantic"]["bestmove"],
  "fine_changed":(w["wdl"],w["precise_dtz"])!=(bw["wdl"],bw["precise_dtz"]),"coarse_changed":w["wdl"]!=bw["wdl"]}

def vertex(a):
 pre=load_pre(a.precommit);e=a.engine
 protocol=pre["variants"][e]["OFF"]["protocol"];paths={"OFF":a.off,"ON":a.on}
 for pol in POLICIES:
  if sha_file(paths[pol])!=pre["variants"][e][pol]["sha256"]:raise SystemExit("P28_BINARY")
 src=[c for c in pre["cells"] if c["material_seed_name"]==a.family]
 if len(src)!=16:raise SystemExit("P28_FAMILY_N")
 rows=[]
 for i,c in enumerate(src,1):
  rec={k:c[k] for k in ("candidate_sha256","material_seed_name","side_to_move","square","vertex","fen","world","states_by_budget")};rec["age"]={}
  for pol in POLICIES:
   dose={}
   for d in DOSES:dose[str(d)]={"SHAM":history(paths[pol],protocol,"SHAM",c,d)}
   if a.mode=="full":
    for m in MODES[1:]:dose["3"][m]=history(paths[pol],protocol,m,c,3)
   rec["age"][pol]={"dose":dose}
  rows.append(rec);print("P28_VERTEX",a.mode,e,a.family,i,16,flush=True)
 out={"schema":"c3x-p28-vertex-v1","scientific_stage":STAGE,"mode":a.mode,"engine":e,"family":a.family,
  "precommit_receipt_sha256":pre["receipt_sha256"],"rows":rows};seal(out)
 Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

def collect(path,engines,mode):
 by={}
 for p in Path(path).rglob("*.json"):
  try:x=json.loads(p.read_text())
  except:continue
  if x.get("schema")!="c3x-p28-vertex-v1" or x.get("mode")!=mode or x.get("engine") not in engines:continue
  k=(x["engine"],x["family"])
  if k in by:raise SystemExit("P28_DUP")
  by[k]=x
 exp={(e,f) for e in engines for f in p26.FAMILIES}
 if set(by)!=exp:raise SystemExit(f"P28_SET {len(by)}/{len(exp)}")
 return by

def fpfield(by,e,pre):
 states=sorted({c["states_by_budget"][str(ANCHOR)]["mapped"] for c in pre["cells"]});out={pol:{} for pol in POLICIES}
 for pol in POLICIES:
  for s in states:
   out[pol][s]={}
   for sq,mp in p26.SQUARES.items():
    v={}
    for bit,fam in mp.items():
     rr=[]
     for r in by[(e,fam)]["rows"]:
      if r["states_by_budget"][str(ANCHOR)]["mapped"]!=s:continue
      z=r["age"][pol]["dose"]["3"];sh=z["SHAM"];bw=p20.world_value(r,sh["semantic"]["bestmove"])
      base={"receipt":sh,"world":bw,"action_changed":False,"fine_changed":False,"coarse_changed":False}
      arms={"00":base}
      for b,m in (("10","MASK_MAIN"),("01","MASK_QSEARCH"),("11","MASK_MAIN_QSEARCH"),("ALL","MASK_ALL")):arms[b]=arm(r,base,z[m])
      rr.append({"targets":{e:{"arms":arms}}})
     if len(rr)!=2:raise SystemExit("P28_SUPPORT")
     v[bit]={"rows":rr}
    q=p20.square_analysis(v,e)["curvature"];out[pol][s][sq]=[q["class"],q["dominant_coordinate"],q["dominant_sign"]]
 return out

def msign(by,e,pre):
 states=sorted({c["states_by_budget"][str(ANCHOR)]["mapped"] for c in pre["cells"]});out={}
 fams_by_sq={sq:set(mp.values()) for sq,mp in p26.SQUARES.items()}
 for s in states:
  out[s]={}
  for sq,fams in fams_by_sq.items():
   sig=[]
   for d in DOSES:
    sums={pol:[0,0] for pol in POLICIES}
    for fam in fams:
     for r in by[(e,fam)]["rows"]:
      if r["states_by_budget"][str(ANCHOR)]["mapped"]!=s:continue
      q=r["age"][pol]["dose"][str(d)] if False else None
      for pol in POLICIES:
       u=r["age"][pol]["dose"][str(d)]["SHAM"]["reuse"];sums[pol][0]+=u["hits"];sums[pol][1]+=u["probes"]
    ho,po=sums["OFF"];hn,pn=sums["ON"];x=hn*po-ho*pn;sig.append(1 if x>0 else -1 if x<0 else 0)
   out[s][sq]=sig
 return out

def mask(a,b):return [a[i]!=b[i] for i in range(3)]

def rule(a):
 pre=load_pre(a.precommit);by=collect(a.results,DONORS,"full")
 obs=[];fields={};sigs={}
 for e in DONORS:
  fields[e]=fpfield(by,e,pre);sigs[e]=msign(by,e,pre)
  for s in sigs[e]:
   for sq,sg in sigs[e][s].items():obs.append({"engine":e,"state":s,"square":sq,"signature":sg,"law_mask":mask(fields[e]["OFF"][s][sq],fields[e]["ON"][s][sq])})
 groups=defaultdict(list)
 for z in obs:groups[",".join(map(str,z["signature"]))].append(z)
 rules={}
 for k,v in groups.items():
  engines={z["engine"] for z in v};masks={tuple(z["law_mask"]) for z in v}
  if engines==set(DONORS) and len(masks)==1:rules[k]={"status":"RESOLVED","mask":list(next(iter(masks))),"n":len(v)}
  else:rules[k]={"status":"UNRESOLVED","n":len(v)}
 out={"schema":"c3x-p28-donor-rule-v1","scientific_stage":STAGE,"heldout_selective_consulted":False,
  "precommit_receipt_sha256":pre["receipt_sha256"],"signature":"four exact hit-rate signs","rules":rules,"donor_observations":obs}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P28_RULE",sum(z["status"]=="RESOLVED" for z in rules.values()),len(rules))

def predict(a):
 pre=load_pre(a.precommit);r=json.loads(Path(a.rule).read_text())
 if r.get("heldout_selective_consulted") is not False:raise SystemExit("P28_RULE_AUTH")
 by=collect(a.mediator,[HELDOUT],"mediator");sg=msign(by,HELDOUT,pre);pred={};resolved=0
 for s in sg:
  pred[s]={}
  for sq,v in sg[s].items():
   k=",".join(map(str,v));z=r["rules"].get(k,{"status":"UNRESOLVED"})
   ok=z["status"]=="RESOLVED";resolved+=int(ok)
   pred[s][sq]={"signature":v,"rule_key":k,"status":"RESOLVED" if ok else "UNRESOLVED","predicted_mask":z.get("mask") if ok else None}
 out={"schema":"c3x-p28-heldout-prediction-v1","scientific_stage":STAGE,"heldout_selective_consulted":False,
  "precommit_receipt_sha256":pre["receipt_sha256"],"rule_receipt_sha256":r["receipt_sha256"],"predictions":pred,"resolved":resolved,"total":16}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P28_PRED",resolved,16)

def adjudicate(a):
 pre=load_pre(a.precommit);pr=json.loads(Path(a.prediction).read_text())
 donors=collect(a.donors,DONORS,"full");held=collect(a.heldout,[HELDOUT],"full");med=collect(a.mediator,[HELDOUT],"mediator")
 allby={**donors,**held};fields={e:fpfield(allby,e,pre) for e in ENGINES};sigs={e:msign(allby,e,pre) for e in ENGINES}
 medsig=msign(med,HELDOUT,pre)
 if medsig!=sigs[HELDOUT]:raise SystemExit("P28_HELDOUT_MEDIATOR_REPLAY_DRIFT")
 effects={};trans={}
 for e in ENGINES:
  changed=0;trans[e]={}
  for s in fields[e]["OFF"]:
   trans[e][s]={}
   for sq in p26.SQUARES:
    m=mask(fields[e]["OFF"][s][sq],fields[e]["ON"][s][sq]);trans[e][s][sq]=m;changed+=int(any(m))
  effects[e]={"changed_law_cells":changed,"total":16}
 dose={e:{str(d):0 for d in DOSES} for e in ENGINES}
 for e in ENGINES:
  for s in sigs[e]:
   for sq,v in sigs[e][s].items():
    for i,d in enumerate(DOSES):dose[e][str(d)]+=int(v[i]!=0)
 resolved=agree=0
 for s,q in pr["predictions"].items():
  for sq,z in q.items():
   if z["status"]=="RESOLVED":
    resolved+=1;agree+=int(trans[HELDOUT][s][sq]==z["predicted_mask"])
 universal=resolved==16 and agree==16
 emed=sum(any(v) for q in sigs[HELDOUT].values() for v in q.values());elaw=effects[HELDOUT]["changed_law_cells"]
 loc="LAW_NULL_NOT_REPLICATED" if elaw else ("LOW_LEVEL_MEDIATOR_EFFECT_WITH_FROZEN_LAW_NULL" if emed else "UPSTREAM_MEDIATOR_NULL")
 verdict="CONDITIONAL_CAUSAL_MORPHISM_RECOVERED" if universal else "ARCHITECTURE_CONDITIONING_PERSISTS_NO_UNIVERSAL_CONDITIONAL_MORPHISM"
 out={"schema":"c3x-p28-adjudication-v1","scientific_stage":STAGE,"precommit_receipt_sha256":pre["receipt_sha256"],
  "within_architecture_law_effects":effects,"dose_nonzero_mediator_cells":dose,
  "ethereal":{"nonzero_mediator_signature_cells":emed,"law_changed_cells":elaw,"null_localization":loc},
  "conditional_morphism":{"resolved":resolved,"agreement":agree,"total":16,"universal":universal},
  "collision_graph":pre["collision_graph"],"verdict":verdict,
  "authority_ceiling":"TT reuse hit-rate is an operational survival/replacement-pressure proxy, not exact entry replacement; 80k law anchor only; indexing held without full-key trace"}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P28_ADJ",verdict,loc,agree,resolved)

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 p=sp.add_parser("precommit");p.add_argument("--parent",required=True);p.add_argument("--constitution",required=True);p.add_argument("--build-dir",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=precommit)
 p=sp.add_parser("vertex");p.add_argument("--precommit",required=True);p.add_argument("--engine",choices=ENGINES,required=True);p.add_argument("--family",choices=p26.FAMILIES,required=True);p.add_argument("--off",required=True);p.add_argument("--on",required=True);p.add_argument("--mode",choices=["full","mediator"],required=True);p.add_argument("--out",required=True);p.set_defaults(fn=vertex)
 p=sp.add_parser("rule");p.add_argument("--precommit",required=True);p.add_argument("--results",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=rule)
 p=sp.add_parser("predict");p.add_argument("--precommit",required=True);p.add_argument("--rule",required=True);p.add_argument("--mediator",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=predict)
 p=sp.add_parser("adjudicate");p.add_argument("--precommit",required=True);p.add_argument("--prediction",required=True);p.add_argument("--donors",required=True);p.add_argument("--mediator",required=True);p.add_argument("--heldout",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=adjudicate)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
