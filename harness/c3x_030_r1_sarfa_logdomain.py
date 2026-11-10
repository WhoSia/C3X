"""C3X 0.30/R1 — log-domain SARFA prior-art replication hardening.

Primary owned PDF: Puri et al., Explain Your Move (ICLR 2020),
arXiv:1912.12191v4, https://drive.google.com/file/d/1C_c0AvNkEtzB2z6Nbji_NdRxlRpODgjs/view

This is a numerically stable replacement-compatible *mathematical kernel*
for C3X 0.29/P42/R30-A, NOT a new attribution algorithm and NOT the authors'
chess-human experiment. R30's straightforward non-target KL implementation
uses exponentiated probabilities, so underflow can incorrectly yield an
infinite KL even with perfectly finite Q-values. Here KL is evaluated in the
log domain with identical finite action supports.

No chess dependencies, UCI engine, or empirical causal evidence. Source Q
values and temperature still require genuine semantic calibration.
"""
import argparse
import json
import math
from pathlib import Path


def log_softmax(values, temperature):
    """Stable log P_i = z_i-logsumexp(z) without exp(q_i) underflow.

    Reject numeric magnitudes whose differencing or scaling is not
    representable, rather than returning fabricated probability claims.
    """
    if (not isinstance(values, (list, tuple)) or len(values) < 2
        or type(temperature) not in (float, int)
        or not math.isfinite(temperature) or temperature <= 0):
        raise ValueError("R030_SARFA_HOLD_TEMPERATURE_OR_SUPPORT")
    if any(type(x) not in (int, float) or not math.isfinite(x) for x in values):
        raise ValueError("R030_SARFA_HOLD_NONFINITE_INPUT")
    mx = max(values)
    z = [(float(x) - float(mx)) / temperature for x in values]
    if any(not math.isfinite(v) for v in z):
        raise ValueError("R030_SARFA_HOLD_UNREPRESENTABLE_Q_SPREAD")
    log_partition = math.log(math.fsum(math.exp(x) for x in z))
    return [x - log_partition for x in z]


def kl_from_log_probs(perturbed, original):
    """D_KL(perturbed || original), preserving finite extreme-logit KL."""
    if len(perturbed) != len(original) or len(original) < 2:
        raise ValueError("R030_SARFA_HOLD_KL_SUPPORT")
    if any(not math.isfinite(x) for x in perturbed + original):
        raise ValueError("R030_SARFA_HOLD_BAD_LOG_PROBABILITY")
    # q log(q/p) = exp(log_q)*(log_q-log_p).
    # The log-density difference must be evaluated *before* exponentiation.
    terms = [math.exp(q) * (q - p) for q, p in zip(perturbed, original)]
    kl = math.fsum(terms)
    if not math.isfinite(kl):
        raise ValueError("R030_SARFA_HOLD_UNREPRESENTABLE_KL")
    # Theoretically >=0. Small negative values arise from cancellation.
    if kl < -1e-9:
        raise ValueError("R030_SARFA_HOLD_NEGATIVE_KL_BEYOND_ROUNDOFF")
    return max(0.0, kl)


def sarfa_logdomain(original, perturbed, selected, temperature=1.0):
    if (not isinstance(original, dict) or not isinstance(perturbed, dict)
        or len(original) < 3
        or set(original) != set(perturbed)
        or selected not in original
        or any(type(key) is not str or not key for key in original)):
        raise ValueError("R030_SARFA_HOLD_SHARED_FIXED_ACTION_SUPPORT_MIN3")
    keys = sorted(original)
    o = log_softmax([original[k] for k in keys], temperature)
    p = log_softmax([perturbed[k] for k in keys], temperature)
    target = keys.index(selected)
    delta = math.exp(o[target]) - math.exp(p[target])
    others = [k for k in keys if k != selected]
    log_o_rem = log_softmax([original[k] for k in others], temperature)
    log_p_rem = log_softmax([perturbed[k] for k in others], temperature)
    kl = kl_from_log_probs(log_p_rem, log_o_rem)
    relevance = 1.0 / (1.0 + kl)
    positive = max(0.0, delta)
    score = (2.0 * relevance * positive / (relevance + positive)
             if relevance + positive > 0.0 else 0.0)
    return {
        "schema": "c3x030-r1-sarfa-logdomain-eq1-4-v1",
        "original_primary_drive_pdf": "https://drive.google.com/file/d/1C_c0AvNkEtzB2z6Nbji_NdRxlRpODgjs/view",
        "inherited_original_029_method": "harness/c3x_029_p42_r30_sarfa_section2_kernel.py",
        "selected_action": selected,
        "temperature": float(temperature),
        "specificity_delta_raw_signed": delta,
        "specificity_nonnegative_admitted": positive,
        "offtarget_kl_perturbed_to_original": kl,
        "offtarget_relevance": relevance,
        "sarfa_harmonic_saliency": score,
        "status": ("SECTION2_NONNEGATIVE_SALIENCY" if delta > 0.0
                   else "NO_POSITIVE_SELECTED_ACTION_DROP"),
        "fixed_action_support": len(keys),
        "no_chess_engine_or_physical_intervention": True,
        "not_a_new_attribution_method": True,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    record = json.loads(Path(a.input).read_text(encoding="utf-8"))
    data = sarfa_logdomain(**record)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False)+"\n", encoding="utf-8")
    print("C3X_030_R1_SARFA_LOG_DOMAIN", data["status"],
          "KL", data["offtarget_kl_perturbed_to_original"])


if __name__ == "__main__":
    main()
