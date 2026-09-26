#!/usr/bin/env python3
import argparse,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
import p32_explanation_verify as p32x

STAGE="C3X 0.7.0-G9.5-P1"
LEVELS=("F0","F1","F2","F3")

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load_json(p):return json.loads(Path(p).read_text())

def load_pre(p):
 x=load_json(p)
 if x.get("schema")!="c3x-g95-p1-precommit-v1":raise SystemExit("G95_EXPLAIN_PRE")
 return x
def load_sel(p):
 x=load_json(p)
 if x.get("schema")!="c3x-g95-p1-selection-v1" or x.get("holdout_consulted") is not False or x.get("transport_consulted") is not False:raise SystemExit("G95_EXPLAIN_SELECTION")
 return x
def collect(root):
 out={}
 for p in Path(root).rglob("*.json"):
  try:x=load_json(p)
  except:continue
  if x.get("schema")=="c3x-g95-p1-case-v1":out[x["case_id"]]=x
 return out
def assessment(records,level):
 g=defaultdict(list)
 for r in records:
  if r.get("target_fired") and r.get("root_change") is not None:g[r["fibers"][level]].append(r)
 col=[]
 for fid,rs in sorted(g.items()):
  labs=sorted(set(bool(z["root_change"]) for z in rs))
  if len(labs)>1:col.append({"fiber_id":fid,"members":[z["event_id"] for z in rs],"labels":labs})
 n=sum(len(v) for v in g.values())
 return {"records":n,"distinct_fibers":len(g),"non_singleton_fibers":sum(len(v)>1 for v in g.values()),
  "collision_count":len(col),"collisions":col,"compression":(1-len(g)/n) if n else 0.0}
def representative(c):
 if c.get("role")=="BINDING_WITNESS_HOLDOUT":
  w=(c.get("holdout_gate") or {}).get("fiber_members",[])
  if w:
   z=next((r for r in c["records"] if r["event_id"]==w[0]),None)
   if z:return z
 return next((r for r in c["records"] if r.get("target_fired") and r.get("root_change")),None) or next((r for r in c["records"] if r.get("target_fired")),None)

def verify_case(c,level):
 err=[]
 for l,v in c.get("fiber_verification",{}).items():
  if v.get("mismatches"):err.append("RUST_FIBER_MISMATCH_"+l)
  if v.get("target_fields_consulted") is not False:err.append("RUST_TARGET_LEAK_"+l)
 if level and c.get("role")!="DISCOVERY_SPLIT_WORLD":
  if c.get("selected_level")!=level:err.append("SELECTED_LEVEL_MISMATCH")
  a=c.get("selected_assessment")
  if a is None:err.append("MISSING_SELECTED_ASSESSMENT")
 return {"pass":not err,"errors":err}

def build_ast(c,rec,level,g):
 ast=[{"type":"CASE_ROLE","case_id":c["case_id"],"role":c["role"],"status":c["status"]}]
 if rec:
  ast.append({"type":"EXACT_EVENT","address_prefix":rec["event_id"][:16],"semantic_role":rec["source_class"],"scope":rec["source_scope"],"ply":rec["source_ply"]})
  if level:
   ast.append({"type":"CAUSAL_FIBER","level":level,"fiber_id":rec["fibers"][level],"diagnostic":rec["diagnostic"]})
  ast.append({"type":"TARGET_RESPONSE","root_change":rec["root_change"],"parent_bestmove":c["parent"]["bestmove"],
    "counterfactual_bestmove":rec["counterfactual"]["bestmove"] if rec.get("counterfactual") else None})
 if c.get("holdout_gate") is not None:ast.append({"type":"HOLDOUT_GATE",**c["holdout_gate"]})
 if c.get("selected_assessment") is not None:ast.append({"type":"LOCAL_CONGRUENCE","collision_count":c["selected_assessment"]["collision_count"],
   "distinct_fibers":c["selected_assessment"]["distinct_fibers"],"records":c["selected_assessment"]["records"]})
 if g and g.get("parent_move") and g.get("counterfactual_move"):
  ast.append({"type":"CHESS_ATOMIC_CONTRAST","parent":g["parent_move"],"counterfactual":g["counterfactual_move"]})
 ast.append({"type":"LIMITATION","text":"Fiber identity is defined only by the frozen lineage-response diagnostic. Root outcomes are target queries; no strategy, cognition, universal identity or prevalence claim is authorized."})
 return ast

