from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import chess
import chess.pgn

from .loop import FORBIDDEN_DEMAND_KEYS

STAGE_TITLE = "C3X 0.8.0-G10-P1 — Prospective Explanation-Demand Validity, Opening-Theory Degeneracy Exclusion, Human↔Engine Candidate-Salience Triangulation, Cross-Engine/Budget Stability, Decision-Pressure Stratification, Annotation-Supported Positive-Control Recovery, Frozen Real-PGN Case-Bank Constitution & Fresh Local-Certificate Induction Admission Court"
QUESTION_AUTHORITY = "RESEARCH_QUESTION_ADMISSION_ONLY"

ELO_BANDS = (1200, 1800, 2400)
SF_BUDGETS = (2000, 5000, 10000, 40000)
MEDIUM_BUDGET = 10000
P1_POLICY = {
    "schema": "c3x-g10-p1-policy-v1",
    "base_eval_target": 48,
    "annotation_positive_target": 24,
    "annotation_negative_target": 24,
    "final_bank_target": 36,
    "final_bank_minimum": 18,
    "theory_past_distance_max": 2,
    "human_pair_mass_min": 0.20,
    "human_each_candidate_min": 0.03,
    "human_supported_band_min": 2,
    "sf_pair_budget_support_min": 3,
    "cross_engine_pair_support_min": 2,
    "annotation_enrichment_floor": 1.05,
    "selector_shrinkage_threshold": 0.25,
    "uses_certificate_yield": False,
    "annotation_used_for_selection": False,
    "decision_pressure_used_for_exclusion": False,
}

SOURCE_LOCKS = {
    "maia3_code": {
        "repo": "CSSLab/maia3",
        "commit": "1e13597c42d4858b7cfd7cfdae01e297263364b2",
        "model_repo": "UofTCSSLab/Maia3-5M",
    },
    "chess_openings": {
        "repo": "lichess-org/chess-openings",
        "commit": "c67912be581f0793dbaa776be5ccf111e01f88d9",
        "license": "CC0",
    },
    "engines": {
        "stockfish_19": "edb0d9db6731067ec50ce619ff372b463bc4dd5d",
        "berserk": "32628515050b83805bab4afa1026dd2bcaa93f55",
        "ethereal": "0e47e9b67f345c75eb965d9fb3e2493b6a11d09a",
    },
}


def p1_preseal() -> dict[str, Any]:
    return {
        "schema": "c3x-g10-p1-preseal-v1",
        "stage": STAGE_TITLE,
        "parent": "G10-P0 CLOSED/PASS",
        "policy": dict(P1_POLICY),
        "source_locks": SOURCE_LOCKS,
        "rating_bands": list(ELO_BANDS),
        "stockfish_budgets": list(SF_BUDGETS),
        "fresh_certificate_outcomes_opened": False,
        "certificate_yield_visible": False,
        "annotation_used_for_selection": False,
        "authority_ceiling": [
            "explanation-demand validity",
            "research-question admission",
            "no local causal result",
            "no transportable law",
            "no objective chess truth",
            "no human cognition or utility claim",
        ],
    }


def stable_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def board_key(fen: str) -> str:
    parts = str(fen).split()
    if len(parts) < 4:
        raise ValueError("invalid FEN")
    return " ".join(parts[:4])


def phase_from_board(board: chess.Board) -> str:
    nonpawn = 0
    values = {
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
    }
    for pt, value in values.items():
        nonpawn += value * len(board.pieces(pt, chess.WHITE))
        nonpawn += value * len(board.pieces(pt, chess.BLACK))
    if board.fullmove_number <= 15 and nonpawn >= 42:
        return "opening"
    if nonpawn <= 18:
        return "endgame"
    return "middlegame"


def _parse_opening_pgn(pgn: str) -> tuple[str, ...]:
    game = chess.pgn.read_game(io.StringIO(str(pgn).strip() + " *"))
    if game is None:
        raise ValueError(f"cannot parse opening PGN: {pgn}")
    return tuple(m.uci() for m in game.mainline_moves())


def load_opening_catalog(paths: Iterable[str | Path]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, ...]] = set()
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                moves = _parse_opening_pgn(row["pgn"])
                if not moves or moves in seen:
                    continue
                seen.add(moves)
                board = chess.Board()
                for uci in moves:
                    board.push_uci(uci)
                out.append({
                    "eco": row["eco"],
                    "name": row["name"],
                    "moves": moves,
                    "epd": board.epd(),
                })
    out.sort(key=lambda x: (len(x["moves"]), x["eco"], x["name"], x["moves"]))
    return out


