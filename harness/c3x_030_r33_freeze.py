"""Freeze the new TWIC panel before any engine observations."""
import argparse
import json
from pathlib import Path

from c3x_030_r28_freeze import digest, freeze
from c3x_030_r29_local_tt_move import write

ARCHIVE = "7540c3430a4124b513f46338a2d3a8f964ab22b774fb438da04921bc7385f03d"
PRIOR_NAMES = ("r26", "r27", "lesson", "r28", "r29", "r30", "reversals")


def make_panel(archive, prior_paths, output):
    if digest(archive.read_bytes()) != ARCHIVE:
        raise ValueError("Unexpected TWIC 1671 archive")
    sources = {name: path.read_bytes() for name, path in zip(PRIOR_NAMES, prior_paths, strict=True)}
    data = {name: json.loads(raw) for name, raw in sources.items()}
    games = data["r26"]["games"] + data["r27"]["games"]
    positions = data["r26"]["positions"] + data["r27"]["positions"]
    for name in ("r28", "r29", "r30", "reversals"):
        games.extend(data[name]["positions"])
        positions.extend(data[name]["positions"])
    lesson = data["lesson"]
    positions.extend(row for mode in ("near", "transfer") for row in lesson[mode].values())
    panel = freeze(archive, {"games": games}, lesson, cap=64,
                   excluded_game_digests={row["game_sha256"] for row in games},
                   excluded_board_keys={tuple(row["fen"].split()[:4]) for row in positions})
    for row in panel["positions"]:
        row["id"] = row["id"].replace("R28-", "R33-", 1)
    panel["exclusion_inputs_sha256"] = {name: digest(raw) for name, raw in sources.items()}
    write(output, panel)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("archive", *PRIOR_NAMES, "output"):
        parser.add_argument(arg, type=Path)
    args = parser.parse_args()
    make_panel(args.archive, [getattr(args, name) for name in PRIOR_NAMES], args.output)


if __name__ == "__main__":
    main()
