#!/usr/bin/env python3
"""P12: exact abstraction insufficiency on a finite legal response relation.

Only literal reusable action identities; does not equate UCI labels across boards
unless a source auditor separately certifies the same action schema.
"""
from itertools import combinations

def audit_feature_sufficiency(allowed_by_reply,feature_by_reply):
    if not allowed_by_reply:
        return {"status":"ABSTAIN_EMPTY_REPLY_DOMAIN"}
    if set(allowed_by_reply)!=set(feature_by_reply):
        return {"status":"HOLD_FEATURE_DOMAIN_MISMATCH"}
    cells={}
    for r,z in feature_by_reply.items():
        cells.setdefault(z,[]).append(r)
    policies={}
    for z,replies in sorted(cells.items(),key=lambda x:str(x[0])):
        shared=set(allowed_by_reply[replies[0]])
        for r in replies[1:]:
            shared &= set(allowed_by_reply[r])
        if not shared:
            bad=next(((a,b) for a,b in combinations(replies,2)
                if not (set(allowed_by_reply[a])&set(allowed_by_reply[b]))),None)
            return {"status":"REFUTED_FEATURE_SUFFICIENCY",
                    "feature":z,"collision_pair":list(bad) if bad else None,
                    "cell_reply_count":len(replies)}
        policies[str(z)]=sorted(shared)[0]
    return {"status":"CERTIFIED_FINITE_ACTION_SCHEMA_ONLY","policy":policies,
            "caution":"LITERAL_SHARED_ACTION_LABELS_REQUIRE_SOURCE_SEMANTIC_AUDIT"}