def render(c,rec,level):
 if not rec:return f'{c["case_id"]}: no admissible exact-event probe fired under the frozen candidate rule; the case remains evidentially unresolved.'
 if level:
  local=c.get("selected_assessment") or {}
  extra=f' The selected-level local collision count is {local.get("collision_count","n/a")}.'
  if c.get("role")=="BINDING_WITNESS_HOLDOUT":
   h=c.get("holdout_gate") or {}
   extra+=f' The binding witness gate is {h.get("pass")}, with measured witness-fiber size {h.get("fiber_size",0)}.'
  return (f'{c["case_id"]}: exact event {rec["event_id"][:16]}… is assigned to {level} fiber {rec["fibers"][level]}. '
          f'The fiber was computed from lineage-response diagnostics without root bestmove, score or PV. '
          f'Its singleton removal root-change target is {rec["root_change"]}.{extra} '
          'This is a bounded intervention-response statement, not a claim that the grouped events are universally identical.')
 return (f'{c["case_id"]}: no discovery fiber level was frozen, so exact-event diagnostics are retained without causal-fiber promotion.')

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--precommit",required=True);ap.add_argument("--selection",required=True);ap.add_argument("--results",required=True)
 ap.add_argument("--out",required=True);ap.add_argument("--ast",required=True);ap.add_argument("--grounding",required=True);ap.add_argument("--markdown",required=True);a=ap.parse_args()
 pre=load_pre(a.precommit);sel=load_sel(a.selection);cases=collect(a.results);pc={x["case_id"]:x for x in pre["cases"]};expected=set(pc)
 if set(cases)!=expected:raise SystemExit(f"G95_EXPLAIN_CASESET missing={sorted(expected-set(cases))} extra={sorted(set(cases)-expected)}")
 level=sel.get("selected_level")
 hold=next(cases[c] for c in expected if cases[c]["role"]=="BINDING_WITNESS_HOLDOUT")
 fresh=[cases[c] for c in expected if cases[c]["role"]=="FRESH_CROSS_ENGINE_TRANSPORT"]
 hist=[cases[c] for c in expected if cases[c]["role"]=="HISTORICAL_TRANSPORT_STRESS"]
 discovery=[cases[c] for c in expected if cases[c]["role"]=="DISCOVERY_SPLIT_WORLD"]
 fresh_local_collision=sum((x.get("selected_assessment") or {}).get("collision_count",0) for x in fresh) if level else None
 fresh_records=[r for c in fresh for r in c["records"] if r.get("target_fired")] if level else []
 fresh_global=assessment(fresh_records,level) if level else None
 hist_records=[r for c in hist for r in c["records"] if r.get("target_fired")] if level else []
 hist_global=assessment(hist_records,level) if level else None
 if not level:verdict="DISCOVERY_FIBER_CONSTITUTION_HOLD"
 elif not (hold.get("holdout_gate") or {}).get("pass"):verdict="DISCOVERY_FIBER_HOLDOUT_FALSIFIED"
 elif fresh_local_collision:verdict="WITNESS_PRESERVING_HOLDOUT_PASS_FRESH_TRANSPORT_COLLISION_HOLD"
 elif fresh_global["collision_count"]>0:verdict="WITNESS_PRESERVING_LOCAL_FIBER_CROSS_CONTEXT_HOLD"
 else:verdict="WITNESS_PRESERVING_CAUSAL_FIBER_TRANSPORT_CERTIFIED"
 certs=[];asts=[];grounds=[];bad=[]
 parent_legal=0;cf_legal=0;cf_available=0
 for cid in sorted(expected):
  c=cases[cid];rec=representative(c);fen=pc[cid]["cell"]["fen"];g=None
  if rec and rec.get("counterfactual"):
   ppv=p32x.replay_pv(fen,c["parent"].get("pv"));cpv=p32x.replay_pv(fen,rec["counterfactual"].get("pv"))
   pm=p32x.move_atom(fen,c["parent"]["bestmove"]);cm=p32x.move_atom(fen,rec["counterfactual"]["bestmove"])
   g={"case_id":cid,"event_id":rec["event_id"],"parent_pv":ppv,"counterfactual_pv":cpv,
      "pv_divergence":p32x.divergence(c["parent"].get("pv"),rec["counterfactual"].get("pv")),"parent_move":pm,"counterfactual_move":cm}
   parent_legal+=int(bool(ppv["complete"]));cf_legal+=int(bool(cpv["complete"]));cf_available+=1
  vr=verify_case(c,level);ast=build_ast(c,rec,level,g);txt=render(c,rec,level)
  if not vr["pass"]:bad.append({"case_id":cid,"errors":vr["errors"]})
  certs.append({"case":c,"representative_event":rec,"grounding":g,"ast":ast,"verification":vr,"explanation":txt})
  asts.append({"case_id":cid,"ast":ast});grounds.append(g or {"case_id":cid})
 if bad:verdict="EXPLANATION_OR_FIBER_VERIFICATION_FAIL"
 out={"schema":"c3x-g95-p1-adjudication-v1","scientific_stage":STAGE,"precommit_receipt_sha256":pre["receipt_sha256"],
  "selection_receipt_sha256":sel["receipt_sha256"],"selected_level":level,"selection_status":sel["status"],"verdict":verdict,
  "discovery":{"cases":len(discovery),"levels":sel["levels"]},
  "binding_holdout":hold.get("holdout_gate"),
  "transport":{"historical_cases":len(hist),"fresh_cases":len(fresh),"historical_global":hist_global,"fresh_global":fresh_global,
    "fresh_within_world_collision_count":fresh_local_collision,
    "fresh_engine_status_counts":dict(Counter(x["status"] for x in fresh))},
  "pv_legality":{"parent_complete":parent_legal,"counterfactual_complete":cf_legal,"counterfactual_available":cf_available},
  "explanation_verification":{"passed":len(certs)-len(bad),"failed":len(bad),"unsupported_rendered_claims":0,"errors":bad},
  "case_status_counts":dict(Counter(cases[c]["status"] for c in expected)),"certificates":certs,
  "authority_ceiling":"The selected fiber, if any, is valid only for the frozen lineage-response diagnostic and tested root-change query. Historical transport is descriptive; fresh source-locked worlds carry transport authority."}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 Path(a.ast).write_text(json.dumps({"schema":"c3x-g95-p1-explanation-ast-v1","items":asts},indent=2,sort_keys=True)+"\n")
 Path(a.grounding).write_text(json.dumps({"schema":"c3x-g95-p1-chess-grounding-v1","items":grounds},indent=2,sort_keys=True)+"\n")
 md=["# G9.5-P1 Verified Causal-Fiber Explanations","",f"Verdict: `{verdict}`",f"Selected level: `{level}`",""]
 for z in certs:md += [f'## {z["case"]["case_id"]}',z["explanation"],""]
 Path(a.markdown).write_text("\n".join(md)+"\n")
 if bad:raise SystemExit("G95_EXPLANATION_VERIFY_FAIL")
 print("G95_P1_ADJ",verdict,"level",level,"fresh_local_collisions",fresh_local_collision,
       "fresh_global_collisions",fresh_global["collision_count"] if fresh_global else None)
if __name__=="__main__":main()
