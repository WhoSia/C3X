"""Finite utility-backed plan separation: a LOWER bound vs rival UPPER bound.
Only declared abstract utilities; no claim of real chess or engine causal proof.
"""
from c3x_029_p29_value_probe import adjudicate
def certify(a,b):
    x,y=adjudicate(a),adjudicate(b)
    if x["status"]!="DECLARED_FINITE_UTILITY_ONLY":
        return {"status":"HOLD_A_PLAN_NOT_GUARANTEED_OR_ORACLE","a":x}
    if y["status"] not in ("DECLARED_FINITE_UTILITY_ONLY","PLAN_NOT_GUARANTEED"):
        return {"status":"HOLD_B_ORACLE","b":y}
    lower=x["plan_value"];upper=y["unrestricted_value"]
    if lower>upper:return {"status":"FINITE_SEPARATION_RELATIVE_TO_DECLARED_UTILITY",
        "candidate_a_lower_bound":lower,"candidate_b_upper_bound":upper,"strict_margin":lower-upper,
        "warning":"Fixed horizon and declared utility only; not native chess or engine cause"}
    return {"status":"NO_VALUE_SEPARATION_CERTIFICATE",
        "candidate_a_lower_bound":lower,"candidate_b_upper_bound":upper,"gap":lower-upper}
