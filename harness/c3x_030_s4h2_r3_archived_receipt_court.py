#!/usr/bin/env python3
"""S4-H2/R3 independent offline audit of original R2 native source receipts.

Consumes archived bytes, not fresh engine output or an updated mutable result.
Distinguishes a physical mask receipt from an ordinary TT miss, and a signed
within-run value link from a cross-arm counterfactual causal mechanism.
"""
import argparse
import hashlib
import json
from pathlib import Path

SOURCE_RAW_SHA="dc1f10272ccbc01c8097f4488057085535fe2cea7c75946895f6b5c81c149120"
ARMS=("original","sham","zero","one","two","many")
SCHEMA="c3x030-s4h2-development-intervention-native-v1"

def sha(x):return hashlib.sha256(x).hexdigest()

def inspect_arm(arm,record,key):
    physical=record["mask_receipts"]
    signed=record["physically_supported_child_root_arithmetic_links"]
    ids={}
    ordinals=set()
    for item in physical:
        ident=item["id"];ordinal=int(item["ordinal"])
        if ident in ids or ordinal in ordinals:
            raise ValueError("S4H2R3_DUPLICATE_MASK_PROVENANCE")
        if (item["key"]!=key or item["ply"]!="1" or
            item["hit_before"]!="1" or item["hit_after"]!="0"):
            raise ValueError("S4H2R3_NOT_ACTUAL_PHYSICAL_TARGET_MASK")
        ids[ident]=item;ordinals.add(ordinal)
    if ordinals!=set(range(len(physical))):
        raise ValueError("S4H2R3_MASK_LOG_ORDINAL_GAP")
    if arm in ("original","sham","zero") and physical:
        raise ValueError("S4H2R3_CONTROL_MASK")
    if len(physical)>(0 if arm in ("original","sham","zero") else
                       1 if arm=="one" else 2 if arm=="two" else 8):
        raise ValueError("S4H2R3_MASK_BOUNDED_COUNT")
    seen=set()
    for edge in signed:
        ident=edge["child_invocation_id"]
        if ident not in ids or ident in seen:
            raise ValueError("S4H2R3_NONPHYSICAL_OR_DUPLICATE_LINK")
        seen.add(ident);mask=ids[ident]
        if (edge["parent_root_invocation_id"]!=mask["parent"]
            or edge["physical_tt_key"]!=key
            or int(edge["physical_mask_ordinal"])!=int(mask["ordinal"])
            or edge["observed_root_candidate_value"] != -edge["child_return_value"]):
            raise ValueError("S4H2R3_PARENT_OR_VALUE_MISMATCH")
    if record["bounded_mask_count"]!=len(physical) or record["verified_links"]!=len(signed):
        raise ValueError("S4H2R3_FALSE_SUMMARY")
    if record["not_full_counterfactual_mediation"] is not True:
        raise ValueError("S4H2R3_FORBIDDEN_CAUSAL_CLAIM")
    return {"bounded_masks":len(physical),"physically_supported_links":len(signed)}

