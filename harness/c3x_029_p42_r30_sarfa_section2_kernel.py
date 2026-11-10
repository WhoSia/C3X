#!/usr/bin/env python3
"""C3X P42/R30-A: SARFA original mathematics, deterministic no-engine kernel.

Primary OWNED reference: Puri et al., ICLR 2020, arXiv:1912.12191v4,
https://drive.google.com/file/d/1C_c0AvNkEtzB2z6Nbji_NdRxlRpODgjs/view
Section 2, Eqs. (1)-(4): action softmax, delta selected probability,
KL(other actions perturbed || original), 1/(1+KL), harmonic mean.

Input = comparable original/perturbed action-value vectors on the SAME fixed
action support. Original paper assumes Q-values. If given Stockfish CPs,
a temperature in cp must be calibrated and disclosed; raw CP are NOT
policy logits. No invalid chessboard perturbations are created here.

Negative signed delta is NOT physically an 'importance' in Eq. 4; report
it separately and return 0 nonnegative saliency, with explicit status.
"""
import argparse
import json
import math
from pathlib import Path


def _probabilities(values, temperature):
    if len(values) < 2 or not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("SARFA_HOLD_ACTION_COUNT_OR_TEMPERATURE")
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in values):
        raise ValueError("SARFA_HOLD_NONFINITE_Q")
    z = [v / temperature for v in values]
    high = max(z)
    weights = [math.exp(t - high) for t in z]
    total = math.fsum(weights)
    return [a / total for a in weights]


def sarfa(original, perturbed, selected, temperature=1.0):
    """Exact Section-2 formula in stable arithmetic; nonnegative admitted domain."""
    if not isinstance(original, dict) or not isinstance(perturbed, dict):
        raise ValueError("SARFA_HOLD_Q_VECTOR_TYPES")
    if (len(original) < 3 or set(original) != set(perturbed)
        or selected not in original or any(type(k) is not str for k in original)):
        raise ValueError("SARFA_HOLD_SHARED_ACTION_SUPPORT_MIN3")
    keys = sorted(original)
    o = _probabilities([original[k] for k in keys], temperature)
    p = _probabilities([perturbed[k] for k in keys], temperature)
    target = keys.index(selected)
    delta = o[target] - p[target]
    rest = [k for k in keys if k != selected]
    old_rest = _probabilities([original[k] for k in rest], temperature)
    new_rest = _probabilities([perturbed[k] for k in rest], temperature)
    # KL(P_rem_perturbed || P_rem_original). Avoid log(0) from underflow.
    # When a positive perturbed probability meets an underflow-zero baseline,
    # divergence is +inf and relevance becomes zero.
    divergence = math.fsum(
        n * math.log(n / b)
        for n, b in zip(new_rest, old_rest)
        if n > 0.0 and b > 0.0
    ) if all(n == 0.0 or b > 0.0 for n, b in zip(new_rest, old_rest)) else math.inf
    divergence = max(0.0, divergence)
    relevance = 0.0 if math.isinf(divergence) else 1.0 / (1.0 + divergence)
    admitted = max(0.0, delta)
    saliency = (2.0 * relevance * admitted / (relevance + admitted)
                if relevance + admitted > 0 else 0.0)
    return {
        "schema": "c3x042-r30-sarfa-section2-kernel-v1",
        "selected_action": selected,
        "temperature": temperature,
        "specificity_delta_raw_signed": delta,
        "specificity_nonnegative_admitted": admitted,
        "offtarget_kl_perturbed_to_original": divergence,
        "offtarget_relevance": relevance,
        "sarfa_harmonic_saliency": saliency,
        "status": "SECTION2_NONNEGATIVE_SALIENCY" if delta > 0
                  else "NO_POSITIVE_SELECTED_ACTION_DROP",
        "original_q_value_units_not_inferred": True,
        "causal_chess_root_mediation": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="JSON {original,perturbed,selected,temperature}")
    p.add_argument("--out", required=True)
    a = p.parse_args()
    data = json.loads(Path(a.input).read_text(encoding="utf-8"))
    result = sarfa(**data)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("R30_SARFA_KERNEL", result["status"], "score",
          result["sarfa_harmonic_saliency"])


if __name__ == "__main__":
    main()