def opening_relation(moves_before: Iterable[str], catalog: list[dict[str, Any]]) -> dict[str, Any]:
    seq = tuple(moves_before)
    exact: list[dict[str, Any]] = []
    inside: list[dict[str, Any]] = []
    past: list[dict[str, Any]] = []
    for row in catalog:
        om = row["moves"]
        if seq == om:
            exact.append(row)
        elif len(seq) < len(om) and om[:len(seq)] == seq:
            inside.append(row)
        elif len(seq) > len(om) and seq[:len(om)] == om:
            past.append(row)

    if exact:
        best = max(exact, key=lambda x: len(x["moves"]))
        relation = "EXACT_NAMED_POSITION"
        distance = 0
    elif inside:
        best = min(inside, key=lambda x: len(x["moves"]))
        relation = "INSIDE_KNOWN_OPENING_LINE"
        distance = len(best["moves"]) - len(seq)
    elif past:
        best = max(past, key=lambda x: len(x["moves"]))
        relation = "PAST_NAMED_OPENING"
        distance = len(seq) - len(best["moves"])
    else:
        best = None
        relation = "NO_NAMED_PREFIX"
        distance = None

    theory_proximity = bool(
        relation in ("EXACT_NAMED_POSITION", "INSIDE_KNOWN_OPENING_LINE")
        or (
            relation == "PAST_NAMED_OPENING"
            and distance is not None
            and distance <= int(P1_POLICY["theory_past_distance_max"])
        )
    )
    return {
        "relation": relation,
        "distance_plies": distance,
        "opening_eco": None if best is None else best["eco"],
        "opening_name": None if best is None else best["name"],
        "opening_depth_plies": None if best is None else len(best["moves"]),
        "theory_proximity": theory_proximity,
        "classification_source": "lichess-org/chess-openings@c67912be581f0793dbaa776be5ccf111e01f88d9",
        "ply_only_proxy_used": False,
    }


def _rank_of(move: str, ranked_moves: list[str]) -> int | None:
    try:
        return ranked_moves.index(move) + 1
    except ValueError:
        return None


def maia_policy_features(
    policy_by_elo: dict[int | str, dict[str, float]],
    *,
    played_uci: str,
    candidate_pair: tuple[str, str] | list[str],
) -> dict[str, Any]:
    a, b = str(candidate_pair[0]), str(candidate_pair[1])
    bands: dict[str, Any] = {}
    supported = 0
    top1s: list[str] = []
    for elo in ELO_BANDS:
        probs = {str(k): float(v) for k, v in (policy_by_elo.get(elo) or policy_by_elo.get(str(elo)) or {}).items()}
        ranked = [m for m, _ in sorted(probs.items(), key=lambda kv: (-kv[1], kv[0]))]
        mass = sum(max(0.0, p) for p in probs.values())
        norm = [p / mass for p in probs.values() if p > 0] if mass > 0 else []
        entropy = -sum(p * math.log2(p) for p in norm) if norm else None
        pa, pb = probs.get(a, 0.0), probs.get(b, 0.0)
        pair_mass = pa + pb
        pair_supported = (
            pair_mass >= float(P1_POLICY["human_pair_mass_min"])
            and min(pa, pb) >= float(P1_POLICY["human_each_candidate_min"])
        )
        supported += int(pair_supported)
        top1 = ranked[0] if ranked else None
        if top1:
            top1s.append(top1)
        bands[str(elo)] = {
            "played_probability": probs.get(played_uci, 0.0),
            "played_rank": _rank_of(played_uci, ranked),
            "candidate_a_probability": pa,
            "candidate_b_probability": pb,
            "candidate_pair_mass": pair_mass,
            "candidate_a_rank": _rank_of(a, ranked),
            "candidate_b_rank": _rank_of(b, ranked),
            "pair_supported": pair_supported,
            "top1_move": top1,
            "topk_mass": mass,
            "topk_normalized_entropy_bits": entropy,
            "topk_size": len(ranked),
        }

    return {
        "schema": "c3x-g10-p1-maia-salience-v1",
        "instrument": "Maia-3 5M",
        "rating_bands": bands,
        "supported_band_count": supported,
        "human_pair_supported": supported >= int(P1_POLICY["human_supported_band_min"]),
        "top1_diversity": len(set(top1s)),
        "rating_band_top1_reversal": len(set(top1s)) > 1,
        "authority": "PREDICTIVE_HUMAN_POLICY_MODEL_ONLY",
        "actual_human_judgment": False,
    }


def _moves_from_obs(obs: dict[str, Any], k: int = 3) -> list[str]:
    return [str(x["uci"]) for x in (obs.get("candidates") or [])[:k] if x.get("uci")]


