"""Freeze the TWIC 1664 cohort with R26–R29 exclusions."""
import argparse
import json
from pathlib import Path

from c3x_030_r28_freeze import digest, freeze
from c3x_030_r29_local_tt_move import write

ARCHIVE = "87bcd88e628c85b6e7e5b36894738fc9e6ef4012345740e57ff05795a908940f"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("archive", "r26", "r27", "r28", "r29", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    if digest(args.archive.read_bytes()) != ARCHIVE:
        raise ValueError("Unexpected TWIC 1664 archive")
    previous = {key: getattr(args, key).read_bytes() for key in ("r26", "r27", "r28", "r29")}
    r26, r27, r28, r29 = (json.loads(raw) for raw in previous.values())
    prior_games = r26["games"] + r28["positions"] + r29["positions"]
    prior_positions = r26["positions"] + r28["positions"] + r29["positions"]
    prior_positions += list(r27["near"].values()) + list(r27["transfer"].values())
    cohort = freeze(args.archive, {"games": prior_games}, r27,
                    excluded_game_digests={row["game_sha256"] for row in prior_games},
                    excluded_board_keys={tuple(row["fen"].split()[:4]) for row in prior_positions})
    for row in cohort["positions"]:
        row["id"] = row["id"].replace("R28-", "R30-", 1)
    cohort["exclusion_inputs_sha256"] = {key: digest(raw) for key, raw in previous.items()}
    write(args.output, cohort)


if __name__ == "__main__":
    main()
