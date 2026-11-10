#!/usr/bin/env python3
"""C3X P42/R30-B: Sandmann-inspired internal vs final choice discrepancy audit.

Original owned Sandmann, Lapuschkin & Samek (2026) v4:
https://drive.google.com/file/d/1dAF7reY9DpwBlZFERxrF54qSNYOLbRi0/view

The source is about Leela intermediate-layer policy and later output override.
This tiny tool DOES NOT reproduce their logit lens or trained-network steering.
It enforces a source-observation contract for candidate-score snapshots:
same support and chess state, observed action, ranked candidate, sham condition,
and actual final action. Do not equate intermediate preference with actual
physical causal mediation or regret.

Input: historical or synthetic externally acquired snapshots; never invent them.
All values are score proxies, not calibrated probability without a scale.
"""
import argparse
import json
import math
from pathlib import Path


def top_action(scores):
    if not isinstance(scores, dict) or not scores:
        raise ValueError("R30_B_HOLD_EMPTY_SCORE_VECTOR")
    if any(type(k) is not str or not k or type(v) not in (int, float)
           or not math.isfinite(v) for k, v in scores.items()):
        raise ValueError("R30_B_HOLD_INVALID_SCORE_VECTOR")
    return min(scores, key=lambda name: (-scores[name], name))


def audit(snapshot):
    required = {
        "state_key", "source_engine", "depth", "intermediate_candidate_scores",
        "final_candidate_scores", "final_action", "observed_candidate_support",
    }
    if not isinstance(snapshot, dict) or not required.issubset(snapshot):
        raise ValueError("R30_B_HOLD_MISSING_SOURCE_OBSERVATION")
    p, q = snapshot["intermediate_candidate_scores"], snapshot["final_candidate_scores"]
    support = snapshot["observed_candidate_support"]
    if (not isinstance(support, list) or len(support) < 2
        or len(set(support)) != len(support) or set(p) != set(q) or set(p) != set(support)
        or snapshot["final_action"] not in support):
        raise ValueError("R30_B_HOLD_SUPPORT_OR_REPORTED_ACTUAL_ACTION")
    if (not isinstance(snapshot["state_key"], str) or not snapshot["state_key"]
        or not isinstance(snapshot["source_engine"], str)
        or not snapshot["source_engine"]
        or type(snapshot["depth"]) is not int or snapshot["depth"] <= 0):
        raise ValueError("R30_B_HOLD_PROVENANCE")
    lead = top_action(p)
    final_top = top_action(q)
    action = snapshot["final_action"]
    # A score vector alone cannot prove the actual final action is the
    # vector argmax: previous TT and aspiration/iterative search complexities.
    # Return both and detect mismatch explicitly.
    inconsistency = action != final_top
    return {
        "schema": "c3x042-r30-sandmann-inspired-source-stage-diagnostic-v1",
        "state_key": snapshot["state_key"], "source_engine": snapshot["source_engine"],
        "depth": snapshot["depth"], "intermediate_preferred": lead,
        "final_score_preferred": final_top, "actual_final_action": action,
        "intermediate_vs_final_score_override": lead != final_top,
        "intermediate_vs_actual_final_action": lead != action,
        "score_argmax_vs_actual_action_inconsistent": inconsistency,
        "intermediate_preference_margin": p[lead] - max(
            p[k] for k in support if k != lead),
        "final_action_score_disadvantage_to_best_in_final_snapshot": q[final_top] - q[action],
        "not_source_level_causal_intervention": True,
        "not_leela_logit_lens_replication": True,
        "not_independent_chess_quality_judgment": True,
    }


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--input", required=True)
    a.add_argument("--out", required=True)
    args = a.parse_args()
    snapshot = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = audit(snapshot)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("R30_SOURCE_STAGE_AUDIT",
          "mismatch", result["intermediate_vs_actual_final_action"],
          "inconsistent", result["score_argmax_vs_actual_action_inconsistent"])


if __name__ == "__main__":
    main()