def _pair_present(pair: tuple[str, str], obs: dict[str, Any]) -> bool:
    s = set(_moves_from_obs(obs, 3))
    return pair[0] in s and pair[1] in s


def engine_stability_features(
    observations: dict[str, dict[str, Any]],
    *,
    candidate_pair: tuple[str, str] | list[str],
) -> dict[str, Any]:
    pair = (str(candidate_pair[0]), str(candidate_pair[1]))
    sf_keys = [f"stockfish_19@{n}" for n in SF_BUDGETS]
    medium_keys = [
        f"stockfish_19@{MEDIUM_BUDGET}",
        f"berserk@{MEDIUM_BUDGET}",
        f"ethereal@{MEDIUM_BUDGET}",
    ]
    sf_support = sum(_pair_present(pair, observations[k]) for k in sf_keys if k in observations)
    cross_support = sum(_pair_present(pair, observations[k]) for k in medium_keys if k in observations)
    top1s = {
        k: (_moves_from_obs(v, 1)[0] if _moves_from_obs(v, 1) else None)
        for k, v in observations.items()
    }
    pair_sets = {
        k: sorted(_moves_from_obs(v, 2))
        for k, v in observations.items()
    }
    return {
        "schema": "c3x-g10-p1-engine-stability-v1",
        "candidate_pair": list(pair),
        "stockfish_budget_pair_support": sf_support,
        "stockfish_budget_observed": sum(k in observations for k in sf_keys),
        "cross_engine_medium_pair_support": cross_support,
        "cross_engine_medium_observed": sum(k in observations for k in medium_keys),
        "engine_pair_stable": (
            sf_support >= int(P1_POLICY["sf_pair_budget_support_min"])
            and cross_support >= int(P1_POLICY["cross_engine_pair_support_min"])
        ),
        "top1_by_world": top1s,
        "top2_set_by_world": pair_sets,
        "top1_diversity": len({x for x in top1s.values() if x}),
        "order_flip_allowed": True,
        "authority": "QUESTION_IDENTITY_STABILITY_ONLY",
        "causal_intervention_semantics_reopened": False,
    }


def decision_pressure_features(
    *,
    board_fen: str,
    p0_candidates: list[dict[str, Any]],
    clock_after_move_seconds: float | None,
) -> dict[str, Any]:
    scores = [c.get("score_cp") for c in p0_candidates[:3]]
    finite = [int(x) for x in scores if x is not None]
    gap = None
    spread = None
    if len(finite) >= 2:
        gap = abs(finite[0] - finite[1])
    if len(finite) >= 3:
        spread = max(finite) - min(finite)
    if clock_after_move_seconds is None:
        clock_band = "CLOCK_UNAVAILABLE"
    elif clock_after_move_seconds < 30:
        clock_band = "UNDER_30S_AFTER_MOVE"
    elif clock_after_move_seconds < 120:
        clock_band = "30_TO_119S_AFTER_MOVE"
    else:
        clock_band = "AT_LEAST_120S_AFTER_MOVE"
    return {
        "schema": "c3x-g10-p1-decision-pressure-v1",
        "phase": phase_from_board(chess.Board(board_fen)),
        "p0_top2_gap_cp": gap,
        "p0_top3_spread_cp": spread,
        "clock_after_move_seconds": clock_after_move_seconds,
        "clock_band": clock_band,
        "private_cognitive_state_inferred": False,
        "authority": "OBSERVED_OR_ENGINE_DERIVED_CONTEXT_ONLY",
    }


