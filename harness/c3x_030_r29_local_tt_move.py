"""Freeze and replay a single effective TT move read in the Nd7/a4 comparison."""
import argparse
import json
from pathlib import Path

from c3x_030_r20_d1_pair import fields
from c3x_030_r23_native_replay import NET, digest, run

CASE = "twic1670-08-61"
REFERENCE = ("f6d7", "a5a4")
REPLY = "b3b4"
NODES = 32000


def nominate(probes, producer_attempt):
    eligible = [entry for entry in probes if entry["root"] == REFERENCE[1]
                and entry["hint"] == REPLY and entry["hit"] == "1"
                and int(entry["attempt"]) <= producer_attempt]
    if not eligible:
        raise ValueError("No predeclared b4 TT move read before or in the producing attempt")
    attempt = max(int(entry["attempt"]) for entry in eligible)
    return next(entry for entry in eligible if int(entry["attempt"]) == attempt)


def nominate_cutoff(probes, cutoffs, producer_attempt):
    cutoff_ids = {row["seq"] for row in cutoffs}
    candidates = [row for row in probes if row["root"] == REFERENCE[1]
                  and int(row["attempt"]) == producer_attempt and row["seq"] in cutoff_ids
                  and row["excluded"] == "0"]
    if not candidates:
        raise ValueError("Alternative has no ply-one TT cutoff in the producing attempt")
    return candidates[0]


def probe_signature(entry):
    changed = {"mask", "effective", "effective_value", "mask_move", "mask_value"}
    return {key: value for key, value in entry.items() if key not in changed}


def trace_at(directory, proof, target, roots=REFERENCE):
    log = (directory / "stderr.txt").read_text().splitlines()
    probes = fields(log, "C3X_R29_PLY1")
    matches = [row for row in probes if row["seq"] == target["seq"]]
    if len(matches) != 1 or probe_signature(matches[0]) != probe_signature(target):
        raise ValueError("The mask arm reached a different pre-treatment read")
    entry = matches[0]
    replies = fields(log, "C3X_R29_REPLY")
    child = fields(log, "C3X_R29_CHILD")
    direct = [row for row in child if row["root"] == entry["root"]
              and row["attempt"] == entry["attempt"]
              and row["candidate_next"] == entry["candidate_next"]
              and int(row["before"]) < int(entry["seq"]) <= int(row["after"])]
    if len(direct) != 1:
        raise ValueError("Expected one direct root child enclosing the read")
    candidates = fields(log, "C3X_R23_CANDIDATE")
    same_attempt = [row for row in candidates if row["attempt"] == entry["attempt"]]
    target_row = next((row for row in same_attempt if row["id"] == entry["candidate_next"]), None)
    return {
        "read": entry,
        "masked": [row for row in probes if row["mask"] == "1"],
        "cutoffs": [row for row in fields(log, "C3X_R29_CUTOFF") if row["seq"] == entry["seq"]],
        "replies": [row["move"] for row in replies if row["seq"] == entry["seq"]],
        "direct_child": direct[0],
        "target_candidate": target_row,
        "contrast_candidates": [row for row in same_attempt if row["move"] in roots],
        "target_attempt_end": next((row for row in fields(log, "C3X_R23_END")
                                    if row["attempt"] == entry["attempt"]), None),
        "best": proof["best"],
        "producer": proof["best_source"],
        "last_report": proof["reports"][-1],
    }


def replay(binary, case, net, directory, *, logging=True, probe=True, target=0, mask=False, policy="move"):
    env = {"C3X_R29_PROBES": str(int(probe)), "C3X_R29_TARGET": str(target),
           "C3X_R29_MASK_MOVE": str(int(mask and policy == "move")),
           "C3X_R29_MASK_VALUE": str(int(mask and policy == "value")),
           "C3X_NO_TT_PICKER": "0", "C3X_NO_TT_VALUE": "0"}
    return run(binary, case, net, directory, logging=logging, paired=False, nnue=True,
               nodes=NODES, environment=env)


def write(path, payload):
    with path.open("x") as stream:
        json.dump(payload, stream, indent=2)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("discover", "replay"))
    for path in ("cohort", "clean", "patched", "net", "output", "freeze"):
        parser.add_argument(path, type=Path)
    parser.add_argument("--policy", choices=("move", "value"), default="move")
    args = parser.parse_args()
    assets = {name: digest(getattr(args, name)) for name in ("cohort", "clean", "patched", "net")}
    if assets["net"] != NET:
        raise ValueError("Stockfish NNUE SHA mismatch")
    source, = (row for row in json.loads(args.cohort.read_text())["positions"] if row["id"] == CASE)
    case = {"history": source["moves"]}
    if args.mode == "discover":
        clean, _ = replay(args.clean, case, args.net, args.output / "upstream", logging=False, probe=False)
        off, _ = replay(args.patched, case, args.net, args.output / "trace-off", logging=False, probe=False)
        on, proof = replay(args.patched, case, args.net, args.output / "discovery")
        if clean != off or clean != on or proof["best"]["move"] != REFERENCE[0]:
            raise ValueError("Read-only instrumentation fails the baseline")
        baseline = proof["best_source"]
        log = (args.output / "discovery" / "stderr.txt").read_text().splitlines()
        probes = fields(log, "C3X_R29_PLY1")
        attempt = int(baseline["attempt"])
        nomination = (nominate(probes, attempt) if args.policy == "move" else
                      nominate_cutoff(probes, fields(log, "C3X_R29_CUTOFF"), attempt))
        write(args.freeze, {"assets": assets, "case": CASE, "node_budget": NODES,
                            "policy": args.policy,
                            "original_producer": baseline, "target": nomination,
                            "discovery_trace": digest(args.output / "discovery" / "stderr.txt")})
        return

    frozen = json.loads(args.freeze.read_text())
    if (frozen["assets"] != assets or frozen["case"] != CASE or frozen["node_budget"] != NODES
            or frozen.get("policy", "move") != args.policy):
        raise ValueError("Frozen experiment identity mismatch")
    target = frozen["target"]
    outputs, uci = {}, {}
    for name in ("sham", "mask", "mask-repeat", "restore"):
        masked = name.startswith("mask")
        folder = args.output / name
        uci[name], proof = replay(args.patched, case, args.net, folder,
                                  target=int(target["seq"]), mask=masked, policy=args.policy)
        outputs[name] = trace_at(folder, proof, target)
        receipt = outputs[name]
        if len(receipt["masked"]) != int(masked) or receipt["read"]["mask"] != str(int(masked)):
            raise ValueError("Unexpected mask count or event")
        if receipt["read"]["effective"] != ("(none)" if masked and args.policy == "move" else target["hint"]):
            raise ValueError("Unexpected effective hint")
        if args.policy == "value":
            if receipt["read"]["mask_value"] != str(int(masked)) or receipt["read"]["mask_move"] != "0":
                raise ValueError("The intervention touched an unintended channel")
            if bool(receipt["cutoffs"]) == masked:
                raise ValueError("Expected cutoff in control and fresh search when withheld")
    for left, right in (("sham", "restore"), ("mask", "mask-repeat")):
        raw_left = (args.output / left / "stderr.txt").read_bytes()
        raw_right = (args.output / right / "stderr.txt").read_bytes()
        if outputs[left] != outputs[right] or uci[left] != uci[right] or raw_left != raw_right:
            raise ValueError(f"{left} and {right} did not reproduce")
    write(args.output / "result.json", {"frozen": frozen, "arms": outputs,
                                      "mask_changes_uci": uci["sham"] != uci["mask"]})


if __name__ == "__main__":
    main()
