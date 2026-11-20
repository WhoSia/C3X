"""Report observable outcomes of local TT interventions without equating bounds to ranks."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from c3x_030_r29_local_tt_move import write


def compare(arms):
    control, mask = (arms[name] for name in ("sham", "mask"))
    previous_child, masked_child = (row["direct_child"] for row in (control, mask))
    old_parent, new_parent = (row["target_candidate"] for row in (control, mask))
    paired_children = all(row["stopped"] == "0" for row in (previous_child, masked_child))
    paired_parents = old_parent is not None and new_parent is not None
    def leading(parent):
        return None if parent is None else parent["update"] == "1"
    return {
        "first_reply_changed": control["replies"][:1] != mask["replies"][:1],
        "cutoff_removed": bool(control["cutoffs"]) and not mask["cutoffs"],
        "child_return_changed": (previous_child["child_value"] != masked_child["child_value"]
                                 if paired_children else None),
        "target_became_leader": (not leading(old_parent) and leading(new_parent)) if paired_parents else None,
        "target_lost_lead": (leading(old_parent) and not leading(new_parent)) if paired_parents else None,
        "final_move_changed": control["best"]["move"] != mask["best"]["move"],
        "public_stream_changed": mask.get("uci_changed"),
        "last_score_changed": (control["last_report"]["public"]["score"], control["last_report"]["public"]["bound"])
                              != (mask["last_report"]["public"]["score"], mask["last_report"]["public"]["bound"]),
    }


def summarize(data):
    strata = defaultdict(Counter)
    summaries = []
    for row in data["positions"]:
        counts = strata[row["stratum"]]
        counts["positions"] += 1
        for arm, pair in row["arms"].items():
            counts[f"{arm}_tested"] += 1
            effects = compare(pair)
            for key, value in effects.items():
                if value is True:
                    counts[f"{arm}_{key}"] += 1
                elif value is None:
                    counts[f"{arm}_{key}_unavailable"] += 1
            summaries.append({"case": row["id"], "stratum": row["stratum"], "arm": arm,
                              "in_producer_attempt": int(pair["sham"]["read"]["attempt"]) == row["source_attempt"],
                              **effects})
    return {"strata": {key: dict(val) for key, val in sorted(strata.items())}, "effects": summaries}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    write(args.output, summarize(json.loads(args.results.read_text())))


if __name__ == "__main__":
    main()
