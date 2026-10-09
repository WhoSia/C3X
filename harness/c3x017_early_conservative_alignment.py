#!/usr/bin/env python3
"""C3X 0.17: conservative depth-1+ root trace audit; never infer TT mediation.
Read-only; intentionally refuses positional zip alignment after root-order changes.
"""
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

KINDS = {"window_enter", "window_exit", "after_sort", "candidate"}
CORE = ("bestmove", "score_kind", "score_value", "score_flag", "nodes", "pv")

def check_events(events, censored):
    if not events:
        raise ValueError("EMPTY_TRACE")
    if [e.get("seq") for e in events] != list(range(1, len(events) + 1)):
        raise ValueError("NONCONTIGUOUS_SEQUENCE")
    if any(e.get("kind") not in KINDS or e.get("depth", 0) < 1 for e in events):
        raise ValueError("INVALID_EVENT")
    # Even with an apparent full event list, the trace cap is a hard scope boundary.
    return bool(censored)

def candidate_groups(events):
    groups = defaultdict(list)
    for e in events:
        if e["kind"] == "candidate":
            groups[(e["depth"], e["move"])].append(e)
    return groups

def audit_world(world):
    cells = world["cells"]
    for arm in ("O", "F", "Z"):
        if arm not in cells:
            raise ValueError("MISSING_ARM")
    traces = {arm: cells[arm]["passive_root_events"] for arm in ("O", "F", "Z")}
    censored = {arm: check_events(traces[arm], cells[arm]["trace_censored"]) for arm in traces}
    if any(censored.values()):
        return {"id": world["id"], "status": "TRACE_CENSORED", "censored": censored}
    for key in CORE:
        if cells["O"]["UCI"][key] != cells["Z"]["UCI"][key]:
            raise ValueError("NEGATIVE_CONTROL_OUTPUT_DRIFT")
    a, b = candidate_groups(traces["O"]), candidate_groups(traces["F"])
    keys = set(a) | set(b)
    different = []
    ambiguous = []
    for key in sorted(keys):
        left, right = a.get(key, []), b.get(key, [])
        if len(left) != len(right):
            ambiguous.append({"depth_move": list(key), "reason": "CANDIDATE_VISIT_MULTIPLICITY",
                              "count_O": len(left), "count_F": len(right)})
            continue
        # One depth/move event on both sides is uniquely identifiable by candidate.
        # Repeated visits can occur in aspiration re-search and cannot be assigned
        # a shared identity without trial/call IDs.
        if len(left) != 1:
            ambiguous.append({"depth_move": list(key), "reason": "REPEATED_VISITS_NEED_TRIAL_ID",
                              "count": len(left)})
            continue
        x, y = left[0], right[0]
        fields = ("child_return", "before", "after", "alpha", "beta")
        drift = [f for f in fields if x.get(f) != y.get(f)]
        if drift:
            different.append({"depth_move": list(key), "fields": drift,
                              "seq_O": x["seq"], "seq_F": y["seq"]})
    return {"id": world["id"], "status": "SCOPED_EVENT_ALIGNMENT",
            "candidate_differences": different, "ambiguous_groups": ambiguous,
            "counts": {"O": len(traces["O"]), "F": len(traces["F"]), "Z": len(traces["Z"])},
            "warning": "Not first physical divergence; depth+move matching is descriptive, not a causal mediator."}

def audit(source, source_sha):
    if len(source.get("worlds", [])) != 12 or source.get("new_native_processes") != 72:
        raise ValueError("FROZEN_COHORT_OR_PROCESS_COUNT_DRIFT")
    ids = [w["id"] for w in source["worlds"]]
    if ids != list(range(1, 13)):
        raise ValueError("ID_ORDER_DRIFT")
    rows = [audit_world(w) for w in source["worlds"]]
    return {"schema": "c3x017-early-depth-conservative-alignment-v1",
            "input_sha256": source_sha, "cases": rows,
            "status_counts": dict(Counter(r["status"] for r in rows)),
            "limits": ["No TT writer-reader instrumentation",
                       "Depth+move match does not identify iterative or aspiration trial",
                       "Repeated candidate visits withheld, not positionally zipped",
                       "Absence of detected difference is not evidence of absence",
                       "Root order intervention effects are not learned human chess motifs"]}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--native-json", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--expected-sha256", required=True)
    args = p.parse_args()
    raw = Path(args.native_json).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != args.expected_sha256:
        raise ValueError("RAW_SHA256_MISMATCH")
    result = audit(json.loads(raw), digest)
    Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("C3X017_EARLY_CONSERVATIVE_ALIGNMENT", result["status_counts"])

if __name__ == "__main__":
    main()
