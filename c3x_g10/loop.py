from __future__ import annotations

import io
from typing import Any, Iterable

import chess
import chess.engine
import chess.pgn

from c3x_explain.core import candidate_packet

QUESTION_ONLY = "QUESTION_PROPOSAL_ONLY"
CAUSAL_LOCAL = "C3X_LOCAL_CAUSAL_CERTIFICATE"
HEURISTIC_ONLY = "CONVENTIONAL_HEURISTIC_COMMENTARY_ONLY"

FROZEN_DEMAND_POLICY = {
    "schema": "c3x-g10-p0-demand-policy-v1",
    "minimum_multipv": 3,
    "max_top2_gap_cp": 35,
    "max_played_rank": 3,
    "reject_mate_like_abs_cp_at_or_above": 90000,
    "requires_distinct_top_moves": True,
    "uses_causal_outcomes": False,
    "forbidden_selection_inputs": [
        "certificate_id",
        "decision_cells",
        "falsifiers",
        "intervention_outcome",
        "causal_family",
        "structural_signature",
        "replication_status",
    ],
}

FORBIDDEN_DEMAND_KEYS = frozenset(FROZEN_DEMAND_POLICY["forbidden_selection_inputs"])


def _board_key(fen: str) -> str:
    parts = str(fen).split()
    if len(parts) < 4:
        raise ValueError("FEN must contain at least four fields")
    return " ".join(parts[:4])


def _pair_id(a: str, b: str) -> str:
    return f"{a}::{b}"


def _pair_members(pair: Any) -> tuple[str, str]:
    if isinstance(pair, str):
        xs = pair.split("::")
        if len(xs) != 2:
            raise ValueError("pair id must contain exactly two UCI moves")
        return xs[0], xs[1]
    if isinstance(pair, dict):
        pid = pair.get("pair_id")
        if pid:
            return _pair_members(pid)
        a = (pair.get("A") or {}).get("uci")
        b = (pair.get("B") or {}).get("uci")
        if a and b:
            return str(a), str(b)
    raise ValueError("certificate pair is missing or malformed")


def _certificate_baseline_fen(c: dict[str, Any]) -> str:
    return str(
        c.get("position_fen")
        or c.get("fen")
        or c.get("original_fen")
        or ((c.get("counterfactual_boards") or {}).get("B0") or {}).get("fen")
        or ""
    )


def _nested_bound(c: dict[str, Any]) -> str | None:
    return c.get("bound") or (c.get("chain") or {}).get("bound")


def _structural_signature(c: dict[str, Any]) -> str | None:
    return c.get("structural_signature") or (c.get("chain") or {}).get("structural_signature")


def _engine_relative_atoms(c: dict[str, Any]) -> list[str]:
    xs = c.get("engine_relative_atoms")
    if xs is None:
        xs = (c.get("chain") or {}).get("engine_relative_atoms")
    return [str(x) for x in (xs or [])]


def g10_p0_preseal() -> dict[str, Any]:
    return {
        "schema": "c3x-g10-p0-preseal-v1",
        "stage": (
            "C3X 0.8.0-G10-P0 — Origin-Return Dual-Track Reconstitution, "
            "Real-PGN Explanation-Demand Discovery, Position-Specific Local Causal "
            "Certificate Induction, Chess-Native Consequence Compression, "
            "Authority-Separated Certificate↔Commentary Routing & Prospective "
            "Contrast-to-Explanation Loop Constitution"
        ),
        "generation_alias": "Generation X — Contrast-to-Explanation Loop",
        "scientific_parent": "G9.5-P18 CLOSED/HOLD",
        "implementation_parent": "Explain I8 CLOSED/HUMAN-UTILITY CLAIM HOLD",
        "demand_policy": dict(FROZEN_DEMAND_POLICY),
        "h_family_privileged": False,
        "fresh_intervention_outcomes_opened": False,
        "authority_ceiling": [
            "constitution and dual-track realizability",
            "position-specific local certificate handling",
            "verified chess-native consequence routing",
            "no transportable causal law",
            "no objective chess truth",
            "no human-utility claim",
        ],
        "success_requires": [
            "outcome-blind real-PGN demand proposal",
            "local certificate contract independent of the failed H family",
            "legal chess-native consequence compression",
            "historical P16 known-positive contract witness round-trip",
            "authority-separated commentary handoff",
            "existing I0-I8 regression remains green",
        ],
    }