def audit(original,eligibility):
    if sha(original)!=SOURCE_RAW_SHA:
        raise ValueError("S4H2R3_NOT_ARCHIVED_NATIVE_R2_SOURCE")
    r=json.loads(original);e=json.loads(eligibility)
    if r.get("schema")!=SCHEMA or r.get("verdict")!="PASS_DEVELOPMENT_SOURCE_INTERVENTION_OBSERVATION":
        raise ValueError("S4H2R3_SOURCE_SCHEMA_OR_VERDICT")
    if sha(eligibility)!=r["eligibility_receipt_sha256"]:
        raise ValueError("S4H2R3_ELIGIBILITY_RECEIPT_SHA")
    if e.get("split")!="development" or e.get("source_probes_only") is not True:
        raise ValueError("S4H2R3_ELIGIBILITY_SPLIT_OR_PROVENANCE")
    if (r.get("native_searches")!=96 or r.get("native_nodes",0)<=0
        or r.get("no_holdout_cases_executed") is not True
        or r.get("controls_all_equal") is not True
        or r.get("causal_mediation_proven") is not False):
        raise ValueError("S4H2R3_SCOPE")
    if r.get("pre_treatment_eligibility_binary_sha256")!=r.get("same_modified_binary_sha256"):
        raise ValueError("S4H2R3_BINARY_IDENTITY")
    cases=r["case_results"]
    frozen={x["case_id"]:x for x in e["cases"]}
    if len(cases)!=8 or set(cases)!=set(frozen):
        raise ValueError("S4H2R3_DEV_CASE_SUPPORT")
    counters={a:{"bounded_masks":0,"physically_supported_links":0,"root_changes":0} for a in ARMS}
    games=set()
    for id,case in sorted(cases.items()):
        k=case["frozen_eligibility_key"]
        if (case["split"]!="development" or case["game_id"]!=frozen[id]["game_id"]
            or frozen[id]["frozen_key"]!=k or frozen[id]["eligible"] is not True):
            raise ValueError("S4H2R3_ELIGIBILITY_OR_GAME_LEAK")
        games.add(case["game_id"])
        if not case["sham_matches_original"] or not case["zero_matches_sham"]:
            raise ValueError("S4H2R3_CONTROL_DRIFT")
        if set(case["exact_physical_mask_invocation_trace"])!=set(ARMS):
            raise ValueError("S4H2R3_ARMS_CHANGED")
        for arm in ARMS:
            z=inspect_arm(arm,case["exact_physical_mask_invocation_trace"][arm],k)
            if (case["physical_mask_receipt_count"][arm]!=z["bounded_masks"] or
                case["masked_child_root_signed_links"][arm]!=z["physically_supported_links"]):
                raise ValueError("S4H2R3_RESULT_TRACE_INCONSISTENCY")
            counters[arm]["bounded_masks"]+=z["bounded_masks"]
            counters[arm]["physically_supported_links"]+=z["physically_supported_links"]
            counters[arm]["root_changes"]+=case["root_bestmove_changes_versus_sham"][arm]
    if len(games)!=4:raise ValueError("S4H2R3_GAME_DEPENDENCE")
    if any(counters[a]["root_changes"]!=r["root_change_counts_by_arm"][a] for a in ARMS):
        raise ValueError("S4H2R3_ROOT_CHANGE_SUMMARY")
    return {"schema":"c3x030-s4h2-r3-independent-archived-source-court-v1",
       "native_r2_raw_sha256":sha(original),"original_eligibility_raw_sha256":sha(eligibility),
       "native_searches_inherited":96,"new_native_searches":0,
       "native_nodes_inherited":r["native_nodes"],
       "development_games":4,"development_fens":8,"holdout_searches":0,
       "arm_counters":counters,
       "controls_identical":True,
       "two_mask_root_changes_without_logged_physical_child_return_root_link":
           counters["two"]["root_changes"]>0 and counters["two"]["physically_supported_links"]==0,
       "source_provenance_valid":True,
       "complete_counterfactual_mediator_proven":False,
       "population_or_paper_superiority":"HOLD",
       "verdict":"PASS_R2_PHYSICAL_SOURCE_PROVENANCE_ONLY"}

def main():
    p=argparse.ArgumentParser()
    for field in ("r2-original","eligibility-original","out"):
        p.add_argument("--"+field,required=True)
    x=vars(p.parse_args())
    r=audit(Path(x["r2_original"]).read_bytes(),
            Path(x["eligibility_original"]).read_bytes())
    dest=Path(x["out"]);dest.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(r,indent=2,sort_keys=True)+"\n").encode()
    dest.write_bytes(raw)
    print("C3X_S4H2_R3_ARCHIVED_RECEIPTS",r["verdict"],r["arm_counters"],sha(raw))
if __name__=="__main__":main()
