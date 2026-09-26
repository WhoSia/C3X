#!/usr/bin/env python3
import argparse,hashlib,json,sys
from collections import Counter
from pathlib import Path
import p32_explanation_verify as p32x

STAGE="C3X 0.7.0-G9.5-P3"
def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load(p):return json.loads(Path(p).read_text())

def main():
 ap=argparse.ArgumentParser()
 for k in ("precommit","field","scope","verification","diagnosis","profiles","targets","out","ast","grounding","markdown"):ap.add_argument("--"+k,required=True)
 a=ap.parse_args();pre=load(a.precommit);field=load(a.field);scope=load(a.scope);ver=load(a.verification);diag=load(a.diagnosis);prof=load(a.profiles);tar=load(a.targets)
 if pre.get("schema")!="c3x-g95-p3-precommit-v1" or field.get("schema")!="c3x-field-p3-discovery-v1" or scope.get("schema")!="c3x-field-p3-scope-v1" or ver.get("schema")!="c3x-field-p3-verification-v1":raise SystemExit("P3_EXPLAIN_SCHEMA")
 pm={r["record_id"]:r for r in prof["records"]};tm={r["record_id"]:r for r in tar["records"]}
 if set(pm)!=set(tm):raise SystemExit("P3_EXPLAIN_JOIN")
 preds={r["record_id"]:r for r in scope.get("global_predictions",[])};bad_ids={r["record_id"] for r in ver["global"]["contradictions"]}
 cm={(c["position_id"],c["engine"]):c for c in pre["cases"] if c["role"]=="HELDOUT_REGIME_TRANSPORT"}
 items=[];asts=[];grounds=[];errs=[];cnt=Counter();pok=cok=0
 for rid in sorted(pm):
  p=pm[rid];t=tm[rid];pr=preds.get(rid)
  if pr is None:status="ABSTAIN_NO_GLOBAL_FIELD"
  elif pr["status"]=="ABSTAIN_UNSEEN_CONTEXT":status="ABSTAIN_UNSEEN_CONTEXT"
  elif rid in bad_ids:status="CONTRADICTED_CONTEXT_CELL"
  elif bool(t["root_change"]):status="CERTIFIED_ROOT_CHANGE"
  else:status="CERTIFIED_NO_ROOT_CHANGE"
  cnt[status]+=1;case=cm[(p["position_id"],p["engine"])];fen=case["cell"]["fen"]
  ppv=p32x.replay_pv(fen,t.get("parent_pv"));cpv=p32x.replay_pv(fen,t.get("counterfactual_pv"));pok+=int(ppv["complete"]);cok+=int(cpv["complete"])
  pmove=p32x.move_atom(fen,t["parent_bestmove"]);cmove=p32x.move_atom(fen,t["counterfactual_bestmove"])
  errors=[]
  if status=="CERTIFIED_ROOT_CHANGE" and not t["root_change"]:errors.append("STATUS_TARGET")
  if status=="CERTIFIED_NO_ROOT_CHANGE" and t["root_change"]:errors.append("STATUS_TARGET")
  if status=="CONTRADICTED_CONTEXT_CELL" and rid not in bad_ids:errors.append("CONTRADICTION_SUPPORT")
  if errors:errs.append({"record_id":rid,"errors":errors})
  sid=scope.get("selected_global_schema_id")
  ast=[{"type":"EXACT_EVENT","event_id_prefix":p["event_id"][:16],"fiber_id":p["fiber_id"]},{"type":"TOPOLOGY_CONTEXT","schema_id":sid,"status":status},{"type":"HELDOUT_TARGET","root_change":bool(t["root_change"])},{"type":"CHESS_ATOMIC_CONTRAST","parent":pmove,"counterfactual":cmove,"pv_divergence":p32x.divergence(t.get("parent_pv"),t.get("counterfactual_pv"))},{"type":"LIMITATION","text":"Authority is limited to the frozen P3 schema field and singleton-removal ROOT_CHANGE query; abstention is not non-causality and diagnosis cannot modify the field."}]
  text=f"{rid}: {status}. F0 fiber {p['fiber_id']} under schema {sid}. Parent move {t['parent_bestmove']}; singleton-removal move {t['counterfactual_bestmove']}. This is a bounded certificate state, not a universal mechanism claim."
  g={"record_id":rid,"parent_pv":ppv,"counterfactual_pv":cpv,"parent_move":pmove,"counterfactual_move":cmove}
  items.append({"record_id":rid,"status":status,"profile":p,"target":t,"prediction":pr,"ast":ast,"grounding":g,"verification":{"pass":not errors,"errors":errors},"explanation":text});asts.append({"record_id":rid,"ast":ast});grounds.append(g)
 verdict=ver["verdict"] if not errs else "EXPLANATION_SERVICE_VERIFICATION_FAIL"
 out={"schema":"c3x-g95-p3-adjudication-v1","scientific_stage":STAGE,"verdict":verdict,"field_status":field["status"],"selected_global_schema_id":scope.get("selected_global_schema_id"),"discovery_support":field["support"],"engine_specific_selected":{e:(field["engine_specific"][e]["selected_schema"] or {}).get("id") for e in ("stockfish_19","berserk","ethereal")},"heldout_scope":scope["global_coverage"],"heldout_transport":ver,"post_verification_diagnosis":diag,"status_counts":dict(cnt),"pv_legality":{"parent_complete":pok,"counterfactual_complete":cok,"available":len(items)},"explanation_verification":{"passed":len(items)-len(errs),"failed":len(errs),"unsupported_rendered_claims":0,"errors":errs},"certificates":items,"authority_ceiling":"Finite-support topology-aware ROOT_CHANGE field under frozen P3 corpus, engines, history and search envelope."}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");Path(a.ast).write_text(json.dumps({"schema":"c3x-g95-p3-explanation-ast-v1","items":asts},indent=2,sort_keys=True)+"\n");Path(a.grounding).write_text(json.dumps({"schema":"c3x-g95-p3-chess-grounding-v1","items":grounds},indent=2,sort_keys=True)+"\n")
 md=["# G9.5-P3 Topology-Aware Exact-Event Explanations","",f"Verdict: {verdict}",f"Schema: {scope.get('selected_global_schema_id')}",""]
 for z in items:md += [f"## {z['record_id']}",z["explanation"],""]
 Path(a.markdown).write_text("\n".join(md)+"\n")
 if errs:raise SystemExit("P3_EXPLANATION_FAIL")
 print("G95_P3_ADJ",verdict,"schema",scope.get("selected_global_schema_id"),"status",dict(cnt))
if __name__=="__main__":main()
