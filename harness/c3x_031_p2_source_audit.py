"""P2 acquisition-only original TWIC 1670 source census.

Do not run native Stockfish or generate labels here. The raw PGN archive remains
private Drive custody; GitHub receives only a SHA-bound aggregate receipt.
"""
import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import unicodedata
import zipfile

import chess
import chess.pgn

SOURCE_URL = "https://theweekinchess.com/zips/twic1670g.zip"
ISSUE = 1670


def h(data):
    return hashlib.sha256(data).hexdigest()


def family(event):
    return unicodedata.normalize("NFC", event).strip()


def census(path):
    raw = Path(path).read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip() is not None:
            raise ValueError("Publisher ZIP CRC invalid")
        names = z.namelist()
        if names != ["twic1670.pgn"]:
            raise ValueError(f"Unexpected archive members: {names}")
        pgn_raw = z.read(names[0])
    text = io.TextIOWrapper(io.BytesIO(pgn_raw), encoding="latin-1")
    events, failures, game_keys, seen = Counter(), Counter(), set(), 0
    initial_legal = 0
    for game in iter(lambda: chess.pgn.read_game(text), None):
        seen += 1
        event = family(game.headers.get("Event", "?"))
        events[event] += 1
        if game.errors:
            failures["pgn_parser_errors"] += 1
            continue
        if game.board().fen() != chess.STARTING_FEN or game.board().chess960:
            failures["nonstandard_start"] += 1
            continue
        moves = [move.uci() for move in game.mainline_moves()]
        if not moves:
            failures["empty_game"] += 1
            continue
        initial_legal += 1
        key = h(" ".join(moves).encode())
        if key in game_keys:
            failures["duplicate_move_history_within_issue"] += 1
        game_keys.add(key)
    if seen != 8391:
        raise ValueError("Observed PGN game count disagrees with TWIC1670 issue listing")
    return {
        "phase": "P2_PUBLISHER_ACQUISITION_ONLY",
        "issue": ISSUE,
        "publisher": "Mark Crowther, The Week in Chess",
        "url": SOURCE_URL,
        "source_zip_sha256": h(raw),
        "source_zip_bytes": len(raw),
        "source_member_name": names[0],
        "source_member_sha256": h(pgn_raw),
        "source_member_bytes": len(pgn_raw),
        "pgn_parsed_game_count": seen,
        "legal_standard_start_game_count": initial_legal,
        "distinct_normalized_event_headers": len(events),
        "distinct_full_game_move_hashes": len(game_keys),
        "failures": dict(sorted(failures.items())),
        "event_family_counts": dict(sorted(events.items())),
        "native_engine_searches": 0,
        "treatment_outcomes_observed": False,
        "independent_cohort_cleared": False,
        "required_next_steps": [
            "Full game-and-event-family exclusion against R33 and every previous source",
            "Freeze exactly sampled full game histories before native interventions",
            "Seal source binary, NNUE and trained P1 model with original hashes"
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source_zip", type=Path)
    ap.add_argument("out", type=Path)
    args = ap.parse_args()
    result = census(args.source_zip)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("P2_SOURCE", result["source_zip_sha256"],
          "games", result["pgn_parsed_game_count"],
          "families", result["distinct_normalized_event_headers"],
          "native_searches", result["native_engine_searches"])


if __name__ == "__main__":
    main()
