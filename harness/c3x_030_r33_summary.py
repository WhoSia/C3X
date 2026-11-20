"""Summarize frozen fresh-position early-return trials with explicit denominators."""
import argparse
import json
import re
from pathlib import Path

from c3x_030_r20_d1_pair import fields
from c3x_030_r29_local_tt_move import write
from c3x_030_r30_public_iteration import public_view
from c3x_030_r33_gate_panel import digest

PRETREATMENT = ("attempt", "candidate", "root", "key", "depth", "beta")


def candidate(logfile, target):
    rows = fields(logfile.read_text().splitlines(), "C3X_R23_CANDIDATE")
    matches = [row for row in rows if row["id"] == target["candidate"]]
    if len(matches) > 1:
        raise ValueError("Duplicate candidate")
    row = matches[0] if matches else None
    if row and (row["attempt"], row["move"]) != (target["attempt"], target["root"]):
        raise ValueError("Candidate matched wrong root identity")
    return row


def summarize(discovery, result, source):
    targets = discovery["targets"]
    outcomes = result["outcomes"]
    if len(targets) != len(outcomes) or len(outcomes) != 128:
        raise ValueError("Expected complete selected panel")
    report = []
    for target, item in zip(targets, outcomes, strict=True):
        if item["target"] != target:
            raise ValueError("Target order changed after treatment")
        original = discovery["cases"][target["position"]]["bestmove"]
        original_event = next(
            row for row in fields((source / target["position"] / "observed" / "stderr.txt").read_text().splitlines(),
                                  "C3X_R33_CLOSE")
            if row["event"] == target["target"]["event"]
        )
        folder = source / target["position"] / "observed"
        old_candidate = candidate(folder / "stderr.txt", target["target"])
        public = [re.sub(r"\b(?:nps|time) \d+ ?", "", line) for line in
                  (folder / "stdout.txt").read_text().splitlines()
                  if line.startswith(("info depth ", "bestmove "))]
        original_public = public_view("\n".join(public))
        rows = {}
        for arm, repeated in item["arms"].items():
            first = repeated[0]
            direct = first["target"]["close"]
            if direct["event"] != original_event["event"] or direct["stopped"] not in ("0", "1"):
                raise ValueError("Unmatched or invalid event return")
            if first["best"]["move"] != first["uci"][-1].split()[1]:
                raise ValueError("Final move and UCI disagree")
            new_candidate = first["source"]
            if new_candidate and new_candidate["id"] != target["target"]["candidate"]:
                raise ValueError("Unexpected root candidate")
            comparable = bool(old_candidate and new_candidate and new_candidate["alpha"] == old_candidate["alpha"]
                              and new_candidate["beta"] == old_candidate["beta"])
            changed_public = public_view("\n".join(first["uci"]))
            rows[arm] = {
                "best": first["best"]["move"],
                "final_changed": first["best"]["move"] != original,
                "public_changed": changed_public["iterations"] != original_public["iterations"],
                "final_card_changed": changed_public["final"] != original_public["final"],
                "metadata_only": first["uci"] != public and changed_public == original_public,
                "event_return_changed": direct["value"] != original_event["value"],
                "event_stopped": direct["stopped"] == "1",
                "null_tried": direct["null_tried"] == "1",
                "null_cut": direct["null_cut"] == "1",
                "board_replies": int(direct["replies"]),
                "root_completed": bool(new_candidate),
                "root_comparable": comparable,
                "root_value_changed": comparable and new_candidate["value"] != old_candidate["value"],
                "root_update_changed": comparable and new_candidate["update"] != old_candidate["update"],
                "old_root": old_candidate,
                "new_root": new_candidate,
            }
        if target["group"] == "0":
            a, b = rows["futility_off"], rows["both_off"]
            if any(a[key] != b[key] for key in
                   ("best", "public_changed", "final_card_changed", "event_return_changed",
                    "null_tried", "null_cut", "board_replies", "new_root")):
                raise ValueError("Null-ineligible negative control diverged")
        report.append({"position": target["position"], "stratum": target["group"],
                       "target": target["target"], "original_event": original_event,
                       "original_best": original, "arms": rows})
    by_group={}
    for group in ("0", "1"):
        subgroup=[r for r in report if r["stratum"] == group]
        counts={"positions":len(subgroup)}
        for arm in ("futility_off", "both_off"):
            trials=[row["arms"][arm] for row in subgroup]
            for key in ("final_changed", "public_changed", "final_card_changed", "metadata_only",
                        "event_return_changed", "event_stopped",
                        "null_tried", "null_cut", "root_completed", "root_comparable",
                        "root_value_changed", "root_update_changed"):
                counts[f"{arm}_{key}"]=sum(int(row[key]) for row in trials)
            counts[f"{arm}_board_replies"] = sum(row["board_replies"] for row in trials)
        by_group[group]=counts
    changed=[{"position":row["position"],"group":row["stratum"],"original":row["original_best"],
              **{arm:row["arms"][arm]["best"] for arm in row["arms"]}}
             for row in report if any(a["final_changed"] for a in row["arms"].values())]
    return {"source":discovery["source_sha256"],
            "counts":by_group,"changed":changed,"per_target":report}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("discovery","result","source_logs","output"):
        parser.add_argument(name,type=Path)
    args=parser.parse_args()
    summary=summarize(json.loads(args.discovery.read_text()),
                      json.loads(args.result.read_text()),args.source_logs)
    write(args.output,summary)


if __name__=="__main__":
    main()
