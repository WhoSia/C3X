"""Freeze a new TWIC issue under the R28 position rule and earlier event exclusions."""
import argparse
import json
from pathlib import Path

from c3x_030_r28_freeze import digest, freeze
from c3x_030_r29_local_tt_move import write

ARCHIVE = "36ac4a1324a21674649f7b5eb12e0ef21167b18288917cce6aba3d8120669dd9"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("archive", "r26", "r27", "r28", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    if digest(args.archive.read_bytes()) != ARCHIVE:
        raise ValueError("Unexpected TWIC 1663 bytes")
    r26, r27, r28 = [json.loads(getattr(args, name).read_text()) for name in ("r26", "r27", "r28")]
    excluded = r26["games"] + r28["positions"]
    frozen = freeze(args.archive, {"games": excluded}, r27)
    previous = {row["game_sha256"] for row in excluded}
    for row in frozen["positions"]:
        if row["game_sha256"] in previous:
            raise ValueError("Previous full game reappeared")
        row["id"] = row["id"].replace("R28-", "R29-", 1)
    frozen["exclusion_inputs_sha256"] = {
        name: digest(getattr(args, name).read_bytes()) for name in ("r26", "r27", "r28")
    }
    write(args.output, frozen)


if __name__ == "__main__":
    main()
