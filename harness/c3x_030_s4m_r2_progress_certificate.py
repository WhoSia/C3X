"""Check finite forced-win certificates on a supplied turn-based game graph.

A listed successor set is authoritative. A zero rank anchors a verified
winning terminal. Positive ranks bound plies to that terminal under the
witness strategy and all supplied opponent replies.
"""
from collections.abc import Mapping, Set
from dataclasses import dataclass


@dataclass(frozen=True)
class Node:
    winner_to_move: bool
    successors: frozenset[str]


def verify_progress(
    graph: Mapping[str, Node],
    winning_terminals: Set[str],
    root: str,
    ranks: Mapping[str, int],
) -> dict[str, tuple[str, ...]]:
    """Return reachable proof edges, raising ValueError on invalid evidence."""
    if root not in ranks:
        raise ValueError("Root is missing from the certificate")
    proof = {}
    pending = [root]
    while pending:
        state = pending.pop()
        if state in proof:
            continue
        rank = ranks[state]
        node = graph.get(state)
        if node is None or type(rank) is not int or rank < 0:
            raise ValueError(f"Invalid state or rank: {state}")
        if node.successors - graph.keys():
            raise ValueError(f"Unknown successor in graph: {state}")
        if not node.successors:
            if rank != 0 or state not in winning_terminals:
                raise ValueError(f"Terminal does not establish the claimed win: {state}")
            proof[state] = ()
            continue
        if rank == 0 or state in winning_terminals:
            raise ValueError(f"Invalid terminal anchor: {state}")
        descending = tuple(sorted(
            child for child in node.successors
            if type(ranks.get(child)) is int and 0 <= ranks[child] < rank
        ))
        if node.winner_to_move:
            if not descending:
                raise ValueError(f"No descending winning move: {state}")
            edges = descending[:1]
        else:
            if len(descending) != len(node.successors):
                raise ValueError(f"Opponent has an uncovered reply: {state}")
            edges = descending
        proof[state] = edges
        pending.extend(edges)
    return proof
