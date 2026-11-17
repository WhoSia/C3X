"""Carry a paired native TT mask to the first stable R21 question family."""

import argparse
import json
from pathlib import Path

from c3x_030_r20_d1_pair import fields, run, summarize
from c3x_030_s4l_r10_reply_transport import digest
from c3x_030_s4l_r11_allocation import SF

ROUND, ROOTS, BUDGET = "1.2", ["h2h4", "e2d2"], 24000


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("discover", "pair"))
    parser.add_argument("binary", type=Path)
    parser.add_argument("selection", type=Path)
    parser.add_argument("selection_sha256")
    parser.add_argument("output", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    binary = args.binary.resolve()
    if digest(binary) != SF or digest(args.selection) != args.selection_sha256:
        raise ValueError("Binary or frozen selection differs")
    cases = json.loads(args.selection.read_text())["selection"]
    case = next(row for row in cases if len(row["replies"]) == 2)
    if case["round"] != ROUND or case["roots"] != ROOTS:
        raise ValueError("First complete pair differs")
    identity = {"round": ROUND, "roots": ROOTS, "budget": BUDGET, "binary_sha256": SF,
                "selection_file_sha256": args.selection_sha256, "history": case["history"]}
    options = {"history": case["history"], "roots": ROOTS, "budget": BUDGET}
    if args.mode == "discover":
        _, stderr, _ = run(binary, args.output, **options)
        hits = fields(stderr, "C3X_S4H2_ELIGIBLE")
        if not hits or hits[0]["ordinal"] != "0" or hits[0]["hit_before"] != "1":
            raise ValueError("No eligible first actual hit")
        output = {**identity, "key": int(hits[0]["key"]),
                  "discovery_stderr_sha256": digest(args.output / "stderr.txt")}
    else:
        if not args.receipt:
            parser.error("The paired stage requires the discovery freeze")
        prior = json.loads(args.receipt.read_text())
        if any(prior.get(name) != value for name, value in identity.items()):
            raise ValueError("Discovery does not match the requested pair")
        key = prior["key"]
        args.output.mkdir()
        rows = {}
        for arm in ("sham", "mask"):
            effect = arm == "mask"
            repeats = []
            for attempt in (1, 2):
                public, logs, uci = run(binary, args.output / f"{arm}-{attempt}", key, effect, **options)
                if public["move"] not in ROOTS:
                    raise ValueError("Selected an excluded root")
                repeats.append(summarize(public, logs, uci, key, effect))
            if repeats[0] != repeats[1]:
                raise ValueError(f"Non-repeating run in {arm}")
            rows[arm] = repeats[0]
        output = {"discovery_sha256": digest(args.receipt), "repeats_per_arm": 2, "arms": rows}
    print(json.dumps(output, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
