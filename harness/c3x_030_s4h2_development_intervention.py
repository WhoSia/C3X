#!/usr/bin/env python3
"""C3X S4-H2: source-native, preregistered development-only TT intervention.

Reads independently frozen eligibility keys. Never uses observed treatment
outcomes to reselect source keys. No holdout runner in this module.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
from c3x_030_p11s4g_native_paired_court import run_source,native_mask_receipts,inspect_edges,CAPS,ARMS,SHAM_KEY
from c3x_030_p11s4a_native_trace_court import compare_records
from c3x_030_s4h2_r2_physical_trace_audit import verify_and_preserve

def digest(raw):return hashlib.sha256(raw).hexdigest()

def execute(protocol,eligibility,baseline,modified):
    if protocol.get("schema")!="c3x030-s4h2-preoutcome-native-execution-protocol-v1":
        raise ValueError("S4H2_DEV_PROTOCOL_SCHEMA")
    if eligibility.get("schema")!="c3x030-s4h2-source-only-eligibility-receipts-v1":
        raise ValueError("S4H2_DEV_ELIGIBILITY_SCHEMA")
    if eligibility.get("split")!="development" or eligibility.get("source_probes_only") is not True:
        raise ValueError("S4H2_DEV_NOT_DEVELOPMENT_OR_OUTCOME_BLIND")
    if (eligibility.get("engine_scores_read") is not False
        or eligibility.get("engine_bestmove_read") is not False
        or eligibility.get("engine_pv_read") is not False
        or eligibility.get("treatment_searches")!=0):
        raise ValueError("S4H2_DEV_PRETREATMENT_LEAK")
    if protocol.get("arm_order")!=list(ARMS):
        raise ValueError("S4H2_DEV_UNEXPECTED_ARMS")
    if any(protocol["mask_hit_caps"].get(arm)!=CAPS.get(arm) for arm in ARMS[1:]):
        raise ValueError("S4H2_DEV_DOSE_CHANGED")
    if os.environ.get("C3X_S4H2_ELIGIBILITY_MODE")=="1":
        raise ValueError("S4H2_DEV_DISCOVERY_MODE_MUST_BE_DISABLED")
    selection={x["case_id"]:x for x in eligibility["cases"]}
    cases=[x for x in protocol["cases"] if x["split"]=="development"]
    if len(cases)!=8 or set(selection)!={c["case_id"] for c in cases}:
        raise ValueError("S4H2_DEV_MISSING_OR_EXTRA_CASES")
    if digest(Path(baseline).read_bytes())==digest(Path(modified).read_bytes()):
        raise ValueError("S4H2_DEV_ORIGINAL_EQUALS_INTERVENTION_BINARY")
    out={"schema":"c3x030-s4h2-development-intervention-native-v1",
         "original_binary_sha256":digest(Path(baseline).read_bytes()),
         "same_modified_binary_sha256":digest(Path(modified).read_bytes()),
         "pre_registered_protocol_sha256":eligibility["protocol_sha256"],
         "pre_treatment_eligibility_binary_sha256":eligibility["binary_sha256"],
         "no_holdout_cases_executed":True,"causal_mediation_proven":False,
         "full_paper_superiority":"HOLD","case_results":{}}
    if eligibility["binary_sha256"]!=out["same_modified_binary_sha256"]:
        raise ValueError("S4H2_DEV_DISCOVERY_TREATMENT_BINARY_MISMATCH")
    for case in cases:
        id=case["case_id"];e=selection[id]
        if e["split"]!="development" or e["game_id"]!=case["game_id"]:
            raise ValueError("S4H2_DEV_TAINTED_CASE_IDENTITY")
        if e["eligible"] is not True or not isinstance(e["frozen_key"],str):
            raise ValueError("S4H2_DEV_ELIGIBLE_ONLY_PILOT_EXPECTS_HIT")
        key=e["frozen_key"]
        controls={}
        # Each arm is a fresh engine process, with two consecutive node-budget searches.
        controls["original"]=run_source(baseline,case["fen"],key,SHAM_KEY,0)
        for arm in ARMS[1:]:
            k=SHAM_KEY if arm=="sham" else key
            controls[arm]=run_source(modified,case["fen"],key,k,CAPS[arm])
        sham=controls["sham"]
        masks={arm:native_mask_receipts(controls[arm]) for arm in ARMS}
        for arm in ("original","sham","zero"):
            if masks[arm]:raise ValueError("S4H2_DEV_UNEXPECTED_CONTROL_MASK")
        # Zero physical contacts is a legitimate negative, not a reason to reselect.
        for arm,cap in (("one",1),("two",2)):
            if len(masks[arm])>cap:raise ValueError("S4H2_DEV_MASK_OVER_CAP")
        for arm in ("one","two","many"):
            if any(r["key"]!=key for r in masks[arm]):
                raise ValueError("S4H2_DEV_MASK_WRONG_KEY")
        edges={arm:inspect_edges(controls[arm]["events"]) for arm in ARMS}
        baseline_match=compare_records({"trials":controls["original"]["trials"]},
                                       {"trials":sham["trials"],"events":[]})
        zero_match=compare_records({"trials":sham["trials"]},
                                   {"trials":controls["zero"]["trials"],"events":[]})
        changed={arm:sum(a["bestmove"]!=b["bestmove"]
            for a,b in zip(sham["trials"],controls[arm]["trials"])) for arm in ARMS}
        exact_physical_trace=verify_and_preserve(masks,edges,key)
        physical_links={arm:exact_physical_trace[arm]["verified_links"] for arm in ARMS}
        out["case_results"][id]={
          "game_id":case["game_id"],"split":"development",
          "frozen_eligibility_key":key,
          "physical_mask_receipt_count":{k:len(v) for k,v in masks.items()},
          "masked_child_root_signed_links":physical_links,
          "exact_physical_mask_invocation_trace":exact_physical_trace,
          "root_bestmove_changes_versus_sham":changed,
          "sham_matches_original":baseline_match["noninterference_pass"],
          "zero_matches_sham":zero_match["noninterference_pass"],
          "baseline_sham_mismatches":baseline_match["mismatches"],
          "zero_sham_mismatches":zero_match["mismatches"],
          "native_trials":{k:controls[k]["trials"] for k in ARMS},
          "bounded_logs_not_full_search_tree":True}
        print("S4H2_DEV_NATIVE",id,"mask",{k:len(v) for k,v in masks.items()},
              "root_change",changed,"control_equal",
              baseline_match["noninterference_pass"] and zero_match["noninterference_pass"],flush=True)
    out["native_searches"]=len(cases)*len(ARMS)*2
    out["native_nodes"]=sum(t["nodes"] for z in out["case_results"].values()
                            for arm in ARMS for t in z["native_trials"][arm])
    out["controls_all_equal"]=all(z["sham_matches_original"] and z["zero_matches_sham"]
                                  for z in out["case_results"].values())
    out["root_change_counts_by_arm"]={arm:sum(z["root_bestmove_changes_versus_sham"][arm]
                                   for z in out["case_results"].values()) for arm in ARMS}
    out["verdict"]="PASS_DEVELOPMENT_SOURCE_INTERVENTION_OBSERVATION" if out["controls_all_equal"] else "HOLD_DEVELOPMENT_CONTROL_DRIFT"
    return out

def main():
    p=argparse.ArgumentParser()
    for x in ("protocol","eligibility","baseline","modified","out"):
        p.add_argument("--"+x,required=True)
    a=p.parse_args()
    pr=Path(a.protocol).read_bytes()
    el=Path(a.eligibility).read_bytes()
    e=json.loads(el)
    if e.get("protocol_sha256")!=digest(pr):
        raise ValueError("S4H2_DEV_PROTOCOL_ELIGIBILITY_SHA_MISMATCH")
    result=execute(json.loads(pr),e,a.baseline,a.modified)
    result["eligibility_receipt_sha256"]=digest(el)
    target=Path(a.out)
    target.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n").encode()
    target.write_bytes(raw)
    print("C3X_S4H2_DEV_RESULT",result["verdict"],"SEARCHES",result["native_searches"],
          "NODES",result["native_nodes"],"SHA",digest(raw),flush=True)
    if not result["controls_all_equal"]:
        raise SystemExit(2)

if __name__=="__main__":main()
