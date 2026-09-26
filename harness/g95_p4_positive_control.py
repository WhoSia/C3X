#!/usr/bin/env python3
import argparse,hashlib,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"harness"))
import p32_event_court as p32

STAGE="C3X 0.7.0-G9.5-P4"

def canon(o):
 return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def seal(o):
 o.pop("receipt_sha256",None)
 o["receipt_sha256"]=hashlib.sha256(canon(o)).hexdigest()
 return o

def load(p):
 return json.loads(Path(p).read_text())

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--p32-pre",required=True)
 ap.add_argument("--p32-final",required=True)
 ap.add_argument("--binary",required=True)
 ap.add_argument("--engine",required=True)
 ap.add_argument("--case-id",required=True)
 ap.add_argument("--expected-removal-size",type=int,required=True)
 ap.add_argument("--out",required=True)
 a=ap.parse_args()

 pre=load(a.p32_pre);final=load(a.p32_final);p4=load(a.p4_precommit)
 if p4.get("schema")!="c3x-g95-p4-precommit-v1": raise SystemExit("P4_PC_PRECOMMIT")
 if p32.sha_file(a.binary)!=p4["variants"][a.engine]["sha256"]: raise SystemExit("P4_PC_BINARY_ID")
 if pre.get("schema")!="c3x-p32-precommit-v1" or final.get("schema")!="c3x-p32-adjudication-v1":
  raise SystemExit("P4_PC_PARENT_SCHEMA")
 c0=next((z for z in pre["cases"] if z["case_id"]==a.case_id),None)
 cert=next((z["case"] for z in final["certificates"] if z["case"]["case_id"]==a.case_id),None)
 if c0 is None or cert is None:
  raise SystemExit("P4_PC_CASE")
 rem=cert.get("removal",{})
 if rem.get("status")!="CERTIFIED" or len(rem.get("addresses",[]))!=a.expected_removal_size:
  raise SystemExit("P4_PC_PARENT_CERT")

 work=Path(a.out).parent/"runs"
 protocol=p32.protocol_for(a.engine)
 base=p32.run_history(a.binary,protocol,c0["cell"],"CATALOG",c0["family"],8,None,work/"baseline")
 cf=p32.run_history(a.binary,protocol,c0["cell"],"REMOVE_SET",c0["family"],cert["selected_frontier"],rem["addresses"],work/"remove")

 base_ok=base["semantic"]["bestmove"]==cert["baseline"]["bestmove"]
 expected_cf=rem["semantic"]["bestmove"]
 cf_ok=cf["semantic"]["bestmove"]==expected_cf
 changed=cf["semantic"]["bestmove"]!=base["semantic"]["bestmove"]

 out={
  "schema":"c3x-g95-p4-positive-control-v1",
  "scientific_stage":STAGE,
  "authority":"INSTRUMENT_CALIBRATION_ONLY_NO_FRESH_SUPPORT_VOTE",
  "engine":a.engine,
  "case_id":a.case_id,
  "expected_removal_size":a.expected_removal_size,
  "baseline_match":base_ok,
  "counterfactual_match":cf_ok,
  "root_change_reproduced":changed,
  "parent_baseline_bestmove":cert["baseline"]["bestmove"],
  "parent_counterfactual_bestmove":expected_cf,
  "current_baseline_bestmove":base["semantic"]["bestmove"],
  "current_counterfactual_bestmove":cf["semantic"]["bestmove"],
  "address_set_sha256":hashlib.sha256(("\n".join(sorted(rem["address_ids"]))).encode()).hexdigest(),
  "fresh_support_vote":False,
  "status":"PASS" if base_ok and cf_ok and changed else "FAIL"
 }
 seal(out)
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print("G95_P4_POSITIVE_CONTROL",a.engine,out["status"],a.case_id)
 if out["status"]!="PASS":
  raise SystemExit("P4_POSITIVE_CONTROL_FAIL")

if __name__=="__main__":
 main()
