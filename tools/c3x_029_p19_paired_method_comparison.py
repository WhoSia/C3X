"""P19: compare two explanation methods on the SAME independently labeled cases.

No score if any case is unmatched; no advantage from unequal coverage.
"""
def paired(rows_a, rows_b):
    if not rows_a or not rows_b:return {"status":"HOLD_EMPTY"}
    def mapping(rows):
        d={}
        for r in rows:
            if not isinstance(r,dict) or any(k not in r for k in ("case_id","game_id","emitted","error")):
                return None
            if r["case_id"] in d:return None
            d[r["case_id"]]=r
        return d
    a,b=mapping(rows_a),mapping(rows_b)
    if a is None or b is None:return {"status":"HOLD_INVALID_CASES"}
    if set(a)!=set(b):return {"status":"HOLD_UNMATCHED_CASE_UNIVERSE"}
    if any(a[k]["game_id"]!=b[k]["game_id"] for k in a):
        return {"status":"HOLD_SOURCE_MISMATCH"}
    if any(type(r["emitted"]) is not bool or (r["emitted"] and type(r["error"]) is not bool) or
           (not r["emitted"] and r["error"] is not None) for r in list(a.values())+list(b.values())):
        return {"status":"HOLD_INVALID_LABEL"}
    both=[k for k in a if a[k]["emitted"] and b[k]["emitted"]]
    if not both:return {"status":"HOLD_NO_COMMON_COVERAGE"}
    ea=sum(a[k]["error"] for k in both);eb=sum(b[k]["error"] for k in both)
    return {"status":"PAIRED_DESCRIPTIVE_ONLY","matched_total":len(a),"both_emitted":len(both),
        "common_coverage":len(both)/len(a),"a_errors":ea,"b_errors":eb,
        "a_risk":ea/len(both),"b_risk":eb/len(both),
        "paired_error_difference_a_minus_b":(ea-eb)/len(both),
        "warning":"not an independent game-level effect estimate; error oracle must be audited"}
