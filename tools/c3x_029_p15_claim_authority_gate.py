"""P15: claim authority is a partial order, not one vague PASS flag.
External original legality is not conferred by an asserted boolean.
"""
KINDS={"descriptive","contrastive","decision_relevant","aligned","transferred"}
def assess(row):
    if not isinstance(row,dict):return {"status":"HOLD_NOT_A_RECORD"}
    if row.get("kind") not in KINDS:return {"status":"HOLD_UNDEFINED_CLAIM"}
    if not isinstance(row.get("source_id"),str) or not row["source_id"]:
        return {"status":"HOLD_NO_SOURCE"}
    if row.get("native_replay") is not True or row.get("legal_replay") is not True:
        return {"status":"HOLD_SOURCE_NOT_INDEPENDENTLY_REPLAYED"}
    if row["kind"] in {"contrastive","aligned","transferred"} and row.get("competitor_refuted") is not True:
        return {"status":"HOLD_NO_MATCHED_COMPETITOR_REFUTER"}
    if row["kind"] in {"decision_relevant","aligned","transferred"} and row.get("matched_intervention") is not True:
        return {"status":"HOLD_NO_MATCHED_NATIVE_INTERVENTION"}
    if row["kind"]=="aligned" and row.get("same_root_event_join") is not True:
        return {"status":"HOLD_NO_WITHIN_RUN_JOIN"}
    if row["kind"]=="transferred" and row.get("disjoint_prospective") is not True:
        return {"status":"HOLD_NO_PROSPECTIVE_TRANSFER"}
    return {"status":"DECLARED_PREREQUISITES_PRESENT_ONLY","kind":row["kind"],
            "warning":"replay flags require external audit, this tool cannot certify source bytes"}
