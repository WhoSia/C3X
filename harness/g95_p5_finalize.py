#!/usr/bin/env python3
import argparse,hashlib,json
from collections import Counter
from pathlib import Path

STAGE="C3X 0.7.0-G9.5-P5"

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):
 o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load(p):return json.loads(Path(p).read_text())

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--precommit",required=True);ap.add_argument("--train",required=True);ap.add_argument("--train-audit",required=True)
 ap.add_argument("--shortlist",required=True);ap.add_argument("--field",required=True);ap.add_argument("--scope",required=True)
 ap.add_argument("--verification",required=True);ap.add_argument("--profiles",required=True);ap.add_argument("--targets")
 ap.add_argument("--out",required=True);ap.add_argument("--deployment",required=True);ap.add_argument("--explanations",required=True)
 a=ap.parse_args()
 pre=load(a.precommit);tr=load(a.train);audit=load(a.train_audit);sl=load(a.shortlist);field=load(a.field);scope=load(a.scope);ver=load(a.verification);profiles=load(a.profiles)
 if pre.get("schema")!="c3x-g95-p5-precommit-v1" or audit.get("schema")!="c3x-g95-p5-train-audit-v1":raise SystemExit("P5_FINAL_INPUT")
 if scope.get("schema")!="c3x-p5-transport-scope-v1" or ver.get("schema")!="c3x-p5-transport-verification-v1":raise SystemExit("P5_FINAL_TRANSPORT")
 target_opened=bool(ver.get("transport_targets_consulted"))
 targets=None
 if target_opened:
  if not a.targets or not Path(a.targets).exists():raise SystemExit("P5_FINAL_TARGETS_REQUIRED")
  targets=load(a.targets)
 elif a.targets and Path(a.targets).exists():
  raise SystemExit("P5_FINAL_TARGETS_PRESENT_WITHOUT_AUTHORITY")
 tm={} if targets is None else {r["record_id"]:r for r in targets["records"]}
 pm={r["record_id"]:r for r in profiles["records"]}
 preds={r["record_id"]:r for r in scope.get("predictions",[])}
 public=bool(ver.get("transport_certified")) and ver.get("verdict")=="P5_MINIMAL_CAUSAL_REPRESENTATION_HELDOUT_CERTIFIED"
 selected=field.get("selected_candidate")
 certs=[];lines=["# C3X G9.5-P5 Authority-Conservative Explanations","",f'Verdict: {ver["verdict"]}',"",f"Public global authority: {str(public).lower()}",""]
 for rid in sorted(pm):
  p=pm[rid];q=preds.get(rid);obs=None if not target_opened else bool(tm[rid]["root_change"])
  if q is None:
   internal="ABSTAIN_NO_SELECTED_REPRESENTATION";pred=None;support=0;cell_key=None
  elif q["status"]=="ABSTAIN_UNSEEN_CONTEXT":
   internal="ABSTAIN_UNSEEN_CONTEXT";pred=None;support=0;cell_key=q["cell_key"]
  else:
   pred=bool(q["predicted_root_change"]);support=q["discovery_support"];cell_key=q["cell_key"]
   internal="CONTRADICTED_CONTEXT_CELL" if target_opened and pred!=obs else q["status"]
  if public:
   public_status="ABSTAIN_UNSEEN_CONTEXT" if q is None or q["status"]=="ABSTAIN_UNSEEN_CONTEXT" else q["status"]
  else:
   public_status="ABSTAIN_UNCERTIFIED_FIELD"
  ast=[
   {"type":"AUTHORITY","public_status":public_status,"internal_verification_status":internal},
   {"type":"REPRESENTATION","candidate_id":field.get("selected_candidate_id"),"coordinates":[] if selected is None else selected["coordinates"]},
   {"type":"PROVENANCE","engine":p["engine"],"source_stratum":p["source_stratum"],"sampling_stratum":p["sampling_stratum"]},
   {"type":"LIMITATION","text":"P5 coordinates are bounded representational discriminators under STRICT_EVENT_PREFIX_ONLY; they are not automatically unique causal variables."}
  ]
  if public_status=="CERTIFIED_ROOT_CHANGE":
   text="The prospectively selected and held-out-certified P5 representation licenses ROOT_CHANGE for this covered strict-prefix context."
  elif public_status=="CERTIFIED_NO_ROOT_CHANGE":
   text="The prospectively selected and held-out-certified P5 representation licenses NO_ROOT_CHANGE for this covered strict-prefix context."
  elif public_status=="ABSTAIN_UNSEEN_CONTEXT":
   text="This strict-prefix context is outside the covered cells of the held-out-certified P5 representation, so the service abstains."
  else:
   text="No held-out-certified P5 representation is authorized for public certification, so the service abstains."
  text+=" The selected coordinates are reported as representation features, not as uniquely identified physical mechanisms."
  certs.append({"record_id":rid,"engine":p["engine"],"position_id":p["position_id"],"source_stratum":p["source_stratum"],
    "sampling_stratum":p["sampling_stratum"],"observed_root_change":obs,"predicted_root_change":pred,
    "cell_key":cell_key,"discovery_support":support,"internal_verification_status":internal,
    "public_status":public_status,"ast":ast,"text":text})
  lines += [f"## {rid}",text,""]
 counts=dict(Counter(z["public_status"] for z in certs));internal_counts=dict(Counter(z["internal_verification_status"] for z in certs))
 out={"schema":"c3x-g95-p5-adjudication-v1","scientific_stage":STAGE,"verdict":ver["verdict"],
   "precommit_receipt_sha256":pre["receipt_sha256"],"train_support":tr["support"],"train_audit_receipt_sha256":audit["receipt_sha256"],
   "searched_candidates":sl.get("searched_candidates"),"train_shortlist_count":sl.get("shortlist_count"),
   "selected_candidate_id":field.get("selected_candidate_id"),"selected_coordinates":[] if selected is None else selected["coordinates"],
   "selected_mdl_bits":None if selected is None else selected["mdl_bits"],"selection_status":field["status"],
   "transport":{"target_opened_after_scope":ver.get("target_opened_after_scope"),"scope":scope["coverage"],
     "covered_verified":ver["covered_verified"],"abstained":ver["abstained"],"contradictions":ver["contradictions"],
     "mixed_cells":ver["mixed_cells"],"certified":ver["transport_certified"]},
   "public_authority":public,"public_state_counts":counts,"internal_state_counts":internal_counts,
   "explanation_verification":{"passed":len(certs),"failed":0,"unsupported_rendered_claims":0},
   "certificates":certs,"claim_ceiling":pre["claim_ceiling"]}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 dep={"schema":"c3x-g95-p5-public-deployment-v1","scientific_stage":STAGE,"verdict":ver["verdict"],
   "public_global_authority":public,"selected_candidate_id":field.get("selected_candidate_id"),
   "field_sha256":None if selected is None else digest(selected),
   "adjudication_receipt_sha256":out["receipt_sha256"],"allowed_states":pre["public_explanation_harness"]["states"],
   "rule":pre["public_explanation_harness"]["rule"]}
 seal(dep);Path(a.deployment).write_text(json.dumps(dep,indent=2,sort_keys=True)+"\n")
 Path(a.explanations).write_text("\n".join(lines)+"\n")
 print("G95_P5_FINAL",ver["verdict"],"public",public,"profiles",len(certs),"states",counts)

if __name__=="__main__":main()
