"""P24: distinguish contrast, verifiability and reply coverage of two candidate plans.
All input truth labels must come from an independent board-law/strategy oracle.
"""
def score(rows):
    if not rows: return {"status":"HOLD_EMPTY"}
    ids=set(); counts={"supported":0,"discriminating":0,"shared":0,"refuted":0}
    for r in rows:
        if not {"reply_id","a_plan","b_plan","verified"}<=r.keys():
            return {"status":"HOLD_MISSING_FIELDS"}
        if r["reply_id"] in ids:return {"status":"FAIL_DUPLICATE_REPLY"}
        ids.add(r["reply_id"])
        if r["verified"] is not True or type(r["a_plan"]) is not bool or type(r["b_plan"]) is not bool:
            return {"status":"HOLD_ORACLE"}
        if r["a_plan"] and not r["b_plan"]:counts["discriminating"]+=1
        elif r["a_plan"] and r["b_plan"]:counts["shared"]+=1
        elif not r["a_plan"] and not r["b_plan"]:counts["refuted"]+=1
        else:counts["supported"]+=1
    return {"status":"DECLARED_ORACLE_ONLY","n":len(rows),"counts":counts,
            "a_only_reply_fraction":counts["discriminating"]/len(rows),
            "warning":"candidate-specific reply alignment and plan truth require independent chess replay"}
