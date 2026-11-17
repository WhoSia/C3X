"""Measure changed forecast answers with the identical reply menus and judge."""

import argparse
import json
from pathlib import Path

from c3x_030_r20_p40_value import BINARY
from c3x_030_r22_menu_score import POLICIES, score, summarize
from c3x_030_s4l_r10_reply_transport import digest
from c3x_030_s4l_r11_allocation import NET, SF


def analyze(cohort, low, high, judge):
    low_rows, high_rows = (score(cohort, data["rows"], judge["rows"]) for data in (low, high))
    changes = {}
    for game, original in low_rows.items():
        depths = original["depths"]
        if depths["12"]["reference_rank"] is None or depths["12"]["reference_rank"] != depths["14"]["reference_rank"]:
            continue
        target = depths["12"]["reference_rank"]
        delta = {}
        for policy in POLICIES:
            before = depths["12"]["policies"][policy]["forecast_rank"]
            after = high_rows[game]["depths"]["12"]["policies"][policy]["forecast_rank"]
            delta[policy] = {"before": before, "after": after, "target": target,
                             "changed": before != after,
                             "gained": before != target and after == target,
                             "lost": before == target and after != target}
        changes[game] = delta
    return {"low": summarize(low_rows), "high": summarize(high_rows), "stable_changes": changes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cohort", "baseline", "more_nodes", "judge"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    cohort, low, high, judge = (json.loads(p.read_text()) for p in
                              (args.cohort, args.baseline, args.more_nodes, args.judge))
    if (judge["forecast_sha256"] != digest(args.baseline) or judge["binary_sha256"] != BINARY
        or judge["net_sha256"] != NET or high.get("leaf_nodes") != 48000
        or any(data["cohort_sha256"] != digest(args.cohort) for data in (low, high, judge))
        or any(data["binary_sha256"] != SF or data["rows"].keys() != judge["rows"].keys()
               for data in (low, high))
        or any(low["rows"][key].keys() != high["rows"][key].keys() for key in low["rows"])):
        raise ValueError("Frozen menus, source or eligible replies do not match")
    print(json.dumps(analyze(cohort, low, high, judge), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
