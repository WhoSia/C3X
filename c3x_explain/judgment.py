"""C3X Explain I10: transparent typed chess judgment from *existing verified* I9 atoms.

NOT a neural model, calibrated confidence, proof of objective best play,
or an upgrade to underlying causal certificates.
"""
from __future__ import annotations
from typing import Any

SCHEMA = "c3x-explain-i10-typed-evidence-judgment-v1"
CAUSAL = "C3X_CAUSAL_CONTRAST"
ORDINARY_CP_CEILING = 8000  # exclude python-chess artificial mate_score conversions

def _abstain(moment: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA, "ply": moment.get("ply"), "played_uci": moment.get("played_uci"),
        "decision": "ABSTAIN", "reason": reason, "preferred_move": None, "challenger": None,
        "candidate_gap_cp": None, "evidence_atom_ids": [], "local_causal_certificate_ids": [],
        "calibrated_probability": None, "objective_chess_truth": None,
        "explanation": "Available evidence does not justify a comparable two-move engine preference.",
    }

def _ordinary_cp(candidate: dict[str, Any]) -> bool:
    v = candidate.get("score_cp")
    return type(v) is int and abs(v) <= ORDINARY_CP_CEILING

def judge_moment(moment: dict[str, Any]) -> dict[str, Any]:
    """A typed decision, with fail-closed evidence and abstention.

    Only emitted after legacy legality/provenance firewall and literal-realization
    verifier succeed. The original chess game remains the authority for legality.
    """
    if moment.get("firewall", {}).get("pass") is not True:
        return _abstain(moment, "LEGACY_LEGALITY_PROVENANCE_FIREWALL_NOT_PASS")
    if moment.get("realization_verification", {}).get("pass") is not True:
        return _abstain(moment, "I7_REALIZATION_VERIFICATION_NOT_PASS")
    rows = moment.get("candidates") or []
    first = next((c for c in rows if c.get("rank") == 1), None)
    second = next((c for c in rows if c.get("rank") == 2), None)
    if first is None or second is None:
        return _abstain(moment, "TWO_DISTINCT_ORIGINAL_ENGINE_CANDIDATES_REQUIRED")
    if sum(c.get("rank") == 1 for c in rows) != 1 or sum(c.get("rank") == 2 for c in rows) != 1:
        return _abstain(moment, "DUPLICATE_MULTIPV_RANK")
    if (not first.get("uci") or not second.get("uci") or first["uci"] == second["uci"] or
        first.get("depth") is None or second.get("depth") is None or
        first.get("depth") != second.get("depth")):
        return _abstain(moment, "ROOT_IDENTITY_OR_COMPLETED_DEPTH_NOT_COMPARABLE")
    if first.get("score_bound") or second.get("score_bound"):
        return _abstain(moment, "BOUND_ONLY_ENGINE_INFO_NOT_EXACT_ROOT_COMPARISON")
    if not _ordinary_cp(first) or not _ordinary_cp(second):
        return _abstain(moment, "UNKNOWN_MATE_OR_NONINTEGER_CP_VALUE")
    if first["score_cp"] <= second["score_cp"]:
        return _abstain(moment, "NO_STRICT_COMPARABLE_LEADER")
    # Bind this exact MultiPV contrast to the pre-existing candidate_contrast
    # and forbid free-floating scores from being treated as a verified explanation.
    supporting = []
    atoms = moment.get("atoms") or []
    for atom in atoms:
        if atom.get("type") == "candidate_contrast" and atom.get("provenance") == "CONVENTIONAL_HEURISTIC_COMMENTARY":
            if (atom.get("claim") or {}).get("top_uci") == first["uci"] and atom.get("atom_id"):
                supporting.append(atom["atom_id"])
    if not supporting:
        return _abstain(moment, "NO_PROVENANCE_LINKED_ENGINE_CONTRAST")
    support = [a["atom_id"] for a in atoms
               if a.get("atom_id") and a.get("type") in
               {"verified_line_evidence", "tactical_fact", "tactical_contrast", "concept_proxy_delta"}]
    # A causal packet is an *additional local contrast*, never a proof that
    # this low-budget MultiPV leader is objectively best.
    graph_cert_ids = {str(n.get("payload", {}).get("certificate_id"))
                      for n in moment.get("typed_graph", {}).get("nodes", [])
                      if n.get("node_type") == "causal_certificate"
                      and n.get("payload", {}).get("certificate_id")}
    local_causal = []
    for atom in atoms:
        if atom.get("type") != "causal_contrast" or atom.get("provenance") != CAUSAL:
            continue
        cert = (atom.get("claim") or {}).get("certificate") or {}
        cid = str(cert.get("certificate_id", ""))
        pair = str(cert.get("pair", ""))
        if cid in graph_cert_ids and set(pair.split("::")) == {first["uci"], second["uci"]}:
            local_causal.append(cid)
    gap = first["score_cp"] - second["score_cp"]
    leader_name = first.get("san") or first["uci"]
    second_name = second.get("san") or second["uci"]
    wording = (f"At this bounded engine-analysis depth {first['depth']}, "
               f"{leader_name} ranks above {second_name} by {gap} centipawns. "
               "This records an engine preference, not a proof of the best chess move.")
    if local_causal:
        wording += " A separately admitted local C3X intervention certificate is linked; its engine-relative scope remains limited."
    return {
        "schema": SCHEMA, "ply": moment.get("ply"), "played_uci": moment.get("played_uci"),
        "decision": "ENGINE_SNAPSHOT_PREFERENCE_ONLY",
        "reason": "TWO_ROOTS_SCORE_COMPARABLE_WITH_PROVENANCE",
        "preferred_move": first["uci"], "preferred_san": leader_name,
        "challenger": second["uci"], "challenger_san": second_name,
        "candidate_gap_cp": gap, "completed_depth": first["depth"],
        "evidence_atom_ids": sorted(set(supporting + support)),
        "local_causal_certificate_ids": sorted(set(local_causal)),
        "calibrated_probability": None, "objective_chess_truth": None,
        "explanation": wording,
        "authority_ceiling": "ENGINE_PREFERENCE_AT_BOUNDED_BUDGET_NOT_CHESS_TRUTH_OR_FULL_CAUSAL_PATH",
    }

