"""Finite minimax plan-value check; declared utilities only, NOT native chess."""
import math
def adjudicate(candidate):
    if not isinstance(candidate,dict) or not candidate:return {"status":"HOLD_EMPTY_REPLY_UNIVERSE"}
    unrestricted=[];restricted=[];policy={};missing=[]
    for reply,acts in candidate.items():
        if not isinstance(reply,str) or not reply or not isinstance(acts,list) or not acts:
            return {"status":"HOLD_MISSING_ACTIONS","reply":reply}
        if any(not isinstance(a,dict) or type(a.get("plan")) is not bool or
               type(a.get("utility")) not in (int,float) or not math.isfinite(a["utility"]) or
               not isinstance(a.get("action"),str) or not a["action"] for a in acts):
            return {"status":"HOLD_INVALID_ORACLE","reply":reply}
        if len({a["action"] for a in acts})!=len(acts):
            return {"status":"FAIL_DUPLICATE_ACTION","reply":reply}
        unrestricted.append(max(a["utility"] for a in acts))
        feasible=[a for a in acts if a["plan"]]
        if not feasible:missing.append(reply)
        else:
            best=max(feasible,key=lambda a:(a["utility"],a["action"]))
            restricted.append(best["utility"]);policy[reply]=best["action"]
    val=min(unrestricted)
    if missing:return {"status":"PLAN_NOT_GUARANTEED","plan_guaranteed":False,"unrestricted_value":val,
                       "missing_replies":sorted(missing),"plan_value":None,"plan_opportunity_cost":None}
    qval=min(restricted)
    return {"status":"DECLARED_FINITE_UTILITY_ONLY","plan_guaranteed":True,"unrestricted_value":val,
            "plan_value":qval,"plan_opportunity_cost":val-qval,"contingent_policy":policy,
            "warning":"Chess legality, native search and utility oracle not independently verified"}
def compare(a,b):
    x,y=adjudicate(a),adjudicate(b)
    good={"DECLARED_FINITE_UTILITY_ONLY","PLAN_NOT_GUARANTEED"}
    if x["status"] not in good or y["status"] not in good:return {"status":"HOLD_INPUT","a":x,"b":y}
    out={"status":"FINITE_UTILITY_COMPARISON_ONLY" if x["plan_guaranteed"] and y["plan_guaranteed"] else "DESCRIPTIVE_PLAN_SCOPE_ONLY",
         "a":x,"b":y,"value_difference_a_minus_b":x["unrestricted_value"]-y["unrestricted_value"]}
    return out
