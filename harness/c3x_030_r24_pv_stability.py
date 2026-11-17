"""Audit same-root, same-score principal variations with native proof."""

import argparse
from itertools import combinations
import json
from pathlib import Path

from c3x_030_r23_native_replay import NET, RECEIPT, run
from c3x_030_s4l_r10_reply_transport import board_at, digest

CASES = "a00e96af939cc0679c2dfe2f5b05c6c2c0b549774c715cc7bbb34cb5c7a94942"
CLEAN = "fc2f6b069a775a463c6d17cce30f0bd24339ec446ab621e29c4933719026e8b5"
TRACED = "8c4ef2aef9e3fd4613389c9063a4fcdb7030b8689e4c78fd4cdfeb173d89adef"


def observations(uci, proof):
    lines = [line for line in uci if RECEIPT.match(line)]
    output = []
    for line, entry in zip(lines, proof["reports"], strict=True):
        public = entry["public"]
        source = entry["source"]
        completed = entry["attempt_end"] and entry["attempt_end"]["stopped"] == "0"
        output.append({
            "move": public["move"],
            "pv": line.split(" pv ", 1)[1].split(),
            "cp": int(public["score"]) if public["kind"] == "cp" else None,
            "bound": public["bound"],
            "native": int(source["value"]) if source else None,
            "eligible": bool(entry["status"] == "exact" and completed and public["kind"] == "cp"),
            "depth": int(public["depth"]),
            "producer_iteration": int(entry["attempt"]["iteration"]) if source else None,
            "producer": public["producer"],
            "attempt": source["attempt"] if source else None,
            "nodes": int(public["nodes"]),
        })
    return output


def compare(left, right, history):
    if (not left["eligible"] or not right["eligible"]
            or (left["move"], left["cp"]) != (right["move"], right["cp"])):
        return None
    a, b = left["pv"], right["pv"]
    split = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), None)
    out = {"native_equal": left["native"] == right["native"]}
    if split is None:
        return {**out, "kind": "identical" if a == b else "prefix"}
    pivot = board_at([*history, *a[:split]])
    first, second = pivot.parse_uci(a[split]), pivot.parse_uci(b[split])
    after_a, after_b = pivot.copy(), pivot.copy()
    joins = []
    for i, (x, y) in enumerate(zip(a[split:], b[split:]), start=split + 1):
        after_a.push_uci(x)
        after_b.push_uci(y)
        if after_a.fen() == after_b.fen():
            joins.append(i)
    return {
        **out, "kind": "divergent", "first_divergence_ply": split + 1,
        "chooser": "white" if pivot.turn else "black",
        "moves": [first.uci(), second.uci()], "san": [pivot.san(first), pivot.san(second)],
        "same_ply_full_fen": joins,
    }


def validated_search(clean, trace, net, case, directory, **spec):
    plain, _ = run(clean, case, net, directory / "clean", logging=False, paired=False, nnue=True, **spec)
    logged, proof = run(trace, case, net, directory / "trace", logging=True, paired=False, nnue=True, **spec)
    if plain != logged:
        raise ValueError("Trace changed the public output")
    rows = observations(logged, proof)
    return {
        "reports": rows, "bestmove": proof["best"]["move"], "best_producer": proof["best"]["producer"],
        "actual_nodes": int(proof["best"]["nodes"]), "spec": spec,
    }


def trajectory(clean, trace, net, case, path):
    continuous = validated_search(clean, trace, net, case, path / "trajectory", nodes=300000)
    pairs = []
    for (i, earlier), (j, later) in combinations(enumerate(continuous["reports"]), 2):
        paired = compare(earlier, later, case["history"])
        if paired:
            pairs.append({"indices": [i, j], **paired})
    return {"continuous": continuous, "trajectory_pairs": pairs}


def suite(clean, trace, net, cases, output):
    result = {}
    for case in cases:
        path = output / case["id"]
        row = trajectory(clean, trace, net, case, path)
        contrasts = {}
        for depth in (10, 12, 14):
            arms = [validated_search(clean, trace, net, case, path / f"depth-{depth}-hash-{h}",
                                     depth=depth, hash_mib=h) for h in (16, 64)]
            last = [r["reports"][-1] for r in arms]
            paired = (compare(*last, case["history"])
                      if all(x["bestmove"] == row["move"] and x["best_producer"] == row["producer"]
                             for x, row in zip(arms, last, strict=True))
                      else None)
            contrasts[str(depth)] = {"arms": arms, "match": paired}
        result[case["id"]] = {**row, "hash": contrasts}
    return result


def check_inputs(cases, clean, trace, net, *, case_sha=CASES):
    if tuple(map(digest, (cases, clean, trace, net))) != (case_sha, CLEAN, TRACED, NET):
        raise ValueError("Unexpected R24 positions or engine")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cases", "clean", "trace", "net", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    check_inputs(args.cases, args.clean, args.trace, args.net)
    print(json.dumps(suite(args.clean, args.trace, args.net,
                           json.loads(args.cases.read_text())["cases"], args.output), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
