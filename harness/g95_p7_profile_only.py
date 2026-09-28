#!/usr/bin/env python3
"""Baseline-only train profile materialization for C3X G9.5-P7.

Execution-recovery utility. It reuses the frozen P7 precommit and constructs
CSEG profiles without running any counterfactual replay or reading any target.
It may establish failure of target-independent necessary state gates only.
"""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import c3x_cseg_input_v1 as cseg
sys.path.insert(0,str(ROOT/"harness"))
import p32_event_court as p32

STAGE="C3X 0.7.0-G9.5-P7"

def load(p):return json.loads(Path(p).read_text())
def sha_file(p):
 import hashlib
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--precommit",required=True);ap.add_argument("--case-id",required=True)
 ap.add_argument("--binary",required=True);ap.add_argument("--sampler",required=True);ap.add_argument("--sampling-plan",required=True)
 ap.add_argument("--cseg-kernel",required=True);ap.add_argument("--go-verifier",required=True)
 ap.add_argument("--profile-out",required=True);ap.add_argument("--manifest-out",required=True)
 a=ap.parse_args()
 pre=load(a.precommit);case=next((x for x in pre["cases"] if x["case_id"]==a.case_id),None)
 if not case or case["role"]!="STRUCTURAL_TRAIN":raise SystemExit("P7_PROFILE_ONLY_CASE")
 v=pre["variants"][case["engine"]]
 if sha_file(a.binary)!=v["sha256"]:raise SystemExit("P7_PROFILE_ONLY_BINARY")
 protocol=v["protocol"]
 work=Path(a.profile_out).parent/".profile-only";work.mkdir(parents=True,exist_ok=True)
 parent=p32.run_history(a.binary,protocol,case["cell"],"CATALOG",case["family"],case["frontier"],None,work/"parent")
 trace_path=work/"parent-trace.json";trace_path.write_text(json.dumps(parent["trace"],sort_keys=True)+"\n")
 sample_path=work/"sampling.json"
 subprocess.run([a.sampler,"sample","--trace",str(trace_path),"--plan",a.sampling_plan,
  "--max-events",str(pre["execution"]["candidate_events_per_world"]),"--out",str(sample_path)],check=True)
 samp=load(sample_path)
 if samp.get("target_fields_consulted") is not False or samp.get("raw_full_key_emitted") is not False:
  raise SystemExit("P7_PROFILE_ONLY_SAMPLER_FIREWALL")
 internal=cseg.prepare_batch(case["cell"]["fen"],parent["trace"],samp["selected"])
 internal_path=work/"cseg-internal.json";internal_path.write_text(json.dumps(internal,sort_keys=True)+"\n")
 states_path=work/"cseg-states.json";go_path=work/"go-parity.json"
 subprocess.run([a.cseg_kernel,"materialize","--input",str(internal_path),"--out",str(states_path)],check=True)
 subprocess.run([a.go_verifier,str(internal_path),str(states_path),str(go_path)],check=True)
 states=load(states_path);go=load(go_path)
 if go.get("pass") is not True or states.get("target_fields_consulted") is not False or states.get("raw_tt_key_emitted") is not False:
  raise SystemExit("P7_PROFILE_ONLY_CSEG_FIREWALL")
 rows=[]
 for st in states["records"]:
  rows.append({"record_id":f'{case["case_id"]}:{st["event_id"][:16]}',"engine":case["engine"],
   "position_id":case["position_id"],"source_stratum":case["source_stratum"],"source_kind":case["source_kind"],
   "event_id":st["event_id"],"sampling_stratum":st["sampling_stratum"],"state_ids":st["state_ids"],
   "graph_census":st["graph_census"],"current_event":st["current_event"],"board_atoms":st["board_atoms"],
   "causal_availability":"BASELINE_PREFIX_ONLY","target_fields_consulted":False,"raw_tt_key_emitted":False,
   "counterfactual_information_consulted":False,"fiber_id_consulted":False})
 out={"schema":"c3x-cseg-profile-batch-p7-v1","scientific_stage":STAGE,"case_id":case["case_id"],
  "role":"STRUCTURAL_TRAIN","source_stratum":case["source_stratum"],"records":rows,
  "target_fields_consulted":False,"raw_tt_key_emitted":False,"counterfactual_information_consulted":False,"fiber_id_consulted":False}
 Path(a.profile_out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 man={"schema":"c3x-g95-p7-profile-only-recovery-v1","scientific_stage":STAGE,"case_id":case["case_id"],
  "canonical_science_run":36385972623,"canonical_science_head":"b8cd6905a8f7d7e7078a7b7b4d381999d16d79de",
  "selected_records":len(rows),"target_fields_consulted":False,"counterfactual_replay_executed":False,
  "go_cseg_parity":go.get("pass"),"science_changed":False,"purpose":"TARGET_INDEPENDENT_NECESSARY_GATE_ONLY"}
 Path(a.manifest_out).write_text(json.dumps(man,indent=2,sort_keys=True)+"\n")
 print("P7_PROFILE_ONLY",case["case_id"],len(rows))

if __name__=="__main__":main()
