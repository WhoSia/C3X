#!/usr/bin/env python3
"""C3X 0.18: strict preflight for #6/#8 natural TT intervention authorization.
Source-exact writer epochs and a consumed reader must exist before altering SF16.
"""
import argparse, json
from pathlib import Path

REQUIRED=("case_id","engine_sha","trace_sha256","writer","reader")
WRITER=("key64","slot","write_epoch","depth","bound","value","root_ancestry")
READER=("key64","slot","observed_write_epoch","depth","alpha","beta",
        "used_value","root_ancestry","consumption_kind")

def authorize(doc):
    missing=[k for k in REQUIRED if k not in doc]
    if missing: return False, "MISSING_TOP:"+",".join(missing)
    if doc["case_id"] not in (6,8): return False,"CASE_NOT_FROZEN_6_OR_8"
    if doc["engine_sha"]!="68e1e9b3811e16cad014b590d7443b9063b3eb52":
        return False,"ENGINE_NOT_FROZEN"
    for name, keys in (("writer",WRITER),("reader",READER)):
        if not isinstance(doc[name],dict): return False,name.upper()+"_NOT_OBJECT"
        gaps=[k for k in keys if k not in doc[name]]
        if gaps: return False,name.upper()+"_FIELDS_MISSING:"+",".join(gaps)
    w,r=doc["writer"],doc["reader"]
    if (w["key64"],w["slot"],w["write_epoch"]) != (
            r["key64"],r["slot"],r["observed_write_epoch"]):
        return False,"PHYSICAL_WRITER_READER_MISMATCH"
    if not r["used_value"]: return False,"TT_PROBED_NOT_CONSUMED"
    if not doc.get("no_contact_sham_verified",False):
        return False,"NO_CONTACT_SHAM_UNVERIFIED"
    if not doc.get("observer_noninterference_verified",False):
        return False,"OBSERVER_NONINTERFERENCE_UNVERIFIED"
    if not doc.get("trace_complete",False):
        return False,"TRACE_CENSORED"
    if not doc.get("independent_lineage_audit_verified",False):
        return False,"INDEPENDENT_LINEAGE_AUDIT_MISSING"
    return True,"ELIGIBLE_FOR_SEPARATE_INTERVENTION_DESIGN_NOT_CAUSAL_PROOF"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--evidence",required=True)
    a=p.parse_args()
    evidence=json.loads(Path(a.evidence).read_text())
    approved,reason=authorize(evidence)
    print(json.dumps({"authorized":approved,"reason":reason},sort_keys=True))
    if not approved: raise SystemExit(2)
if __name__=="__main__":
    main()
