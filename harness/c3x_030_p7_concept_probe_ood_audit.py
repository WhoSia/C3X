#!/usr/bin/env python3
"""C3X 0.30 P7: Pálsson/Lomasov-inspired concept probe audit contract.

Only scores externally produced by an ACTUAL trained probe are accepted.
No inference, weights, activation capture, or chess-engine calls occur here.
This judges concept decodability and standard-vs-Chess960 shift, NOT
causal influence on an engine decision.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

SCHEMA = "c3x030-p7-concept-probe-ood-audit-v1"
DOMAINS = frozenset(("standard", "chess960"))


def _validate(rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError("P7_HOLD_EMPTY_ROWS")
    seen = set()
    groups = defaultdict(set)
    position_splits = defaultdict(set)
    concepts = set()
    for r in rows:
        if not isinstance(r, dict):
            raise ValueError("P7_HOLD_BAD_ROW")
        for k in ("split", "domain", "concept", "game_id", "position_id", "position_sha256", "label"):
            if k not in r:
                raise ValueError("P7_HOLD_REQUIRED_FIELD_" + k)
        split = r["split"]
        domain = r["domain"]
        concept = r["concept"]
        if split not in ("train", "test") or domain not in DOMAINS:
            raise ValueError("P7_HOLD_SPLIT_OR_DOMAIN")
        if not all(isinstance(r[k], str) and r[k] for k in ("concept", "game_id", "position_id")):
            raise ValueError("P7_HOLD_IDENTIFIERS")
        if not isinstance(r["position_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", r["position_sha256"]):
            raise ValueError("P7_HOLD_POSITION_FINGERPRINT_FORMAT")
        if type(r["label"]) is not int or r["label"] not in (0, 1):
            raise ValueError("P7_HOLD_BINARY_LABEL")
        if split == "train":
            if domain != "standard" or "probe_probability" in r:
                raise ValueError("P7_HOLD_TRAINING_CONTRACT")
        else:
            p = r.get("probe_probability")
            if (type(p) not in (float, int) or not (0.0 <= p <= 1.0)):
                raise ValueError("P7_HOLD_TEST_PROBABILITY")
        identity = (split, domain, concept, r["position_id"])
        if identity in seen:
            raise ValueError("P7_HOLD_DUPLICATE_POSITION_CONCEPT")
        seen.add(identity)
        groups[r["game_id"]].add(split)
        position_splits[r["position_sha256"]].add(split)
        concepts.add(concept)
    if any(len(v) > 1 for v in groups.values()):
        raise ValueError("P7_HOLD_GAME_GROUP_LEAKAGE")
    if any(len(v) > 1 for v in position_splits.values()):
        raise ValueError("P7_HOLD_POSITION_FINGERPRINT_LEAKAGE")
    return concepts


def _scores(test, prevalence):
    n = len(test)
    labels = [r["label"] for r in test]
    preds = [1 if r["probe_probability"] >= .5 else 0 for r in test]
    positives = sum(labels)
    negatives = n - positives
    if n == 0 or positives == 0 or negatives == 0:
        raise ValueError("P7_HOLD_SINGLE_CLASS_TEST_OR_EMPTY")
    tp = sum(y == 1 and p == 1 for y, p in zip(labels, preds))
    tn = sum(y == 0 and p == 0 for y, p in zip(labels, preds))
    acc = (tp + tn) / n
    brier = sum((r["probe_probability"] - r["label"]) ** 2 for r in test) / n
    base_pred = 1 if prevalence >= .5 else 0
    base_acc = sum(y == base_pred for y in labels) / n
    base_brier = sum((prevalence - y) ** 2 for y in labels) / n
    return {
        "n": n, "game_clusters": len({r["game_id"] for r in test}),
        "positives": positives, "negatives": negatives,
        "probe_accuracy": acc, "probe_balanced_accuracy": (tp / positives + tn / negatives) / 2,
        "probe_brier": brier,
        "training_majority_accuracy": base_acc,
        "training_prevalence_brier": base_brier,
        "brier_improvement_over_training_prevalence": base_brier - brier,
        "positive_label_prevalence": positives / n,
    }


def audit(rows):
    concepts = sorted(_validate(rows))
    results = {}
    for concept in concepts:
        train = [r for r in rows if r["concept"] == concept and r["split"] == "train"]
        if not train or {r["label"] for r in train} != {0, 1}:
            raise ValueError("P7_HOLD_TRAIN_CLASS_SUPPORT_" + concept)
        prevalence = sum(r["label"] for r in train) / len(train)
        by_domain = {}
        for domain in ("standard", "chess960"):
            test = [r for r in rows if r["concept"] == concept and
                    r["split"] == "test" and r["domain"] == domain]
            by_domain[domain] = _scores(test, prevalence)
        results[concept] = {
            "train_count": len(train),
            "train_game_clusters": len({r["game_id"] for r in train}),
            "train_positive_prevalence": prevalence,
            "test": by_domain,
            "accuracy_chess960_minus_standard":
                by_domain["chess960"]["probe_accuracy"] - by_domain["standard"]["probe_accuracy"],
            "brier_chess960_minus_standard":
                by_domain["chess960"]["probe_brier"] - by_domain["standard"]["probe_brier"],
        }
    return {
        "schema": SCHEMA, "method": "heldout_binary_probe_score_and_domain_shift_audit",
        "concepts": results,
        "actual_model_executions_performed_by_this_tool": 0,
        "actual_chess_engine_searches_performed_by_this_tool": 0,
        "probe_decodability_is_source_choice_causality": False,
        "game_group_disjoint_by_split": True,
        "position_sha256_disjoint_by_split": True,
        "training_domain": "standard",
        "heldout_domains": ["standard", "chess960"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    raw = json.loads(Path(args.rows).read_text(encoding="utf-8"))
    result = audit(raw)
    Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print("C3X_P7_CONCEPT_OOD_AUDIT_PASS", len(result["concepts"]))


if __name__ == "__main__":
    main()
