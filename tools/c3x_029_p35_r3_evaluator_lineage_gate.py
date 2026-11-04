#!/usr/bin/env python3
"""P35/R3: inspect evaluator-arm identifiability from native UCI banners.

This is a pre-execution version/arm safety gate. It makes no chess strength,
NNUE circuit, or actual search mediation measurement.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


class VersionGateError(ValueError):
    pass


@dataclass(frozen=True)
class UCICapability:
    engine_name: str
    is_stockfish16: bool
    nnue_toggle_available: bool
    option_names: tuple[str, ...]


def parse_uci_banner(raw: str) -> UCICapability:
    if not isinstance(raw, str) or not raw.strip():
        raise VersionGateError("EMPTY_UCI_BANNER")
    names = [line[len("id name "):].strip() for line in raw.splitlines()
             if line.startswith("id name ")]
    if len(names) != 1 or not names[0] or "uciok" not in raw.splitlines():
        raise VersionGateError("INCOMPLETE_UCI_HANDSHAKE")
    opts = []
    for line in raw.splitlines():
        m = re.match(r"^option name (.+?) type ", line)
        if m:
            opts.append(m.group(1).strip())
    is_sf16 = bool(re.fullmatch(r"Stockfish 16(?:\s+.*)?", names[0])) and not bool(
        re.match(r"^Stockfish 16(?:\.|\d)", names[0])
    )
    return UCICapability(names[0], is_sf16, "Use NNUE" in opts, tuple(opts))


def gate_classical_vs_nnue(raw: str, *, requested_arm: str,
                           require_pinned_stockfish16: bool = True) -> dict:
    if requested_arm not in ("classical", "nnue"):
        raise VersionGateError("INVALID_ARM")
    cap = parse_uci_banner(raw)
    if require_pinned_stockfish16 and not cap.is_stockfish16:
        raise VersionGateError("NOT_STOCKFISH_16_SOURCE_EXPERIMENT")
    if not cap.nnue_toggle_available:
        raise VersionGateError("NO_USE_NNUE_OPTION_CANNOT_COMPARE_CLASSICAL")
    return {
        "status": "UCI_CAPABILITY_GATE_PASS_NOT_SOURCE_SHA_PASS",
        "engine_name": cap.engine_name,
        "requested_arm": requested_arm,
        "uci_command": f"setoption name Use NNUE value {'false' if requested_arm == 'classical' else 'true'}",
        "requires": ["source_sha256", "network_sha256", "engine_binary_sha256",
                     "legal_history_sha256", "actual_eval_route_provenance"],
        "claim_ceiling": "UCI option available; actual route, strength and mechanism unverified",
    }


def compare_version_experiments(conditions: list[dict]) -> dict:
    """A changed source version is never a controlled evaluator intervention."""
    if len(conditions) != 2:
        raise VersionGateError("REQUIRES_PAIRED_ARMS")
    mandatory = ("source_sha256", "network_sha256", "search_code_sha256",
                 "engine_binary_sha256", "position_history_sha256",
                 "nodes_requested", "threads", "hash_mb")
    if any(any(k not in arm for k in mandatory) for arm in conditions):
        return {"status": "HOLD_INCOMPLETE_PROVENANCE"}
    left, right = conditions
    different = tuple(k for k in mandatory if left[k] != right[k])
    if different:
        return {"status": "VERSION_OR_RUNTIME_CONFOUNDED", "changed_fields": different,
                "effect_identified": False}
    if left.get("evaluator_arm") == right.get("evaluator_arm"):
        return {"status": "SAME_EVALUATOR_ARM", "effect_identified": False}
    return {"status": "COMPARABLE_EVALUATOR_REGIMES_NOT_CAUSAL_MEDIATION",
            "effect_identified": False,
            "note": "Shared source/net and node budget do not identify leaf-mediated root effects"}
