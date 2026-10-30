"""C3X 0.28: finite observational-nonidentification court for explanatory claims.

A candidate root score and engine trace do NOT identify strategic predicates
of legal continuations. This program checks the abstract logical relation
with two possible explanation worlds; it does not assert the worlds are legal
chess states. Chess legality is a SEPARATE 0.27 witness requirement.
"""
from itertools import product


def observation(world):
    """Only the same two root scores and same causal mechanism trace are observed."""
    return (world["score_A"], world["score_B"], world["mechanism_trace"])


def bestmove(world):
    return "A" if world["score_A"] >= world["score_B"] else "B"


def strategic_claim(world):
    """Proposed explanation: A (unlike B) preserves predicate P against reply set."""
    return all(world["P_A_replies"]) and not all(world["P_B_replies"])


def court():
    worlds = []
    for a_reply, b_reply in product((False, True), repeat=2):
        worlds.append({
            "score_A": 30, "score_B": 20,
            "mechanism_trace": ("TT-contact", "SEE-prune", "parent-consumed", "root-A"),
            "P_A_replies": (a_reply,),
            "P_B_replies": (b_reply,),
        })
    assert all(bestmove(w) == "A" for w in worlds)
    assert len({observation(w) for w in worlds}) == 1
    values = {strategic_claim(w) for w in worlds}
    assert values == {False, True}
    witness = next(w for w in worlds if strategic_claim(w))
    refuter = next(w for w in worlds if not strategic_claim(w))
    return {
        "possible_abstract_worlds": len(worlds),
        "distinct_score_and_mechanism_observations": 1,
        "distinct_truth_values_for_chess_semantic_claim": len(values),
        "witness": {k: v for k, v in witness.items() if k.startswith("P_")},
        "refuter": {k: v for k, v in refuter.items() if k.startswith("P_")},
        "logical_conclusion": "SCORES_PLUS_CAUSAL_TRACE_DO_NOT_ENTAIL_STRATEGIC_PREDICATE",
        "legal_chess_worlds_constructed": False,
        "native_engine_used": False,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(court(), indent=2, sort_keys=True))
