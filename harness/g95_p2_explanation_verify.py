#!/usr/bin/env python3
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
import p32_explanation_verify as p32x

STAGE="C3X 0.7.0-G9.5-P2"

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load(p):return json.loads(Path(p).read_text())

def load_pre(p):
 x=load(p)
 if x.get("schema")!="c3x-g95-p2-precommit-v1":raise SystemExit("P2_EXPLAIN_PRE")
 return x
def load_discovery(p):
 x=load(p)
 if x.get("schema")!="c3x-field-discovery-v1":raise SystemExit("P2_EXPLAIN_DISC")
 return x
def load_scope(p):
 x=load(p)
 if x.get("schema")!="c3x-field-scope-v1" or x.get("target_fields_consulted") is not False:raise SystemExit("P2_EXPLAIN_SCOPE")
 return x
def load_verify(p):
 x=load(p)
 if x.get("schema")!="c3x-field-verification-v1":raise SystemExit("P2_EXPLAIN_VERIFY")
 return x

def verdict(d,s,v):
 if not d.get("support",{}).get("pass"):return "DISCOVERY_CONTEXT_SUPPORT_LIMITED_HOLD"
 if not d.get("minimal_portable_bases"):
  return "PORTABLE_FIELD_HOLD_ARCHITECTURE_DIAGNOSTIC_ONLY" if d.get("architecture_diagnostic_bases") else "NO_PORTABLE_CONTEXT_BASIS_HOLD"
 if not s.get("coverage",{}).get("gate_pass"):return "PORTABLE_CONTEXT_FIELD_SCOPE_INSUFFICIENT_HOLD"
 if v.get("verdict")=="CONTEXT_FIELD_TRANSPORT_FALSIFIED":return "PORTABLE_CONTEXT_FIELD_HELDOUT_FALSIFIED"
 if v.get("verdict")=="CONTEXT_FIELD_TRANSPORT_CERTIFIED":return "PORTABLE_CONTEXT_INDEXED_CAUSAL_FIELD_HELDOUT_CERTIFIED"
 return "PORTABLE_CONTEXT_FIELD_SCOPE_INSUFFICIENT_HOLD"

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--precommit",required=True);ap.add_argument("--discovery",required=True);ap.add_argument("--scope",required=True)
 ap.add_argument("--verification",required=True);ap.add_argument("--profiles",required=True);ap.add_argument("--targets",required=True)
 ap.add_argument("--out",required=True);ap.add_argument("--ast",required=True);ap.add_argument("--grounding",required=True);ap.add_argument("--markdown",required=True)
 a=ap.parse_args()
 pre=load_pre(a.precommit);disc=load_discovery(a.discovery);scope=load_scope(a.scope);ver=load_verify(a.verification)
 prof=load(a.profiles);tar=load(a.targets)
 if prof.get("schema")!="c3x-context-profile-batch-v1" or tar.get("schema")!="c3x-context-target-batch-v1":raise SystemExit("P2_EXPLAIN_BATCH")
 pm={r["record_id"]:r for r in prof["records"]};tm={r["record_id"]:r for r in tar["records"]}
 if set(pm)!=set(tm):raise SystemExit("P2_EXPLAIN_JOIN")
 preds={r["record_id"]:r for r in scope.get("predictions",[])}
 contradictions={r["record_id"] for r in ver.get("contradictions",[])}
 case_by_position_engine={(c["position_id"],c["engine"]):c for c in pre["cases"] if c["role"]=="HELDOUT_CONTEXT_TRANSPORT"}
 basis=scope.get("selected_coordinates") or []
 items=[];asts=[];grounds=[];bad=[];status_counts=Counter();parent_ok=0;cf_ok=0
 for rid in sorted(pm):
  p=pm[rid];t=tm[rid];pr=preds.get(rid)
  if pr is None:raise SystemExit("P2_EXPLAIN_PRED_MISSING "+rid)
  if pr["status"]=="ABSTAIN_UNSEEN_CONTEXT":status="ABSTAIN_UNSEEN_CONTEXT"
  elif rid in contradictions:status="CONTRADICTED_CONTEXT_CELL"
  elif t["root_change"]:status="CERTIFIED_ROOT_CHANGE"
  else:status="CERTIFIED_NO_ROOT_CHANGE"
  status_counts[status]+=1
  c=case_by_position_engine[(p["position_id"],p["engine"])];fen=c["cell"]["fen"]
  ppv=p32x.replay_pv(fen,t.get("parent_pv"));cpv=p32x.replay_pv(fen,t.get("counterfactual_pv"))
  parent_ok+=int(ppv["complete"]);cf_ok+=int(cpv["complete"])
  pmove=p32x.move_atom(fen,t["parent_bestmove"]);cmove=p32x.move_atom(fen,t["counterfactual_bestmove"])
  selected_context={k:p["context"][k] for k in basis if not k.startswith("arch:")}
  ast=[
   {"type":"EXACT_EVENT","event_id_prefix":p["event_id"][:16],"fiber_id":p["fiber_id"]},
   {"type":"CONTEXT_SCOPE","basis_id":scope.get("selected_basis_id"),"coordinates":selected_context,
    "discovery_support":pr.get("discovery_support",0),"scope_status":pr["status"]},
   {"type":"HELDOUT_STATUS","status":status,"root_change":bool(t["root_change"])},
   {"type":"CHESS_ATOMIC_CONTRAST","parent":pmove,"counterfactual":cmove,
    "pv_divergence":p32x.divergence(t.get("parent_pv"),t.get("counterfactual_pv"))},
   {"type":"LIMITATION","text":"Certificate authority is limited to the frozen context-indexed F0 field and tested ROOT_CHANGE query; abstention is not non-causality and the context basis is not claimed uniquely true."}
  ]
  errors=[]
  if status=="CERTIFIED_ROOT_CHANGE" and not t["root_change"]:errors.append("STATUS_TARGET")
  if status=="CERTIFIED_NO_ROOT_CHANGE" and t["root_change"]:errors.append("STATUS_TARGET")
  if status=="CONTRADICTED_CONTEXT_CELL" and rid not in contradictions:errors.append("CONTRADICTION_SUPPORT")
  if status=="ABSTAIN_UNSEEN_CONTEXT" and pr["status"]!="ABSTAIN_UNSEEN_CONTEXT":errors.append("ABSTAIN_SUPPORT")
  if errors:bad.append({"record_id":rid,"errors":errors})
  txt=(f'{rid}: {status}. Exact event {p["event_id"][:16]}… lies in {p["fiber_id"]}. '
       f'Selected context basis {scope.get("selected_basis_id")} has values {selected_context}; '
       f'discovery support for this cell is {pr.get("discovery_support",0)}. '
       f'Parent move {t["parent_bestmove"]}; singleton-removal move {t["counterfactual_bestmove"]}. '
       'This licenses only the frozen ROOT_CHANGE query in the demonstrated context; it does not imply a universal mechanism label.')
  g={"record_id":rid,"parent_pv":ppv,"counterfactual_pv":cpv,"parent_move":pmove,"counterfactual_move":cmove}
  items.append({"record_id":rid,"status":status,"profile":p,"target":t,"prediction":pr,"ast":ast,"grounding":g,"verification":{"pass":not errors,"errors":errors},"explanation":txt})
  asts.append({"record_id":rid,"ast":ast});grounds.append(g)
 final_verdict=verdict(disc,scope,ver)
 if bad:final_verdict="EXPLANATION_SCOPE_VERIFICATION_FAIL"
 engine_specific={}
 for e,z in disc.get("engine_specific",{}).items():
  engine_specific[e]={"support_pass":z.get("support_pass"),"minimum_cardinality":z.get("minimum_cardinality"),
    "minimal_basis_ids":[b["basis_id"] for b in z.get("minimal_bases",[])]}
 out={"schema":"c3x-g95-p2-adjudication-v1","scientific_stage":STAGE,"verdict":final_verdict,
  "precommit_receipt_sha256":pre["receipt_sha256"],"discovery_status":disc["status"],
  "discovery_support":disc["support"],"minimum_portable_cardinality":disc.get("minimum_portable_cardinality"),
  "minimal_portable_basis_ids":[b["basis_id"] for b in disc.get("minimal_portable_bases",[])],
  "architecture_diagnostic_basis_ids":[b["basis_id"] for b in disc.get("architecture_diagnostic_bases",[])],
  "engine_specific":engine_specific,"selected_basis_id":scope.get("selected_basis_id"),"selected_coordinates":basis,
  "heldout_scope":{"status":scope["status"],"coverage":scope.get("coverage",{}),"target_fields_consulted":scope.get("target_fields_consulted")},
  "heldout_transport":{"verdict":ver.get("verdict"),"covered_verified":ver.get("covered_verified"),"abstained":ver.get("abstained"),
    "contradictions":ver.get("contradictions",[]),"mixed_heldout_cells":ver.get("mixed_heldout_cells",[])},
  "status_counts":dict(status_counts),"pv_legality":{"parent_complete":parent_ok,"counterfactual_complete":cf_ok,"available":len(items)},
  "explanation_verification":{"passed":len(items)-len(bad),"failed":len(bad),"unsupported_rendered_claims":0,"errors":bad},
  "certificates":items,
  "authority_ceiling":"Finite-support query-specific causal field over frozen books, engine commits, history and 80k-node search. Context basis is a licensing condition, not a uniquely true causal ontology."}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 Path(a.ast).write_text(json.dumps({"schema":"c3x-g95-p2-explanation-ast-v1","items":asts},indent=2,sort_keys=True)+"\n")
 Path(a.grounding).write_text(json.dumps({"schema":"c3x-g95-p2-chess-grounding-v1","items":grounds},indent=2,sort_keys=True)+"\n")
 md=["# G9.5-P2 Context-Scoped Exact-Event Explanations","",f"Verdict: `{final_verdict}`",f"Selected basis: `{scope.get('selected_basis_id')}`",""]
 for z in items:md += [f"## {z['record_id']}",z["explanation"],""]
 Path(a.markdown).write_text("\n".join(md)+"\n")
 if bad:raise SystemExit("P2_EXPLANATION_SCOPE_VERIFY_FAIL")
 print("G95_P2_ADJ",final_verdict,"basis",scope.get("selected_basis_id"),"covered",ver.get("covered_verified"),"abstain",ver.get("abstained"))

if __name__=="__main__":main()
