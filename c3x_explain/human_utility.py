from __future__ import annotations

from hashlib import sha256
from statistics import mean
from typing import Any

RATING_BANDS = ("beginner", "intermediate", "advanced", "expert")
COMMENTARY_ARMS = ("c3x", "baseline")
UNDERSTANDING_ARMS = ("c3x", "baseline", "no_commentary")
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
        "schema": "c3x-human-utility-preseal-v2",
        "stage": (
            "C3X Explain I8 — Human-Utility World Contact, Rating-Band-Stratified Human Utility, "
            "Blind Baseline Preference, Explanation-Induced Move Understanding, Calibration/Trust "
            "& Authority-Separated Commentary Evaluation"
        ),
        "status": "HUMAN_OUTCOME_UNOPENED",
        "rating_bands": list(RATING_BANDS),
        "endpoints": list(PRESEALED_ENDPOINTS),
        "trial_families": {
            "blind_preference": {
                "arms": list(COMMENTARY_ARMS),
                "purpose": "paired subjective comparison without causal attribution to understanding",
            },
            "move_understanding": {
                "arms": list(UNDERSTANDING_ARMS),
                "purpose": (
                    "single-arm randomized exposure; compare post-exposure understanding across "
                    "C3X, baseline, and no-commentary controls"
                ),
            },
        },
        "primary_estimands": [
            "within-rating-band C3X-minus-baseline correctness/usefulness/clarity",
            "within-rating-band blind preference probability for C3X vs baseline",
            "within-rating-band post-exposure understanding accuracy: C3X vs baseline",
            "within-rating-band post-exposure understanding accuracy: C3X vs no-commentary",
            "trust calibration only on reference-validity controls",
        ],
        "separation_rules": [
            "machine evidence coverage is not a human-utility score",
            "human preference cannot promote causal authority",
            "correctness, usefulness, clarity, preference, understanding, and trust are separate endpoints",
            "paired A/B preference trials cannot identify explanation-induced understanding",
            "understanding trials expose exactly one assigned arm before the outcome question",
            "free-form prose quality cannot override I5-I7 factuality or verification failures",
            "human outcomes must remain unset until real adjudication is ingested",
        ],
        "missingness_policy": {
            "primary": "report denominator and observed count by rating band and arm",
            "no_posthoc_imputation": True,
            "sensitivity": "report worst/best-case accuracy bounds for missing understanding outcomes",
        },
        "trust_calibration_requirement": (
            "Trust calibration is reportable only when the study includes known reference-valid "
            "and reference-invalid control items; mean trust alone is not calibration."
        ),
        "closure_boundary": (
            "I8 infrastructure may close without participant outcomes, but no claim that C3X is "
            "more useful, preferred, clearer, better calibrated, or better for understanding may be made."
        ),
    }

def _digest(*parts: str) -> bytes:
    return sha256("|".join(parts).encode("utf-8")).digest()

def _pair_order(trial_id: str, seed: str) -> tuple[str, str]:
    return ("c3x", "baseline") if _digest(seed, "pair", trial_id)[0] % 2 == 0 else ("baseline", "c3x")

def _single_arm(trial_id: str, participant_id: str, seed: str) -> str:
    idx = int.from_bytes(_digest(seed, "single", trial_id, participant_id)[:4], "big") % len(UNDERSTANDING_ARMS)
    return UNDERSTANDING_ARMS[idx]

def _require_band(rating_band: str) -> None:
    if rating_band not in RATING_BANDS:
        raise ValueError(f"unknown rating_band: {rating_band}")

def build_preference_trial(
    *,
    trial_id: str,
    rating_band: str,
    position_fen: str,
    c3x_text: str,
    baseline_text: str,
    played_move: str,
    seed: str,
    reference_validity: dict[str, bool] | None = None,
) -> dict[str, Any]:
    _require_band(rating_band)
    order = _pair_order(trial_id, seed)
    text = {"c3x": c3x_text, "baseline": baseline_text}
    arms = {"A": order[0], "B": order[1]}
    return {
        "participant_packet": {
            "schema": "c3x-human-preference-trial-v2",
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
            },
        },
        "adjudication_key": {
            "schema": "c3x-human-preference-key-v2",
            "trial_id": trial_id,
            "rating_band": rating_band,
            "arm_identity": arms,
            "reference_validity": reference_validity or {},
        },
    }

def build_understanding_trial(
    *,
    trial_id: str,
    participant_id: str,
    rating_band: str,
    position_fen: str,
    c3x_text: str,
    baseline_text: str,
    played_move: str,
    understanding_prompt: str,
    understanding_options: list[str],
    understanding_answer: str,
    seed: str,
) -> dict[str, Any]:
    _require_band(rating_band)
    if len(understanding_options) < 2 or understanding_answer not in understanding_options:
        raise ValueError("understanding answer must be one of at least two options")
    arm = _single_arm(trial_id, participant_id, seed)
    text = {"c3x": c3x_text, "baseline": baseline_text, "no_commentary": ""}
    return {
        "participant_packet": {
            "schema": "c3x-move-understanding-trial-v2",
            "trial_id": trial_id,
            "rating_band": rating_band,
            "position_fen": position_fen,
            "played_move": played_move,
            "commentary": text[arm],
            "question": {
                "prompt": understanding_prompt,
                "options": list(understanding_options),
            },
        },
        "adjudication_key": {
            "schema": "c3x-move-understanding-key-v2",
            "trial_id": trial_id,
            "participant_id_hash": sha256(participant_id.encode("utf-8")).hexdigest(),
            "rating_band": rating_band,
            "assigned_arm": arm,
            "understanding_answer": understanding_answer,
        },
    }

