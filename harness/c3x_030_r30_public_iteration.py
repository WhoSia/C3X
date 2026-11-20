"""Compare what public UCI displays expose in already paired Stockfish runs."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

from c3x_030_r29_local_tt_move import write


def public_view(log):
    iterations = []
    best = None
    for line in log.splitlines():
        if line.startswith("bestmove "):
            best = line.split()[1]
        match = re.match(r"^info depth (\d+) .*? score (cp|mate) (-?\d+)(.*)$", line)
        if not match or " pv " not in match[4]:
            continue
        fields, pv = match[4].split(" pv ", 1)
        bounds = set(fields.split()) & {"lowerbound", "upperbound"}
        if len(bounds) > 1:
            raise ValueError("Conflicting score bounds")
        iterations.append((int(match[1]), match[2], int(match[3]), next(iter(bounds), None), pv))
    if best is None or not iterations:
        raise ValueError("Missing single-PV UCI analysis or best move")
    return {"final": (best, *iterations[-1][1:]), "iterations": iterations}


def audit(results, baseline, masks):
    counts = defaultdict(Counter)
    rows = []
    for case in results["positions"]:
        if not case["arms"]:
            continue
        path = baseline / case["id"] / "baseline" / "stdout.txt"
        public = public_view(path.read_text())
        for arm, receipts in case["arms"].items():
            treatment = masks / case["id"] / f"{arm}-mask" / "stdout.txt"
            masked = public_view(treatment.read_text())
            effects = {"tested": True, "final_card_changed": public["final"] != masked["final"],
                       "iteration_changed": public["iterations"] != masked["iterations"],
                       "uci_stream_changed": receipts["mask"]["uci_changed"]}
            effects["trajectory_only"] = effects["iteration_changed"] and not effects["final_card_changed"]
            effects["metadata_only"] = effects["uci_stream_changed"] and not (
                effects["iteration_changed"] or effects["final_card_changed"])
            counts[arm].update(key for key, value in effects.items() if value)
            rows.append({"id": case["id"], "arm": arm, **effects})
    return {"counts": {arm: dict(results) for arm, results in counts.items()}, "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("baseline", "masks", "output"):
        parser.add_argument(arg, type=Path)
    args = parser.parse_args()
    write(args.output, audit(json.loads((args.masks / "result.json").read_text()),
                             args.baseline, args.masks))


if __name__ == "__main__":
    main()
