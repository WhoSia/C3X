#!/usr/bin/env python3
"""C3X 0.29-P0: finite contrastive-predicate nonidentifiability court.

Uses KRK upstream one-reply sets A={g7,h7} and B={g7,g8,h7}.
It does NOT itself verify chess legality, engine values or human learning.
"""
from itertools import combinations
FILES="abcdefgh"
BOARD=tuple(f+str(r) for r in range(1,9) for f in FILES)
A=frozenset(("g7","h7"))
B=frozenset(("g7","g8","h7"))

def acceptable(predicate_true):
    return A <= predicate_true and not B <= predicate_true

def court():
    support=A | B
    assignments=[]
    for k in range(len(support)+1):
        for xs in combinations(sorted(support),k):
            if acceptable(set(xs)):
                assignments.append(tuple(xs))
    assert assignments == [("g7","h7")]
    rank7=frozenset(x for x in BOARD if x.endswith("7"))
    not_g8=frozenset(BOARD)-{"g8"}
    assert rank7 & support == not_g8 & support == A
    assert rank7 != not_g8
    assert acceptable(rank7) and acceptable(not_g8)
    return {
       "reachable_support": sorted(support),
       "permitted_predicate_assignments_on_support": assignments,
       "unconstrained_board_squares": len(BOARD)-len(support),
       "number_of_global_boolean_extensions": 2**(len(BOARD)-len(support)),
       "explanation_pair": ["king stays on rank 7","king is not on g8"],
       "pair_equivalent_on_reachable_support": True,
       "pair_distinct_outside_reachable_support": True,
       "illustrative_disagreement_square": "a7",
       "inference":"ONE_VALID_LOCAL_CONTRAST_DOES_NOT_IDENTIFY_ONE_GLOBAL_STRATEGIC_REASON",
       "full_chess_rules_verification": False,
       "new_native_engine_data": False
    }

if __name__=="__main__":
    import json
    print(json.dumps(court(),indent=2))
