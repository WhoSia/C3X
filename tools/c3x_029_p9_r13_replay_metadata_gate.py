#!/usr/bin/env python3
"""Fail-closed metadata contract for future C3X pinned versus shifted engine runs."""
import argparse,json
from pathlib import Path

PIN={"upstream_sha":"68e1e9b3811e16cad014b590d7443b9063b52",
     "threads":1,"hash_mb":16,"nnue":False,"depth":12,
     "root_order":"O","role":"STRICT"}
ARMS={"TT0_SEE_SHAM","TT1_SEE_SHAM","TT0_SEE_FLIP","TT1_SEE_FLIP"}

def classify(data):
    if data.get("schema")!="c3x029-P9-R13-replay-metadata-v1":
        raise ValueError("INVALID_SCHEMA")
    if set(data.get("arms",{}))!=ARMS:
        raise ValueError("MISSING_OR_EXTRA_ARM")
    if data.get("case_id")!="may2026-broadcast-game2":
        raise ValueError("UNREGISTERED_CASE")
    if data.get("source_sha256")!="0ff43e28dcb3a5e48dea6b61e4450fc8bb9e1f96363871c33c4b73524664db61":
        raise ValueError("SOURCE_SHA_MISMATCH")
    if not data.get("binary_sha256") or not data.get("patch_chain_sha256"):
        return {"status":"HOLD_UNVERIFIED_BINARY_OR_PATCH","pinned":False}
    if any(data.get(k)!=v for k,v in PIN.items()):
        return {"status":"CONFIGURATION_SHIFT_NOT_ORIGINAL_REPLAY","pinned":False,
                "differences":[k for k,v in PIN.items() if data.get(k)!=v]}
    if data.get("cold_processes_per_arm",0)<2:
        return {"status":"HOLD_INSUFFICIENT_COLD_REPEATS","pinned":True}
    observed=data["arms"]
    if any(set(observed[a])<{"bestmove","nodes","score_cp","tt_contact","see_contact","source_replay_equal"} for a in ARMS):
        return {"status":"HOLD_INCOMPLETE_EVENT_PROOF","pinned":True}
    if not all(observed[a]["source_replay_equal"] and observed[a]["tt_contact"] and observed[a]["see_contact"] for a in ARMS):
        return {"status":"FAIL_SOURCE_OR_OBSERVER_PARITY","pinned":True}
    return {"status":"READY_FOR_EXACT_NUMERIC_REPLAY_COMPARISON","pinned":True,
            "caution":"DOES_NOT_CERTIFY_CAUSAL_MEDIATION"}

def main():
    p=argparse.ArgumentParser();p.add_argument("--input",required=True)
    args=p.parse_args();print(json.dumps(classify(json.loads(Path(args.input).read_text())),sort_keys=True))

if __name__=="__main__":main()
