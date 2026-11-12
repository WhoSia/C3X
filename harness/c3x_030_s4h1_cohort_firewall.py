#!/usr/bin/env python3
"""C3X 0.30 S4-H1: audit the pre-outcome S4-H0 legal-history cohort.

Identity and chess-legality audit only. Never computes an engine outcome,
a treatment effect, or a paper-superiority verdict. Requires python-chess.
Do not regenerate or reselect the manifest after observing outcomes.
"""
import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
import chess

SCHEMA = "c3x030-f2-blind-holdout-manifest-v1"
FORBIDDEN = {
    "label", "outcome", "score", "bestmove", "expected_bestmove",
    "judge_label", "sarfa_positive", "independent_response_verified",
    "native_event_to_root_certified", "treatment", "effect", "reward",
}
ALLOWED_ROW = {"case_id", "game_id", "fen", "history_uci"}
EXPECTED = {"development": 4, "holdout": 8}
PLIES = (8, 10)

def audit(manifest):
    if manifest.get("schema") != SCHEMA:
        raise ValueError("S4H1_SCHEMA")
    if manifest.get("random_population_sample") is not False or (
        manifest.get("evaluation_positions_from_same_game_are_correlated") is not True
    ) or manifest.get("no_evaluation_or_treatment_outcomes_in_manifest") is not True:
        raise ValueError("S4H1_SAMPLING_SCOPE")
    groups = {}
    all_fens = set()
    for split, key in (("development", "development_entries"), ("holdout", "entries")):
        rows = manifest.get(key)
        if not isinstance(rows, list) or len(rows) != 2 * EXPECTED[split]:
            raise ValueError("S4H1_SPLIT_CASE_COUNT")
        grouped = defaultdict(dict)
        for row in rows:
            if not isinstance(row, dict) or set(row) != ALLOWED_ROW or set(row) & FORBIDDEN:
                raise ValueError("S4H1_ROW_FIELDS_OR_OUTCOME_LEAK")
            cid, gid, history, fen = (row[k] for k in ("case_id", "game_id", "history_uci", "fen"))
            if not isinstance(gid, str) or not gid or not isinstance(cid, str):
                raise ValueError("S4H1_CASE_ID")
            match = re.fullmatch(re.escape(gid) + r"_ply(8|10)", cid)
            if match is None:
                raise ValueError("S4H1_CASE_ID_HISTORY")
            ply = int(match.group(1))
            if (not isinstance(history, list) or len(history) != ply or
                not all(isinstance(x, str) for x in history)):
                raise ValueError("S4H1_HISTORY_LENGTH")
            board = chess.Board()
            try:
                for uci in history:
                    move = chess.Move.from_uci(uci)
                    if move not in board.legal_moves:
                        raise ValueError("illegal move")
                    board.push(move)
            except (ValueError, chess.InvalidMoveError) as exc:
                raise ValueError("S4H1_ILLEGAL_HISTORY") from exc
            if not board.is_valid() or board.fen() != fen:
                raise ValueError("S4H1_FEN_RECONSTRUCTION")
            if fen in all_fens:
                raise ValueError("S4H1_DUPLICATE_FEN_ACROSS_GAMES")
            all_fens.add(fen)
            if ply in grouped[gid]:
                raise ValueError("S4H1_DUPLICATE_SNAPSHOT")
            grouped[gid][ply] = history
        if len(grouped) != EXPECTED[split]:
            raise ValueError("S4H1_GAME_COUNT")
        for gid, snapshots in grouped.items():
            if set(snapshots) != set(PLIES) or snapshots[10][:8] != snapshots[8]:
                raise ValueError("S4H1_PREFIX_OR_MISSING_SNAPSHOT")
        groups[split] = grouped
    if set(groups["development"]) & set(groups["holdout"]):
        raise ValueError("S4H1_CROSS_SPLIT_GAME_LEAK")
    return {
        "schema": "c3x030-s4h1-cohort-firewall-audit-v1",
        "development_games": len(groups["development"]),
        "holdout_games": len(groups["holdout"]),
        "development_positions": 2 * len(groups["development"]),
        "holdout_positions": 2 * len(groups["holdout"]),
        "cross_split_game_overlap": 0,
        "legal_history_reconstruction": True,
        "within_game_fens_correlated": True,
        "researcher_authored_not_population_random": True,
        "engine_searches_performed": 0,
        "causal_effect_or_superiority_tested": False,
        "verdict": "PASS_IDENTITY_FIREWALL_ONLY",
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    raw = Path(a.manifest).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if not re.fullmatch(r"[0-9a-f]{64}", a.expected_sha256) or digest != a.expected_sha256:
        raise ValueError("S4H1_FROZEN_MANIFEST_SHA_MISMATCH")
    result = audit(json.loads(raw))
    result["manifest_raw_sha256"] = digest
    dest = Path(a.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("S4H1_IDENTITY_FIREWALL", result["verdict"], digest)

if __name__ == "__main__":
    main()
