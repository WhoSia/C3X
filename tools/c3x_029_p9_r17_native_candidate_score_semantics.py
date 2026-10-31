#!/usr/bin/env python3
"""R17 evidence admission: native candidate scores require witnessed semantics.

Do not elevate a generic Stockfish fail-soft return to a game-value bound.
"""
from copy import deepcopy

REQUIRED=("engine_sha256","process_id","treatment_arm","root_call",
          "iteration_depth","aspiration_attempt","candidate_uci","score_pov",
          "completed","cp","kind","provenance")

def admit(record):
    missing=[k for k in REQUIRED if k not in record]
    if missing:return {"status":"HOLD_MISSING_FIELDS","missing":missing}
    p=record["provenance"]
    if not isinstance(p,dict):return {"status":"HOLD_UNTYPED_PROVENANCE"}
    if p.get("origin") not in ("root_move_store","root_candidate_search_return"):
        return {"status":"HOLD_UNKNOWN_SCORE_ORIGIN"}
    if not p.get("same_root_window_documented"):
        return {"status":"HOLD_NO_WINDOW_PROVENANCE"}
    if p.get("bound_interpretation")!="verified_root_candidate_interval":
        return {"status":"ABSTAIN_FAILSOFT_BOUND_NOT_CERTIFIED"}
    if not p.get("score_pov_verified"):
        return {"status":"HOLD_SCORE_POV"}
    if record["kind"] not in ("exact","lower","upper") or type(record["cp"]) is not int:
        return {"status":"HOLD_INVALID_TYPED_SCORE"}
    if record["completed"] is not True:return {"status":"HOLD_UNFINISHED_SEARCH"}
    return {"status":"ADMITTED_PROVENANCE_DECLARATION_ONLY",
            "caution":"SOURCE_LOG_AND_COLLECTOR_VALIDATION_REQUIRED"}

def admit_pair(a,b):
    xa,xb=admit(a),admit(b)
    if xa["status"]!="ADMITTED_PROVENANCE_DECLARATION_ONLY" or xb["status"]!="ADMITTED_PROVENANCE_DECLARATION_ONLY":
        return {"status":"ABSTAIN_UNVERIFIED_SCORE_SEMANTICS","a":xa,"b":xb}
    return {"status":"ELIGIBLE_FOR_BOUND_COMPARISON_ONLY_AFTER_NATIVE_BYTE_AUDIT"}

