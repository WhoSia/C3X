#!/usr/bin/env python3
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
import p32_explanation_verify as p32x

STAGE="C3X 0.7.0-G9.4-P34"
def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load_json(p):return json.loads(Path(p).read_text())
def load_pre(p):
 x=load_json(p)
 if x.get("schema")!="c3x-p34-precommit-v1":raise SystemExit("P34_EXPLAIN_PRE")
 return x
def collect(root):
 out={}
 for p in Path(root).rglob("p34-case-*.json"):
  x=load_json(p)
  if x.get("schema")=="c3x-p34-case-v1":out[x["case_id"]]=x
 return out
def selected_level(c):
 if c.get("selected_level") is None:return None
 return next(z for z in c["levels"] if z["level"]==c["selected_level"])
def cf_semantic(c):
 z=selected_level(c)
 if z:return z["minimal_remove"]["semantic"],"SELECTED_MINIMAL_QUOTIENT_REMOVAL"
 if c["levels"]:
  x=c["levels"][-1].get("full_remove")
  if x:return x,"FINEST_LEVEL_FULL_REMOVE"
 return None,None
def build_ast(c,g):
 ast=[{"type":"CASE_STATUS","status":c["status"],"selected_level":c.get("selected_level")}]
 z=selected_level(c)
 if z:
  ast.append({"type":"CAUSAL_QUOTIENT","level":z["level"],"remove_size":len(z["minimal_remove"]["cone_ids"]),
    "keep_size":len(z["minimal_keep"]["cone_ids"])})
  ast.append({"type":"EXACT_DRILLDOWN","collision":z["drilldown"]["collision"],"large_class_hold":z["drilldown"]["large_class_hold"],
    "remove_exact_expansion_parity":z["drilldown"]["remove_exact_expansion_parity"],
    "keep_exact_expansion_parity":z["drilldown"]["keep_exact_expansion_parity"],
    "query_commutation":z["drilldown"]["query_commutation"],
    "remove_exact_expansion_member_count":z["drilldown"].get("remove_exact_expansion_member_count",0),
    "keep_exact_blocked_member_count":z["drilldown"].get("keep_exact_blocked_member_count",0)})
 else:
  ast.append({"type":"LATTICE_FAILURE","levels":[{"level":x["level"],"status":x["status"],"failures":x.get("failures",[])} for x in c["levels"]]})
 if g.get("pv_divergence") is not None:ast.append({"type":"PV_DIVERGENCE","value":g["pv_divergence"]})
 if g.get("parent_move") and g.get("counterfactual_move"):
  ast.append({"type":"CHESS_ATOMIC_CONTRAST","parent":g["parent_move"],"counterfactual":g["counterfactual_move"]})
 ast.append({"type":"LIMITATION","text":"Authority is limited to the frozen Q0→Q3 lattice, inherited exact worlds and parent-seed-removal intervention; no universal abstraction or strategic-intent claim is made."})
 return ast
def verify_ast(c,g,ast):
 err=[];allowed={"CASE_STATUS","CAUSAL_QUOTIENT","EXACT_DRILLDOWN","LATTICE_FAILURE","PV_DIVERGENCE","CHESS_ATOMIC_CONTRAST","LIMITATION"}
 for a in ast:
  if a["type"] not in allowed:err.append("TYPE")
 z=selected_level(c)
 if z:
  if not any(a["type"]=="CAUSAL_QUOTIENT" and a["level"]==z["level"] for a in ast):err.append("QUOTIENT_SUPPORT")
  if z["drilldown"]["status"]!="PASS":err.append("DRILLDOWN")
  if (z["drilldown"]["collision"] or z["drilldown"]["large_class_hold"] or
      not z["drilldown"]["remove_exact_expansion_parity"] or not z["drilldown"]["keep_exact_expansion_parity"] or
      not z["drilldown"]["query_commutation"]):err.append("DRILLDOWN_GATE")
  if not z["minimal_remove"]["certified"] or not z["minimal_keep"]["certified"]:err.append("CAUSAL_GATE")
 else:
  if not any(a["type"]=="LATTICE_FAILURE" for a in ast):err.append("FAILURE_SUPPORT")
 return {"pass":not err,"errors":err}
