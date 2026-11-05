"""P40/R4 algebraic plan opportunity-cost intervals; no real chess oracle."""
from math import inf,isfinite,isnan

def bounds(record):
    a,b=record["lower"],record["upper"]
    a=-inf if a is None else float(a)
    b=inf if b is None else float(b)
    if isnan(a) or isnan(b) or a==inf or b==-inf or a>b:
        raise ValueError("BAD_INTERVAL")
    return a,b

def evaluate_plan(branches, total_responses, epsilon=20, verified_judge=False):
    if not 0<len(branches)<=total_responses:raise ValueError("BAD_SCOPE")
    if not isfinite(epsilon) or epsilon<0:raise ValueError("BAD_THRESHOLD")
    results=[]
    selective=False
    for r,case in sorted(branches.items()):
        legal=case["legal"]
        plan=set(case["plan"])
        if not legal or len(plan)!=len(case["plan"]) or not plan<=set(legal):
            raise ValueError("INVALID_PLAN")
        selective|=plan!=set(legal)
        if not plan:
            results.append((r,None,None,"UNAVAILABLE"))
            continue
        intervals={u:bounds(v) for u,v in legal.items()}
        best_lo=max(x[0] for x in intervals.values())
        best_hi=max(x[1] for x in intervals.values())
        plan_lo=max(intervals[u][0] for u in plan)
        plan_hi=max(intervals[u][1] for u in plan)
        lower=(max(0,best_lo-plan_hi)
               if isfinite(best_lo) and isfinite(plan_hi) else 0.0)
        upper=(max(0,best_hi-plan_lo)
               if isfinite(best_hi) and isfinite(plan_lo) else inf)
        results.append((r,lower,upper,"BOUNDED"))
    if not selective:raise ValueError("TRIVIAL_ALL_LEGAL_PLAN")
    if any(z[3]=="UNAVAILABLE" for z in results):
        decision="PLAN_UNAVAILABLE"
    elif max(z[1] for z in results)>epsilon:
        decision="HIGH_REGRET_WITNESS"
    elif len(branches)==total_responses and max(z[2] for z in results)<=epsilon:
        decision="LOW_REGRET_CERTIFIED"
    else:
        decision="UNRESOLVED"
    return {"decision":decision,
            "scope":"ALL_LEGAL" if len(branches)==total_responses else "SAMPLED",
            "judge":"VERIFIED" if verified_judge else "HOLD_UNVERIFIED",
            "scientific_status":("VALIDATED_JUDGE_DEPENDENT"
                                 if verified_judge else "HOLD_NO_INDEPENDENT_VALUE_JUDGE"),
            "response_count":len(branches),"total_response_count":total_responses,
            "regret_by_response":[{"r":r,"lower":lo,"upper":hi,"state":state}
                                  for r,lo,hi,state in results],
            "claim_ceiling":"Bounded mathematical opportunity cost only, not observed chess quality."}
