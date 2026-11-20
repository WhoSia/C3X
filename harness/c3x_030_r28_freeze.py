"""Freeze an event-balanced development sample from a TWIC standard-chess PGN."""
import argparse
from collections import defaultdict
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile

import chess.pgn


SEED = "C3X-R28-reliance-v1"
PLY_CHECKPOINTS = (30, 41, 50, 61, 70, 81)
CAP = 32


def digest(data):
    return hashlib.sha256(data).hexdigest()


def keyed(text):
    return digest(f"{SEED}/{text}".encode())


def family(event):
    return re.sub(r"\s+(?:Gp[A-Z]|rapid|blitz)(?=\s|$)", "", event.casefold(),
                  flags=re.IGNORECASE).strip()


def freeze(archive, r26, r27):
    excluded = {family(game["event"]) for game in r26["games"]}
    excluded.update(family(item["source"]["event"]) for item in r27["transfer"].values())
    pools = defaultdict(list)
    with zipfile.ZipFile(archive) as zf:
        (member,) = zf.namelist()
        with zf.open(member) as stream:
            pgn = io.TextIOWrapper(stream, encoding="latin-1")
            ordinal = 0
            while game := chess.pgn.read_game(pgn):
                ordinal += 1
                event = game.headers["Event"]
                group = family(event)
                board = game.board()
                if (group in excluded or event == "?" or game.errors or board.chess960
                        or board.fen() != chess.STARTING_FEN):
                    continue
                moves = [move.uci() for move in game.mainline_moves()]
                game_hash = digest(" ".join(moves).encode())
                ply = PLY_CHECKPOINTS[int(keyed(game_hash), 16) % len(PLY_CHECKPOINTS)]
                if len(moves) < ply:
                    continue
                for move in moves[:ply]:
                    board.push_uci(move)
                legal = board.legal_moves.count()
                if legal < 2 or board.is_game_over():
                    continue
                pools[group].append({
                    "game_sha256": game_hash, "source_ordinal": ordinal,
                    "event": event, "family": group, "ply": ply, "fen": board.fen(),
                    "moves": moves[:ply], "legal_moves": legal,
                })

    groups = sorted(pools, key=keyed)
    for group in groups:
        pools[group].sort(key=lambda row: keyed(row["game_sha256"]))
    seen_games, seen_boards, sample = set(), set(), []
    for offset in range(max(map(len, pools.values()), default=0)):
        for group in groups:
            if offset >= len(pools[group]):
                continue
            row = pools[group][offset]
            board_key = tuple(row["fen"].split()[:4])
            if row["game_sha256"] in seen_games or board_key in seen_boards:
                continue
            seen_games.add(row["game_sha256"])
            seen_boards.add(board_key)
            sample.append({"id": f"R28-{len(sample) + 1:03}", **row})
            if len(sample) == CAP:
                break
        if len(sample) == CAP:
            break
    if len(sample) != CAP:
        raise ValueError(f"Expected {CAP} unique positions, found {len(sample)}")
    return {"seed": SEED, "source_archive_sha256": digest(archive.read_bytes()),
            "source_member": member, "excluded_families": sorted(excluded),
            "eligible_event_families": len(groups), "positions": sample}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("archive", "r26", "r27", "output"):
        parser.add_argument(arg, type=Path)
    args = parser.parse_args()
    sample = freeze(args.archive, json.loads(args.r26.read_text()), json.loads(args.r27.read_text()))
    sample["exclusion_input_sha256"] = {
        "r26": digest(args.r26.read_bytes()), "r27": digest(args.r27.read_bytes()),
    }
    with args.output.open("x") as out:
        json.dump(sample, out, indent=2, sort_keys=True, ensure_ascii=False)
        out.write("\n")


if __name__ == "__main__":
    main()
