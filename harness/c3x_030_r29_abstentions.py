"""Identify where the frozen event rule abstains in the recorded source trace."""
import argparse
import json
from pathlib import Path

from c3x_030_r20_d1_pair import fields
from c3x_030_r29_local_tt_move import write


def review(position, trace):
    cutoffs = {row["seq"] for row in fields(trace, "C3X_R29_CUTOFF")}
    eligible = [row for row in fields(trace, "C3X_R29_PLY1")
                if row["root"] == position["source"]["alternative"] and row["excluded"] == "0"
                and int(row["attempt"]) <= position["source_attempt"]]
    producer = [row for row in eligible if int(row["attempt"]) == position["source_attempt"]]
    return {
        "case": position["id"], "stratum": position["stratum"],
        "reply": position["independent_reply"],
        "foil_probes": len(eligible),
        "foil_probes_at_producer": len(producer),
        "foil_reads_at_producer": [row for row in producer if row["hit"] == "1"],
        "reply_in_earlier_ply_one_hints": any(row["hint"] == position["independent_reply"] for row in eligible),
        "producer_cutoffs": sum(row["seq"] in cutoffs for row in producer),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    rows = json.loads((args.logs / "result.json").read_text())["positions"]
    write(args.output, [review(row, (args.logs / row["id"] / "sham" / "stderr.txt").read_text().splitlines())
                        for row in rows if not row["arms"]])


if __name__ == "__main__":
    main()
