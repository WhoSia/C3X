"""Aggregate paired R11 endpoints and measure referee depth sensitivity."""

import argparse
import json
from statistics import mean
from pathlib import Path

from c3x_030_s4l_r11_score import METHODS, direction


def aggregate(report):
    rows = report["rows"]
    result = {}
    for arm in METHODS:
        trials = [row["arms"][arm] for row in rows]
        scored = [trial for trial in trials if "sign_match" in trial]
        errors = [trial["gap_error"] for trial in scored if "gap_error" in trial]
        result[arm] = {
            "actual_nodes": sum(trial["actual_nodes"] for trial in trials),
            "terminal_coverage": sum(all(trial["terminal"]) for trial in trials),
            "paired_coverage": len(scored),
            "sign_matches": sum(trial["sign_match"] for trial in scored),
            "reply_hits": sum(sum(trial["reply_hits"]) for trial in scored),
            "cp_pairs": len(errors),
            "gap_mae": mean(errors) if errors else None,
        }
        if arm != "pv":
            result[arm]["discovery_hits"] = sum(sum(trial["discovery_hits"]) for trial in scored)
            result[arm]["restricted_judge_sign_matches"] = sum(
                trial["restricted_judge_sign_match"] for trial in scored)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("primary", type=Path)
    parser.add_argument("sensitivity", type=Path)
    args = parser.parse_args()
    first, second = (json.loads(path.read_text()) for path in (args.primary, args.sensitivity))
    if (first["depth"], second["depth"]) != (12, 14):
        raise ValueError("Expected depth 12 and 14 scores in order")
    changes = []
    for left, right in zip(first["rows"], second["rows"], strict=True):
        if left["round"] != right["round"] or left["roots"] != right["roots"]:
            raise ValueError("Depth reports use different candidates")
        if all(left["judge"]) and all(right["judge"]):
            if direction(left["judge"]) != direction(right["judge"]):
                changes.append(left["round"])
    print(json.dumps({"12": aggregate(first), "14": aggregate(second),
                      "judge_sign_changed": changes}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
