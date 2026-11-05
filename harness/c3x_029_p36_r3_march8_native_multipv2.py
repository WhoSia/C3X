#!/usr/bin/env python3
"""P36/R3 eight-game native SF16 MultiPV screen after engine-blind source freeze.

This is candidate/margin screening only; no explanation superiority, heldout
admission or actual leaf-to-root causal mediation is asserted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import chess
import chess.engine

MARCH_SOURCE_SHA256 = "1a5ad83fc9f440dcdadde17b11cc81a953f4895aaf8b8588470b3078209dc7fc"
ROOT_NODES = 24000
FROZEN_PLY = 30
EXPECTED_CASES = (
    "00090c4e53df5b2d", "00470a57672750d1",
    "00846ac66ee43492", "00f04cd20636fdc2",
    "01662a4d51803d33", "01af9df4f5e8e39f",
    "01f4ddb70d4011c6", "02154be9fa2cf21d",
)


def fail_unless(condition: bool, label: str) -> None:
    if not condition:
        raise ValueError("P36_R3_HOLD_" + label)


def validate_case(case: dict) -> chess.Board:
    fail_unless(case["fixed_ply"] == FROZEN_PLY, "PLY_MISMATCH")
    board = chess.Board()
    for move_uci in case["full_game_uci"][:FROZEN_PLY]:
        move = chess.Move.from_uci(move_uci)
        fail_unless(move in board.legal_moves, "ILLEGAL_SOURCE_HISTORY")
        board.push(move)
    fail_unless(board.fen() == case["fixed_board_fen"], "FROZEN_FEN_MISMATCH")
    fail_unless(not board.is_game_over(claim_draw=False), "TERMINAL_ROOT")
    return board


def stratum(margin: int | None) -> str:
    if margin is None:
        return "mate_or_unscored"
    if margin < 0:
        raise ValueError("P36_R3_HOLD_NEGATIVE_MULTIPV_MARGIN")
    if margin < 20:
        return "near"
    if margin < 100:
        return "intermediate"
    return "wide"


def run_case(engine_path: str, case: dict) -> dict:
    board = validate_case(case)
    legal_count = board.legal_moves.count()
    fail_unless(legal_count >= 2, "INSUFFICIENT_LEGAL_CANDIDATES")
    with chess.engine.SimpleEngine.popen_uci(engine_path, timeout=90) as engine:
        fail_unless("Stockfish 16" in engine.id.get("name", ""), "ENGINE_ID")
        fail_unless("Use NNUE" in engine.options, "NNUE_OPTION")
        engine.configure({"Threads": 1, "Hash": 16, "Use NNUE": True})
        raw_infos = engine.analyse(
            board, chess.engine.Limit(nodes=ROOT_NODES),
            multipv=2, info=chess.engine.INFO_ALL
        )
    fail_unless(isinstance(raw_infos, list) and len(raw_infos) == 2, "TWO_PV_RESULTS")
    rows = []
    for info in raw_infos:
        pv = info.get("pv")
        fail_unless(pv and pv[0] in board.legal_moves, "MISSING_OR_ILLEGAL_PV")
        side_score = info["score"].pov(board.turn)
        mate = side_score.mate()
        cp = None if mate is not None else side_score.score()
        fail_unless(cp is not None or mate is not None, "SCORE_MISSING")
        child = board.copy(stack=True)
        child.push(pv[0])
        reply = pv[1].uci() if len(pv) > 1 else None
        if len(pv) > 1:
            fail_unless(pv[1] in child.legal_moves, "FIRST_REPLY_ILLEGAL")
        rows.append({
            "root_uci": pv[0].uci(),
            "score_cp_side_to_move": cp,
            "score_mate_side_to_move": mate,
            "score_lowerbound": bool(info.get("lowerbound", False)),
            "score_upperbound": bool(info.get("upperbound", False)),
            "pv_uci": [m.uci() for m in pv],
            "pv_first_opponent_reply": reply,
            "legal_opponent_reply_count": child.legal_moves.count(),
            "depth": info.get("depth"),
            "seldepth": info.get("seldepth"),
            "actual_nodes_shared_analysis": info.get("nodes"),
        })
    fail_unless(len({r["root_uci"] for r in rows}) == 2, "DUPLICATE_MULTIPV_ROOT")
    if all(row["score_cp_side_to_move"] is not None for row in rows):
        margin = rows[0]["score_cp_side_to_move"] - rows[1]["score_cp_side_to_move"]
        fail_unless(margin >= 0, "PV_SCORE_ORDER")
    else:
        margin = None
    return {
        "case_id": case["case_id"],
        "pgn_index": case["pgn_index"],
        "tags": case["tags"],
        "original_game_uci_sha256": case["full_game_uci_sha256"],
        "fixed_ply": case["fixed_ply"],
        "position_fen": case["fixed_board_fen"],
        "original_prefix_uci": case["full_game_uci"][:FROZEN_PLY],
        "legal_root_count": legal_count,
        "candidate_margin_cp": margin,
        "candidate_margin_stratum": stratum(margin),
        "two_candidate_search": rows,
        "status": "ORIGINAL_SF16_MULTIPV2_SCREEN_ONLY",
    }


def court(manifest_path: Path, engine_path: str, source_path: Path) -> dict:
    src_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    fail_unless(src_hash == MARCH_SOURCE_SHA256, "MARCH_ORIGINAL_SOURCE_SHA")
    raw_manifest = manifest_path.read_bytes()
    manifest = json.loads(raw_manifest)
    fail_unless(manifest["official_source_sha256"] == MARCH_SOURCE_SHA256,
                "MANIFEST_SOURCE_SHA")
    fail_unless(manifest["status"] == "SOURCE_FROZEN_ENGINE_BLIND_PENDING_HISTORICAL_OVERLAP_AUDIT",
                "MANIFEST_PREOUTCOME_STATUS")
    cases = manifest["case_selection"]
    fail_unless(tuple(c["case_id"] for c in cases) == EXPECTED_CASES, "CASE_IDS_NOT_PRESEALED")
    fail_unless(len({c["full_game_uci_sha256"] for c in cases}) == 8, "DUPLICATE_GAMES")
    observations = []
    for case in cases:
        result = run_case(engine_path, case)
        observations.append(result)
        print("P36_R3_NATIVE_CASE", case["case_id"], result["candidate_margin_stratum"],
              result["candidate_margin_cp"], flush=True)
    return {
        "status": "P36_R3_MARCH8_NATIVE_MULTIPV_SCREEN_DONE_NOT_EXPLANATION_ADVANTAGE",
        "source_sha256": MARCH_SOURCE_SHA256,
        "manifest_sha256": hashlib.sha256(raw_manifest).hexdigest(),
        "pinned_engine_git_sha": "68e1e9b3811e16cad014b590d7443b9063b3eb52",
        "requested_nodes_per_board": ROOT_NODES,
        "boards": len(observations),
        "stratum_counts": dict(sorted(Counter(r["candidate_margin_stratum"] for r in observations).items())),
        "source_custody_was_preexisting": True,
        "old_0_28_64_overlap": "UNVERIFIED",
        "four_cases_share_american_cup_blitz_event": True,
        "claim_ceiling": "Native finite-node candidate screening on previously held raw source. No independent heldout, real reply outcome or explanation superiority.",
        "observations": observations,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--engine", required=True)
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    result = court(args.manifest, args.engine, args.source)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print("P36_R3_NATIVE_SOURCE_MULTIPV2_SCREEN_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
