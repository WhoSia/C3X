#!/usr/bin/env python3
import argparse,hashlib,json,os,tempfile
from collections import Counter,defaultdict
from contextlib import contextmanager
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"harness"))
import p32_event_court as p32

STAGE="C3X 0.7.0-G9.5-P11"
ENGINES=("stockfish_19","berserk","ethereal")
PATCH_MODES=("NONE","LOWER","UPPER","BOTH")

def load(p): return json.loads(Path(p).read_text())
def canon(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o): return hashlib.sha256(canon(o)).hexdigest()
def seal(o):
 o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def sha_file(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def public_sem(s):
 return {k:s.get(k) for k in ("bestmove","score","wdl","depth","seldepth","nodes","pv")}

@contextmanager
def envset(**vals):
 old={k:os.environ.get(k) for k in vals}
 try:
  for k,v in vals.items():
   if v is None: os.environ.pop(k,None)
   else: os.environ[k]=str(v)
  yield
 finally:
  for k,v in old.items():
   if v is None: os.environ.pop(k,None)
   else: os.environ[k]=v

def run(path,protocol,cell,p32mode,family,frontier,addresses,work,patch="NONE",p34mode="BASE",q3file=None,mediator_all=False):
 with envset(C3X_P11_PATCH=patch,C3X_P34_MODE=p34mode,C3X_P34_LEVEL="3",
             C3X_P34_SET_FILE=str(q3file) if q3file else None,
             C3X_P11_MEDIATOR_ALL="1" if mediator_all else "0"):
  return p32.run_history(path,protocol,cell,p32mode,family,frontier,addresses,work)

def depth_band(d):
 d=int(d)
 return "LE4" if d<=4 else "D5_8" if d<=8 else "D9_12" if d<=12 else "D13_PLUS"

def private_visit_summary(tr):
 es=tr["events"]
 uniq={(e["key"],e["ply"]) for e in es}
 p1={e["key"] for e in es if int(e["ply"])==1}
 by=Counter((e["class"],int(e["ply"]),depth_band(e["depth"])) for e in es)
 windows=defaultdict(set)
 for e in es: windows[(e["key"],int(e["ply"]))].add((int(e["alpha"]),int(e["beta"])))
 revisits=sum(len(v)>1 for v in windows.values())
 cut=[e for e in es if e["class"]=="CUTOFF"]
 return {
  "event_count":len(es),"unique_private_node_keys":len(uniq),"ply1_unique_private_keys":len(p1),
  "multiwindow_revisit_proxy_nodes":revisits,"cutoff_events":len(cut),
  "visits_by_class_ply_depth":{"|".join(map(str,k)):v for k,v in sorted(by.items())}
 }

def summary_delta(a,b):
 keys=set(a["visits_by_class_ply_depth"])|set(b["visits_by_class_ply_depth"])
 d={k:b["visits_by_class_ply_depth"].get(k,0)-a["visits_by_class_ply_depth"].get(k,0) for k in sorted(keys)}
 return {
  "event_count":b["event_count"]-a["event_count"],
  "unique_private_node_keys":b["unique_private_node_keys"]-a["unique_private_node_keys"],
  "ply1_unique_private_keys":b["ply1_unique_private_keys"]-a["ply1_unique_private_keys"],
  "multiwindow_revisit_proxy_nodes":b["multiwindow_revisit_proxy_nodes"]-a["multiwindow_revisit_proxy_nodes"],
  "cutoff_events":b["cutoff_events"]-a["cutoff_events"],
  "visits_by_class_ply_depth":{k:v for k,v in d.items() if v}
 }

def first_divergence(base,cf,start):
 a=base["events"];b=cf["events"];i=max(0,start)
 while i<min(len(a),len(b)) and a[i]["address_id"]==b[i]["address_id"]: i+=1
 if i==len(a)==len(b): return None
 return i

def first_cutoff_divergence(base,cf,start):
 a=[(i,e) for i,e in enumerate(base["events"]) if i>=start and e["class"]=="CUTOFF"]
 b=[(i,e) for i,e in enumerate(cf["events"]) if i>=start and e["class"]=="CUTOFF"]
 j=0
 while j<min(len(a),len(b)) and a[j][1]["address_id"]==b[j][1]["address_id"]: j+=1
 if j==len(a)==len(b): return None
 z=a[j] if j<len(a) else None
 y=b[j] if j<len(b) else None
 def pub(q):
  if q is None:return None
  i,e=q;return {"trace_ordinal":i,"ply":e["ply"],"depth":e["depth"],"bound":e["bound"]}
 return {"baseline":pub(z),"target_counterfactual":pub(y)}

def p34_bucket(e):
 pb=0 if e["ply"]<=0 else 1 if e["ply"]==1 else 2 if e["ply"]==2 else 3 if e["ply"]<=4 else 4 if e["ply"]<=8 else 5
 db=0 if e["depth"]<=0 else 1 if e["depth"]<=4 else 2 if e["depth"]<=8 else 3 if e["depth"]<=12 else 4 if e["depth"]<=16 else 5 if e["depth"]<=24 else 6
 payload=0 if e["payload"]==0 else 1 if e["payload"]==1 else 2 if e["payload"]==-1 else 3 if e["payload"]>0 else 4
 wr=0 if e["tt_value"]<=e["alpha"] else 2 if e["tt_value"]>=e["beta"] else 1
 return [1 if e["scope"]=="QSEARCH" else 0,int(e["class_id"]),pb,int(e["bound"]),payload,db,1 if e["tt_move"] else 0,wr]

def pick_mediator(base,cf,target_ordinal):
 i=first_divergence(base,cf,target_ordinal+1)
 if i is None:return None,None
 # P34 downstream intervention is deliberately bounded to ply <= 8.
 tail=[e for e in base["events"][i:] if int(e["ply"])<=8]
 for cls in ("CUTOFF","MOVE_ORDER_SEED",None):
  for e in tail:
   if cls is None or e["class"]==cls:
    return e,p34_bucket(e)
 return None,None

def write_q3(path,row):
 Path(path).write_text("\t".join(str(x) for x in row)+"\n")

def archetype_ok(r):
 a=r.get("a0_archetype",{})
 return bool(r.get("root_change")) and a.get("scope")=="MAIN" and a.get("ply_bucket")=="PLY1" and a.get("depth_band")=="D5_8" and a.get("key_history")=="REPEAT_KEY" and a.get("same_key_move_relation")=="SAME_MOVE" and a.get("bound_bucket") in ("LOWER","UPPER")

def precommit(a):
 c=load(a.constitution);closure=load(a.p10_closure);merged=load(a.p10_merged);p10pre=load(a.p10_precommit)
 if c.get("schema")!="c3x-g95-p11-constitution-v1" or c["parent"]["closure_receipt_sha256"]!=closure.get("receipt_sha256"):raise SystemExit("P11_PARENT")
 if merged.get("schema")!="c3x-p10-event-merged-v1" or p10pre.get("schema")!="c3x-g95-p10-precommit-v1":raise SystemExit("P11_INPUT")
 targets=[r for r in merged["records"] if archetype_ok(r)]
 if len(targets)!=int(c["support_gate"]["parent_targets_required"]):raise SystemExit(f"P11_TARGET_N {len(targets)}")
 cases={(x["engine"],x["position_id"]):x for x in p10pre["cases"]}
 outt=[]
 for r in sorted(targets,key=lambda z:z["record_id"]):
  k=(r["engine"],r["position_id"])
  if k not in cases:raise SystemExit("P11_CELL_JOIN")
  z={x:r[x] for x in ("record_id","engine","position_id","source_id","event_id","event_address_public","a0_archetype","baseline","counterfactual","first_pv_divergence")}
  z["target_id"]=hashlib.sha256(r["record_id"].encode()).hexdigest()[:16]
  z["cell"]=cases[k]["cell"];outt.append(z)
 variants={}
 for e in ENGINES:
  fs=list(Path(a.build_dir).rglob(f"c3x-p11-{e}"))
  if len(fs)!=1:raise SystemExit(f"P11_BINARY_SET {e} {len(fs)}")
  variants[e]={"sha256":sha_file(fs[0]),"protocol":p32.protocol_for(e)}
 out={"schema":"c3x-g95-p11-precommit-v1","scientific_stage":STAGE,"selective_p11_outcomes_consulted":False,
      "constitution_sha256":digest(c),"parent_p10_receipt_sha256":closure["receipt_sha256"],
      "parent_target_count":len(outt),"variants":variants,"targets":outt,
      "mediation":c["mediation"],"patch_contrast":c["patch_contrast"],"claim_ceiling":c["claim_ceiling"]}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P11_PRECOMMIT",out["receipt_sha256"],len(outt))

def load_pre(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p11-precommit-v1" or x.get("selective_p11_outcomes_consulted") is not False:raise SystemExit("P11_PRE")
 y=dict(x);h=y.pop("receipt_sha256")
 if digest(y)!=h:raise SystemExit("P11_PRE_HASH")
 return x

def case_run(a):
 pre=load_pre(a.precommit);t=next((x for x in pre["targets"] if x["target_id"]==a.target_id),None)
 if not t:raise SystemExit("P11_TARGET_ID")
 v=pre["variants"][t["engine"]]
 if sha_file(a.binary)!=v["sha256"]:raise SystemExit("P11_BINARY")
 root=Path(a.out).parent/f".p11-{a.target_id}";root.mkdir(parents=True,exist_ok=True)
 base=run(a.binary,v["protocol"],t["cell"],"CATALOG","MOVE_ORDER",1,None,root/"base",patch="NONE")
 matches=[(i,e) for i,e in enumerate(base["trace"]["events"]) if e["address_id"]==t["event_id"]]
 if len(matches)!=1:
  out={"schema":"c3x-g95-p11-case-v1","scientific_stage":STAGE,"target_id":a.target_id,"engine":t["engine"],"position_id":t["position_id"],
       "bound_sign":t["a0_archetype"]["bound_bucket"],"status":"EVENT_ADDRESS_DRIFTS","match_count":len(matches)}
  seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");return
 ordinal,event=matches[0];addr=dict(event["address"]);addr["address_id"]=event["address_id"]
 if base["semantic"].get("bestmove")!=t["baseline"].get("bestmove"):raise SystemExit("P11_PARENT_BASELINE_DRIFT")
 tc=run(a.binary,v["protocol"],t["cell"],"REMOVE_SET","MOVE_ORDER",1,[addr],root/"target",patch="NONE")
 fired=bool(tc["trace"]["targets"] and tc["trace"]["targets"][0]["fired"])
 exact=fired and tc["semantic"].get("bestmove")==t["counterfactual"].get("bestmove")
 bsum=private_visit_summary(base["trace"]);tsum=private_visit_summary(tc["trace"])
 div=first_divergence(base["trace"],tc["trace"],ordinal+1)
 cdiv=first_cutoff_divergence(base["trace"],tc["trace"],ordinal+1)
 cand,q3=pick_mediator(base["trace"],tc["trace"],ordinal)
 med=None;both=None;medstat="NO_POST_TARGET_MEDIATOR_CANDIDATE"
 mediator_doc=None
 if q3 is not None:
  qf=root/"mediator.tsv";write_q3(qf,q3)
  med=run(a.binary,v["protocol"],t["cell"],"BASE","MOVE_ORDER",8,None,root/"mediator",patch="NONE",p34mode="REMOVE_SET",q3file=qf,mediator_all=True)
  both=run(a.binary,v["protocol"],t["cell"],"REMOVE_SET","MOVE_ORDER",8,[addr],root/"target-plus-mediator",patch="NONE",p34mode="REMOVE_SET",q3file=qf,mediator_all=True)
  bm=base["semantic"].get("bestmove");tm=tc["semantic"].get("bestmove");mm=med["semantic"].get("bestmove");xm=both["semantic"].get("bestmove")
  if mm==tm and xm==tm:medstat="MEDIATOR_CLASS_CAUSAL_ALIGNMENT"
  elif mm!=bm or xm!=tm:medstat="MEDIATOR_CLASS_INTERACTION_REDIRECT"
  else:medstat="OBSERVED_PATH_DIVERGENCE"
  mediator_doc={"class":cand["class"],"scope":cand["scope"],"ply":cand["ply"],"depth_band":depth_band(cand["depth"]),
                "bound":cand["bound"],"q3":q3,"m_only_bestmove":mm,"t_plus_m_bestmove":xm}
 else:
  medstat="OBSERVED_PATH_DIVERGENCE" if div is not None else "NO_POST_TARGET_MEDIATOR_CANDIDATE"
 out={"schema":"c3x-g95-p11-case-v1","scientific_stage":STAGE,"target_id":a.target_id,"record_id":t["record_id"],
      "engine":t["engine"],"position_id":t["position_id"],"source_id":t["source_id"],"bound_sign":t["a0_archetype"]["bound_bucket"],
      "status":"PASS" if exact else "PARENT_REPLAY_DRIFT","parent_exact_replay":exact,"target_fired":fired,
      "baseline_move":base["semantic"].get("bestmove"),"target_counterfactual_move":tc["semantic"].get("bestmove"),
      "first_trace_divergence_ordinal":div,"first_cutoff_divergence":cdiv,
      "visit_delta_summary":summary_delta(bsum,tsum),
      "research_proxy_delta":tsum["multiwindow_revisit_proxy_nodes"]-bsum["multiwindow_revisit_proxy_nodes"],
      "mediator_class":mediator_doc,"mediation_status":medstat,"first_pv_divergence":t.get("first_pv_divergence"),
      "raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P11_CASE",a.target_id,out["status"],medstat,div)

def locate_case(p9pre,engine,position_id):
 for c in p9pre["cases"]:
  if c["engine"]==engine and c["position_id"]==position_id:return c
 raise SystemExit("P11_REG_CASE_JOIN")

def fulladdr(d):
 z=dict(d)
 if "address_id" not in z:z["address_id"]=digest({k:z[k] for k in ("scope","class","class_id","key","ply","depth","tt_move","bound","payload","occ")})
 return z

def regression(a):
 pre=load_pre(a.precommit);seed=load(a.p10_seed_replay);p9pre=load(a.p9_precommit)
 if seed.get("schema")!="c3x-g95-p10-p9-seed-replay-v1" or seed.get("case_count")!=7:raise SystemExit("P11_REG_PARENT")
 bins={"stockfish_19":a.stockfish_bin,"berserk":a.berserk_bin,"ethereal":a.ethereal_bin}
 rows=[];none_ok=True
 for z in seed["cases"]:
  eng=z["engine"];case=locate_case(p9pre,eng,z["position_id"]);path=bins[eng]
  if sha_file(path)!=pre["variants"][eng]["sha256"]:raise SystemExit("P11_REG_BINARY")
  proto=pre["variants"][eng]["protocol"];pos=fulladdr(z["positive_event_address"]);ctrl=z.get("matched_control")
  for mode in PATCH_MODES:
   root=Path(a.out).parent/".p11-reg"/f'{z["case_index"]:02d}-{eng}-{mode.lower()}'
   base=run(path,proto,case["cell"],"CATALOG",case["family"],case["frontier"],None,root/"base",patch=mode)
   cf=run(path,proto,case["cell"],"REMOVE_SET",case["family"],case["frontier"],[pos],root/"positive",patch=mode)
   fired=bool(cf["trace"]["targets"] and cf["trace"]["targets"][0]["fired"])
   control_break=False;control_fired=None;control_move=None
   if ctrl:
    ca=fulladdr(ctrl["event_address"])
    cr=run(path,proto,case["cell"],"REMOVE_SET",case["family"],case["frontier"],[ca],root/"control",patch=mode)
    control_fired=bool(cr["trace"]["targets"] and cr["trace"]["targets"][0]["fired"])
    control_move=cr["semantic"].get("bestmove");control_break=control_fired and control_move!=base["semantic"].get("bestmove")
   bm=base["semantic"].get("bestmove");cm=cf["semantic"].get("bestmove")
   if not fired:cl="EVENT_ADDRESS_DRIFTS"
   elif control_break:cl="CONTROL_BREAKS"
   elif bm!=z["expected_baseline_bestmove"]:cl="BASELINE_DRIFT"
   elif cm==z["expected_counterfactual_bestmove"]:cl="SURVIVES_EXACTLY"
   elif cm==bm:cl="EFFECT_DISAPPEARS"
   else:cl="EFFECT_REDIRECTS"
   if mode=="NONE" and cl!="SURVIVES_EXACTLY":none_ok=False
   rows.append({"case_index":z["case_index"],"engine":eng,"position_id":z["position_id"],"patch_mode":mode,
                "classification":cl,"target_fired":fired,"baseline_move":bm,"counterfactual_move":cm,
                "expected_baseline_move":z["expected_baseline_bestmove"],"expected_counterfactual_move":z["expected_counterfactual_bestmove"],
                "control_present":bool(ctrl),"control_fired":control_fired,"control_move":control_move,"control_break":control_break})
 out={"schema":"c3x-g95-p11-patch-regression-v1","scientific_stage":STAGE,"authority":"ENGINEERING_PATCH_CONTRAST_ONLY",
      "fresh_confirmatory_vote":False,"case_count":7,"rows":rows,"none_mode_pass":none_ok}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P11_REGRESSION","PASS" if none_ok else "FAIL",len(rows))
 if not none_ok:raise SystemExit(2)

def adjudicate(a):
 pre=load_pre(a.precommit);reg=load(a.regression);cases=[]
 for p in Path(a.cases).rglob("*.json"):
  try:x=load(p)
  except:continue
  if x.get("schema")=="c3x-g95-p11-case-v1":cases.append(x)
 if len(cases)!=pre["parent_target_count"]:raise SystemExit(f"P11_CASE_N {len(cases)}")
 cases=sorted(cases,key=lambda z:z["target_id"])
 exact=sum(x.get("parent_exact_replay") is True for x in cases)
 eng=sorted({x["engine"] for x in cases if x.get("status")=="PASS"})
 bounds=sorted({x["bound_sign"] for x in cases if x.get("status")=="PASS"})
 med=Counter(x.get("mediation_status") for x in cases)
 pos=defaultdict(set)
 for x in cases:
  if x.get("status")=="PASS":pos[x["position_id"]].add(x["engine"])
 cross={k:sorted(v) for k,v in pos.items() if len(v)>=2}
 patch=Counter((x["patch_mode"],x["classification"]) for x in reg["rows"])
 support=exact==len(cases) and len(eng)>=2 and len(bounds)>=2 and reg.get("none_mode_pass") is True
 verdict="P11_BOUNDED_MEDIATION_AND_PATCH_DIAGNOSTIC_CLOSED" if support else "P11_MEDIATION_OR_REGRESSION_HOLD"
 out={"schema":"c3x-g95-p11-adjudication-v1","scientific_stage":STAGE,"authority":"CONDITIONAL_MECHANISM_FOLLOWUP",
      "fresh_confirmatory_vote":False,"status":"CLOSED_PASS" if support else "HOLD","verdict":verdict,
      "support":{"pass":support,"targets":len(cases),"exact_parent_replays":exact,"valid_engines":eng,"valid_bound_variants":bounds,
                 "same_position_cross_engine":cross},
      "mediation_status_counts":dict(sorted(med.items())),
      "patch_classification_counts":{f"{k[0]}|{k[1]}":v for k,v in sorted(patch.items())},
      "cases":cases,"patch_regression_receipt_sha256":reg["receipt_sha256"],"claim_ceiling":pre["claim_ceiling"],
      "raw_tt_key_emitted":False}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 lines=["# C3X G9.5-P11 — Minimal TT Diagnostic Surface","",f"Status: **{out['status']} / {verdict}**",
        f"Inherited witnesses: **{len(cases)}**; exact parent replays: **{exact}/{len(cases)}**",
        f"Cross-engine same-position mediation sets: **{len(cross)}**","",
        "## Witness diagnostics"]
 for x in cases:
  m=x.get("mediator_class") or {}
  lines.append(f"- {x['engine']} / {x['position_id']} / {x['bound_sign']}: {x.get('baseline_move')}→{x.get('target_counterfactual_move')}; first-div={x.get('first_trace_divergence_ordinal')}; cutoffΔ={x.get('visit_delta_summary',{}).get('cutoff_events')}; mediator={m.get('class','none')} / {x.get('mediation_status')}")
 lines += ["","## Patch regression"]
 for mode in PATCH_MODES:
  q=Counter(x["classification"] for x in reg["rows"] if x["patch_mode"]==mode)
  lines.append(f"- {mode}: "+", ".join(f"{k}={v}" for k,v in sorted(q.items())))
 lines += ["","Raw TT keys are not emitted. Mediation is bounded to the frozen P34-Q3 class intervention and is not a formal natural indirect effect."]
 Path(a.markdown).write_text("\n".join(lines)+"\n")
 print("P11_ADJUDICATE",out["status"],verdict,exact,len(cross))

def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
 q=sp.add_parser("precommit");q.add_argument("--constitution",required=True);q.add_argument("--p10-closure",required=True);q.add_argument("--p10-merged",required=True);q.add_argument("--p10-precommit",required=True);q.add_argument("--build-dir",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=precommit)
 q=sp.add_parser("case");q.add_argument("--precommit",required=True);q.add_argument("--target-id",required=True);q.add_argument("--binary",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=case_run)
 q=sp.add_parser("regression");q.add_argument("--precommit",required=True);q.add_argument("--p10-seed-replay",required=True);q.add_argument("--p9-precommit",required=True);q.add_argument("--stockfish-bin",required=True);q.add_argument("--berserk-bin",required=True);q.add_argument("--ethereal-bin",required=True);q.add_argument("--out",required=True);q.set_defaults(fn=regression)
 q=sp.add_parser("adjudicate");q.add_argument("--precommit",required=True);q.add_argument("--cases",required=True);q.add_argument("--regression",required=True);q.add_argument("--out",required=True);q.add_argument("--markdown",required=True);q.set_defaults(fn=adjudicate)
 a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
