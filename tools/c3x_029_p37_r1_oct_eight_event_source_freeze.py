#!/usr/bin/env python3
"""P37/R1 — eight-family, exact-URL, engine-blind chess source admission.

No chess engines, evaluations, candidate scores, forecasts, or posthoc replacements.
Each Lichess broadcast round PGN is a separately precommitted event source.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
from pathlib import Path

import chess
import chess.pgn

SOURCES = (
    ("sahel-open-a", "MR4eFoUH", "Sahel International Chess Festival", "2026-10-25"),
    ("kazchess-masters", "tZQNFMoC", "KazChess Masters Almaty", "2026-10-26"),
    ("chinese-league", "ZvY3jr6Q", "Chinese Chess League Division A", "2026-10-27"),
    ("clutch-champions", "LVWRdrsl", "Clutch Chess Champions Showdown", "2026-10-27"),
    ("freiburger-open", "lEQStSIp", "Freiburger Bogoljubow Open", "2026-10-28"),
    ("magdeburg-open", "TGKbOvjn", "Magdeburg Open 2026", "2026-10-29"),
    ("cerrado-garcia-palacios", "3veI3mSx", "Cerrado Internacional Garcia-Palacios", "2026-10-29"),
    ("greg-hjorth-open", "GcyAs4TL", "Greg Hjorth Open", "2026-10-30"),
)
PLY = 30
MIN_FULL_GAME_PLIES = 60
MIN_DATE = "2026-10-25"
MAX_DATE = "2026-11-05"
RESULTS = {"1-0", "0-1", "1/2-1/2"}
HEADERS = ("Event", "Date", "White", "Black", "Result")
RANK_HEADERS = ("Event", "Site", "Date", "Round", "White", "Black", "Result")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(ok: bool, code: str) -> None:
    if not ok:
        raise ValueError("P37_SOURCE_HOLD_" + code)


def parse_game(game: chess.pgn.Game, source_id: str, index: int) -> tuple[dict | None, str]:
    if game.errors:
        return None, "PGN_PARSE_ERROR"
    headers = game.headers
    if any(not headers.get(h) or headers[h] in ("?", "*") for h in HEADERS):
        return None, "MISSING_HEADER"
    if headers["Result"] not in RESULTS:
        return None, "UNFINISHED"
    date = headers["Date"].replace(".", "-")
    if not re.fullmatch(r"20\d\d-\d\d-\d\d", date):
        return None, "INCOMPLETE_DATE"
    if not MIN_DATE <= date <= MAX_DATE:
        return None, "WRONG_DATE"
    if headers.get("Variant", "Standard") not in ("Standard", "Chess", ""):
        return None, "VARIANT"
    if headers.get("SetUp", "0") != "0" or "FEN" in headers:
        return None, "NONSTANDARD_START"
    board = chess.Board()
    moves: list[str] = []
    frozen = None
    node = game
    while node.variations:
        move = node.variation(0).move
        if move not in board.legal_moves:
            return None, "ILLEGAL_MAINLINE"
        moves.append(move.uci())
        board.push(move)
        node = node.variation(0)
        if len(moves) == PLY:
            if board.is_game_over(claim_draw=False):
                return None, "TERMINAL_FIXED"
            frozen = board.fen(en_passant="fen")
    if len(moves) < MIN_FULL_GAME_PLIES or frozen is None:
        return None, "SHORT_GAME"
    full_sha = sha256(" ".join(moves).encode("ascii"))
    tags = {key: headers.get(key, "") for key in RANK_HEADERS}
    ranking_body = json.dumps({"tags": tags, "history_sha256": full_sha},
                              ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    rank_sha = sha256(ranking_body.encode("utf-8"))
    return {
        "case_id": rank_sha[:16],
        "source_id": source_id,
        "pgn_ordinal": index,
        "selection_sha256": rank_sha,
        "full_game_uci_sha256": full_sha,
        "full_game_uci": moves,
        "headers": tags,
        "fixed_ply": PLY,
        "frozen_fen": frozen,
        "total_plies": len(moves),
    }, "ELIGIBLE"


def freeze_round(source_id: str, round_id: str, label: str,
                 expected_start: str, raw: bytes) -> dict:
    require(len(raw) >= 70 and b"[Event " in raw[:10000], "NON_PGN_" + source_id)
    try:
        decoded = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as err:
        raise ValueError("P37_SOURCE_HOLD_UTF8_" + source_id) from err
    candidates = []
    counts = {}
    stream = io.StringIO(decoded)
    n = 0
    while True:
        game = chess.pgn.read_game(stream)
        if game is None:
            break
        n += 1
        row, status = parse_game(game, source_id, n)
        counts[status] = counts.get(status, 0) + 1
        if row is not None:
            candidates.append(row)
    require(n > 0, "NO_PGN_GAMES_" + source_id)
    require(len(candidates) > 0, "NO_ELIGIBLE_" + source_id)
    candidates.sort(key=lambda row: (row["selection_sha256"], row["pgn_ordinal"]))
    chosen = candidates[0]
    require(chosen["headers"]["Event"], "NO_EVENT_" + source_id)
    return {
        "source_id": source_id, "round_id": round_id, "event_family": label,
        "design_start_date": expected_start,
        "original_url": f"https://lichess.org/api/broadcast/round/{round_id}.pgn",
        "raw_bytes": len(raw), "raw_sha256": sha256(raw),
        "total_games": n, "eligible_games": len(candidates),
        "counts": counts, "selected": chosen,
        "upstream_sha256_published": False,
    }


def freeze(directory: Path) -> dict:
    sources = []
    for source_id, round_id, label, expected in SOURCES:
        filename = directory / f"{round_id}.pgn"
        require(filename.exists(), "SOURCE_MISSING_" + round_id)
        raw = filename.read_bytes()
        sources.append(freeze_round(source_id, round_id, label, expected, raw))
    require(len({row["selected"]["full_game_uci_sha256"] for row in sources}) == 8,
            "DUPLICATE_FULL_GAME_BETWEEN_EVENTS")
    require(len({row["round_id"] for row in sources}) == 8, "DUPLICATE_ROUND")
    require(len({row["event_family"] for row in sources}) == 8, "DUPLICATE_EVENT_LABEL")
    return {
        "status": "EIGHT_EVENT_SOURCE_ONLY_FROZEN_HISTORY_LEDGER_GATE_PENDING",
        "selection_precommit": "docs/C3X_029_P37_R1_EIGHT_LATE_OCT_EVENT_SOURCE_PRECOMMIT_20261105.md",
        "license": "CC BY-SA 4.0 (Lichess broadcast games)",
        "selection_used_engine": False,
        "source_count": 8,
        "event_family_count": 8,
        "selected_game_count": 8,
        "fixed_ply": PLY,
        "source_transport_has_two_byte_identical_fetches": True,
        "upstream_published_checksum_available": False,
        "historical_all_game_exclusion": "PENDING",
        "historical_all_event_exclusion": "PENDING",
        "scientific_claim_ceiling": "Event-stratified source-only freeze; not yet fully admitted independent heldout, no model forecast.",
        "sources": sources,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--round-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = freeze(args.round_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print("P37_SOURCE_FROZEN_NO_ENGINE_OR_FORECAST", result["event_family_count"],
          result["selected_game_count"], flush=True)


if __name__ == "__main__":
    main()
