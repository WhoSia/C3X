"""Freeze game histories without engine evaluation for C3X 0.30 R26."""
import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import zipfile

import chess
import chess.pgn

SEED = "C3X-030-R26-20261117"
CHECKPOINTS = (30, 61, 96)
GAMES_PER_SOURCE = 16


def digest(data):
    return hashlib.sha256(data).hexdigest()


def parse_candidates(data, source):
    try:
        decoded = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        decoded = data.decode("latin-1")
    stream = io.StringIO(decoded)
    tallies = Counter()
    candidates = []
    while (game := chess.pgn.read_game(stream)) is not None:
        tallies["records"] += 1
        if game.errors or type(game.board()) is not chess.Board or game.board().fen() != chess.STARTING_FEN:
            tallies["invalid_or_nonstandard"] += 1
            continue
        moves = tuple(move.uci() for move in game.mainline_moves())
        if len(moves) < 64:
            tallies["short"] += 1
            continue
        game_digest = digest(" ".join(moves).encode("ascii"))
        key = digest(f"{SEED}/{source}/{game_digest}".encode("ascii"))
        candidates.append((key, game_digest, moves, tallies["records"], game.headers["Event"]))
    return candidates, dict(tallies)


def select_games(candidates, source, seen_prefixes):
    games = []
    by_event = Counter()
    for _, game_digest, moves, ordinal, event in sorted(candidates):
        prefix = moves[:12]
        if prefix in seen_prefixes or (source == "twic1670" and by_event[event] >= 4):
            continue
        by_event[event] += 1
        seen_prefixes.add(prefix)
        games.append({
            "id": f"{source}-{len(games) + 1:02}", "ordinal": ordinal,
            "game_sha256": game_digest, "event": event, "moves": moves,
        })
        if len(games) == GAMES_PER_SOURCE:
            break
    if len(games) != GAMES_PER_SOURCE:
        raise ValueError(f"{source} yielded {len(games)} games")
    return games


def position_rows(game):
    board = chess.Board()
    for ply, uci in enumerate(game["moves"], 1):
        board.push_uci(uci)
        if ply in CHECKPOINTS and not board.is_game_over():
            yield {
                "id": f"{game['id']}-{ply}", "game_id": game["id"],
                "ply": ply, "fen": board.fen(), "moves": game["moves"][:ply],
                "legal_moves": board.legal_moves.count(),
                "pieces": len(board.piece_map()),
            }


def freeze(twic, tcec):
    seen_prefixes = set()
    result = {"seed": SEED, "sources": {}, "games": [], "positions": []}
    for source, path in (("twic1670", twic), ("tcec29l2", tcec)):
        raw = path.read_bytes()
        data = raw
        if source == "twic1670":
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                data = archive.read("twic1670.pgn")
        candidates, tallies = parse_candidates(data, source)
        result["sources"][source] = {
            "file": path.name, "archive_sha256": digest(raw),
            "pgn_sha256": digest(data), "eligible": len(candidates), **tallies,
        }
        games = select_games(candidates, source, seen_prefixes)
        result["games"].extend(games)
        for game in games:
            result["positions"].extend(position_rows(game))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("twic", type=Path)
    parser.add_argument("tcec", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = freeze(args.twic, args.tcec)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(result["sources"], len(result["games"]), len(result["positions"]))


if __name__ == "__main__":
    main()
