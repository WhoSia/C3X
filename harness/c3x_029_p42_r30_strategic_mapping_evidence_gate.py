#!/usr/bin/env python3
"""C3X P42/R30-C: Ciancarini/Pareschi strategy-stage provenance audit.

Primary OWNED mapping review, arXiv 2609.18286v1, 84 Core/19 Context:
https://drive.google.com/file/d/1OxYGSk2bmFD4Rdr0tXHJPAWT_w-wkMyF/view

Classify *what a real C3X execution demonstrated*, never infer causality
from the paper's bibliographic labels. Stage tags R1..R9 are adapted
as a research inventory, not a reproduction of all 84 study codings.

The crucial gate is explicit same-world source mechanism plus physical
intervention + actual final root action + independent same-horizon future
plan + prospective qualification before a flagship causal-strategic claim.
"""
import argparse
import json
from pathlib import Path

STAGES = {
    "R1": "board representation / legality",
    "R2": "position assessment",
    "R3": "candidate generation",
    "R4": "search and lookahead",
    "R5": "contingent strategic planning",
    "R6": "evaluation and trade-off reasoning",
    "R7": "decision and action selection",
    "R8": "explanation and verbalization",
    "R9": "reflection, calibration, and metacognition",
}
REQUIRED_FIELDS = {
    "experiment", "source_receipt", "stages", "same_original_position",
    "actual_physical_source_intervention", "actual_final_root_change",
    "independently_judged_plan", "same_endpoint_horizon",
    "prospective_before_outcome_source",
    "explanation_move_mask_control", "human_utility_evaluated",
}


def audit_experiment(row):
    if not isinstance(row, dict) or not REQUIRED_FIELDS.issubset(row):
        raise ValueError("R30_C_HOLD_INCOMPLETE_EVIDENCE_ROW")
    if (not isinstance(row["experiment"], str) or not row["experiment"]
        or not isinstance(row["source_receipt"], str) or not row["source_receipt"]
        or not isinstance(row["stages"], list) or not row["stages"]
        or len(set(row["stages"])) != len(row["stages"])
        or not set(row["stages"]).issubset(STAGES)):
        raise ValueError("R30_C_HOLD_STAGE_OR_PROVENANCE")
    flags = REQUIRED_FIELDS - {"experiment", "source_receipt", "stages"}
    if any(type(row[k]) is not bool for k in flags):
        raise ValueError("R30_C_HOLD_NONBOOLEAN_ADMISSION_GATE")
    # A successful prospective flag alone cannot substitute for independent
    # judge, and explanation quality cannot substitute for mechanism.
    causal = all(row[k] for k in (
        "same_original_position", "actual_physical_source_intervention",
        "actual_final_root_change", "independently_judged_plan",
        "same_endpoint_horizon", "prospective_before_outcome_source"))
    return {
        "experiment": row["experiment"], "source_receipt": row["source_receipt"],
        "actually_tested_reasoning_stages": row["stages"],
        "flagship_same_world_causal_strategic_admission": causal,
        "explanation_behavioral_validity_tested":
            row["explanation_move_mask_control"] and row["human_utility_evaluated"],
        "failure_gates": [k for k in (
            "same_original_position", "actual_physical_source_intervention",
            "actual_final_root_change", "independently_judged_plan",
            "same_endpoint_horizon", "prospective_before_outcome_source")
            if not row[k]],
        "mapping_review_does_not_establish_causal_mechanism": True,
    }


def audit_many(rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError("R30_C_HOLD_EMPTY_EVIDENCE_COLLECTION")
    if len({r.get("experiment") for r in rows}) != len(rows):
        raise ValueError("R30_C_HOLD_DUPLICATE_EXPERIMENT")
    results = [audit_experiment(row) for row in rows]
    return {
        "schema": "c3x042-r30-mapping-84-study-inspired-evidence-gate-v1",
        "primary_drive_pdf": "https://drive.google.com/file/d/1OxYGSk2bmFD4Rdr0tXHJPAWT_w-wkMyF/view",
        "not_original_review_84_core_coding_replication": True,
        "n_experiments": len(results),
        "n_admitted_same_world": sum(
            r["flagship_same_world_causal_strategic_admission"] for r in results),
        "records": results,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    d = json.loads(Path(a.input).read_text(encoding="utf-8"))
    result = audit_many(d)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("R30_C_EVIDENCE_AUDIT", result["n_experiments"],
          "SAME_WORLD_ADMITTED", result["n_admitted_same_world"])


if __name__ == "__main__":
    main()
