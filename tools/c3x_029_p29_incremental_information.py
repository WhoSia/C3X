"""Game-macro paired Brier gain from declared prospectively frozen forecasts.
This does NOT enforce forecast chronology or independently verify chess outcomes.
"""
from collections import defaultdict
import math
def compare(rows,min_games=5):
    if not rows:return {"status":"HOLD_EMPTY"}
    games=defaultdict(list);seen=set()
    for r in rows:
        if not isinstance(r,dict) or not {"case_id","game_id","split","y","plan_p","baseline_p"}<=r.keys():
            return {"status":"HOLD_SCHEMA"}
        if r["case_id"] in seen:return {"status":"FAIL_DUPLICATE_CASE"}
        seen.add(r["case_id"])
        if r["split"]!="heldout":return {"status":"HOLD_NOT_HELDOUT"}
        if not isinstance(r["game_id"],str) or not r["game_id"]:return {"status":"HOLD_GAME_ID"}
        if type(r["y"]) is not bool:return {"status":"HOLD_ORACLE_LABEL"}
        if any(type(r[k]) not in (int,float) or not math.isfinite(r[k]) or not 0<=r[k]<=1 for k in ("plan_p","baseline_p")):
            return {"status":"HOLD_PROBABILITY"}
        y=int(r["y"])
        games[r["game_id"]].append((r["baseline_p"]-y)**2-(r["plan_p"]-y)**2)
    if len(games)<min_games:return {"status":"HOLD_INSUFFICIENT_INDEPENDENT_GAMES","games":len(games)}
    macro=[sum(v)/len(v) for v in games.values()]
    gain=sum(macro)/len(macro)
    return {"status":"DECLARED_HELDOUT_LABELS_ONLY","game_macro_brier_gain":gain,
            "case_brier_gain":sum(sum(v) for v in games.values())/len(rows),
            "games":len(games),"cases":len(rows),
            "direction":"PLAN_IMPROVES" if gain>0 else "PLAN_WORSE" if gain<0 else "TIE",
            "caution":"External audit needed for label truth, source-game independence, and forecast freeze"}