def judgment_packet(explanation_graph: dict[str, Any]) -> dict[str, Any]:
    moments = [judge_moment(m) for m in explanation_graph.get("moments", [])]
    return {
        "schema": "c3x-explain-i10-decision-first-packet-v1",
        "origin_schema": explanation_graph.get("schema"),
        "model_kind": "DETERMINISTIC_TYPED_EVIDENCE_ROUTER_NOT_TRAINED_DECISION_MODEL",
        "judgments": moments,
        "decision_count": sum(m["decision"] != "ABSTAIN" for m in moments),
        "abstention_count": sum(m["decision"] == "ABSTAIN" for m in moments),
        "human_utility": None, "probabilistic_calibration": None,
        "authority_note": "No new C3X causal or chess-value authority is created by this layer.",
    }

def judgment_markdown(packet: dict[str, Any]) -> str:
    lines = ["# C3X I10 — Evidence-Grounded Chess Judgment", "",
             "This is a bounded original-engine ranking, not a calibrated neural decision or objective chess proof.", ""]
    for p in packet.get("judgments", []):
        lines.extend([f"## Ply {p.get('ply')}", "",
                      p.get("explanation") or "", "",
                      f"- Decision: `{p.get('decision')}`",
                      f"- Reason: `{p.get('reason')}`",
                      "- Supporting atoms: " + (", ".join(p.get("evidence_atom_ids", [])) or "none"),
                      "- Local causal certificates: " + (", ".join(p.get("local_causal_certificate_ids", [])) or "none"), ""])
    lines.extend(["## Limit", "", str(packet.get("authority_note", "")), ""])
    return "\n".join(lines)
