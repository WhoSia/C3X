"""Freeze and run the raw-value extension without inspecting engine predictions."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

from c3x_030_r21_root_screen import games, moves_of
from c3x_030_r24_pv_stability import check_inputs, trajectory
from c3x_030_s4l_r10_reply_transport import digest

PGN = "b0f04b20bef85542e6c84852669a0c8e4763bf8fea86284a0f2eafc54e036cff"
PRIOR = (
    "f573f137f37904e6a3c5ea14ff931a2a250af7016474d4a2f778d6e82e30d89a",
    "9385e63bf74aca7a6a8a6685dc1aa4b4f4f600d0390b112d00b5a8767eaef4c2",
    "8a44899274ec3086e38de05627720339cd54306175133f488add93b3b63eabb1",
)


def numeric_round(game):
    return tuple(map(int, game.headers["Round"].split(".")))


def select(pgn, prior):
    if digest(pgn) != PGN or tuple(map(digest, prior)) != PRIOR:
        raise ValueError("Unexpected raw PGN or exclusion cohort")
    used = {tuple(row["history"][:12]) for path in prior
            for row in json.loads(path.read_text())["selection"]}
    result = []
    for game in sorted(games(pgn), key=numeric_round):
        history = moves_of(game)
        if len(history) <= 24 or game.headers["Result"] == "*" or tuple(history[:12]) in used:
            continue
        used.add(tuple(history[:12]))
        result.append({"id": "s28-l2-" + game.headers["Round"], "history": history[:24]})
        if len(result) == 24:
            return {"pgn_sha256": PGN, "exclude_sha256": PRIOR, "cases": result}
    raise ValueError("Not enough eligible games")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--exclude", type=Path, nargs=3)
    parser.add_argument("--case-sha")
    for name in ("clean", "trace", "net", "output"):
        parser.add_argument("--" + name, type=Path)
    args = parser.parse_args()
    if args.exclude:
        output = select(args.input, args.exclude)
    else:
        if not all((args.clean, args.trace, args.net, args.output, args.case_sha)):
            parser.error("Replay requires the frozen SHA, two engines, network and run directory")
        check_inputs(args.input, args.clean, args.trace, args.net, case_sha=args.case_sha)
        cases = json.loads(args.input.read_text())["cases"]

        def run_case(case):
            return (case["id"], trajectory(args.clean, args.trace, args.net,
                                           case, args.output / case["id"]))

        with ThreadPoolExecutor(max_workers=4) as pool:
            output = dict(pool.map(run_case, cases))
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