def validate_preference_response(response: dict[str, Any]) -> None:
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

def score_preference_response(response: dict[str, Any], key: dict[str, Any]) -> dict[str, Any]:
    validate_preference_response(response)
    arm_identity = key["arm_identity"]
    reverse = {identity: arm for arm, identity in arm_identity.items()}
    c3x_arm, baseline_arm = reverse["c3x"], reverse["baseline"]
    pref = response["preference"]
    pref_c3x = 0.5 if pref == "TIE" else float(arm_identity[pref] == "c3x")
    out: dict[str, Any] = {
        "schema": "c3x-human-preference-scored-v2",
        "trial_id": key["trial_id"],
        "rating_band": key["rating_band"],
        "preference_c3x": pref_c3x,
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

def score_understanding_response(answer: str, key: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(answer, str):
        raise ValueError("answer must be a string")
    return {
        "schema": "c3x-move-understanding-scored-v2",
        "trial_id": key["trial_id"],
        "rating_band": key["rating_band"],
        "assigned_arm": key["assigned_arm"],
        "correct": int(answer == key["understanding_answer"]),
    }

def _mean_or_none(values: list[float]) -> float | None:
    return mean(values) if values else None

def aggregate_human_outcomes(
    preference_rows: list[dict[str, Any]],
    understanding_rows: list[dict[str, Any]],
    *,
    expected_understanding_counts: dict[str, int] | None = None,
) -> dict[str, Any]:
    if not preference_rows and not understanding_rows:
        return {
            "schema": "c3x-human-utility-summary-v2",
            "human_outcome_opened": False,
            "preference_n": 0,
            "understanding_n": 0,
            "verdict": "NO_HUMAN_UTILITY_CLAIM",
        }

    out: dict[str, Any] = {
        "schema": "c3x-human-utility-summary-v2",
        "human_outcome_opened": True,
        "preference_n": len(preference_rows),
        "understanding_n": len(understanding_rows),
        "preference": {},
        "understanding": {},
    }
    if preference_rows:
        out["preference"]["c3x_preference_mean"] = mean(r["preference_c3x"] for r in preference_rows)
        out["preference"]["by_band"] = {}
        for band in RATING_BANDS:
            rows = [r for r in preference_rows if r["rating_band"] == band]
            if not rows:
                continue
            band_out: dict[str, Any] = {
                "n": len(rows),
                "c3x_preference_mean": mean(r["preference_c3x"] for r in rows),
                "c3x": {},
                "baseline": {},
            }
            for identity in COMMENTARY_ARMS:
                for field in (*LIKERT_FIELDS, "trust"):
                    band_out[identity][f"{field}_mean"] = mean(r[identity][field] for r in rows)
                brier = [r[identity]["trust_brier"] for r in rows if r[identity]["trust_brier"] is not None]
                band_out[identity]["trust_brier_mean"] = _mean_or_none(brier)
                band_out[identity]["trust_calibration_reportable"] = bool(brier)
            out["preference"]["by_band"][band] = band_out

    if understanding_rows:
        by_band: dict[str, Any] = {}
        for band in RATING_BANDS:
            by_arm: dict[str, Any] = {}
            for arm in UNDERSTANDING_ARMS:
                rows = [r for r in understanding_rows if r["rating_band"] == band and r["assigned_arm"] == arm]
                observed = len(rows)
                if not observed and not (expected_understanding_counts or {}).get(f"{band}:{arm}"):
                    continue
                correct = sum(r["correct"] for r in rows)
                expected = (expected_understanding_counts or {}).get(f"{band}:{arm}", observed)
                missing = max(0, expected - observed)
                by_arm[arm] = {
                    "observed_n": observed,
                    "expected_n": expected,
                    "missing_n": missing,
                    "observed_accuracy": (correct / observed) if observed else None,
                    "missing_worst_case_accuracy": (correct / expected) if expected else None,
                    "missing_best_case_accuracy": ((correct + missing) / expected) if expected else None,
                }
            if by_arm:
                by_band[band] = by_arm
        out["understanding"]["by_band"] = by_band
    return out

def trial_bank_manifest(preference_trials: list[dict[str, Any]], understanding_trials: list[dict[str, Any]]) -> dict[str, Any]:
    public_ids = []
    for family, rows in (("preference", preference_trials), ("understanding", understanding_trials)):
        for row in rows:
            packet = row["participant_packet"]
            public_ids.append(f"{family}:{packet['trial_id']}:{packet['rating_band']}")
    if len(public_ids) != len(set(public_ids)):
        raise ValueError("duplicate public trial identity")
    serial = "\n".join(sorted(public_ids))
    return {
        "schema": "c3x-i8-trial-bank-manifest-v1",
        "preference_trial_count": len(preference_trials),
        "understanding_trial_count": len(understanding_trials),
        "public_identity_sha256": sha256(serial.encode("utf-8")).hexdigest(),
        "human_outcomes_included": False,
    }
