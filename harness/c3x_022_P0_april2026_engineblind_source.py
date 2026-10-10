#!/usr/bin/env python3
"""C3X022-P0 official April16 chess source freeze BEFORE native search."""
import argparse
import hashlib
import json
from pathlib import Path
from c3x_020_C_March2026_enginefree_blind16 import (
    select_compressed_archive, HISTORY_NAMES as ORIGINAL_SIX
)

ARCHIVE_SHA = "97b036f3a3639ae3be59c1508b1e18c76ac1b2e8fada4587d1b5c5a93c438d5d"
ARCHIVE_URL = "https://database.lichess.org/broadcast/lichess_db_broadcast_2026-04.pgn.zst"
HISTORY = (*ORIGINAL_SIX, "march")
MARCH_SHA = "d79e48633be2b683176f1a6d4650aeea1b7584f11c85c2349a5bddda113febee"
PRECOMMIT = "c3x/ontology/c3x-022-P0-april2026-independent-ecology-source-and-prospective-forecast-precommit.md"

def collect_historical(paths):
    if set(paths) != set(HISTORY):
        raise ValueError("SEVEN_HISTORICAL_INPUTS_REQUIRED")
    all_fens = set()
    game_hashes = set()
    receipts = {}
    for name in HISTORY:
        raw = Path(paths[name]).read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        if name == "march" and sha != MARCH_SHA:
            raise ValueError("MARCH_SHA_DRIFT")
        data = json.loads(raw)
        candidates = data.get("selected")
        if not isinstance(candidates, list) or not candidates:
            raise ValueError("EMPTY_HISTORY_" + name)
        for item in candidates:
            fen = item["fen4"]
            if len(fen.split()) != 4:
                raise ValueError("HISTORY_FEN4_INVALID")
            all_fens.add(fen)
            if "source_game_sha256" in item:
                game_hashes.add(item["source_game_sha256"])
        receipts[name] = {"sha256":sha, "selected_count":len(candidates)}
    return all_fens, game_hashes, receipts

def build(zst, inputs):
    fens, old_games, receipts = collect_historical(inputs)
    archive_sha = hashlib.sha256(Path(zst).read_bytes()).hexdigest()
    if archive_sha != ARCHIVE_SHA:
        raise ValueError("OFFICIAL_APRIL_ARCHIVE_SHA_DRIFT")
    selected, actual_sha, scanned, rejected = select_compressed_archive(zst, fens)
    if actual_sha != ARCHIVE_SHA:
        raise ValueError("SELECTOR_ARCHIVE_SHA_DRIFT")
    if len(selected) != 16 or any(item["source_game_sha256"] in old_games for item in selected):
        raise ValueError("APRIL_SELECTED_GAME_DUPLICATE")
    return {
        "schema":"c3x022-P0-blind-april2026-standard-chess-source16-v1",
        "phase":"SOURCE_ONLY_BEFORE_APRIL_NATIVE_OUTCOMES",
        "protocol":PRECOMMIT, "official_archive_url":ARCHIVE_URL,
        "compressed_source_sha256":ARCHIVE_SHA,
        "source_license":"Lichess broadcast PGN CC BY-SA 4.0",
        "prior_sources":receipts,
        "historical_unique_fen4_count":len(fens),
        "historical_unique_game_hash_count":len(old_games),
        "scanned_games":scanned,"eligible_games":512,
        "excluded_counts":rejected,
        "selection":"March C3X020-C2 first512 legal eligible, fingerprint sort first16, 7-month historical overlap exclusion",
        "no_chess_engine_used":True,
        "selected":selected,
        "limits":["April 16 pilot games are source-defined, not a representative chess population",
                  "All native bestmove outcomes are still unknown at source seal",
                  "STRICT and BROAD are correlated within each game"]
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--zst",required=True)
    for k in HISTORY:a.add_argument("--"+k,required=True)
    a.add_argument("--out",required=True)
    args=a.parse_args()
    paths={name:getattr(args,name) for name in HISTORY}
    data=build(args.zst,paths)
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("C3X022_APRIL_SOURCE_ONLY_FROZEN",
          data["scanned_games"],len(data["selected"]),
          hashlib.sha256(p.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
