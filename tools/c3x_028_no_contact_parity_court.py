#!/usr/bin/env python3
"""C3X 0.28 first-divergence parity lemma, finite transition-system court.

B and C must be IDENTICAL except for a predeclared guarded transition.
If B never visits an enabled guard, C cannot differ under deterministic,
shared-initial-state semantics. Synthetic model; never a native receipt.
"""
from itertools import product


def run(table, start, eligible, override=None, horizon=5):
    state = start
    states = [state]
    contacts = []
    for t in range(horizon):
        if state in eligible:
            contacts.append((t, state))
        state = override[state] if override is not None and state in eligible else table[state]
        states.append(state)
    return tuple(states), tuple(contacts)


def court():
    checked = no_contact = false_parity = triggered = 0
    contact_witness = None
    for edges in product(range(3), repeat=3):
        for override in product(range(3), repeat=3):
            for mask in range(8):
                eligible = {s for s in range(3) if mask & (1 << s)}
                for start in range(3):
                    b, bcontact = run(edges, start, eligible)
                    c, _ = run(edges, start, eligible, override)
                    checked += 1
                    if not bcontact:
                        no_contact += 1
                        if b != c:
                            false_parity += 1
                    else:
                        triggered += 1
                        if b != c and contact_witness is None:
                            contact_witness = dict(table=edges, override=override,
                                eligible=tuple(sorted(eligible)), start=start,
                                B=b, C=c)
    assert false_parity == 0 and contact_witness is not None
    # An unauthorized non-guard edit can violate parity despite zero B contacts.
    base = (1, 1, 2)
    no_reach = {2}
    b, contacts = run(base, 0, no_reach)
    leaked, _ = run((2, 1, 2), 0, no_reach)
    assert not contacts and b != leaked
    return dict(exhaustively_compared=checked, B_no_guard_contact=no_contact,
        no_contact_parity_failures=false_parity, B_guard_contact=triggered,
        actual_guard_contact_change_witness=contact_witness,
        hidden_pre_guard_side_effect_counterexample=dict(
            B=b, leaked_patch=leaked, B_guard_contacts=contacts),
        native_stockfish_executed=False)


if __name__ == '__main__':
    import json
    print(json.dumps(court(), indent=2, sort_keys=True))