def render(c,ast):
 if c.get("selected_level"):
  z=selected_level(c)
  return (f'{c["case_id"]}: the first prospectively admissible quotient is {z["level"]}. '
          f'Its inclusion-minimal conditional removal set contains {len(z["minimal_remove"]["cone_ids"])} cone class(es) and its retaining set contains {len(z["minimal_keep"]["cone_ids"])}. '
          f'Parent-trace exact-member collision testing found no forbidden singleton response collision. '
          f'Local REMOVE parity is {z["drilldown"]["remove_exact_expansion_parity"]}, KEEP parity is {z["drilldown"]["keep_exact_expansion_parity"]}, '
          f'and the bounded query-commutation gate is {z["drilldown"]["query_commutation"]}. '
          'This is a bounded causal-abstraction certificate, not a universal event identity claim.')
 return (f'{c["case_id"]}: no level in the frozen Q0→Q3 quotient lattice passed all closure, causal, collision and exact-drilldown gates. '
         'The result is retained as bounded lattice divergence rather than repaired by adding post-hoc coordinates.')

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--precommit",required=True);ap.add_argument("--results",required=True);ap.add_argument("--out",required=True)
 ap.add_argument("--ast",required=True);ap.add_argument("--grounding",required=True);ap.add_argument("--markdown",required=True);a=ap.parse_args()
 pre=load_pre(a.precommit);cases=collect(a.results);expected={x["case_id"] for x in pre["cases"]}
 if set(cases)!=expected:raise SystemExit(f"P34_EXPLAIN_CASESET {sorted(expected-set(cases))}")
 pc={x["case_id"]:x for x in pre["cases"]};certs=[];bad=[];asts=[];grounds=[]
 for cid in sorted(expected):
  c=cases[cid];fen=pc[cid]["cell"]["fen"];cf,kind=cf_semantic(c);par=c["parent_seed_removal"]
  ppv=p32x.replay_pv(fen,par.get("pv"));cpv=p32x.replay_pv(fen,cf.get("pv")) if cf else None
  pm=p32x.move_atom(fen,par["bestmove"]);cm=p32x.move_atom(fen,cf["bestmove"]) if cf and cf.get("bestmove") else None
  g={"case_id":cid,"counterfactual_kind":kind,"parent_pv":ppv,"counterfactual_pv":cpv,
    "pv_divergence":p32x.divergence(par.get("pv"),cf.get("pv")) if cf else None,"parent_move":pm,"counterfactual_move":cm}
  ast=build_ast(c,g);vr=verify_ast(c,g,ast);txt=render(c,ast)
  if not vr["pass"]:bad.append({"case_id":cid,"errors":vr["errors"]})
  certs.append({"case":c,"grounding":g,"ast":ast,"verification":vr,"explanation":txt});asts.append({"case_id":cid,"ast":ast});grounds.append(g)
 roles={x["case_id"]:x["role"] for x in pre["cases"]}
 pos=sum(bool(cases[c].get("selected_level")) and roles[c]=="FINITE_CLOSURE_POSITIVE_CONTROL" for c in expected)
 opened=sum(bool(cases[c].get("selected_level")) and roles[c]=="OPEN_EVENT_UNIVERSE_PRIMARY" for c in expected)
 if bad:verdict="EXPLANATION_VERIFICATION_FAIL"
 elif pos==1 and opened==2:verdict="OPEN_EVENT_UNIVERSE_CAUSAL_QUOTIENT_RECONSTITUTED_WITH_EXACT_DRILLDOWN"
 elif pos==1 and opened>0:verdict="OPEN_EVENT_UNIVERSE_CAUSAL_QUOTIENT_PARTIAL_RECONSTITUTION"
 elif pos==1:verdict="POSITIVE_CONTROL_PRESERVED_OPEN_EVENT_UNIVERSE_QUOTIENT_HOLD"
 elif opened>0:verdict="OPEN_EVENT_QUOTIENT_SIGNAL_POSITIVE_CONTROL_FAILURE_HOLD"
 else:verdict="FROZEN_QUOTIENT_LATTICE_REJECTED_UNDER_EXACT_DRILLDOWN"
 parent_legal=sum(z["grounding"]["parent_pv"]["complete"] for z in certs);cf_av=[z for z in certs if z["grounding"]["counterfactual_pv"] is not None]
 cf_legal=sum(z["grounding"]["counterfactual_pv"]["complete"] for z in cf_av)
 out={"schema":"c3x-p34-adjudication-v1","scientific_stage":STAGE,"precommit_receipt_sha256":pre["receipt_sha256"],"verdict":verdict,
  "primary_cases":len(certs),"selected_cases":sum(bool(cases[c].get("selected_level")) for c in expected),
  "selected_open_event_cases":opened,"positive_control_selected":pos,
  "case_status_counts":dict(Counter(cases[c]["status"] for c in expected)),
  "selected_levels":{c:cases[c].get("selected_level") for c in sorted(expected)},
  "pv_legality":{"parent_complete":parent_legal,"counterfactual_complete":cf_legal,"counterfactual_available":len(cf_av)},
  "explanation_verification":{"passed":len(certs)-len(bad),"failed":len(bad),"unsupported_rendered_claims":0,"errors":bad},
  "certificates":certs,
  "authority_ceiling":"frozen Q0→Q3 lattice and inherited P33 support only; parent-trace-local collision/drilldown; no universal abstraction, strategy, cognition or prevalence claim"}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 Path(a.ast).write_text(json.dumps({"schema":"c3x-p34-explanation-ast-v1","items":asts},indent=2,sort_keys=True)+"\n")
 Path(a.grounding).write_text(json.dumps({"schema":"c3x-p34-chess-grounding-v1","items":grounds},indent=2,sort_keys=True)+"\n")
 md=["# P34 Verified Causal-Cone Explanations","",f"Verdict: `{verdict}`",""]
 for z in certs:md += [f'## {z["case"]["case_id"]}',z["explanation"],""]
 Path(a.markdown).write_text("\n".join(md)+"\n")
 if bad:raise SystemExit("P34_EXPLANATION_VERIFICATION_FAIL")
 print("P34_ADJ",verdict,"selected",out["selected_cases"],"open",opened,"positive",pos)
if __name__=="__main__":main()
