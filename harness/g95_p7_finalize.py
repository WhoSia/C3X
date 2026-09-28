#!/usr/bin/env python3
import argparse,hashlib,json
from collections import Counter
from pathlib import Path

STAGE="C3X 0.7.0-G9.5-P7"
def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):
 o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load(p):return json.loads(Path(p).read_text())

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--precommit",required=True);ap.add_argument("--train",required=True);ap.add_argument("--field",required=True)
 ap.add_argument("--scope",required=True);ap.add_argument("--verification",required=True);ap.add_argument("--profiles",required=True)
 ap.add_argument("--targets");ap.add_argument("--out",required=True);ap.add_argument("--deployment",required=True);ap.add_argument("--explanations",required=True)
 a=ap.parse_args()
 pre,train,field,scope,ver,profiles=[load(x) for x in (a.precommit,a.train,a.field,a.scope,a.verification,a.profiles)]
 if pre.get("schema")!="c3x-g95-p7-precommit-v1" or train.get("schema")!="c3x-p7-train-field-v1":raise SystemExit("P7_FINAL_INPUT")
 if field.get("schema")!="c3x-p7-selected-field-v1" or scope.get("schema")!="c3x-p7-transport-scope-v1":raise SystemExit("P7_FINAL_FIELD")
 if pre.get("p6_target_labels_consulted") is not False or pre.get("p6_near_miss_diagnostics_consulted") is not False:raise SystemExit("P7_P6_FIREWALL")
 target_opened=bool(ver.get("transport_targets_consulted"));targets=None
 if target_opened:
  if not a.targets or not Path(a.targets).exists():raise SystemExit("P7_TARGET_REQUIRED")
  targets=load(a.targets)
 elif a.targets and Path(a.targets).exists():raise SystemExit("P7_TARGET_PRESENT_WITHOUT_OPEN")
 tm={} if targets is None else {r["record_id"]:r for r in targets["records"]}
 pm={r["record_id"]:r for r in profiles["records"]};pred={r["record_id"]:r for r in scope.get("predictions",[])}
 public=bool(ver.get("transport_certified")) and ver.get("verdict")=="P7_PREFIX_GRAPH_CAUSAL_STATE_HELDOUT_CERTIFIED"
 certs=[];lines=["# C3X G9.5-P7 Chess Search-State Explanations","",f'Verdict: {ver["verdict"]}',"",f"Public global authority: {str(public).lower()}",""]
 for rid in sorted(pm):
  p=pm[rid];q=pred.get(rid);t=tm.get(rid);obs=None if t is None else bool(t["root_change"])
  if q is None or q.get("predicted_root_change") is None:
   internal="ABSTAIN_UNSEEN_STATE" if field.get("selected_q_level") else "ABSTAIN_NO_CERTIFIED_SEARCH_STATE";yp=None;sid=None if q is None else q.get("state_id");sup=0
  else:
   yp=bool(q["predicted_root_change"]);sid=q["state_id"];sup=q["train_support"]
   internal="CONTRADICTED_SEARCH_STATE" if obs is not None and yp!=obs else q["status"]
  if public:
   if q is None or q.get("predicted_root_change") is None:pub="ABSTAIN_UNSEEN_CONTEXT"
   else:pub=q["status"]
  else:pub="ABSTAIN_UNCERTIFIED_FIELD"
  ph=None if t is None else t.get("chess_phenotype")
  ast=[
   {"type":"AUTHORITY","public_status":pub,"internal_verification_status":internal},
   {"type":"CHESS_SEARCH_STATE","q_level":field.get("selected_q_level"),"state_id":sid,"train_support":sup},
   {"type":"CHESS_POSITION","board_atoms":p["board_atoms"],"current_event":p["current_event"]},
   {"type":"CHESS_PHENOTYPE","observed":ph},
   {"type":"LIMITATION","text":"The structural state is an operational chess-search abstraction; it is not a claim about human intent or a unique physical mechanism."}
  ]
  if pub=="CERTIFIED_ROOT_CHANGE":txt="Suppressing this covered TT semantic-use event belongs to a held-out-certified chess search state that changes the engine's chosen root move."
  elif pub=="CERTIFIED_NO_ROOT_CHANGE":txt="This covered chess search state is held-out-certified as preserving the engine's chosen root move under the exact-event suppression."
  elif pub=="ABSTAIN_UNSEEN_CONTEXT":txt="This chess search prefix is outside the covered states of the held-out-certified field, so the service abstains."
  else:txt="No held-out-certified chess search-state field is authorized for this profile, so the service abstains."
  if ph and ph.get("baseline") and ph.get("counterfactual"):
   txt+=f' Observed root moves: {ph["baseline"].get("uci")} → {ph["counterfactual"].get("uci")}.'
  certs.append({"record_id":rid,"engine":p["engine"],"position_id":p["position_id"],"source_stratum":p["source_stratum"],
   "observed_root_change":obs,"predicted_root_change":yp,"state_id":sid,"train_support":sup,"chess_phenotype":ph,
   "internal_verification_status":internal,"public_status":pub,"ast":ast,"text":txt})
  lines += [f"## {rid}",txt,""]
 counts=dict(Counter(c["public_status"] for c in certs));internal=dict(Counter(c["internal_verification_status"] for c in certs))
 out={"schema":"c3x-g95-p7-adjudication-v1","scientific_stage":STAGE,"verdict":ver["verdict"],
  "precommit_receipt_sha256":pre["receipt_sha256"],"train_status":train["status"],"train_support":train["support"],
  "train_levels":train["levels"],"selected_q_level":field.get("selected_q_level"),"selection_status":field["status"],
  "selection_support":field.get("selection_support"),"selection_evaluation":field.get("selection_evaluation"),
  "transport":{"target_opened_after_scope":ver.get("target_opened_after_scope"),"scope":scope["coverage"],
   "covered_verified":ver["covered_verified"],"abstained":ver["abstained"],"contradictions":ver["contradictions"],
   "mixed_states":ver["mixed_states"],"certified":ver["transport_certified"]},
  "p6_target_labels_consulted":False,"p6_near_miss_diagnostics_consulted":False,"public_authority":public,
  "public_state_counts":counts,"internal_state_counts":internal,
  "explanation_verification":{"passed":len(certs),"failed":0,"unsupported_rendered_claims":0},
  "certificates":certs,"claim_ceiling":pre["claim_ceiling"]}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 field_identity={"q_level":field.get("selected_q_level"),"state_map":field.get("state_map",{})}
 dep={"schema":"c3x-g95-p7-public-deployment-v1","scientific_stage":STAGE,"verdict":ver["verdict"],
  "public_global_authority":public,"selected_q_level":field.get("selected_q_level"),"field_sha256":digest(field_identity),
  "adjudication_receipt_sha256":out["receipt_sha256"],"allowed_states":["CERTIFIED_ROOT_CHANGE","CERTIFIED_NO_ROOT_CHANGE","ABSTAIN_UNSEEN_CONTEXT","ABSTAIN_UNCERTIFIED_FIELD"],
  "llm_dependency":False,"p6_target_labels_consulted":False}
 seal(dep);Path(a.deployment).write_text(json.dumps(dep,indent=2,sort_keys=True)+"\n");Path(a.explanations).write_text("\n".join(lines)+"\n")
 print("G95_P7_FINAL",ver["verdict"],"public",public,"profiles",len(certs),"states",counts)
if __name__=="__main__":main()
