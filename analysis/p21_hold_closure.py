#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path

CORE_HASH="2e143b561de457932f0fe91c2455112acdb4dc6aae8804874beae56586b7eb20"
CARRIER_HASH="208117210668e5256a35f3016c891006844e0c341ed4a94f98da685fe36a685e"

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--preseal",required=True)
 ap.add_argument("--core-precommit",required=True)
 ap.add_argument("--carrier-precommit",required=True)
 ap.add_argument("--diagnostic",required=True)
 ap.add_argument("--out",required=True)
 a=ap.parse_args()
 preseal=json.loads(Path(a.preseal).read_text())
 core=json.loads(Path(a.core_precommit).read_text())
 carrier=json.loads(Path(a.carrier_precommit).read_text())
 diag=json.loads(Path(a.diagnostic).read_text())
 assert core["precommit_sha256"]==CORE_HASH
 assert core["authorization"]=="P21-CORE-HOLD"
 assert core["selective_outcomes_consulted"] is False
 assert core["exposure_balance_pass"] is False
 assert carrier["precommit_sha256"]==CARRIER_HASH
 assert carrier["authorization"]=="P21-CARRIER-INTERVENTION-AUTHORIZED"
 assert carrier["selective_outcomes_consulted"] is False
 assert diag["authority"]=="POST_HOLD_NONAUTHORITATIVE_DESIGN_DIAGNOSTIC"
 assert diag["may_reopen_p21"] is False
 assert diag["selective_intervention_outcomes_consulted"] is False
 assert diag["feasible_witness_found"] is True
 assert diag["final_max_smd"]<=0.50+1e-12
 rule=preseal["final_decision_tree"]["primary_verdict_order"][0]
 assert "EXPOSURE_BALANCE_HOLD_NO_P21_CAUSAL_VERDICT" in rule
 out={
  "schema":"c3x-g9.4-p21-final-receipt-v1",
  "scientific_stage":"C3X 0.7.0-G9.4-P21",
  "status":"CLOSED_HOLD",
  "primary_verdict":"EXPOSURE_BALANCE_HOLD_NO_P21_CAUSAL_VERDICT",
  "causal_relation_transport_authority_promoted":False,
  "frozen_decision_tree_branch":1,
  "language_policy":"IMPLEMENTATION_LANGUAGE_NONAUTHORITATIVE_NATIVE_FIRST",
  "inanis_admission":{
    "run_id":36040871547,
    "verdict":"PASS",
    "authority":"CHANNEL_FACTORIZED_CAUSAL_ADMISSION",
    "channels":["MAIN×SEARCH_TT","MAIN×PAWN_EVAL_CACHE","QSEARCH×PAWN_EVAL_CACHE"],
    "structural_zero":"QSEARCH×SEARCH_TT"
  },
  "world_constitution":{
    "run_id":36041203061,
    "pawnless_core":{"worlds":384,"pool_sha256":"3a8381c23f7a03be99b9eeafe88c35b074d1063c833b0fa6e5e66ec47e53671e"},
    "pawn_carrier":{"worlds":384,"pool_sha256":"cf3afe5cef0d4fb9a95339f1b700b7c5b8466336154ba4a8d4adc5993a0dfd73"}
  },
  "core_gate":{
    "run_id":36041727983,
    "precommit_sha256":core["precommit_sha256"],
    "authorization":core["authorization"],
    "exposure_balance_pass":False,
    "heavy_vs_minor_smd":core["heavy_vs_minor_smd"],
    "threshold":core["balance_threshold"],
    "committed_cells":core["counts"]["committed"],
    "core_selective_interventions_executed":False
  },
  "post_hold_diagnostic":{
    "run_id":36043796288,
    "authority":diag["authority"],
    "start_max_smd":diag["start_max_smd"],
    "steps":diag["steps"],
    "final_max_smd":diag["final_max_smd"],
    "feasible_witness_found":diag["feasible_witness_found"],
    "inanis_postselection_engagement_gate_pass":diag["inanis_postselection_engagement_gate_pass"],
    "interpretation":"The frozen P21 selector failed, but the constituted SHAM-only pool contains a quota-preserving <=0.50 SMD witness. This localizes the HOLD to prospective selection design rather than proving absence of exposure overlap. It cannot reopen P21."
  },
  "carrier_lane":{
    "precommit_sha256":carrier["precommit_sha256"],
    "committed_cells":carrier["counts"]["committed"],
    "status":"PRECOMMIT_VALID / SELECTIVE_EXECUTION_INVALID",
    "scientific_authority":"NONE",
    "failure":"All carrier vertex jobs encountered the same harness baseline-envelope KeyError after partial in-memory search execution and emitted no vertex result artifacts.",
    "repair_within_p21":"FORBIDDEN",
    "reserved_for_successor":"precommit/census/world constitution only; selective outcomes must be prospectively reauthorized in a new mainline"
  },
  "lc0":{
    "status":"SINGLE_CHANNEL_COUNTEREXAMPLE_DESIGN_ONLY",
    "channel":"NEURAL_EVAL_CACHE",
    "causal_authority":False,
    "design":"c3x/ontology/p21-lc0-neural-cache-counterexample.json"
  },
  "authority_ceiling":[
    "P21 adds native-Rust Inanis channel admission and fresh SHAM/world-constitution evidence.",
    "P21 does not update the P20 causal relation-law transport verdict.",
    "No P21 HEAVY-vs-MINOR causal mediation conclusion is authorized.",
    "Post-HOLD matching feasibility is design evidence only."
  ],
  "next_mainline_constraint":"A successor may preseal a quota-preserving exposure-balance optimizer/matcher using only SHAM telemetry, but must use a new mainline and fresh selective outcomes; P21 cells may not be retroactively reselected for causal adjudication."
 }
 out["receipt_sha256"]=hashlib.sha256(canon(out)).hexdigest()
 Path(a.out).parent.mkdir(parents=True,exist_ok=True)
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("P21_FINAL_HOLD",out["primary_verdict"],out["receipt_sha256"])

if __name__=="__main__":main()
