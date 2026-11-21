"""Check every direct child call for the targeted root candidate, including re-search."""
import argparse
import json
from pathlib import Path

from c3x_030_r20_d1_pair import fields
from c3x_030_r29_local_tt_move import write


def chain(path, receipt):
    target = receipt["read"]
    rows = [row for row in fields(path.read_text().splitlines(), "C3X_R29_CHILD")
            if all(row[k] == target[k] for k in ("root", "attempt", "candidate_next"))]
    if receipt["direct_child"] not in rows:
        raise ValueError("Selected probe's direct child is missing")
    candidate = receipt["target_candidate"]
    if any(int(row["root_value"]) != -int(row["child_value"]) for row in rows):
        raise ValueError("Wrong score orientation")
    if candidate and (rows[-1]["root_value"] != candidate["value"] or rows[-1]["stopped"] != "0"):
        raise ValueError("Final child and recorded root candidate disagree")
    return {"children": rows, "candidate": candidate, "final": receipt["best"]["move"]}


def audit(baseline, masks):
    cases = json.loads((masks / "result.json").read_text())["positions"]
    return [
        {"id": case["id"], "channel": channel,
         "sham": chain(baseline / case["id"] / "baseline" / "stderr.txt", arms["sham"]),
         "mask": chain(masks / case["id"] / f"{channel}-mask" / "stderr.txt", arms["mask"])}
        for case in cases for channel, arms in case["arms"].items()
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("baseline", "masks", "output"):
        parser.add_argument(arg, type=Path)
    args = parser.parse_args()
    write(args.output, audit(args.baseline, args.masks))


if __name__ == "__main__":
    main()
