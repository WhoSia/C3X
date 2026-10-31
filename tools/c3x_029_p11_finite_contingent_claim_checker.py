#!/usr/bin/env python3
"""C3X 0.29 P11: finite quantified chess-explanation claim checker.

Inputs are independently validated legal-action labels supplied by a collector.
It does not claim to validate chess legality or infer Stockfish's motives.
"""
from itertools import product

def check_claim(reply_legal_actions, satisfying_by_property, declared_domain):
    """Return constructive evidence for forall reply exists ONE action satisfying ALL properties."""
    if not declared_domain:
        return {"status":"ABSTAIN_EMPTY_DOMAIN"}
    if len(declared_domain)!=len(set(declared_domain)):
        return {"status":"FAIL_DUPLICATE_DOMAIN"}
    if set(declared_domain)!=set(reply_legal_actions):
        return {"status":"HOLD_INCOMPLETE_LEGAL_REPLY_DOMAIN"}
    if not satisfying_by_property:
        return {"status":"ABSTAIN_NO_NONTRIVIAL_PROPERTY"}
    witness={}
    for r in declared_domain:
        legal=set(reply_legal_actions[r])
        if not legal:
            return {"status":"HOLD_NO_LEGAL_RESPONSE","reply":r}
        if any(r not in p for p in satisfying_by_property.values()):
            return {"status":"HOLD_INCOMPLETE_PROPERTY_COVERAGE","reply":r}
        allowed=legal.copy()
        for prop in satisfying_by_property.values():
            allowed &= set(prop[r])
        if not allowed:
            return {"status":"REFUTED_COMMON_WITNESS","reply":r,
                    "separate_properties_satisfiable":all(legal & set(p[r]) for p in satisfying_by_property.values())}
        witness[r]=sorted(allowed)[0]
    return {"status":"CERTIFIED_RELATIVE_TO_DECLARED_LEGALITY","witness":witness,
            "scope":"FINITELY_ENUMERATED_REPLY_DOMAIN_NOT_NATIVE_LEGALITY_CERTIFIED"}

def compare_candidates(a,b):
    """Contrast requires full certificate for a and counterexample to same goal for b."""
    if a["status"]=="CERTIFIED_RELATIVE_TO_DECLARED_LEGALITY" and b["status"]=="REFUTED_COMMON_WITNESS":
        return {"status":"CONTRASTIVE_WITNESS_WITH_REFUTER_NOT_CHESS_PREFERENCE"}
    return {"status":"ABSTAIN_NO_CONTRASTIVE_CERTIFICATE"}
