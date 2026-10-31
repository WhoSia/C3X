"""P17: precommitted, game-aware claim error and abstention measurement."""
def evaluate(rows):
    if not rows:return {"status":"HOLD_NO_ROWS"}
    seen=set();by_game={}
    for x in rows:
        if not isinstance(x,dict) or not all(k in x for k in ("case_id","game_id","emitted","error")):
            return {"status":"HOLD_MISSING"}
        if x["case_id"] in seen:return {"status":"FAIL_DUPLICATE_CASE"}
        seen.add(x["case_id"])
        if not isinstance(x["game_id"],str) or not x["game_id"] or type(x["emitted"]) is not bool:
            return {"status":"HOLD_UNTYPED"}
        if x["emitted"] and type(x["error"]) is not bool:return {"status":"HOLD_UNKNOWN_ERROR"}
        if not x["emitted"] and x["error"] is not None:return {"status":"HOLD_REFUSAL_HAS_ERROR_LABEL"}
        by_game.setdefault(x["game_id"],[]).append(x)
    n=len(rows);em=[x for x in rows if x["emitted"]]
    if not em:return {"status":"ZERO_COVERAGE","coverage":0.0,"risk":None,"games":len(by_game)}
    # Two distinct estimands: item-weighted and macro-game conditional error.
    risks=[]
    for v in by_game.values():
        sub=[r for r in v if r["emitted"]]
        if sub:risks.append(sum(r["error"] for r in sub)/len(sub))
    return {"status":"OBSERVED_LABELS_ONLY","coverage":len(em)/n,
            "risk":sum(x["error"] for x in em)/len(em),
            "macro_game_risk":sum(risks)/len(risks),
            "games":len(by_game),"covered_games":len(risks),
            "caution":"labels, cluster independence and claim truth not source verified"}
