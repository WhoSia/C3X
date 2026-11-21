"""Trace the actual producers for one reply fork and one corroborated reversal."""
import argparse
import json
from pathlib import Path

from c3x_030_r23_native_replay import NET, digest, run
from c3x_030_r27_native_choice import locate, tt_environment


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cohort", "clean", "trace", "net", "output"):
        parser.add_argument(name, type=Path)
    parser.add_argument("--cohort-sha256", required=True)
    args = parser.parse_args()
    if digest(args.cohort) != args.cohort_sha256 or digest(args.net) != NET:
        raise ValueError("Frozen history or Stockfish NNUE SHA mismatch")
    cases = {row["id"]: row for row in json.loads(args.cohort.read_text())["positions"]}
    targets = (
        ("R28-024", {"depth": 9}, ("c5d4",)),
        ("R28-024", {"depth": 13}, ("c5d4",)),
        ("R28-003", {"nodes": 32000}, ("f6d5", "e5f4")),
    )
    rows = {}
    for case_id, limit, roots in targets:
        key = f"{case_id}-{next(iter(limit.values()))}"
        folder = args.output / key
        case = {"history": cases[case_id]["moves"]}
        mode = {"paired": False, "nnue": True, "environment": tt_environment(("0", "0")), **limit}
        clean, _ = run(args.clean, case, args.net, folder / "clean", logging=False, **mode)
        off, _ = run(args.trace, case, args.net, folder / "off", logging=False, **mode)
        traced, proof = run(args.trace, case, args.net, folder / "on", logging=True, **mode)
        repeated, repeat_proof = run(args.trace, case, args.net, folder / "repeat", logging=True, **mode)
        log = (folder / "on" / "stderr.txt").read_text()
        if not clean == off == traced == repeated or proof != repeat_proof:
            raise ValueError(f"Tracing or repetition changed the result for {key}")
        if log != (folder / "repeat" / "stderr.txt").read_text():
            raise ValueError(f"Tracing events did not reproduce for {key}")
        row = locate(proof, log, roots)
        if row["best"]["move"] != roots[0]:
            raise ValueError(f"Unexpected recommendation for {key}")
        rows[key] = {"limit": limit, **row}
    (args.output / "producers.json").write_text(json.dumps({
        "inputs_sha256": {name: digest(getattr(args, name)) for name in ("cohort", "clean", "trace", "net")},
        "rows": rows,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
