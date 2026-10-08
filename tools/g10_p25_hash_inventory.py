#!/usr/bin/env python3
"""P25 source hashes. No engine or activation outcomes."""
import argparse
import hashlib
import json
from pathlib import Path
import chess.pgn
from g10_p19_source_census import canonical_fen

def audit(path):
    raw = Path(path).read_bytes()
    seen = set()
    with open(path, encoding="utf-8-sig") as stream:
        while (game := chess.pgn.read_game(stream)) is not None:
            if game.errors:
                raise ValueError("PGN_PARSE_ERROR")
            board = game.board()
            for move in game.mainline_moves():
                board.push(move)
                seen.add(hashlib.sha256(canonical_fen(board).encode()).hexdigest())
    return {"pgn_sha256": hashlib.sha256(raw).hexdigest(),
            "canonical_fen_hashes": sorted(seen)}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("pgn")
    p.add_argument("--out", required=True)
    a = p.parse_args()
    Path(a.out).write_text(json.dumps(audit(a.pgn), indent=2) + "\n")
