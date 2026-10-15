#!/usr/bin/env python3
"""Engine-blind source, legality and historical-overlap audit for I10-P6-R3.

This program imports no engine runner and never reads prior native responses.
It emits a candidate manifest, not a human Git preseal or a P6 result.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import io
import json
import zipfile
from pathlib import Path

import chess
import chess.pgn


SOURCE_URL = "https://lichess.org/api/broadcast/CDVYxqmL.pgn"
PARENT_URL = "https://lichess.org/broadcast/2026-british-chess-championships-championship/CDVYxqmL"
SOURCE_SHA256 = "19aacdb8d778b612643cf809a8e02bc906fbd02682722839a8d85e04848c3ba5"
LICENSE = "CC BY-SA 4.0; Lichess broadcast games"
SALT = "C3X_I10_P6_R3_BRITISH_CHAMPIONSHIP_32_V1"
EXPECTED_BROADCAST_NAME = "2026 British Chess Championships: Championship"
MAIN_EVENT_START = "2026.08.01"
MAIN_EVENT_END = "2026.08.09"
HISTORIC = (
    (11722547447, "C3X025_M5_S_JUNE2026_32_SOURCE_ONLY.json", "71ab8e4c4ddb52d8f63e6e51ea6b4cf991e135246773460c3d6f4800288521be"),
    (11724362365, "C3X025_M6_S_JULY2026_64_SOURCE_ONLY.json", "45d758947b6f224901f2674eaed4dc1dc34f4d5a439ccd62fa408393dd7c2a80"),
)
P5_SOURCE_SHA = "363c4fd6d1bd17ead0890a068c14838296c2393f6de8469633edc0e1bc126a07"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def fen4(board: chess.Board) -> str:
    return " ".join(board.fen(en_passant="fen").split()[:4])


def source_game_sha(headers: chess.pgn.Headers, moves: list[chess.Move]) -> str:
    # The historical M5/M6 selector's game_digest definition.
    return sha(canonical_json_bytes({"headers": dict(headers), "moves_uci": [m.uci() for m in moves]}))


def history_sha(board: chess.Board, prefix: list[chess.Move]) -> str:
    return sha(canonical_json_bytes({"start_fen": board.fen(), "moves_uci": [m.uci() for m in prefix]}))


def valid_mainline(game: chess.pgn.Game) -> tuple[list[chess.Move] | None, str | None]:
    if game.errors:
        return None, "PGN_PARSE_ERROR"
    if game.headers.get("Variant", "Standard") not in ("Standard", "Chess"):
        return None, "NONSTANDARD"
    if game.headers.get("Result") not in {"1-0", "0-1", "1/2-1/2"}:
        return None, "NO_FINAL_RESULT"
    board = game.board()
    if not board.is_valid():
        return None, "INVALID_INITIAL_BOARD"
    moves: list[chess.Move] = []
    for move in game.mainline_moves():
        if move not in board.legal_moves:
            return None, "ILLEGAL_MOVE"
        board.push(move)
        if not board.is_valid():
            return None, "INVALID_REPLAY_BOARD"
        moves.append(move)
    return moves, None


def nested_values(value: object, key: str):
    if isinstance(value, dict):
        if key in value:
            yield value[key]
        for child in value.values():
            yield from nested_values(child, key)
    elif isinstance(value, list):
        for child in value:
            yield from nested_values(child, key)


def load_history(history_dir: Path, artifact_dir: Path) -> tuple[set[str], set[str], list[dict], bool]:
    index_path = history_dir / "history_index.json"
    if not index_path.is_file():
        return set(), set(), [], False
    index = json.loads(index_path.read_bytes())
    receipts = []
    all_fens: set[str] = set()
    all_games: set[str] = set()
    complete = index.get("complete_14_parent_sources") is True
    for row in index["sources"]:
        path = history_dir / row["json_file"]
        if not path.is_file() or sha(path.read_bytes()) != row["json_sha256"]:
            complete = False
            receipts.append({"name": row["name"], "status": "MISSING_OR_SHA_MISMATCH"})
            continue
        doc = json.loads(path.read_bytes())
        fens = {v for v in nested_values(doc, "fen4") if isinstance(v, str) and len(v.split()) == 4}
        games = {v for v in nested_values(doc, "source_game_sha256") if isinstance(v, str) and len(v) == 64}
        all_fens.update(fens)
        all_games.update(games)
        receipts.append({"name": row["name"], "status": "VERIFIED", "sha256": row["json_sha256"],
                         "fen4_count": len(fens), "game_sha_count": len(games)})
    for artifact_id, member, expected in HISTORIC:
        archive_path = artifact_dir / f"historical_artifact_{artifact_id}.zip"
        if not archive_path.is_file():
            complete = False
            receipts.append({"name": f"artifact_{artifact_id}", "status": "MISSING"})
            continue
        with zipfile.ZipFile(archive_path) as archive:
            raw = archive.read(member)
        if sha(raw) != expected:
            complete = False
            receipts.append({"name": f"artifact_{artifact_id}", "status": "SHA_MISMATCH", "actual": sha(raw)})
            continue
        doc = json.loads(raw)
        fens = {v for v in nested_values(doc, "fen4") if isinstance(v, str) and len(v.split()) == 4}
        games = {v for v in nested_values(doc, "source_game_sha256") if isinstance(v, str) and len(v) == 64}
        all_fens.update(fens)
        all_games.update(games)
        receipts.append({"name": f"artifact_{artifact_id}", "status": "VERIFIED", "sha256": sha(raw),
                         "fen4_count": len(fens), "game_sha_count": len(games)})
    return all_fens, all_games, receipts, complete


def load_p5(artifact_dir: Path) -> tuple[set[str], set[str], set[str], dict]:
    path = artifact_dir / "historical_artifact_11789825810.zip"
    if not path.is_file():
        return set(), set(), set(), {"status": "MISSING"}
    with zipfile.ZipFile(path) as archive:
        source = archive.read("source-2026-olympiad-r1-original.pgn")
        if sha(source) != P5_SOURCE_SHA:
            return set(), set(), set(), {"status": "SOURCE_SHA_MISMATCH", "actual": sha(source)}
        names = sorted(n for n in archive.namelist() if n.startswith("game-") and n.endswith(".pgn"))
        if len(names) != 8:
            return set(), set(), set(), {"status": "EXPECTED_EIGHT_GAMES_MISSING", "count": len(names)}
        fens: set[str] = set()
        games: set[str] = set()
        histories: set[str] = set()
        for name in names:
            game = chess.pgn.read_game(io.StringIO(archive.read(name).decode("utf-8")))
            if game is None or game.errors:
                return set(), set(), set(), {"status": "HISTORIC_GAME_PARSE_ERROR", "member": name}
            moves = list(game.mainline_moves())
            board = game.board()
            games.add(sha(canonical_json_bytes({"start_fen": board.fen(), "moves_uci": [m.uci() for m in moves]})))
            for i, move in enumerate(moves):
                fens.add(fen4(board))
                histories.add(history_sha(game.board(), moves[:i]))
                board.push(move)
        return fens, games, histories, {"status": "VERIFIED", "source_sha256": sha(source),
                                         "selected_games": len(names), "all_prefix_fen4_count": len(fens)}


def scan_source(path: Path, historical_fens: set[str], historical_games: set[str],
                p5_fens: set[str], p5_games: set[str], p5_histories: set[str]) -> tuple[dict, list[dict]]:
    raw = path.read_bytes()
    if sha(raw) != SOURCE_SHA256:
        raise ValueError("OFFICIAL_SOURCE_SHA_MISMATCH")
    inventories = collections.Counter()
    exclusions = collections.Counter()
    event_tags = collections.Counter()
    broadcast_names = collections.Counter()
    dates = collections.Counter()
    round_labels = collections.Counter()
    exact_games_seen: set[str] = set()
    uci_games_seen: set[str] = set()
    sicilian = chess.Board()
    for uci in "e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b1c3".split():
        sicilian.push_uci(uci)
    development_fens = {fen4(chess.Board()), fen4(sicilian)}
    candidates = []
    reader = io.StringIO(raw.decode("utf-8"))
    while (game := chess.pgn.read_game(reader)) is not None:
        inventories["source_games"] += 1
        headers = game.headers
        event_tags[headers.get("Event", "")] += 1
        broadcast_names[headers.get("BroadcastName", "")] += 1
        dates[headers.get("Date", "")] += 1
        round_labels[headers.get("Round", "").split(".")[0]] += 1
        moves, problem = valid_mainline(game)
        if problem:
            exclusions[problem] += 1
            continue
        inventories["complete_legal_games"] += 1
        if len(moves) >= 70:
            inventories["complete_legal_70ply_games"] += 1
        if headers.get("BroadcastName") != EXPECTED_BROADCAST_NAME:
            exclusions["OTHER_BROADCAST_SECTION"] += 1
            continue
        date = headers.get("Date", "")
        if not MAIN_EVENT_START <= date <= MAIN_EVENT_END:
            exclusions["OUTSIDE_MAIN_EVENT_DATES"] += 1
            continue
        round_number = headers.get("Round", "").split(".")[0]
        if round_number not in {str(i) for i in range(1, 10)}:
            exclusions["NOT_MAIN_ROUND_1_TO_9"] += 1
            continue
        inventories["scoped_complete_legal_games"] += 1
        fingerprint = source_game_sha(headers, moves)
        initial = game.board()
        uci_hash = sha(canonical_json_bytes({"start_fen": initial.fen(), "moves_uci": [m.uci() for m in moves]}))
        if fingerprint in exact_games_seen or uci_hash in uci_games_seen:
            exclusions["INTRA_SOURCE_DUPLICATE_GAME"] += 1
            continue
        exact_games_seen.add(fingerprint)
        uci_games_seen.add(uci_hash)
        if len(moves) < 70:
            exclusions["FEWER_THAN_70_PLIES"] += 1
            continue
        inventories["scoped_complete_legal_70ply_games"] += 1
        if fingerprint in historical_games or uci_hash in p5_games:
            exclusions["HISTORICAL_COMPLETE_GAME_DUPLICATE"] += 1
            continue
        at = 30 + (int(fingerprint[:8], 16) % 15)
        board = game.board()
        for move in moves[:at]:
            board.push(move)
        if board.is_game_over() or board.legal_moves.count() < 3:
            exclusions["ROOT_NO_LONGER_NONTERMINAL_OR_BRANCHING"] += 1
            continue
        root_fen4 = fen4(board)
        prefix_hash = history_sha(initial, moves[:at])
        if root_fen4 in historical_fens or root_fen4 in p5_fens or root_fen4 in development_fens:
            exclusions["HISTORICAL_ROOT_FEN4_COLLISION"] += 1
            continue
        if prefix_hash in p5_histories:
            exclusions["HISTORICAL_ROOT_HISTORY_COLLISION"] += 1
            continue
        rank = sha((SALT + "|" + fingerprint).encode("ascii"))
        candidates.append({"rank_sha256": rank, "source_game_sha256": fingerprint,
                           "whole_uci_game_sha256": uci_hash,
                           "source_ordinal": inventories["source_games"],
                           "source_round": headers.get("Round"), "source_date": date,
                           "selected_ply_zero_based": at, "full_fen": board.fen(en_passant="fen"),
                           "fen4": root_fen4, "root_history_sha256": prefix_hash,
                           "root_history_uci": [m.uci() for m in moves[:at]],
                           "played_next_uci": moves[at].uci(),
                           "root_legal_move_count": board.legal_moves.count(),
                           "no_native_response_observed": True})
    candidates.sort(key=lambda row: (row["rank_sha256"], row["source_game_sha256"]))
    chosen = []
    selected_fens: set[str] = set()
    selected_histories: set[str] = set()
    for candidate in candidates:
        if candidate["fen4"] in selected_fens or candidate["root_history_sha256"] in selected_histories:
            exclusions["WITHIN_32_ROOT_COLLISION"] += 1
            continue
        selected_fens.add(candidate["fen4"])
        selected_histories.add(candidate["root_history_sha256"])
        chosen.append(candidate)
        if len(chosen) == 32:
            break
    audit = {"schema": "c3x-i10-p6-r3-engine-blind-source-audit-v1", "source_url": SOURCE_URL,
             "parent_url": PARENT_URL, "raw_source_sha256": sha(raw), "raw_source_bytes": len(raw),
             "license": LICENSE, "scope": "Main rounds 1-9, Date 2026.08.01-2026.08.09, exact BroadcastName; broadcast-visible complete games only",
             "selection_rule": "For legal result-bearing standard games with >=70 ply, take root after 30 + int(source_game_sha[:8],16)%15 plies; exclude historical and within-cohort FEN4/history collisions; rank by SHA256(salt|source_game_sha); first 32",
             "salt": SALT, "inventory": dict(inventories), "exclusions": dict(exclusions),
             "event_tags": dict(event_tags), "broadcast_names": dict(broadcast_names),
             "dates": dict(dates), "round_labels": dict(round_labels),
             "selected_count": len(chosen), "source_only": True,
             "status": "CANDIDATE_NOT_HUMAN_PRESEALED"}
    return audit, chosen


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pgn", required=True, type=Path)
    parser.add_argument("--history", required=True, type=Path)
    parser.add_argument("--artifacts", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    prior_fens, prior_games, prior_receipts, prior_complete = load_history(args.history, args.artifacts)
    p5_fens, p5_games, p5_histories, p5_receipt = load_p5(args.artifacts)
    audit, chosen = scan_source(args.pgn, prior_fens, prior_games, p5_fens, p5_games, p5_histories)
    audit["historical_source_receipts"] = prior_receipts
    audit["historical_inventory_complete"] = prior_complete and p5_receipt.get("status") == "VERIFIED"
    audit["historical_fen4_count"] = len(prior_fens)
    audit["historical_source_game_sha_count"] = len(prior_games)
    audit["p5_receipt"] = p5_receipt
    audit["p6_development_fen_exclusion"] = "STARTPOS_AND_EXPOSED_SICILIAN9_INCLUDED_IN_COLLISION_FILTER"
    if len(chosen) != 32 or not audit["historical_inventory_complete"]:
        audit["status"] = "SOURCE_AUDIT_HOLD"
    (args.out / "source_audit.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    manifest = {"schema": "c3x-i10-p6-r3-32-candidate-manifest-v1", "status": audit["status"],
                "source_sha256": SOURCE_SHA256, "source_parent_id": "CDVYxqmL",
                "selection_salt": SALT, "root_positions": chosen,
                "treatment_outcomes_opened": False, "human_git_preseal": False}
    (args.out / "candidate_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"source_games": audit["inventory"]["source_games"],
                      "eligible": audit["inventory"].get("scoped_complete_legal_70ply_games", 0),
                      "selected": len(chosen), "historical_complete": audit["historical_inventory_complete"],
                      "status": audit["status"], "exclusions": audit["exclusions"]}, sort_keys=True))


if __name__ == "__main__":
    main()
