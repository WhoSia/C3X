#!/usr/bin/env python3
"""S4-I development-only direct Stockfish TT early-return diagnostic.

Frozen R2 development keys are reused unchanged; no holdout scores or source
keys are inspected. This is a targeted read-only return-site pilot, not proof
of full TT-to-root counterfactual mediation.
"""
import argparse,hashlib,json,re
from c3x_030_s4j_state_alignment import parse as parse_state, compare as compare_states
from pathlib import Path
from c3x_030_p11s4g_native_paired_court import run_source,native_mask_receipts,SHAM_KEY
from c3x_030_p11s4a_native_trace_court import compare_records

R2_SHA="dc1f10272ccbc01c8097f4488057085535fe2cea7c75946895f6b5c81c149120"
SOURCE_SCHEMA="c3x030-s4h2-development-intervention-native-v1"
PROTOCOL_SCHEMA="c3x030-s4h2-preoutcome-native-execution-protocol-v1"
def digest(x):return hashlib.sha256(x).hexdigest()
def cutoffs(stderr,key):
    x=parse_state(stderr,key)
    return dict(x,observed_cutoffs=x["observed"],source_return_events=x["events"])

def execute(protocol,r2,baseline,modified):
    if r2.get("schema")!=SOURCE_SCHEMA or r2.get("verdict")!="PASS_DEVELOPMENT_SOURCE_INTERVENTION_OBSERVATION":
        raise ValueError("S4I_HOLD_R2_SOURCE")
    if protocol.get("schema")!=PROTOCOL_SCHEMA:
        raise ValueError("S4I_HOLD_FROZEN_PROTOCOL")
    cases=[c for c in protocol["cases"] if c["split"]=="development"]
    if len(cases)!=8 or set(r2["case_results"])!={c["case_id"] for c in cases}:
        raise ValueError("S4I_HOLD_DEV_COHORT")
    if digest(Path(baseline).read_bytes())!=r2["original_binary_sha256"]:
        raise ValueError("S4I_HOLD_BASELINE_BINARY_DRIFT")
    if digest(Path(modified).read_bytes())==r2["original_binary_sha256"]:
        raise ValueError("S4I_HOLD_SAME_BINARIES")
    out={"schema":"c3x030-s4j-native-candidate-search-state-development-v1",
         "inherited_r2_source_sha256":R2_SHA,
         "baseline_source_binary_sha256":digest(Path(baseline).read_bytes()),
         "typed_cutoff_binary_sha256":digest(Path(modified).read_bytes()),
         "untouched_holdout":True,"complete_counterfactual_mediation_proven":False,
         "cases":{}}
    for c in cases:
        id=c["case_id"]
        key=r2["case_results"][id]["frozen_eligibility_key"]
        orig=run_source(baseline,c["fen"],key,SHAM_KEY,0)
        sham=run_source(modified,c["fen"],key,SHAM_KEY,10000)
        two=run_source(modified,c["fen"],key,key,2)
        neg=compare_records({"trials":orig["trials"]},{"trials":sham["trials"],"events":[]})
        masks=native_mask_receipts(two)
        if native_mask_receipts(sham):
            raise ValueError("S4I_HOLD_SHAM_ACTUAL_MASK")
        if len(masks)>2 or any(m["key"]!=key for m in masks):
            raise ValueError("S4I_HOLD_UNEXPECTED_DOSE_OR_KEY")
        arm_cutoffs={"sham":cutoffs(sham["other_stderr"],key),
                      "two":cutoffs(two["other_stderr"],key)}
        alignment=compare_states(arm_cutoffs["sham"],arm_cutoffs["two"])
        root_changes=sum(a["bestmove"]!=b["bestmove"]
                         for a,b in zip(sham["trials"],two["trials"]))
        out["cases"][id]={"game_id":c["game_id"],"frozen_key":key,
          "original_sham_noninterference":neg["noninterference_pass"],
          "original_sham_mismatches":neg["mismatches"],
          "two_actual_mask_receipts":masks,
          "cutoff_return_trace":arm_cutoffs,
          "candidate_cross_arm_state_alignment":alignment,
          "root_move_changes":root_changes,
          "native_trials":{"original":orig["trials"],"sham":sham["trials"],"two":two["trials"]},
          "search_tree_incomplete":True}
        print("S4I_NATIVE",id,"masked",len(masks),
              "TT_early_returns",{k:v["observed_cutoffs"] for k,v in arm_cutoffs.items()},
              "root_changes",root_changes,"control",neg["noninterference_pass"],flush=True)
    out["native_searches"]=len(cases)*3*2
    out["native_nodes"]=sum(t["nodes"] for x in out["cases"].values()
        for arm in ("original","sham","two") for t in x["native_trials"][arm])
    out["control_noninterference"]=all(x["original_sham_noninterference"] for x in out["cases"].values())
    out["total_tt_cutoff_observations"]={arm:sum(x["cutoff_return_trace"][arm]["observed_cutoffs"]
        for x in out["cases"].values()) for arm in ("sham","two")}
    out["root_change_total"]=sum(x["root_move_changes"] for x in out["cases"].values())
    out["candidate_shared_state_total"]=sum(x["candidate_cross_arm_state_alignment"]["shared_candidate_state_count"] for x in out["cases"].values())
    out["candidate_unique_state_total"]=sum(len(x["candidate_cross_arm_state_alignment"]["unique_candidate_states"]) for x in out["cases"].values())
    out["candidate_repeated_state_ambiguity_total"]=sum(len(x["candidate_cross_arm_state_alignment"]["ambiguous_repeated_states"]) for x in out["cases"].values())
    out["causal_mediation_proven"]=False
    out["verdict"]="PASS_BOUNDED_CANDIDATE_STATE_ALIGNMENT_ONLY" if out["control_noninterference"] else "HOLD_TT_CUTOFF_LOGGER_NONINTERFERENCE"
    return out

def main():
    p=argparse.ArgumentParser()
    for name in ("protocol","r2","baseline","modified","out"):
        p.add_argument("--"+name,required=True)
    a=p.parse_args()
    raw=Path(a.r2).read_bytes()
    if digest(raw)!=R2_SHA:raise ValueError("S4I_HOLD_R2_ORIGINAL_SHA")
    pr=Path(a.protocol).read_bytes()
    r2=json.loads(raw)
    if digest(pr)!=r2["pre_registered_protocol_sha256"]:
        raise ValueError("S4I_HOLD_PRETREATMENT_PROTOCOL_DRIFT")
    result=execute(json.loads(pr),r2,a.baseline,a.modified)
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    serialized=(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n").encode()
    dest.write_bytes(serialized)
    print("C3X_S4J_NATIVE_STATE_ALIGNMENT",result["verdict"],
          result["native_searches"],result["native_nodes"],digest(serialized))
    if not result["control_noninterference"]:raise SystemExit(2)

if __name__=="__main__":main()
