"""Trace the exact reply copied into Stockfish and replay ordering interventions."""

import argparse
import json
import os
from pathlib import Path
from unittest.mock import patch

from c3x_030_r23_native_replay import NET, indexed, run
from c3x_030_r24_pv_stability import TRACED, observations
from c3x_030_s4l_r10_reply_transport import board_at, digest

CASES = "9fe892ff296d45117d28f7ee5ea095218b6762bf38cf15775e7dc8b27b478a5c"
FORK = "2fc293d0984fa6afe6bf0c93f682dbb92d8d4dcfe63e7b5103fb65d66d5e0068"
ROOT = "d1e2"
HINTS = {"bh2": "d6h2", "be7": "d6e7"}


def records(lines, field):
    prefix = f"C3X_R25_{field} "
    return [dict(pair.split("=", 1) for pair in line.removeprefix(prefix).split())
            for line in lines if line.startswith(prefix)]


def join_reply(uci, proof, lines):
    rows = observations(uci, proof)
    last = rows[-1]
    begins = indexed(records(lines, "REPLY_BEGIN"), "call")
    ends = indexed(records(lines, "REPLY_END"), "call")
    copies = indexed(records(lines, "COPY"), "producer")
    source = proof["best_source"]
    events = records(lines, "EVALUATED")
    admitted = [entry for entry in begins.values() if entry["admitted"] == "1"]
    if any(entry["iteration"] != "18" for entry in admitted):
        raise ValueError("Hint escaped the intervention iteration")
    trace = None
    if proof["best"]["move"] == ROOT and last["producer"] == proof["best"]["producer"]:
        copy = copies.get(last["producer"])
        if not copy or copy["call"] == "0":
            raise ValueError("Missing final root copy from scoped child")
        begin, end = begins[copy["call"]], ends[copy["call"]]
        evaluated = [row for row in events if row["call"] == copy["call"]]
        updates = [row for row in evaluated if row["pv_update"] == "1"]
        if (copy["attempt"] != begin["attempt"] or copy["attempt"] != source["attempt"]
                or int(copy["value"]) != -int(end["value"])
                or int(copy["value"]) != int(source["value"])
                or not updates
                or len(last["pv"]) < 2
                or not (copy["reply"] == last["pv"][1] == end["reply"] == updates[-1]["move"])):
            raise ValueError("Reply did not match its copied native value and PV")
        trace = {"begin": begin, "end": end, "copy": copy, "updates": updates,
                 "ordered_returns": evaluated, "root_producer": source}
    return {"best": proof["best"], "final": last, "reply_trace": trace,
            "admitted": admitted, "reply_calls": len(begins)}


def one(binary, case, net, directory, depth, hint):
    with patch.dict(os.environ, {"C3X_R25_HINT": hint}):
        uci, proof = run(binary, case, net, directory, logging=True, paired=False, nnue=True, depth=depth)
    return uci, proof


def evaluate(base, traced, case, net, freeze, root):
    output = {}
    for expected in freeze["reports"]:
        depth = expected["depth"]
        directory = root / f"depth-{depth}"
        prior, _ = one(base, case, net, directory / "r23", depth, "sham")
        for mode in (("sham", "bh2", "be7") if depth == 18 else ("sham",)):
            attempts = []
            for repeat in (1, 2):
                path = directory / f"{mode}-{repeat}"
                uci, proof = one(traced, case, net, path, depth, mode)
                lines = (path / "stderr.txt").read_text().splitlines()
                entry = join_reply(uci, proof, lines)
                if mode == "sham":
                    if uci != prior or entry["final"]["pv"] != expected["pv"] or entry["admitted"]:
                        raise ValueError("Sham changed archived expected path or received treatment")
                elif not entry["admitted"] or any(r["picker"] != HINTS[mode] for r in entry["admitted"]):
                    raise ValueError("No admitted targeted picker hint")
                attempts.append(entry)
            if attempts[0] != attempts[1]:
                raise ValueError("Native trace did not repeat")
            output[f"{depth}-{mode}"] = attempts[0]
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cases", "freeze", "base", "traced", "net", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    if tuple(map(digest, (args.cases, args.freeze, args.base, args.net))) != (CASES, FORK, TRACED, NET):
        raise ValueError("Unexpected R24/R23 sources")
    freeze = json.loads(args.freeze.read_text())
    case = next(row for row in json.loads(args.cases.read_text())["cases"] if row["id"] == freeze["case"])
    board = board_at(case["history"])
    board.push_uci(ROOT)
    for hint in HINTS.values():
        board.parse_uci(hint)
    result = evaluate(args.base, args.traced, case, args.net, freeze, args.output)
    print(json.dumps({"case": case["id"], "after_root_fen": board.fen(),
                      "traced_sha256": digest(args.traced), "rows": result}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
