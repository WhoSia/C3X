#!/usr/bin/env python3
"""C3X 0.11 source-disjoint FEN audit: P19 canonical worlds, outcomes sealed.

Requires python-chess. Audit-only: no authority to declare historical coverage
complete, scientific source preseal, routed chain support, or activation PASS.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import chess
import chess.pgn
from g10_p19_source_census import canonical_fen, historical_hashes

def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def read_source(sid: str, path: Path, lo: int, hi: int):
    hashes = set()
    stats = Counter()
    sample = {}
    with path.open("r", encoding="utf-8-sig", errors="strict") as handle:
        while True:
            game = chess.pgn.read_game(handle)
            if game is None:
                break
            stats["games"] += 1
            if game.errors:
                raise ValueError(f"ILLEGAL_OR_UNPARSABLE_PGN:{sid}:{stats['games']}:{game.errors[0]}")
            if game.headers.get("Variant","Standard") not in ("Standard", "From Position"):
                raise ValueError(f"NON_STANDARD_VARIANT:{sid}:{stats['games']}")
            board = game.board()
            if board.chess960 or not board.is_valid():
                raise ValueError(f"INVALID_INITIAL_BOARD:{sid}:{stats['games']}")
            for ply, move in enumerate(game.mainline_moves(), start=1):
                if move not in board.legal_moves:
                    raise ValueError(f"ILLEGAL_MOVE:{sid}:{stats['games']}:{ply}")
                board.push(move)
                if ply < lo or ply > hi:
                    continue
                stats["plies_in_window"] += 1
                if not board.is_valid() or board.is_game_over(claim_draw=False):
                    stats["ineligible_terminal_or_invalid"] += 1
                    continue
                fen = canonical_fen(board)
                digest = sha(fen)
                hashes.add(digest)
                sample.setdefault(digest, {"game": stats["games"],"ply":ply,"fen":fen})
    return hashes, dict(stats), sample

def audit(inputs, historical, lo, hi):
    pools, stats, examples = {}, {}, {}
    owners = defaultdict(set)
    for sid, path in inputs.items():
        pools[sid], stats[sid], examples[sid] = read_source(sid, path, lo, hi)
        for digest in pools[sid]:
            owners[digest].add(sid)
    shared = {h for h, ids in owners.items() if len(ids) > 1}
    per_source = {}
    for sid, pool in pools.items():
        collisions = pool & historical
        cross = pool & shared
        survivors = pool - historical - shared
        per_source[sid] = {
            "games_parsed": stats[sid].get("games",0),
            "eligible_unique_worlds_pre_exclusion": len(pool),
            "historical_collision_worlds": len(collisions),
            "cross_source_collision_worlds": len(cross),
            "unique_worlds_remaining": len(survivors),
            "sample_recovered_fens": [examples[sid][h] for h in sorted(survivors)[:3]],
        }
    return {"schema": "c3x-0.11-p19-canonical-fen-collision-audit-v1",
            "authority": "AUDIT_ONLY_NOT_SOURCE_PRESEAL",
            "legacy_canonical_fen_rule": "board.fen(en_passant='fen') first four fields + ' 0 1'",
            "historical_json_hashes": len(historical),
            "cross_source_shared_worlds": len(shared),
            "positions_rule": {"ply_lo":lo,"ply_hi":hi,"exclude_terminal":True},
            "source": per_source, "outcomes_opened":False,
            "source_preseal_granted":False,
            "historical_coverage_proven_complete":False,
            "verdict":"AUDIT_ONLY_HISTORICAL_COVERAGE_NOT_SEALED"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", action="append", required=True, help="SOURCE_ID=PGN_PATH")
    parser.add_argument("--history-root", required=True)
    parser.add_argument("--ply-lo", type=int, default=12)
    parser.add_argument("--ply-hi", type=int, default=160)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    if args.ply_lo < 1 or args.ply_hi < args.ply_lo:
        parser.error("INVALID_PLY_WINDOW")
    specs = {}
    for raw in args.source:
        sid, sep, path = raw.partition("=")
        if not sep or not sid or sid in specs:
            parser.error("INVALID_OR_DUPLICATE_SOURCE")
        specs[sid] = Path(path)
    expected = {"Charlotte","NZ","Golders","Radnicki","Berjaya","Milton"}
    if set(specs) != expected:
        parser.error("SIX_FROZEN_SOURCE_IDENTITIES_REQUIRED")
    root = Path(args.history_root)
    if not root.is_dir():
        parser.error("MISSING_HISTORY_ROOT")
    historical, files_seen = historical_hashes(root)
    if files_seen == 0:
        parser.error("EMPTY_HISTORY_JSON_CORPUS_FAIL_CLOSED")
    result = audit(specs, historical, args.ply_lo, args.ply_hi)
    result["history_json_files_scanned"] = files_seen
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(result["verdict"],"historical=",len(historical),
          "cross_source_shared_worlds=",result["cross_source_shared_worlds"])
if __name__ == "__main__":
    main()
