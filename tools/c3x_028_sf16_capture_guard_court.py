#!/usr/bin/env python3
"""C3X 0.28 Stockfish sf_16 capture/forcing-move SEE-guard decision court.

Faithfully abstracts the *post-SEE* branch of sf_16 src/search.cpp.
Other earlier pruning gates, search-state eligibility, discovered attack
computation and source execution are OUTSIDE this finite Boolean court.
This is NOT a native run.
"""
from itertools import product


def post_see_prunes(*, see_ge: bool, depth: int, capture: bool,
                    discovered_attack_retains: bool) -> bool:
    """True exactly when this post-SEE branch executes continue.

    When see_ge is false, source code first prunes if depth < 2 - capture.
    Otherwise it checks discovered attacks; if none survive the original
    attack/hanging exclusion, source code prunes.
    """
    if see_ge:
        return False
    if depth < 2 - int(capture):
        return True
    return not discovered_attack_retains


def finite_court():
    rows = []
    for see_ge, depth, capture, retained in product(
        (False, True), (-1, 0, 1, 2), (False, True), (False, True)
    ):
        rows.append({
            "see_ge": see_ge, "depth": depth, "capture": capture,
            "discovered_attack_retains": retained,
            "actual_post_see_continue": post_see_prunes(
                see_ge=see_ge, depth=depth, capture=capture,
                discovered_attack_retains=retained),
        })
    false = [r for r in rows if not r["see_ge"]]
    pruned = [r for r in false if r["actual_post_see_continue"]]
    retained = [r for r in false if not r["actual_post_see_continue"]]
    assert len(rows) == 32 and pruned and retained
    return {
        "examined_boolean_combinations": len(rows),
        "see_ge_false_combinations": len(false),
        "see_ge_false_but_not_pruned": len(retained),
        "see_ge_false_and_pruned": len(pruned),
        "counterexample_see_false_not_pruned": retained[0],
        "counterexample_actual_prune": pruned[0],
        "claims_limited_to_post_see_branch": True,
        "native_execution": False,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(finite_court(), indent=2, sort_keys=True))
