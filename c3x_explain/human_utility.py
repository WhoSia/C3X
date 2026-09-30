from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from statistics import mean
from typing import Any

RATING_BANDS = ("beginner", "intermediate", "advanced", "expert")
LIKERT_FIELDS = ("correctness", "usefulness", "pedagogical_clarity")
PRESEALED_ENDPOINTS = (
    "correctness",
    "usefulness",
    "pedagogical_clarity",
    "preference_vs_baseline",
    "subsequent_move_understanding",
    "trust_calibration",
)

def i8_preseal() -> dict[str, Any]:
    return {
        "schema": "c3x-human-utility-preseal-v1",
        "stage": "C3X Explain I8",
        "status": "HUMAN_OUTCOME_UNOPENED",
        "rating_bands": list(RATING_BANDS),
        "endpoints": list(PRESEALED_ENDPOINTS),
        "primary_contrasts": [
            "C3X commentary vs baseline engine prose",
            "within-rating-band C3X vs baseline preference",
            "subsequent move-understanding after C3X vs baseline exposure",
        ],
        "separation_rules": [
            "machine evidence coverage is not a human-utility score",
            "human preference cannot promote causal authority",
            "correctness, usefulness, clarity, preference, understanding, and trust are separate endpoints",
            "free-form prose quality cannot override I5-I7 factuality or verification failures",
            "human outcomes must remain unset until real adjudication is ingested",
        ],
        "trust_calibration_requirement": (
            "Trust calibration is reportable only when the study includes both reference-valid "
            "and reference-invalid control items."
        ),
    }

def _arm_order(trial_id: str, seed: str) -> tuple[str, str]:
    digest = sha256(f"{seed}|{trial_id}".encode("utf-8")).digest()
    return ("c3x", "baseline") if digest[0] % 2 == 0 else ("baseline", "c3x")

def build_blinded_trial(
    *,
    trial_id: str,
    rating_band: str,
    position_fen: str,
    c3x_text: str,
    baseline_text: str,
    played_move: str,
    understanding_prompt: str,
    understanding_options: list[str],
    understanding_answer: str,
    seed: str,
    reference_validity: dict[str, bool] | None = None,
) -> dict[str, Any]:
    if rating_band not in RATING_BANDS:
        raise ValueError(f"unknown rating_band: {rating_band}")
    if len(understanding_options) < 2 or understanding_answer not in understanding_options:
        raise ValueError("understanding answer must be one of at least two options")
    order = _arm_order(trial_id, seed)
    text = {"c3x": c3x_text, "baseline": baseline_text}
    arms = {"A": order[0], "B": order[1]}
    public = {
        "schema": "c3x-human-utility-trial-v1",
        "trial_id": trial_id,
        "rating_band": rating_band,
        "position_fen": position_fen,
        "played_move": played_move,
        "commentary": {"A": text[arms["A"]], "B": text[arms["B"]]},
        "questions": {
            "correctness": {"scale": [1, 2, 3, 4, 5], "per_arm": True},
            "usefulness": {"scale": [1, 2, 3, 4, 5], "per_arm": True},
            "pedagogical_clarity": {"scale": [1, 2, 3, 4, 5], "per_arm": True},
            "preference": {"choices": ["A", "B", "TIE"]},
            "trust": {"scale": [0, 25, 50, 75, 100], "per_arm": True},
            "subsequent_move_understanding": {
                "prompt": understanding_prompt,
                "options": list(understanding_options),
            },
        },
    }
    key = {
        "schema": "c3x-human-utility-trial-key-v1",
        "trial_id": trial_id,
        "arm_identity": arms,
        "understanding_answer": understanding_answer,
        "reference_validity": reference_validity or {},
    }
    return {"participant_packet": public, "adjudication_key": key}

def validate_response(response: dict[str, Any]) -> None:
    if response.get("preference") not in {"A", "B", "TIE"}:
        raise ValueError("preference must be A, B, or TIE")
    for field in LIKERT_FIELDS:
        per_arm = response.get(field, {})
        for arm in ("A", "B"):
            value = per_arm.get(arm)
            if not isinstance(value, int) or not 1 <= value <= 5:
                raise ValueError(f"{field}.{arm} must be an integer 1..5")
    trust = response.get("trust", {})
    for arm in ("A", "B"):
        value = trust.get(arm)
        if not isinstance(value, (int, float)) or not 0 <= value <= 100:
            raise ValueError(f"trust.{arm} must be in 0..100")
    if not isinstance(response.get("understanding_answer"), str):
        raise ValueError("understanding_answer must be a string")

def score_response(response: dict[str, Any], key: dict[str, Any]) -> dict[str, Any]:
    validate_response(response)
    arm_identity = key["arm_identity"]
    reverse = {identity: arm for arm, identity in arm_identity.items()}
    c3x_arm, baseline_arm = reverse["c3x"], reverse["baseline"]
    pref = response["preference"]
    if pref == "TIE":
        pref_c3x = 0.5
    else:
        pref_c3x = 1.0 if arm_identity[pref] == "c3x" else 0.0

    out: dict[str, Any] = {
        "schema": "c3x-human-utility-scored-response-v1",
        "trial_id": key["trial_id"],
        "preference_c3x": pref_c3x,
        "understanding_correct": int(response["understanding_answer"] == key["understanding_answer"]),
        "c3x": {},
        "baseline": {},
    }
    for field in LIKERT_FIELDS:
        out["c3x"][field] = response[field][c3x_arm]
        out["baseline"][field] = response[field][baseline_arm]
    out["c3x"]["trust"] = float(response["trust"][c3x_arm])
    out["baseline"]["trust"] = float(response["trust"][baseline_arm])

    validity = key.get("reference_validity", {})
    for identity, arm in (("c3x", c3x_arm), ("baseline", baseline_arm)):
        if identity in validity:
            confidence = float(response["trust"][arm]) / 100.0
            target = 1.0 if validity[identity] else 0.0
            out[identity]["trust_brier"] = (confidence - target) ** 2
        else:
            out[identity]["trust_brier"] = None
    return out

def aggregate_scored(scored_rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not scored_rows:
        return {
            "schema": "c3x-human-utility-summary-v1",
            "n": 0,
            "human_outcome_opened": False,
            "note": "No human adjudication rows were supplied.",
        }

    summary: dict[str, Any] = {
        "schema": "c3x-human-utility-summary-v1",
        "n": len(scored_rows),
        "human_outcome_opened": True,
        "preference_c3x_mean": mean(r["preference_c3x"] for r in scored_rows),
        "subsequent_move_understanding_accuracy": mean(r["understanding_correct"] for r in scored_rows),
        "c3x": {},
        "baseline": {},
    }
    for identity in ("c3x", "baseline"):
        for field in (*LIKERT_FIELDS, "trust"):
            summary[identity][f"{field}_mean"] = mean(r[identity][field] for r in scored_rows)
        brier = [r[identity]["trust_brier"] for r in scored_rows if r[identity]["trust_brier"] is not None]
        summary[identity]["trust_brier_mean"] = mean(brier) if brier else None
        summary[identity]["trust_calibration_reportable"] = bool(brier)
    return summary
