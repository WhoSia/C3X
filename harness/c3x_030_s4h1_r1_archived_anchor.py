#!/usr/bin/env python3
"""C3X S4-H1/R1: cross-check independently archived PRE-outcome S4-H0 bytes.

Do not accept a freshly generated hash as its own historical witness.
The original H0 CI was run 43140220882 at commit b356485, predating
S4-H1 run 43145442927. Original H0 log reports the SHA below.
"""
import argparse
import hashlib
import json
from pathlib import Path

H0_RUN_ID = 43140220882
H0_HEAD_SHA = "b356485813bb31c3f9d0bd150f70ebb44fbbbe1f"
H0_MANIFEST_SHA256 = "1741592a52675c5170fdb076bb96b6842cbdced43e40c8a85c82f80c4ba0d247"

def attest(original: bytes, reproduced: bytes) -> dict:
    a = hashlib.sha256(original).hexdigest()
    b = hashlib.sha256(reproduced).hexdigest()
    if a != H0_MANIFEST_SHA256:
        raise ValueError("S4H1_R1_ARCHIVED_H0_NOT_ORIGINAL")
    if b != H0_MANIFEST_SHA256:
        raise ValueError("S4H1_R1_REGENERATED_MANIFEST_DRIFT")
    if original != reproduced:
        raise ValueError("S4H1_R1_SAME_HASH_DIFFERENT_BYTES")
    data = json.loads(original)
    if data.get("schema") != "c3x030-f2-blind-holdout-manifest-v1":
        raise ValueError("S4H1_R1_SCHEMA")
    if len(data.get("entries", [])) != 16 or len(data.get("development_entries", [])) != 8:
        raise ValueError("S4H1_R1_COHORT_SIZE")
    return {
        "schema": "c3x030-s4h1-r1-archived-byte-anchor-v1",
        "original_source_run": H0_RUN_ID,
        "original_source_commit": H0_HEAD_SHA,
        "source_raw_sha256": a,
        "reproduced_raw_sha256": b,
        "bytes_identical": True,
        "independent_archived_run_bytes_compared": True,
        "historical_chronology_inferred_from_ci_run_metadata_not_cryptographic_timestamp": True,
        "independent_real_world_population_sample": False,
        "native_engine_searches": 0,
        "methods_superiority": "HOLD",
        "verdict": "PASS_H0_H1_EXACT_ARCHIVED_BYTE_IDENTITY"
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--archived-h0", required=True)
    p.add_argument("--regenerated-h1", required=True)
    p.add_argument("--out", required=True)
    x = p.parse_args()
    result = attest(Path(x.archived_h0).read_bytes(), Path(x.regenerated_h1).read_bytes())
    out = Path(x.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("C3X_S4H1_R1_ARCHIVED_RAW_IDENTITY", result["verdict"], result["source_raw_sha256"])

if __name__ == "__main__":
    main()
