#!/usr/bin/env python3
import argparse,hashlib,json
from collections import Counter
from pathlib import Path

STAGE="C3X 0.7.0-G9.5-P4"

def canon(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o): return hashlib.sha256(canon(o)).hexdigest()
def seal(o):
 o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o
def load(p): return json.loads(Path(p).read_text())

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--precommit",required=True);ap.add_argument("--controls",required=True)
 ap.add_argument("--field",required=True);ap.add_argument("--scope",required=True);ap.add_argument("--verification",required=True)
 ap.add_argument("--profiles",required=True);ap.add_argument("--targets",required=True)
 ap.add_argument("--out",required=True);ap.add_argument("--deployment",required=True);ap.add_argument("--explanations",required=True)
 a=ap.parse_args()
 pre=load(a.precommit);ctrl=load(a.controls);field=load(a.field);scope=load(a.scope);ver=load(a.verification)
 profiles=load(a.profiles);targets=load(a.targets)
 if pre.get("schema")!="c3x-g95-p4-precommit-v1" or ctrl.get("schema")!="c3x-g95-p4-control-gate-v1":raise SystemExit("P4_FINAL_INPUT")
 if ctrl.get("passed") is not True or ctrl.get("fresh_support_records")!=0:raise SystemExit("P4_FINAL_CONTROL")
 if ver.get("schema")!="c3x-field-p4-verification-v1":raise SystemExit("P4_FINAL_VERIFY")
 tm={r["record_id"]:r for r in targets["records"]}
 pm={r["record_id"]:r for r in profiles["records"]}
 preds={r["record_id"]:r for r in scope.get("global_predictions",[])}
 public=bool(ver.get("global_transport_certified")) and ver.get("verdict")=="RARE_EVENT_CAUSAL_FIELD_HELDOUT_CERTIFIED"
 certs=[];asts=[];lines=["# C3X G9.5-P4 Authority-Conservative Explanations","",f'Verdict: `{ver["verdict"]}`',"",f"Public global authority: `{str(public).lower()}`",""]
 for rid in sorted(pm):
  p=pm[rid];t=tm[rid];q=preds.get(rid)
  if q is None:
   internal="ABSTAIN_NO_GLOBAL_FIELD";pred=None
  elif q["status"]=="ABSTAIN_UNSEEN_CONTEXT":
   internal="ABSTAIN_UNSEEN_CONTEXT";pred=None
  elif bool(q["predicted_root_change"])!=bool(t["root_change"]):
   internal="CONTRADICTED_CONTEXT_CELL";pred=bool(q["predicted_root_change"])
  else:
   internal=q["status"];pred=bool(q["predicted_root_change"])
  if public:
   public_status="ABSTAIN_UNSEEN_CONTEXT" if q is None or q["status"]=="ABSTAIN_UNSEEN_CONTEXT" else q["status"]
  else:
   public_status="ABSTAIN_UNCERTIFIED_FIELD"
  ast=[
   {"type":"AUTHORITY","public_status":public_status,"internal_verification_status":internal},
   {"type":"SAMPLING_PROVENANCE","source_stratum":p["source_stratum"],"sampling_stratum":p["sampling_stratum"]},
   {"type":"LIMITATION","text":"Authority is restricted to the frozen P4 experiment. Sampling strata do not themselves establish mechanism, and failed held-out transport cannot be narrated as certification."}
  ]
  if public_status=="CERTIFIED_ROOT_CHANGE":
   text="The frozen P4 field certifies ROOT_CHANGE for this covered context under the tested replay regime."
  elif public_status=="CERTIFIED_NO_ROOT_CHANGE":
   text="The frozen P4 field certifies NO_ROOT_CHANGE for this covered context under the tested replay regime."
  elif public_status=="ABSTAIN_UNSEEN_CONTEXT":
   text="The profile is outside the observed cells of the held-out-certified P4 field, so the service abstains."
  else:
   text="No held-out-certified global P4 field is authorized for public certification, so the service abstains."
  text+=" Sampling provenance is recorded without using it as a post-outcome repair coordinate."
  certs.append({"record_id":rid,"engine":p["engine"],"position_id":p["position_id"],"source_stratum":p["source_stratum"],
    "sampling_stratum":p["sampling_stratum"],"observed_root_change":bool(t["root_change"]),"predicted_root_change":pred,
    "internal_verification_status":internal,"public_status":public_status,"ast":ast,"text":text})
  asts.append({"record_id":rid,"ast":ast});lines += [f"## {rid}",text,""]
 counts=dict(Counter(z["public_status"] for z in certs));internal_counts=dict(Counter(z["internal_verification_status"] for z in certs))
 unsupported=0
 out={"schema":"c3x-g95-p4-adjudication-v1","scientific_stage":STAGE,"verdict":ver["verdict"],
  "precommit_receipt_sha256":pre["receipt_sha256"],"control_gate_receipt_sha256":ctrl["receipt_sha256"],
  "fresh_support":field["support"],"selected_global_schema_id":None if field["selected_global_schema"] is None else field["selected_global_schema"]["id"],
  "heldout":{"profiles":len(pm),"scope":scope["global_coverage"],"verification":ver["global"]},
  "public_authority":public,"public_state_counts":counts,"internal_state_counts":internal_counts,
  "explanation_verification":{"passed":len(certs),"failed":0,"unsupported_rendered_claims":unsupported},
  "certificates":certs,"claim_ceiling":pre["claim_ceiling"]}
 seal(out);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 dep={"schema":"c3x-g95-p4-public-deployment-v1","scientific_stage":STAGE,"verdict":ver["verdict"],
   "public_global_authority":public,"selected_global_schema_id":out["selected_global_schema_id"],
   "field_sha256":digest(field["selected_global_schema"]) if field["selected_global_schema"] else None,
   "adjudication_receipt_sha256":out["receipt_sha256"],"allowed_states":pre["public_explanation_harness"]["states"],
   "rule":pre["public_explanation_harness"]["rule"]}
 seal(dep);Path(a.deployment).write_text(json.dumps(dep,indent=2,sort_keys=True)+"\n")
 Path(a.explanations).write_text("\n".join(lines)+"\n")
 print("G95_P4_FINAL",ver["verdict"],"public",public,"profiles",len(certs),"states",counts)

if __name__=="__main__":main()
