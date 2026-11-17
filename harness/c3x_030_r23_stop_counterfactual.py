"""Freeze a source-picked leader change and replay the two stopping budgets."""

import argparse
import json
from pathlib import Path

from c3x_030_r23_native_replay import CASES, NET, run
from c3x_030_s4l_r10_reply_transport import digest


def targets(cases, suite):
    for case in cases["cases"]:
        name = case["id"] + "-all-nnue-24000"
        reports = [row for row in suite["rows"][name]["proof"]["reports"] if row["status"] == "exact"]
        for left, right in zip(reports, reports[1:]):
            before, after = left["public"], right["public"]
            if before["move"] == after["move"]:
                continue
            return {"case": case["id"],
                    "source": name,
                    "brackets": [
                        {"nodes_requested": int(row["public"]["nodes"]) + 1,
                         "observed_nodes": int(row["public"]["nodes"]),
                         "expected_move": row["public"]["move"],
                         "nominal_depth": int(row["public"]["depth"]),
                         "attempt": row["attempt"]["attempt"], "producer": row["source"]["id"]}
                        for row in (left, right)
                    ]}
    raise ValueError("No eligible leader transition")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cases", type=Path)
    parser.add_argument("suite", type=Path)
    parser.add_argument("--trace", type=Path)
    parser.add_argument("--clean", type=Path)
    parser.add_argument("--net", type=Path)
    parser.add_argument("--freeze", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if digest(args.cases) != CASES:
        raise ValueError("Unexpected case list")
    cases, suite = (json.loads(path.read_text()) for path in (args.cases, args.suite))
    spec = {**targets(cases, suite), "suite_sha256": digest(args.suite)}
    if args.trace is None:
        print(json.dumps(spec, indent=2, sort_keys=True))
        return
    if (not args.freeze or not args.clean or not args.net or not args.output
            or digest(args.trace) != suite["trace_sha256"] or digest(args.clean) != suite["clean_sha256"]
            or digest(args.net) != NET or spec != json.loads(args.freeze.read_text())):
        raise ValueError("Engine or frozen stopping intervention differs")
    case = next(row for row in cases["cases"] if row["id"] == spec["case"])
    arms = []
    for arm in spec["brackets"]:
        options = {"paired": False, "nnue": True, "nodes": arm["nodes_requested"]}
        directory = args.output / str(arm["nodes_requested"])
        plain, _ = run(args.clean, case, args.net, directory / "clean", logging=False, **options)
        followed, proof = run(args.trace, case, args.net, directory / "trace", logging=True, **options)
        replay, repeated = run(args.trace, case, args.net, directory / "repeat", logging=True, **options)
        if plain != followed or followed != replay or proof != repeated:
            raise ValueError("Unmatched stop bracket control")
        arms.append({**arm, "matched_prior": proof["best"]["move"] == arm["expected_move"],
                     "uci": followed, "proof": proof})
    print(json.dumps({"freeze_sha256": digest(args.freeze), "arms": arms}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