def _assert_demand_has_no_causal_leak(payload: dict[str, Any]) -> None:
    leaked = sorted(FORBIDDEN_DEMAND_KEYS.intersection(payload.keys()))
    if leaked:
        raise ValueError(f"demand proposal contains forbidden causal-outcome fields: {leaked}")
    features = payload.get("features") or {}
    leaked_features = sorted(FORBIDDEN_DEMAND_KEYS.intersection(features.keys()))
    if leaked_features:
        raise ValueError(f"demand features contain forbidden causal-outcome fields: {leaked_features}")


def demand_from_candidate_packet(
    *,
    position_fen: str,
    played_uci: str,
    candidates: list[dict[str, Any]],
    source_id: str,
    game_id: str,
    ply: int,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    p = dict(FROZEN_DEMAND_POLICY if policy is None else policy)
    board = chess.Board(position_fen)
    played = chess.Move.from_uci(played_uci)
    if played not in board.legal_moves:
        raise ValueError("played move is illegal for supplied FEN")
    if len(candidates) < int(p["minimum_multipv"]):
        admitted = False
        reasons = ["insufficient_multipv"]
        top2_gap = None
        played_rank = None
    else:
        ranked = sorted(candidates, key=lambda x: int(x.get("rank", 9999)))
        top, second = ranked[0], ranked[1]
        scores = (top.get("score_cp"), second.get("score_cp"))
        top2_gap = None if None in scores else abs(int(scores[0]) - int(scores[1]))
        played_rank = next((int(c["rank"]) for c in ranked if c.get("uci") == played_uci), None)
        mate_like = any(
            c.get("score_cp") is not None
            and abs(int(c["score_cp"])) >= int(p["reject_mate_like_abs_cp_at_or_above"])
            for c in ranked[:2]
        )
        distinct = top.get("uci") != second.get("uci")
        conditions = {
            "top2_near_equal": top2_gap is not None and top2_gap <= int(p["max_top2_gap_cp"]),
            "played_in_frozen_multipv_window": played_rank is not None and played_rank <= int(p["max_played_rank"]),
            "not_mate_like": not mate_like,
            "distinct_top_moves": bool(distinct),
        }
        admitted = all(conditions.values())
        reasons = [k for k, v in conditions.items() if v]
        if not admitted:
            reasons += [f"failed:{k}" for k, v in conditions.items() if not v]

    ranked_public = [
        {
            "rank": int(c["rank"]),
            "uci": str(c["uci"]),
            "san": c.get("san"),
            "score_cp": c.get("score_cp"),
            "pv_uci": list(c.get("pv_uci") or []),
        }
        for c in sorted(candidates, key=lambda x: int(x.get("rank", 9999)))[: int(p["minimum_multipv"])]
    ]
    proposal = {
        "schema": "c3x-g10-demand-proposal-v1",
        "authority": QUESTION_ONLY,
        "source_id": source_id,
        "game_id": game_id,
        "ply": int(ply),
        "position_fen": position_fen,
        "position_key": _board_key(position_fen),
        "played_uci": played_uci,
        "candidate_pair": (
            _pair_id(ranked_public[0]["uci"], ranked_public[1]["uci"])
            if len(ranked_public) >= 2
            else None
        ),
        "candidates": ranked_public,
        "features": {
            "top2_gap_cp": top2_gap,
            "played_rank": played_rank,
            "multipv_observed": len(candidates),
        },
        "admitted": bool(admitted),
        "admission_reasons": reasons,
        "causal_outcomes_opened": False,
        "certificate_attached": False,
        "fresh": True,
    }
    _assert_demand_has_no_causal_leak(proposal)
    return proposal


def discover_pgn_demands(
    pgn_text: str,
    *,
    engine_path: str,
    source_id: str,
    nodes: int = 10000,
    multipv: int = 3,
    max_proposals: int = 8,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    if game is None:
        raise ValueError("No PGN game found")
    game_id = "|".join(
        str(game.headers.get(k, "?"))
        for k in ("Event", "Site", "Date", "Round", "White", "Black")
    )
    board = game.board()
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    proposals: list[dict[str, Any]] = []
    scanned = 0
    try:
        for ply, move in enumerate(game.mainline_moves(), 1):
            scanned += 1
            cands = candidate_packet(engine, board, multipv, nodes)
            proposal = demand_from_candidate_packet(
                position_fen=board.fen(),
                played_uci=move.uci(),
                candidates=cands,
                source_id=source_id,
                game_id=game_id,
                ply=ply,
                policy=policy,
            )
            if proposal["admitted"]:
                proposals.append(proposal)
                if len(proposals) >= int(max_proposals):
                    break
            board.push(move)
    finally:
        engine.quit()
    return {
        "schema": "c3x-g10-demand-discovery-v1",
        "source_id": source_id,
        "game_id": game_id,
        "positions_scanned": scanned,
        "proposal_count": len(proposals),
        "proposals": proposals,
        "causal_outcomes_opened": False,
        "authority": QUESTION_ONLY,
    }


def normalize_local_certificate(
    c: dict[str, Any],
    *,
    expected_fen: str | None = None,
    expected_pair: str | None = None,
) -> dict[str, Any]:
    cid = c.get("certificate_id") or c.get("receipt_sha256")
    if not cid:
        raise ValueError("local certificate missing certificate id")
    fen = _certificate_baseline_fen(c)
    if not fen:
        raise ValueError("local certificate missing baseline FEN")
    board = chess.Board(fen)
    a, b = _pair_members(c.get("pair") or c.get("pair_id"))
    for move_uci in (a, b):
        move = chess.Move.from_uci(move_uci)
        if move not in board.legal_moves:
            raise ValueError(f"certificate pair contains illegal baseline move: {move_uci}")
    pair_id = _pair_id(a, b)
    if expected_fen and _board_key(fen) != _board_key(expected_fen):
        raise ValueError("local certificate position mismatch")
    if expected_pair and pair_id != expected_pair:
        raise ValueError("local certificate pair mismatch")
    bound = _nested_bound(c)
    if not bound:
        raise ValueError("local certificate missing intervention bound")
    return {
        "schema": "c3x-g10-local-certificate-v1",
        "certificate_id": str(cid),
        "source_schema": c.get("schema"),
        "scientific_stage": c.get("scientific_stage"),
        "scientific_verdict": c.get("scientific_verdict"),
        "position_key": _board_key(fen),
        "position_fen": fen,
        "engine": c.get("engine"),
        "pair_id": pair_id,
        "pair_moves": [a, b],
        "bound": str(bound),
        "structural_signature": _structural_signature(c),
        "engine_relative_atoms": _engine_relative_atoms(c),
        "replication_status": c.get("replication_status"),
        "authority": CAUSAL_LOCAL,
        "authority_ceiling": list(c.get("authority_ceiling") or []),
        "transportable_law": False,
        "human_concept_label": c.get("concept_label"),
    }


def _legal_move_or_none(fen: str, move_uci: str | None) -> str | None:
    if not move_uci:
        return None
    board = chess.Board(fen)
    move = chess.Move.from_uci(move_uci)
    if move not in board.legal_moves:
        raise ValueError(f"decision cell contains illegal move {move_uci}")
    return move_uci


def compress_chess_native_consequence(c: dict[str, Any]) -> dict[str, Any]:
    n = normalize_local_certificate(c)
    boards = c.get("counterfactual_boards") or {}
    cells = c.get("decision_cells") or {}
    if "B0" not in boards or "B0" not in cells:
        raise ValueError("certificate lacks B0 board/decision cell")
    b0_fen = str((boards["B0"] or {}).get("fen") or n["position_fen"])
    b0_native = _legal_move_or_none(b0_fen, (cells["B0"] or {}).get("native_bestmove"))

    target_fen = str(((boards.get("TARGET") or {}).get("fen") or ""))
    target_native = None
    if target_fen and "TARGET" in cells:
        target_native = _legal_move_or_none(target_fen, (cells["TARGET"] or {}).get("native_bestmove"))

    lower = ((cells["B0"] or {}).get("bounds") or {}).get("LOWER") or {}
    t_only = _legal_move_or_none(b0_fen, lower.get("t_only_bestmove"))
    event_fired = bool(lower.get("event_fired"))

    target_edit = (c.get("chain") or {}).get("target_edit") or {}
    packet = {
        "schema": "c3x-g10-chess-native-consequence-v1",
        "certificate_id": n["certificate_id"],
        "position_key": n["position_key"],
        "engine": n["engine"],
        "candidate_pair": n["pair_id"],
        "baseline": {
            "fen": b0_fen,
            "native_bestmove": b0_native,
        },
        "structural_intervention": {
            "edit_id": target_edit.get("edit_id"),
            "from": target_edit.get("from"),
            "to": target_edit.get("to"),
            "piece_type": target_edit.get("piece_type"),
            "target_fen": target_fen or None,
        },
        "board_preference_transition": {
            "before": b0_native,
            "after": target_native,
            "changed": bool(b0_native and target_native and b0_native != target_native),
        },
        "search_mediation_transition": {
            "event_fired": event_fired,
            "native": b0_native,
            "event_suppressed": t_only,
            "changed": bool(b0_native and t_only and b0_native != t_only),
        },
        "verified_legal_objects_only": True,
        "human_semantic_label": None,
        "authority": "VERIFIED_CHESS_NATIVE_CONSEQUENCE_FROM_LOCAL_CERTIFICATE",
        "authority_ceiling": (
            "legal chess consequences of this exact local certificate only; "
            "not objective chess truth, human strategy, cognition, or a transportable law"
        ),
    }
    return packet


def historical_contract_witness(c: dict[str, Any]) -> dict[str, Any]:
    n = normalize_local_certificate(c)
    a, b = n["pair_moves"]
    return {
        "schema": "c3x-g10-demand-proposal-v1",
        "authority": QUESTION_ONLY,
        "source_id": str(c.get("source_id") or "historical"),
        "game_id": str(c.get("position_id") or n["certificate_id"]),
        "ply": None,
        "position_fen": n["position_fen"],
        "position_key": n["position_key"],
        "played_uci": None,
        "candidate_pair": _pair_id(a, b),
        "candidates": [
            {"rank": 1, "uci": a, "san": ((c.get("pair") or {}).get("A") or {}).get("san")},
            {"rank": 2, "uci": b, "san": ((c.get("pair") or {}).get("B") or {}).get("san")},
        ],
        "features": {"historical_contract_witness": True},
        "admitted": True,
        "admission_reasons": ["historical_known_positive_contract_witness"],
        "causal_outcomes_opened": True,
        "certificate_attached": False,
        "fresh": False,
        "outcome_blind_eligible": False,
        "contract_witness_only": True,
    }


def build_roundtrip_packet(
    demand: dict[str, Any],
    *,
    certificate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if demand.get("fresh", False):
        _assert_demand_has_no_causal_leak(demand)
        if demand.get("causal_outcomes_opened"):
            raise ValueError("fresh demand proposal cannot have causal outcomes opened")
    out: dict[str, Any] = {
        "schema": "c3x-g10-roundtrip-v1",
        "demand": demand,
        "demand_authority": QUESTION_ONLY,
        "causal_status": "NO_CERTIFICATE",
        "certificate": None,
        "chess_native_consequence": None,
        "commentary_route": {
            "allowed_provenance": ["CONVENTIONAL_HEURISTIC_COMMENTARY"],
            "causal_wording_authorized": False,
        },
        "transportable_law_claim": False,
        "human_utility_claim": False,
    }
    if certificate is None:
        return out
    expected_pair = demand.get("candidate_pair")
    n = normalize_local_certificate(
        certificate,
        expected_fen=demand.get("position_fen"),
        expected_pair=expected_pair,
    )
    consequence = compress_chess_native_consequence(certificate)
    out["causal_status"] = "LOCAL_CERTIFICATE_ATTACHED"
    out["certificate"] = n
    out["chess_native_consequence"] = consequence
    out["commentary_route"] = {
        "allowed_provenance": [
            "C3X_CAUSAL_CONTRAST",
            "CONVENTIONAL_HEURISTIC_COMMENTARY",
        ],
        "causal_wording_authorized": True,
        "causal_scope": "exact local engine-preference contrast only",
    }
    return out
