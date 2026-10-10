#!/usr/bin/env python3
"""C3X0.24 P4 M4 exact UCI deterministic survivor corroboration.
This module contains *only* pre-FIRST source and untouched StageA logic.
Fixed before July2025 source extraction. NO native engine or outcomes imported.
"""
from typing import Mapping,Optional
MODELS=("M0","M4_survivor")

def m4_survivor_corroboration(*,role:str,eligible:bool,source_reader_native:int|None,
                             baseline_native:int|None,baseline_UCI:str,
                             opposite_UCI:str,depth8to11:Mapping[int,Optional[str]],
                             legal_uci:set[str])->dict:
    base={"M4":baseline_UCI,"predict_flip":False,"reason":"M0_DEFAULT"}
    if baseline_UCI not in legal_uci or opposite_UCI not in legal_uci:
        raise ValueError("P4_ILLEGAL_UNTREATED_ROOT_LEADER")
    if not eligible:
        return {"M4":None,"predict_flip":False,"reason":"PRE_FIRST_INELIGIBLE_HOLD"}
    if role!="STRICT":
        return {**base,"reason":"BROAD_NULL_CONTROL"}
    if (not isinstance(source_reader_native,int) or
        not isinstance(baseline_native,int) or
        source_reader_native!=baseline_native):
        return {**base,"reason":"FIRST_READER_NOT_LINKED_TO_BASELINE_ROOT"}
    # The original depth ladder has exactly 8,9,10,11 observations; missing
    # or illegally mapped depth must not be silently treated as evidence.
    if any(depth8to11.get(i) not in legal_uci for i in (8,9,10,11)):
        return {**base,"reason":"DEPTH_SOURCE_CENSORED_OR_ILLEGAL"}
    d8,d9,d10,d11=(depth8to11[i] for i in (8,9,10,11))
    if opposite_UCI!=baseline_UCI and d11==opposite_UCI and        sum(x==opposite_UCI for x in (d8,d9,d10))>=1:
        return {"M4":opposite_UCI,"predict_flip":True,
                "reason":"CROSS_ORDER_SURVIVOR_RECONFIRMED_SAME_ORDER"}
    if d11!=baseline_UCI and sum(x==d11 for x in (d8,d9,d10))>=2:
        return {"M4":d11,"predict_flip":True,
                "reason":"WITHIN_ORDER_DEPTH_SURVIVOR"}
    return {**base,"reason":"ALTERNATIVE_NOT_CORROBORATED_IN_SAME_ORDER"}

if __name__=="__main__":
    raise SystemExit("P4_M4_DECISION_MODULE_ONLY__CALL_FUNCTION_WITH_SOURCE_ONLY")
