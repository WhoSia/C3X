"""C3X P42: bounded logical refuters of regret -> preference/explanation.
Synthetic finite games only. No chess-world or native-engine evidence.
"""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class BranchWorld:
    # root -> reply -> own action -> exact payoff from ROOT mover's perspective
    values: dict[str, dict[str, dict[str, int]]]
    # precommitted selective response-conditioned permitted moves
    plans: dict[str, dict[str, tuple[str, ...]]]

def score(world: BranchWorld, root: str) -> tuple[int, int]:
    """(worst-opponent optimal root value, worst-response plan regret)."""
    responses = world.values[root]
    plans = world.plans[root]
    if not responses or set(responses) != set(plans):
        raise ValueError("RESPONSE_COVERAGE")
    values = []
    regrets = []
    any_selective = False
    for reply, legal in responses.items():
        permitted = plans[reply]
        if not legal or not permitted or len(permitted) != len(set(permitted)):
            raise ValueError("INVALID_PLAN")
        if not set(permitted) <= set(legal):
            raise ValueError("ILLEGAL_PLAN")
        if len(permitted) < len(legal):
            any_selective = True
        best = max(legal.values())
        planned = max(legal[u] for u in permitted)
        values.append(best)
        regrets.append(best - planned)
    if not any_selective:
        raise ValueError("TRIVIAL_PLAN")
    return min(values), max(regrets)

def constant_shift_refuter() -> dict:
    # Identical conditional structure and zero regret, but opposite
    # choice preference after legal root-specific value translation.
    w = BranchWorld(
        values={
            "a": {"r1": {"u": 40, "v": 10},
                  "r2": {"w": 50, "x": 20}},
            "b": {"r1": {"u": -100, "v": -130},
                  "r2": {"w": -90, "x": -120}},
        },
        plans={
            "a": {"r1": ("u",), "r2": ("w",)},
            "b": {"r1": ("u",), "r2": ("w",)},
        },
    )
    a_value, a_regret = score(w, "a")
    b_value, b_regret = score(w, "b")
    assert (a_value, a_regret) == (40, 0)
    assert (b_value, b_regret) == (-100, 0)
    return {"a_minimax": a_value, "b_minimax": b_value,
            "a_regret": a_regret, "b_regret": b_regret,
            "verdict": "EQUAL_ZERO_REGRET_DOES_NOT_IDENTIFY_ROOT_PREFERENCE"}

def posthoc_oracle_refuter() -> dict:
    # A fully label-dependent singleton selector will always achieve zero
    # regret when each response has a unique best move. This is DATA LEAKAGE,
    # not a usable prospective planning explanation.
    values = {"r1": {"a": 7, "b": 2}, "r2": {"c": 0, "d": -9}}
    leaked_plan = {r: (max(acts, key=acts.get),) for r, acts in values.items()}
    w = BranchWorld(values={"m": values}, plans={"m": leaked_plan})
    _, regret = score(w, "m")
    assert regret == 0
    return {"posthoc_regret": regret,
            "posthoc_plan": leaked_plan,
            "verdict": "ZERO_REGRET_WITH_ORACLE_LEAKAGE_HAS_NO_FORECAST_CONTENT"}

def run_court() -> dict:
    return {"court": "SYNTHETIC_FINITE_TREE_ONLY",
            "constant_shift": constant_shift_refuter(),
            "posthoc_oracle": posthoc_oracle_refuter(),
            "claim_ceiling": "No chess originality, engine cause or human value is established."}

if __name__ == "__main__":
    import json
    print(json.dumps(run_court(), ensure_ascii=False, sort_keys=True, indent=2))
