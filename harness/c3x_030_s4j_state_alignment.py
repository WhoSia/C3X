#!/usr/bin/env python3
"""S4-J strict cross-arm TT cutoff state comparison; not causal mediation.

A candidate identical state is (position TT key, search depth, alpha, beta,
ply, PV flag, cut-node flag). Repeated matches within either run are AMBIGUOUS.
Invocation IDs never match across processes, and return-value differences are
observational only (not an identified intervention-mediated counterfactual).
"""
import re
from collections import defaultdict

EVENT=re.compile(
    r"^C3X_S4I_TT_CUTOFF ordinal=(\d+) id=(\d+) parent=(\d+) key=(\d+) "
    r"ply=1 search_depth=(-?\d+) alpha=(-?\d+) beta=(-?\d+) "
    r"pv=([01]) cutnode=([01]) return_value=(-?\d+)$"
)
MAX_EVENTS=8

def parse(stderr,key):
    seen=[]
    for line in stderr:
        if not line.startswith("C3X_S4I_TT_CUTOFF"): continue
        m=EVENT.fullmatch(line)
        if m is None: raise ValueError("S4J_HOLD_MALFORMED_STATE_EVENT")
        ordinal,ident,parent,tt_key,ply_depth,alpha,beta,pv,cutnode,value=map(int,m.groups())
        if (ordinal!=len(seen) or ordinal>=MAX_EVENTS or ident<=0 or
            tt_key!=int(key) or alpha>=beta):
            raise ValueError("S4J_HOLD_INVALID_STATE_OR_SOURCE")
        state=(tt_key,ply_depth,alpha,beta,1,pv,cutnode)
        seen.append({"ordinal":ordinal,"invocation_id":str(ident),
                     "parent_id":str(parent),"state":list(state),
                     "return_value":value})
    return {"events":seen,"observed":len(seen),
            "right_censored":len(seen)==MAX_EVENTS,
            "coverage_complete":False}

def compare(sham,two):
    a=defaultdict(list);b=defaultdict(list)
    for rec in sham["events"]: a[tuple(rec["state"])].append(rec)
    for rec in two["events"]: b[tuple(rec["state"])].append(rec)
    common=set(a)&set(b)
    unique=[]
    ambiguous=[]
    for key in sorted(common):
        if len(a[key])!=1 or len(b[key])!=1:
            ambiguous.append({"state":list(key),"sham_count":len(a[key]),"two_count":len(b[key])})
            continue
        sh=a[key][0];tr=b[key][0]
        unique.append({"state":list(key),"sham_return":sh["return_value"],
                       "two_return":tr["return_value"],
                       "value_diff":tr["return_value"]-sh["return_value"],
                       "same_return_value":sh["return_value"]==tr["return_value"],
                       "not_matched_invocation_identity":True})
    return {"unique_candidate_states":unique,
            "ambiguous_repeated_states":ambiguous,
            "sham_only_state_count":len(set(a)-set(b)),
            "two_only_state_count":len(set(b)-set(a)),
            "shared_candidate_state_count":len(common),
            "any_right_censoring":bool(sham["right_censored"] or two["right_censored"]),
            "causal_state_alignment_proven":False,
            "root_mediation_proven":False}
