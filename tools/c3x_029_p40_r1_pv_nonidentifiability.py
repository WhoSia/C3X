#!/usr/bin/env python3
"""P40/R1: finite zero-sum search trees sharing exact PV and root values.

This is a logical counterexample, NOT a chess-game reconstruction and NOT a
new proof of a game-theoretic nonidentifiability theorem.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping

# root move -> opponent response -> mover response -> terminal mover payoff
Tree = Mapping[str, Mapping[str, Mapping[str, int]]]


def adversarial_response_value(tree: Tree, root: str, response: str) -> int:
    return max(tree[root][response].values())


def exact_root_summary(tree: Tree) -> dict:
    """Calculate exact minimax per root and a single lexical-tie-breaking PV."""
    candidate_summaries = {}
    for root, responses in sorted(tree.items()):
        reply_values = {r: max(u.values()) for r, u in responses.items()}
        worst = min(reply_values.values())
        response = min(r for r in reply_values if reply_values[r] == worst)
        own = min(u for u, v in responses[response].items() if v == worst)
        candidate_summaries[root] = {
            "root_value": worst, "single_pv": [root, response, own],
        }
    top_value = max(x["root_value"] for x in candidate_summaries.values())
    selected = min(r for r, x in candidate_summaries.items()
                   if x["root_value"] == top_value)
    return {"chosen_root": selected, "candidates": candidate_summaries}


def construct_world(a_offpv: int, b_offpv: int) -> Tree:
    if a_offpv < 0 or b_offpv < 0:
        raise ValueError("OFFPV_MUST_NOT_CHANGE_ROOT_MINIMAX")
    return {
        "A": {"r0": {"u0": 0}, "r1": {"u0": a_offpv}},
        "B": {"r0": {"u0": 0}, "r1": {"u0": b_offpv}},
    }


def explicit_counterexample() -> dict:
    left = construct_world(2, 0)
    right = construct_world(0, 2)
    l_summary, r_summary = exact_root_summary(left), exact_root_summary(right)
    if l_summary != r_summary:
        raise AssertionError("PV_ROOT_SCORE_TRANSCRIPT_CHANGED")
    def offpv_delta(tree):
        return (adversarial_response_value(tree, "A", "r1") -
                adversarial_response_value(tree, "B", "r1"))
    l, r = offpv_delta(left), offpv_delta(right)
    if not (l > 0 and r < 0):
        raise AssertionError("OFFPV_CONTRAST_NOT_REVERSED")
    return {
        "status": "FORMAL_TOY_COUNTEREXAMPLE_NOT_CHESS_EMPIRICAL_RESULT",
        "both_exact_transcripts": l_summary,
        "G0_offpv_A_minus_B": l,
        "G1_offpv_A_minus_B": r,
        "claim_ceiling": "Single-PV plus exact minimax scores do not identify off-PV conditional value in arbitrary finite zero-sum game trees.",
        "cannot_infer": [
            "real chess game embedding",
            "common response move labels across distinct chess positions",
            "C3X forecast superiority",
            "Stockfish NNUE activation causation",
        ],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(explicit_counterexample(), indent=2))
