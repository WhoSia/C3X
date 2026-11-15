"""Screen every London second/second single-candidate deletion and addition."""
import argparse
import json
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory

from c3x_030_s4l_r4_exchange import run
from c3x_030_s4l_r6_forced_probe import CANDIDATES

CASE = "dev_london_ply8"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("binary", "protocol", "r4_result", "r7_result", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    binary, work = args.binary.resolve(), args.output.resolve()
    spec, = [x for x in json.loads(args.protocol.read_text())["cases"]
             if x["case_id"] == CASE and x["split"] == "development"]
    archived = json.loads(args.r7_result.read_text())[CASE]
    prior = json.loads(args.r4_result.read_text())[CASE]
    fen, target = spec["fen"], prior["target"]
    work.mkdir(parents=True)
    enumeration = subprocess.run([str(binary)], input=f"position fen {fen}\ngo perft 1\nquit\n",
                                 text=True, check=True, capture_output=True).stdout
    legal = tuple(re.findall(r"^([a-h][1-8][a-h][1-8][qrbn]?): 1$", enumeration, re.M))
    four = CANDIDATES[CASE]
    if len(legal) != len(set(legal)) or len(legal) != 36 or not set(four) <= set(legal):
        raise ValueError("Unexpected legal root list")
    result = {"legal": legal, "grid": {}}
    with TemporaryDirectory(prefix="snapshots-", dir=work) as folder:
        paths = [(block, Path(folder) / f"{block}.bin") for block in ("tt", "history")]
        donor = run(binary, work / "donor", fen, target, "second", exports=paths)
        if donor != archived["natural"]["second"]:
            raise ValueError("Donor replay differs")
        for limit, depth in (("depth8", 8), ("nodes12k", None)):
            grid = result["grid"][limit] = {}
            for move in legal:
                menus = {f"omit-{move}": tuple(m for m in legal if m != move)}
                if move not in four:
                    menus[f"add-{move}"] = (*four, move)
                for label, moves in menus.items():
                    row = run(binary, work / limit / label, fen, target, "sham",
                              imports=paths, second_moves=moves, second_depth=depth)
                    if row["masks"] or row["go1"] != archived["natural"]["sham"]["go1"]:
                        raise ValueError(f"Recipient replay differs for {limit}/{label}")
                    if row["go2"]["move"] not in moves:
                        raise ValueError(f"Winner outside menu for {limit}/{label}")
                    grid[label] = row
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