def refined_gate(record: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    p0 = record.get("p0") or {}
    human = (record.get("validity") or {}).get("human_salience") or {}
    stability = (record.get("validity") or {}).get("engine_stability") or {}
    opening = record.get("opening") or {}
    if not p0.get("admitted"):
        reasons.append("P0_NOT_ADMITTED")
    opening_degenerate = bool(opening.get("theory_proximity") and human.get("human_pair_supported"))
    if opening_degenerate:
        reasons.append("OPENING_THEORY_DEGENERACY")
    if not human.get("human_pair_supported"):
        reasons.append("HUMAN_PAIR_SALIENCE_UNSUPPORTED")
    if not stability.get("engine_pair_stable"):
        reasons.append("QUESTION_IDENTITY_ENGINE_BUDGET_UNSTABLE")
    return {
        "schema": "c3x-g10-p1-refined-gate-v1",
        "admitted": not reasons,
        "reasons": reasons or ["ALL_PRECOMMITTED_VALIDITY_GATES_PASS"],
        "opening_degenerate": opening_degenerate,
        "annotation_used": False,
        "certificate_yield_used": False,
        "authority": QUESTION_AUTHORITY,
    }


def _select_balanced(
    rows: list[dict[str, Any]],
    *,
    target: int,
    key_fields: tuple[str, ...],
) -> list[dict[str, Any]]:
    if target <= 0:
        return []
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key: list[str] = []
        for f in key_fields:
            value: Any = row
            for part in f.split("."):
                value = (value or {}).get(part) if isinstance(value, dict) else None
            key.append(str(value))
        groups[tuple(key)].append(row)
    for vals in groups.values():
        vals.sort(key=lambda x: stable_hash(x.get("case_id")))
    ordered_keys = sorted(groups)
    selected: list[dict[str, Any]] = []
    while len(selected) < target and any(groups[k] for k in ordered_keys):
        for k in ordered_keys:
            if groups[k] and len(selected) < target:
                selected.append(groups[k].pop(0))
    return selected


def freeze_base_evaluation_bank(admitted_rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = _select_balanced(
        admitted_rows,
        target=int(P1_POLICY["base_eval_target"]),
        key_fields=("source_month", "phase", "opening.theory_proximity"),
    )
    payload = {
        "schema": "c3x-g10-p1-base-evaluation-bank-v1",
        "authority": "EVALUATION_BANK_ONLY",
        "selection_inputs": ["source_month", "phase", "opening.theory_proximity", "stable_case_hash"],
        "maia_outcomes_opened": False,
        "cross_engine_outcomes_opened": False,
        "annotation_labels_used": False,
        "certificate_outcomes_opened": False,
        "cases": selected,
    }
    payload["bank_sha256"] = stable_hash(payload["cases"])
    return payload


def freeze_final_case_bank(scored_base_rows: list[dict[str, Any]]) -> dict[str, Any]:
    eligible = [x for x in scored_base_rows if (x.get("refined_gate") or {}).get("admitted")]
    selected = _select_balanced(
        eligible,
        target=int(P1_POLICY["final_bank_target"]),
        key_fields=("source_month", "phase"),
    )
    payload = {
        "schema": "c3x-g10-p1-final-case-bank-v1",
        "authority": QUESTION_AUTHORITY,
        "selection_rule": {
            "required": [
                "P0_ADMITTED",
                "NOT_OPENING_THEORY_DEGENERATE",
                "HUMAN_PAIR_SALIENCE_SUPPORTED",
                "ENGINE_BUDGET_PAIR_STABLE",
            ],
            "balancing": ["source_month", "phase", "stable_case_hash"],
            "annotation_used": False,
            "certificate_yield_used": False,
        },
        "fresh_local_certificate_induction_opened": False,
        "cases": selected,
    }
    payload["bank_sha256"] = stable_hash(payload["cases"])
    return payload


def annotation_control_stats(scored_controls: list[dict[str, Any]]) -> dict[str, Any]:
    pos = [x for x in scored_controls if x.get("annotation_label") is True]
    neg = [x for x in scored_controls if x.get("annotation_label") is False]

    def rate(rows: list[dict[str, Any]], field: str) -> float | None:
        if not rows:
            return None
        if field == "p0":
            return sum(bool((x.get("p0") or {}).get("admitted")) for x in rows) / len(rows)
        if field == "refined":
            return sum(bool((x.get("refined_gate") or {}).get("admitted")) for x in rows) / len(rows)
        raise KeyError(field)

    p0p, p0n = rate(pos, "p0"), rate(neg, "p0")
    rp, rn = rate(pos, "refined"), rate(neg, "refined")

    def enrich(a: float | None, b: float | None) -> float | None:
        if a is None or b is None:
            return None
        if b == 0:
            return None if a == 0 else float("inf")
        return a / b

    return {
        "schema": "c3x-g10-p1-annotation-positive-control-v1",
        "annotated_n": len(pos),
        "matched_unannotated_n": len(neg),
        "p0_admission_rate_annotated": p0p,
        "p0_admission_rate_unannotated": p0n,
        "p0_enrichment_ratio": enrich(p0p, p0n),
        "refined_admission_rate_annotated": rp,
        "refined_admission_rate_unannotated": rn,
        "refined_enrichment_ratio": enrich(rp, rn),
        "selection_threshold_tuned_on_annotation": False,
        "authority": "EXTERNAL_ATTENTION_POSITIVE_CONTROL_ONLY",
    }


def _recursive_forbidden_keys(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for k, v in value.items():
            if k in FORBIDDEN_DEMAND_KEYS or k in {
                "intervention_outcome",
                "certificate_yield",
                "causal_family",
                "replication_status",
            }:
                found.add(k)
            found |= _recursive_forbidden_keys(v)
    elif isinstance(value, list):
        for x in value:
            found |= _recursive_forbidden_keys(x)
    return found


def adjudicate_demand_validity(
    *,
    pool_summary: dict[str, Any],
    scored_base_rows: list[dict[str, Any]],
    scored_controls: list[dict[str, Any]],
    final_bank: dict[str, Any],
    instrument_status: dict[str, Any],
) -> dict[str, Any]:
    forbidden = sorted(_recursive_forbidden_keys({
        "base": scored_base_rows,
        "controls": scored_controls,
        "bank": final_bank,
    }))
    if forbidden:
        raise ValueError(f"forbidden causal-outcome fields leaked into P1: {forbidden}")

    human_ok = bool(instrument_status.get("maia3_all_rating_bands_pass"))
    engine_ok = bool(instrument_status.get("all_three_engines_pass"))
    opening_ok = bool(instrument_status.get("opening_corpus_pass"))
    annotation_ok = bool(instrument_status.get("annotation_source_pass"))
    final_n = len(final_bank.get("cases") or [])
    phases = sorted({x.get("phase") for x in (final_bank.get("cases") or []) if x.get("phase")})
    controls = annotation_control_stats(scored_controls)
    base_n = len(scored_base_rows)
    refined_n = sum(bool((x.get("refined_gate") or {}).get("admitted")) for x in scored_base_rows)
    shrinkage = None if base_n == 0 else 1.0 - refined_n / base_n
    opening_deg_share = None if base_n == 0 else sum(
        bool((x.get("refined_gate") or {}).get("opening_degenerate")) for x in scored_base_rows
    ) / base_n
    unstable_share = None if base_n == 0 else sum(
        not bool(((x.get("validity") or {}).get("engine_stability") or {}).get("engine_pair_stable"))
        for x in scored_base_rows
    ) / base_n

    ratios = [controls.get("p0_enrichment_ratio"), controls.get("refined_enrichment_ratio")]
    finite_ratios = [float(x) for x in ratios if x is not None and math.isfinite(float(x))]
    annotation_enriched = any(x >= float(P1_POLICY["annotation_enrichment_floor"]) for x in finite_ratios)
    if any(x == float("inf") for x in ratios if x is not None):
        annotation_enriched = True

    if not human_ok:
        verdict = "HOLD_HUMAN_SALIENCE_INSTRUMENT_UNREALIZED"
    elif not (engine_ok and opening_ok and annotation_ok):
        verdict = "HOLD_DEMAND_SELECTOR_EXTERNAL_VALIDITY_UNRESOLVED"
    elif final_n < int(P1_POLICY["final_bank_minimum"]) or len(phases) < 2:
        verdict = "HOLD_DEMAND_SELECTOR_EXTERNAL_VALIDITY_UNRESOLVED"
    elif not annotation_enriched:
        verdict = "HOLD_DEMAND_SELECTOR_EXTERNAL_VALIDITY_UNRESOLVED"
    elif (
        (shrinkage is not None and shrinkage >= float(P1_POLICY["selector_shrinkage_threshold"]))
        or (opening_deg_share is not None and opening_deg_share >= 0.20)
        or (unstable_share is not None and unstable_share >= 0.20)
    ):
        verdict = "PASS_WITH_SELECTOR_SHRINKAGE_CASE_BANK_FROZEN"
    else:
        verdict = "PASS_DEMAND_VALIDITY_CASE_BANK_FROZEN"

    return {
        "schema": "c3x-g10-p1-court-v1",
        "stage": STAGE_TITLE,
        "verdict": verdict,
        "authority": "EXPLANATION_DEMAND_VALIDITY_AND_RESEARCH_ADMISSION_ONLY",
        "pool_summary": pool_summary,
        "instrument_status": instrument_status,
        "annotation_positive_control": controls,
        "base_evaluation_n": base_n,
        "refined_gate_pass_n": refined_n,
        "selector_shrinkage_fraction": shrinkage,
        "opening_degenerate_share": opening_deg_share,
        "engine_unstable_share": unstable_share,
        "final_case_bank_n": final_n,
        "final_case_bank_sha256": final_bank.get("bank_sha256"),
        "final_case_bank_phases": phases,
        "fresh_local_certificate_induction_opened": False,
        "certificate_yield_visible": False,
        "p0_thresholds_retuned_against_certificate_yield": False,
        "authority_ceiling": [
            "question admission only",
            "no local causal result",
            "no transportable law",
            "no objective chess truth",
            "no human cognition or utility claim",
        ],
    }
