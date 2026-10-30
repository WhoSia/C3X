"""Independent finite bound-versus-exact-root-choice counterexample court.

This is alpha-beta-inspired mathematics only. The code never treats raw
Stockfish TT bound labels as a sound common final-score domain.
"""


from itertools import product


def classify(exact, alpha, beta):
    if not alpha < beta:
        raise ValueError("bad window")
    return "UPPER" if exact <= alpha else "LOWER" if exact >= beta else "EXACT"


def possibilities(label, value, domain):
    if label == "EXACT":
        return {value} & set(domain)
    if label == "LOWER":
        return {x for x in domain if x >= value}
    if label == "UPPER":
        return {x for x in domain if x <= value}
    raise ValueError(label)


def preferred(a, b):
    return "A" if a >= b else "B"


def verdict(a_label, a_value, b_label, b_value, domain=range(-5, 6)):
    A = possibilities(a_label, a_value, domain)
    B = possibilities(b_label, b_value, domain)
    if not A or not B:
        return "INCONSISTENT"
    choices = {preferred(a, b) for a, b in product(A, B)}
    return ("CERTAIN_A" if choices == {"A"} else
            "CERTAIN_B" if choices == {"B"} else "AMBIGUOUS")


def self_test():
    assert classify(3, 0, 2) == "LOWER"
    assert classify(-3, -2, 2) == "UPPER"
    assert verdict("LOWER", 1, "UPPER", 0) == "CERTAIN_A"
    assert verdict("UPPER", 2, "LOWER", 1) == "AMBIGUOUS"
    assert verdict("LOWER", 2, "UPPER", 1) == "CERTAIN_A"
    assert verdict("UPPER", 2, "LOWER", 1) == "AMBIGUOUS"
    witnesses = [(a, b, preferred(a, b))
                 for a, b in product(range(-5, 6), repeat=2)
                 if a <= 2 and b >= 1]
    assert len(witnesses) == 40
    assert {x[2] for x in witnesses} == {"A", "B"}
    return {
        "ambiguous_joint_assignments": len(witnesses),
        "possible_winners": sorted({x[2] for x in witnesses}),
        "stockfish_executed": False,
    }


if __name__ == "__main__":
    print(self_test())
