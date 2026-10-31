"""P18: deterministic game-level bootstrap for a reported observed risk estimate.
No confidence interval if independent game count or labels are inadequate.
"""
import random
from collections import defaultdict
def bootstrap_game_macro(rows,iterations=1000,seed=0):
    if type(iterations) is not int or iterations<100 or iterations>100000:
        return {"status":"HOLD_INVALID_ITERATIONS"}
    groups=defaultdict(list)
    for x in rows:
        if not isinstance(x,dict) or not isinstance(x.get("game_id"),str) or not x["game_id"] or type(x.get("error")) is not bool:
            return {"status":"HOLD_UNVERIFIED_LABELS"}
        groups[x["game_id"]].append(x["error"])
    if len(groups)<5:return {"status":"HOLD_TOO_FEW_GAMES","games":len(groups)}
    vals=[sum(y)/len(y) for _,y in sorted(groups.items())]
    rng=random.Random(seed);n=len(vals);draws=[]
    for _ in range(iterations):
        draws.append(sum(vals[rng.randrange(n)] for _ in range(n))/n)
    draws.sort()
    return {"status":"DESCRIPTIVE_CLUSTER_BOOTSTRAP_ONLY","game_macro_error":sum(vals)/n,
            "percentile_95":[draws[int(.025*(iterations-1))],draws[int(.975*(iterations-1))]],
            "games":n,"warning":"bootstrap assumes exchangeable independent source games"}
