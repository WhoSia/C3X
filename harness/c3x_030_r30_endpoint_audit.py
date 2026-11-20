"""Retrospective TT-event transport audit. Alpha-beta bounds are not exact ranks.

Inputs: R29 unseen-logs/result.json and abstentions.json.
Unit: physical event (not independent game or human participant).
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path


def read_identity(read):
    ignored = {"mask", "mask_move", "mask_value", "effective", "effective_value"}
    return {key: value for key, value in read.items() if key not in ignored}


def audit_trial(case, policy, arms):
    if set(arms) != {"sham", "mask", "restore"}:
        raise ValueError(f"Incomplete matched triplet: {case['id']}, {policy}")
    sham, mask, restore = (arms[k] for k in ("sham", "mask", "restore"))
    if sham != {k: v for k, v in restore.items() if k != "uci_changed"}:
        raise ValueError(f"Restoration differs: {case['id']}, {policy}")
    if read_identity(sham["read"]) != read_identity(mask["read"]):
        raise ValueError(f"Pre-treatment read differs: {case['id']}, {policy}")
    if sham["read"]["mask"] != "0" or mask["read"]["mask"] != "1":
        raise ValueError(f"Mask identity failed: {case['id']}, {policy}")
    if len(sham["masked"]) != 0 or len(mask["masked"]) != 1:
        raise ValueError(f"More than one read affected: {case['id']}, {policy}")
    event_attempt = int(sham["read"]["attempt"])
    baseline_producer = int(case["source_attempt"])
    if event_attempt > baseline_producer:
        raise ValueError("Post-producer treatment is invalid")
    child_control, child_mask = sham["direct_child"], mask["direct_child"]
    child_observable = child_control["stopped"] == child_mask["stopped"] == "0"
    target_control, target_mask = sham["target_candidate"], mask["target_candidate"]
    root_observable = target_control is not None and target_mask is not None
    choice_changed = sham["best"]["move"] != mask["best"]["move"]
    control_producer = int(sham["producer"]["attempt"])
    mask_producer = int(mask["producer"]["attempt"])
    child_changed = (child_control["child_value"] != child_mask["child_value"]
                     if child_observable else None)
    root_update_changed = (target_control["update"] != target_mask["update"]
                           if root_observable else None)
    score_a, score_b = sham["last_report"]["public"], mask["last_report"]["public"]
    return {
        "case": case["id"], "stratum": case["stratum"], "policy": policy,
        "read_seq": sham["read"]["seq"], "event_attempt": event_attempt,
        "baseline_producer_attempt": baseline_producer,
        "within_original_producer": event_attempt == baseline_producer,
        "child_return_changed": child_changed,
        "target_candidate_update_changed": root_update_changed,
        "target_candidate_update_is_rank": False,
        "cutoff_removed": bool(sham["cutoffs"]) and not bool(mask["cutoffs"]),
        "first_reply_changed": sham["replies"][:1] != mask["replies"][:1],
        "final_choice_changed": choice_changed,
        "control_choice": sham["best"]["move"], "masked_choice": mask["best"]["move"],
        "producer_changed": control_producer != mask_producer,
        "control_producer": control_producer, "masked_producer": mask_producer,
        "public_score_changed": (score_a["score"], score_a["bound"], score_a["kind"]) !=
                                (score_b["score"], score_b["bound"], score_b["kind"]),
        "control_score": [score_a["score"], score_a["bound"]],
        "masked_score": [score_b["score"], score_b["bound"]],
        "causal_scope": ("final-choice total effect; intermediate path not established" if choice_changed
                         else "local search effect; final choice unchanged"),
    }


def audit(unseen, abstentions):
    cases = unseen["positions"]
    names = [x["id"] for x in cases]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate position ID")
    trials = []
    for case in cases:
        for policy, arms in case["arms"].items():
            if policy not in {"move", "value"}:
                raise ValueError("Unrecognized treatment")
            trials.append(audit_trial(case, policy, arms))
    tested = {x["case"] for x in trials}
    missing = {x["id"] for x in cases} - tested
    absent = [x["case"] for x in abstentions]
    if len(absent) != len(set(absent)) or set(absent) != missing:
        raise ValueError("Abstention ledger does not match all untested positions")
    count = Counter()
    bins = defaultdict(Counter)
    for case in cases:
        bins[case["stratum"]]["positions"] += 1
    for row in trials:
        for tallies in (count, bins[row["stratum"]]):
            tallies["interventions"] += 1
            tallies[row["policy"] + "_reads"] += 1
            tallies["in_producer" if row["within_original_producer"] else "earlier"] += 1
            for name in ("first_reply_changed", "child_return_changed",
                         "target_candidate_update_changed", "final_choice_changed",
                         "producer_changed", "public_score_changed", "cutoff_removed"):
                if row[name] is True:
                    tallies[name] += 1
                elif row[name] is None:
                    tallies[name + "_unobserved"] += 1
    for row in abstentions:
        bins[row["stratum"]]["abstained_positions"] += 1
    count["positions"] = len(cases)
    count["tested_positions"] = len(tested)
    count["abstained_positions"] = len(missing)
    return {
        "status": "retrospective analysis of prior exposed cohort",
        "unit": "source event; multiple interventions may share a game",
        "limits": ["No independent human data", "No point estimate from alpha-beta bounds",
                   "Final move total effect does not establish node-to-node mediation",
                   "No external generalization from one TWIC issue"],
        "totals": dict(sorted(count.items())),
        "by_stratum": {k: dict(sorted(v.items())) for k, v in sorted(bins.items())},
        "final_choice_cases": [r for r in trials if r["final_choice_changed"]],
        "producer_update_cases": [r for r in trials if r["target_candidate_update_changed"]],
        "trials": trials,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("unseen_result", type=Path)
    ap.add_argument("abstentions", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()
    result = audit(json.loads(args.unseen_result.read_text()),
                   json.loads(args.abstentions.read_text()))
    result["input_sha256"] = {key: hashlib.sha256(getattr(args, key).read_bytes()).hexdigest()
                              for key in ("unseen_result", "abstentions")}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
