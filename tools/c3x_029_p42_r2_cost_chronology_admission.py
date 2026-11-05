"""C3X P42/R2: adversarial structural fairness and chronology admission.

This deliberately does NOT confer chess validity, temporal proof, judge
independence, or empirical performance. External proofs remain external.
"""
from __future__ import annotations
import math

REQUIRED = ("pv", "partial_tree_k3", "foil_json", "c3x")
METRICS = ("native_nodes", "legal_expansions", "cpu_ms", "engine_queries",
           "model_tokens", "model_calls")

def _nonnegative_int(value):
    return type(value) is int and value >= 0

def audit_resource_account(case, tolerance=0.10):
    """Enumerate observed cost mismatches. Never infer fairness from caps."""
    if not isinstance(tolerance, (float, int)) or not math.isfinite(tolerance) or not 0 <= tolerance < 1:
        raise ValueError("BAD_TOLERANCE")
    methods = case.get("methods", {})
    reasons = []
    per_metric = {}
    for name in REQUIRED:
        if name not in methods:
            reasons.append("MISSING_METHOD_" + name)
    if reasons:
        return {"status": "HOLD", "reasons": sorted(reasons),
                "claim_ceiling": "Not a scientific quality verdict."}
    for name in REQUIRED:
        rec = methods[name]
        for metric in METRICS:
            if metric not in rec or not _nonnegative_int(rec[metric]):
                reasons.append("MISSING_OR_INVALID_ACTUAL_" + name + "_" + metric)
    if reasons:
        return {"status": "HOLD", "reasons": sorted(reasons),
                "claim_ceiling": "Not a scientific quality verdict."}
    for metric in METRICS:
        observed = [methods[name][metric] for name in REQUIRED]
        lo, hi = min(observed), max(observed)
        per_metric[metric] = {"minimum": lo, "maximum": hi}
        if hi and (hi - lo) / hi > tolerance:
            reasons.append("UNMATCHED_ACTUAL_" + metric)
    # 'Matched' means measured resource vectors, not performance, legality,
    # fair label exposure, independent judge, or an honest provenance ledger.
    return {"status": "HOLD" if reasons else "MATCHED_DECLARED_COST_ONLY",
            "reasons": sorted(reasons),
            "observed": per_metric,
            "claim_ceiling": "Self-reported resource ledger only, not independently audited costs or chess results."}

def audit_research_admission(case, historical, *, trusted_legal=False,
                             trusted_source=False, trusted_chronology=False,
                             trusted_cost=False, trusted_judge=False,
                             tolerance=0.10):
    """Independent certifications are required; bools are NOT proof by themselves.

    Caller must not set trusted_* from untrusted JSON fields. This is a
    claim-boundary interface, NOT a verifier of externally produced evidence.
    """
    from c3x_029_p41_r3_independent_plan_court_preflight import verify_case
    original = verify_case(case, historical)
    cost = audit_resource_account(case, tolerance)
    requirements = {
        "source_custody": trusted_source,
        "legal_full_history": trusted_legal,
        "prediction_precedes_judge": trusted_chronology,
        "native_cost_ledger": trusted_cost,
        "independent_value_referee": trusted_judge,
    }
    reasons = list(original["failures"]) + cost["reasons"]
    for name, confirmed in requirements.items():
        if confirmed is not True:
            reasons.append("EXTERNAL_PROOF_MISSING_" + name)
    if not reasons:
        # Even externally attested structural readiness is not value performance.
        decision = "READY_FOR_SEPARATE_VALUE_EVALUATION_NOT_CHESS_PASS"
    else:
        decision = "HOLD"
    return {"status": decision, "reasons": sorted(set(reasons)),
            "legacy_status": original["status"],
            "cost_status": cost["status"],
            "claim_ceiling": "No engine output, scientific significance, causal attribution or chess truth proven."}
