#!/usr/bin/env python3
"""P36/R1 deterministic engine-blind PGN source freeze (no engine calls).

Precommitted contract: official July 2026 Lichess broadcast zstd archive;
first 1000 eligible game records, choose eight smallest SHA-256 case identities.
This code MUST run before any engine-score or explanation candidate screening.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

import chess
import chess.pgn
import zstandard

OFFICIAL_SOURCE_SHA256 = "e93b3ded55d463ff6839c06b42b740dc1d725145f7f4da460172a3cf84041a8b"
SOURCE_URL = "https://database.lichess.org/broadcast/lichess_db_broadcast_2026-07.pgn.zst"
ELIGIBLE_SCAN_COUNT = 1000
SELECT_COUNT = 8
FROZEN_PLY = 30
REQUIRED_HEADERS = ("Event", "Date", "White", "Black", "Result")
ALLOWED_RESULTS = {"1-0", "0-1", "1/2-1/2"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_archive(path: Path, expected_sha256: str = OFFICIAL_SOURCE_SHA256) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    actual = digest.hexdigest()
    if actual != expected_sha256:
        raise ValueError("HOLD_OFFICIAL_SOURCE_SHA256_MISMATCH:" + actual)
    return actual


def candidate_from_game(game: chess.pgn.Game, index: int) -> tuple[dict | None, str]:
    if game.errors:
        return None, "PGN_ERROR"
    if any(not game.headers.get(k) or game.headers[k] == "?" for k in REQUIRED_HEADERS):
        return None, "MISSING_HEADER"
    if game.headers["Result"] not in ALLOWED_RESULTS:
        return None, "UNFINISHED_RESULT"
    if game.headers.get("Variant", "Standard") not in ("Standard", "Chess", ""):
        return None, "NONSTANDARD_VARIANT"
    if game.headers.get("SetUp", "0") != "0" or "FEN" in game.headers:
        return None, "NONINITIAL_SETUP"
    node = game
    board = game.board()
    uci_moves: list[str] = []
    frozen_fen = None
    while node.variations:
        node = node.variation(0)
        move = node.move
        if move not in board.legal_moves:
            return None, "ILLEGAL_MAINLINE"
        uci_moves.append(move.uci())
        board.push(move)
        if len(uci_moves) == FROZEN_PLY:
            frozen_fen = board.fen()
            if board.is_game_over(claim_draw=False):
                return None, "TERMINAL_FROZEN_BOARD"
    if len(uci_moves) < 60:
        return None, "TOO_SHORT"
    if frozen_fen is None:
        return None, "MISSING_FROZEN_PLY"
    full_move_history = " ".join(uci_moves)
    game_sha = sha(full_move_history.encode("ascii"))
    tags = {k: game.headers.get(k, "") for k in
            ("Event", "Site", "Date", "Round", "White", "Black", "Result")}
    identity_input = json.dumps({"tags": tags, "game_uci_sha256": game_sha},
                                sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    rank_sha = sha(identity_input.encode("utf-8"))
    return {
        "pgn_index": index,
        "case_id": rank_sha[:16],
        "selection_sha256": rank_sha,
        "full_game_uci_sha256": game_sha,
        "full_game_uci": uci_moves,
        "tags": tags,
        "fixed_ply": FROZEN_PLY,
        "fixed_board_fen": frozen_fen,
        "total_plies": len(uci_moves),
    }, "ELIGIBLE"


def freeze_source(source: Path, *, max_eligible: int = ELIGIBLE_SCAN_COUNT,
                  select_n: int = SELECT_COUNT, expected_sha256: str = OFFICIAL_SOURCE_SHA256) -> dict:
    source_sha = verify_archive(source, expected_sha256)
    counts = Counter()
    candidates = []
    history_hashes = set()
    with source.open("rb") as f:
        with zstandard.ZstdDecompressor().stream_reader(f) as reader:
            with io.TextIOWrapper(reader, encoding="utf-8", errors="replace") as text:
                game_index = 0
                while len(candidates) < max_eligible:
                    game = chess.pgn.read_game(text)
                    if game is None:
                        break
                    game_index += 1
                    row, reason = candidate_from_game(game, game_index)
                    counts[reason] += 1
                    if row is None:
                        continue
                    if row["full_game_uci_sha256"] in history_hashes:
                        counts["DUPLICATE_HISTORY"] += 1
                        counts["ELIGIBLE"] -= 1
                        continue
                    history_hashes.add(row["full_game_uci_sha256"])
                    candidates.append(row)
    if len(candidates) != max_eligible:
        raise ValueError(f"HOLD_SOURCE_ELIGIBLE_INSUFFICIENT_{len(candidates)}")
    candidates.sort(key=lambda x: (x["selection_sha256"], x["pgn_index"]))
    selected = candidates[:select_n]
    if len(selected) != select_n:
        raise ValueError("HOLD_COHORT_SIZE")
    return {
        "status": "SOURCE_FROZEN_ENGINE_BLIND_PENDING_HISTORICAL_OVERLAP_AUDIT",
        "official_source_url": SOURCE_URL,
        "official_source_sha256": source_sha,
        "selection_contract": {
            "eligible_count": max_eligible, "selected_count": select_n,
            "fixed_ply": FROZEN_PLY, "ranking": "SHA256(tags+whole-game-history)",
            "engine_access_for_selection": False,
        },
        "pgn_records_scanned": sum(v for k, v in counts.items()
                                   if k != "DUPLICATE_HISTORY"),
        "counts_by_reason": dict(sorted(counts.items())),
        "case_selection": selected,
        "game_overlap_old_0_28_64": "UNVERIFIED",
        "event_family_independence": "UNVERIFIED",
        "scientific_claim_ceiling":
            "Deterministic external original-source freeze, not independent heldout admission "
            "and not a chess-value or explanation result.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-zst", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    manifest = freeze_source(args.source_zst)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print("P36_ENGINE_BLIND_SOURCE_FREEZE_ONLY",
          manifest["official_source_sha256"],
          len(manifest["case_selection"]),
          "NO_ENGINE_CALLS", flush=True)


if __name__ == "__main__":
    main()
