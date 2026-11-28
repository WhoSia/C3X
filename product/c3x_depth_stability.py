"""T04-d: finite-depth evidence contract, not a draw or confidence theorem."""
QUICK_DEPTHS=(8,10)
AUDIT_DEPTHS=(8,10,14,18,22)
SMALL_GAP_CP=20

def depth_profile(name):
    if name=="quick":return QUICK_DEPTHS
    if name=="audit":return AUDIT_DEPTHS
    raise ValueError("C3X_BAD_DEPTH_PROFILE")

def assess(rows,profile="quick"):
    depths=depth_profile(profile)
    gaps={};reasons=[]
    def add(r):
        if r not in reasons:reasons.append(r)
    for d in depths:
        a,b=(r["forced_root_evaluations"].get(str(d)) for r in rows)
        if not a or not b or any(type(x.get("depth")) is not int or x["depth"]<d for x in (a,b)):
            gaps[str(d)]=None;add("INCOMPLETE");continue
        if any(x.get("bound","none")!="none" for x in (a,b)):
            gaps[str(d)]=None;add("BOUND_ONLY");continue
        av,bv=(x.get("mover_cp_or_null_if_mate") for x in (a,b))
        if type(av) is not int or type(bv) is not int:
            gaps[str(d)]=None;add("MATE_OR_NONFINITE");continue
        gaps[str(d)]=av-bv
    finite=[v for v in gaps.values() if v is not None]
    if finite and min(finite)<0<max(finite):add("DEPTH_SIGN_REVERSAL")
    if any(abs(v)<=SMALL_GAP_CP for v in finite):add("SMALL_GAP")
    if profile=="quick":add("SHALLOW_ONLY")
    if reasons:
        status="UNRESOLVED"
    elif all(v>SMALL_GAP_CP for v in finite):status="SAMPLED_A_PREFERENCE"
    elif all(v< -SMALL_GAP_CP for v in finite):status="SAMPLED_B_PREFERENCE"
    else:status="UNRESOLVED";add("INSUFFICIENT_EVIDENCE")
    return {"status":status,"reasons":reasons,"profile":profile,"depths":list(depths),
            "gaps_cp":gaps,"finite_observed_range_cp":[min(finite),max(finite)] if finite else None,
            "threshold_cp":SMALL_GAP_CP,"confidence_interval":False,
            "draw_proven":False,"global_best_proven":False,"independent_referee":False,
            "scope":"forced fixed pair at sampled depths, not unrestricted best move or statistical confidence"}
