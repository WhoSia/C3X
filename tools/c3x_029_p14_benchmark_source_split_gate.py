#!/usr/bin/env python3
"""C3X P14: provenance admission BEFORE scoring BinProp-style motif claims.

Rejects cross-split leakage at source-game, position-root and continuation level.
Does NOT infer chess legality or compare unseen binaries.
"""
from collections import defaultdict

SPLITS={"support","development","heldout"}
GROUPS={"positive","negative","nearby_negative"}

def audit(records):
    if not records: return {"status":"HOLD_EMPTY"}
    required={"case_id","game_id","root_id","continuation_id","split","group","source_state_verified","engine_label_verified"}
    missing=[(i,sorted(required-set(x))) for i,x in enumerate(records) if not required.issubset(x)]
    if missing:return {"status":"HOLD_MISSING_FIELDS","cases":missing}
    if any(not all(isinstance(x[k],str) and x[k] for k in ("case_id","game_id","root_id","continuation_id")) for x in records):
        return {"status":"HOLD_INVALID_IDENTITY"}
    if any(x["split"] not in SPLITS or x["group"] not in GROUPS for x in records):
        return {"status":"HOLD_INVALID_SPLIT_GROUP"}
    if any(type(x[k]) is not bool or not x[k] for x in records for k in ("source_state_verified","engine_label_verified")):
        return {"status":"HOLD_UNVERIFIED_OR_UNTYPED_SOURCE"}
    if len({x["case_id"] for x in records})!=len(records):
        return {"status":"FAIL_DUPLICATE_CASES"}
    for key in ("game_id","root_id","continuation_id"):
        groups=defaultdict(set)
        for x in records: groups[x[key]].add(x["split"])
        leakage=sorted(k for k,splits in groups.items() if len(splits)>1)
        if leakage:return {"status":"FAIL_CROSS_SPLIT_LEAKAGE","key":key,"ids":leakage}
    heldout=[x for x in records if x["split"]=="heldout"]
    if not heldout:return {"status":"HOLD_NO_HELDOUT"}
    if {x["group"] for x in heldout}!=GROUPS:
        return {"status":"HOLD_INCOMPLETE_HELDOUT_GROUPS"}
    return {"status":"METADATA_ADMISSIBLE_NOT_BYTE_VERIFIED",
            "heldout_count":len(heldout),"heldout_games":len({x["game_id"] for x in heldout}),
            "caution":"declared checks are not independent chess legality/engine replay proofs"}
