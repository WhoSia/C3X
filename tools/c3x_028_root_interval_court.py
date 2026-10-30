#!/usr/bin/env python3
"""C3X 0.28: pure-Python bounded-root-choice court (NO engine or cohort data).

A score interval [lo, hi] is a *sound, simultaneously meaningful* envelope
for a candidate's final root-comparable exact value. For the theorem below,
assume any combination of values independently within the intervals is
feasible (rectangular uncertainty set); ties prefer an earlier candidate.

These strong assumptions generally FAIL for raw Stockfish TT bounds, separate
aspiration windows, censored traces or mutually dependent candidate scores.
This module never declares a native C3X/E1/E2 certificate.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class Interval:
    name: str
    lo: int
    hi: int

    def __post_init__(self):
        if not self.name or type(self.lo) is not int or type(self.hi) is not int or self.lo > self.hi:
            raise ValueError("invalid integer score interval")


def winner(values: tuple[int, ...]) -> int:
    """Earlier list index wins score ties."""
    if not values:
        raise ValueError("empty candidate set")
    return max(range(len(values)), key=lambda j: values[j])


def logically_possible_winners(candidates: list[Interval]) -> list[str]:
    """Exact under rectangular independent interval uncertainty.

    Candidate i may win iff, at i's upper endpoint and rivals' lower
    endpoints, its score beats every earlier priority rival strictly and
    every later rival weakly.
    """
    if not candidates or len({x.name for x in candidates}) != len(candidates):
        raise ValueError("candidate list must be nonempty with unique names")
    possible = []
    for i, c in enumerate(candidates):
        if all(c.hi > rival.lo if j < i else c.hi >= rival.lo
               for j, rival in enumerate(candidates) if j != i):
            possible.append(c.name)
    return possible


def guaranteed_winner(candidates: list[Interval]) -> str | None:
    """Unique winner guaranteed for EVERY joint interval assignment, if any."""
    if not candidates or len({x.name for x in candidates}) != len(candidates):
        raise ValueError("candidate list must be nonempty with unique names")
    for i, c in enumerate(candidates):
        if all(c.lo > rival.hi if j < i else c.lo >= rival.hi
               for j, rival in enumerate(candidates) if j != i):
            return c.name
    return None


def exhaustive_possible(candidates: list[Interval]) -> set[str]:
    """Completely independent finite oracle; expensive, small integers only."""
    seen = set()
    for assignment in product(*(range(c.lo, c.hi + 1) for c in candidates)):
        seen.add(candidates[winner(assignment)].name)
    return seen


def two_ply_root(leaves: tuple[int, int, int, int]) -> tuple[int, int, str]:
    """Root MAX chooses A or B; opponent chooses MIN over its two replies."""
    a = min(leaves[0], leaves[1])
    b = min(leaves[2], leaves[3])
    return a, b, 'A' if a >= b else 'B'


def enumerate_single_leaf_counterexamples(domain=range(-2, 3)) -> dict:
    """All ordered two-ply trees; intervene on one B reply by +/-1.

    Classifies actual child-score change -> parent score change -> root choice.
    No chess/Stockfish claim; small exact minimax model only.
    """
    counts = {'child_change_parent_same': 0,
              'parent_change_root_same': 0,
              'root_choice_changed': 0,
              'root_changed_without_parent_change': 0}
    witness = {}
    for leaves in product(domain, repeat=4):
        old = two_ply_root(leaves)
        for slot in (2, 3):
            for delta in (-1, 1):
                new_leaves = list(leaves)
                new_leaves[slot] += delta
                new = two_ply_root(tuple(new_leaves))
                if old[1] == new[1]:
                    label = 'child_change_parent_same'
                elif old[2] == new[2]:
                    label = 'parent_change_root_same'
                else:
                    label = 'root_choice_changed'
                counts[label] += 1
                witness.setdefault(label, {'old_leaves': leaves, 'new_leaves': tuple(new_leaves),
                                            'old': old, 'new': new})
                if old[1] == new[1] and old[2] != new[2]:
                    counts['root_changed_without_parent_change'] += 1
    return {'counts': counts, 'witnesses': witness}


def self_court() -> dict:
    """Computationally compare independent exhaustive oracle with theorem."""
    small = [Interval(str(i), lo, hi) for i, (lo, hi) in enumerate(
        (lo, hi) for lo in (-1, 0, 1) for hi in range(lo, 2))]
    checked = 0
    for indices in product(range(len(small)), repeat=3):
        c = [Interval(chr(65 + j), small[idx].lo, small[idx].hi)
             for j, idx in enumerate(indices)]
        assert set(logically_possible_winners(c)) == exhaustive_possible(c)
        guaranteed = guaranteed_winner(c)
        if guaranteed:
            assert exhaustive_possible(c) == {guaranteed}
        else:
            assert len(exhaustive_possible(c)) > 1
        checked += 1
    examples = enumerate_single_leaf_counterexamples()
    assert examples['counts']['root_changed_without_parent_change'] == 0
    assert all(examples['counts'][k] > 0 for k in (
        'child_change_parent_same', 'parent_change_root_same', 'root_choice_changed'))
    return {'interval_triples_exhaustively_compared': checked,
            'minimax_interventions': 5**4 * 2 * 2,
            **examples,
            'native_engine_executed': False,
            'frozen_64_used': False}


if __name__ == '__main__':
    import json
    print(json.dumps(self_court(), sort_keys=True, indent=2))
