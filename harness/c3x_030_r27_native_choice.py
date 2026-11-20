"""Bind the exposed R26 candidate contrast to R23 native root producers."""
import argparse
import json
from pathlib import Path

from c3x_030_r23_native_replay import NET, digest, records, run, source_result

CASE_ID = "twic1670-08-61"
ROOTS = ("f6d7", "a5a4")
NODES = 32000
ARMS = {"baseline": ("0", "0"), "picker_off": ("1", "0"),
        "value_off": ("0", "1"), "both_off": ("1", "1")}
EXPECTED_BEST = {"baseline": "f6d7", "both_off": "a5a4"}


def tt_environment(flags):
    return dict(zip(("C3X_NO_TT_PICKER", "C3X_NO_TT_VALUE"), flags, strict=True))


def locate(proof, log, roots):
    producer = proof["best_source"]
    attempt = proof["best_attempt"]
    if producer is None or attempt is None:
        raise ValueError("Final bestmove has no matching native producer")
    contenders = {}
    for rec in records(log.splitlines(), "CANDIDATE"):
        if rec["attempt"] != producer["attempt"] or rec["move"] not in roots:
            continue
        raw, relation = source_result(rec)
        contenders.setdefault(rec["move"], []).append({
            "candidate_id": int(rec["id"]),
            "raw_return": int(rec["value"]),
            "window": [int(rec["alpha"]), int(rec["beta"])],
            "window_score": raw, "window_relation": relation,
        })
    return {"best": proof["best"], "producer": producer, "attempt": attempt,
            "attempt_end": proof["best_attempt_end"],
            "last_report": proof["reports"][-1], "candidate_records": contenders}


def verify(archive, clean, trace, net, output):
    case, = (row for row in archive["positions"] if row["id"] == CASE_ID)
    search_case = {"history": case["moves"]}
    runs = {"logging": False, "paired": False, "nnue": True, "nodes": NODES}
    clean_uci, _ = run(clean, search_case, net, output / "upstream", **runs,
                       environment=tt_environment(ARMS["baseline"]))
    joined = {}
    for name, flags in ARMS.items():
        arm = output / name
        env = tt_environment(flags)
        off, _ = run(trace, search_case, net, arm / "off", **runs, environment=env)
        traced = dict(runs, logging=True, environment=env)
        on, proof = run(trace, search_case, net, arm / "on", **traced)
        repeated, repeat_proof = run(trace, search_case, net, arm / "repeat", **traced)
        if off != on or on != repeated or proof != repeat_proof:
            raise ValueError(f"Trace interfered with native search in {name}")
        if name == "baseline" and on != clean_uci:
            raise ValueError("Baseline differs from upstream")
        stdout = (arm / "on" / "stderr.txt").read_text()
        if stdout != (arm / "repeat" / "stderr.txt").read_text():
            raise ValueError("Native logs differ")
        item = locate(proof, stdout, ROOTS)
        if name in EXPECTED_BEST and item["best"]["move"] != EXPECTED_BEST[name]:
            raise ValueError("R26 recommendation failed to reproduce")
        joined[name] = item
    return {"case": CASE_ID, "requested_nodes": NODES, "searches": 1 + 3 * len(ARMS),
            "arms": joined}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cohort", "clean", "trace", "net", "output"):
        parser.add_argument(name, type=Path)
    parser.add_argument("--cohort-sha256", required=True)
    args = parser.parse_args()
    if digest(args.cohort) != args.cohort_sha256 or digest(args.net) != NET:
        raise ValueError("Frozen cohort or NNUE SHA mismatch")
    report = verify(json.loads(args.cohort.read_bytes()), args.clean, args.trace,
                    args.net, args.output)
    report["build_identity"] = {name: digest(path) for name, path in
                                (("clean", args.clean), ("trace", args.trace),
                                 ("net", args.net), ("cohort", args.cohort))}
    (args.output / "choice.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
