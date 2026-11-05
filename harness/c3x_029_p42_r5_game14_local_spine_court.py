#!/usr/bin/env python3
"""C3X P42/R5: conservative actual-source local causal-spine adjudicator.

Raw logs contain source TT keys and remain PRIVATE. This checker returns
only aggregate status; it never promotes a local parent update to root cause.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

PREFIX = "c3x042_r5 "
EVENTS = (
    "GUARD_FALLTHROUGH", "ACTUAL_DO_MOVE",
    "MAIN_CHILD_ENTERED", "QSEARCH_CHILD_ENTERED",
    "CHILD_RETURNED_TO_PARENT", "PARENT_VALUE_ASSESSED",
    "PARENT_BESTVALUE_ASSIGNED",
)
CORE = ("GUARD_FALLTHROUGH", "ACTUAL_DO_MOVE",
        "CHILD_RETURNED_TO_PARENT", "PARENT_VALUE_ASSESSED")
REQUIRED_FIELDS = ("event", "seq", "parent64", "child64", "key64",
                   "root_call", "root_move", "move", "did_move",
                   "child_entered", "score", "pre_best", "alpha", "beta")
NUMERIC = set(REQUIRED_FIELDS)-{"event"}

def parse(text: str) -> list[dict]:
    rows=[]
    for line in text.splitlines():
        if not line.startswith(PREFIX):
            continue
        row=dict(re.findall(r"([a-z_0-9]+)=([^\s]+)",line[len(PREFIX):]))
        if not set(REQUIRED_FIELDS)<=set(row):
            raise ValueError("P42_R5_HOLD_INCOMPLETE_NATIVE_TRACE")
        if row["event"] not in EVENTS:
            raise ValueError("P42_R5_HOLD_UNKNOWN_NATIVE_EVENT")
        for key in NUMERIC:
            try:
                row[key]=int(row[key])
            except ValueError as ex:
                raise ValueError("P42_R5_HOLD_NONNUMERIC_"+key) from ex
        rows.append(row)
    return rows

def adjudicate(text: str, expected_processes: int=2) -> dict:
    if type(expected_processes) is not int or expected_processes<=0:
        raise ValueError("P42_R5_HOLD_INVALID_REPLAY_COUNT")
    rows=parse(text)
    runs=[]
    current=[]
    for row in rows:
        if row["event"]=="GUARD_FALLTHROUGH" and current:
            runs.append(current)
            current=[]
        elif not current and row["event"]!="GUARD_FALLTHROUGH":
            return _hold("ORPHAN_EVENT",len(runs))
        current.append(row)
    if current:
        runs.append(current)
    if len(runs)!=expected_processes:
        return _hold("WRONG_REPLAY_COUNT",len(runs))
    counts={"full_local_spine":0,"parent_assignment":0,"parent_value_exceeds_alpha":0,"bestvalue_only_assignments":0,"window_fail_low_like":0,"window_in_range":0,"window_fail_high_like":0}
    for run in runs:
        e=[x["event"] for x in run]
        if len(run)>7 or any(x["seq"]!=idx+1 for idx,x in enumerate(run)):
            return _hold("UNBOUNDED_OR_NONMONOTONE",len(runs))
        identity=tuple(run[0][k] for k in ("parent64","child64","root_call",
                                          "root_move","move"))
        if any(tuple(x[k] for k in ("parent64","child64","root_call",
                                   "root_move","move"))!=identity for x in run):
            return _hold("EVENT_IDENTITY_DRIFT",len(runs))
        if any(run[0][k]==0 for k in ("parent64","child64")):
            return _hold("NULL_PARENT_OR_CHILD",len(runs))
        expect=["GUARD_FALLTHROUGH","ACTUAL_DO_MOVE"]
        expect.append("MAIN_CHILD_ENTERED" if "MAIN_CHILD_ENTERED" in e
                      else "QSEARCH_CHILD_ENTERED")
        expect+=["CHILD_RETURNED_TO_PARENT","PARENT_VALUE_ASSESSED"]
        if "PARENT_BESTVALUE_ASSIGNED" in e:
            expect.append("PARENT_BESTVALUE_ASSIGNED")
        if e!=expect:
            return _hold("LOCAL_PATH_INCOMPLETE_OR_REORDERED",len(runs))
        if run[0]["key64"]!=run[0]["parent64"]:
            return _hold("GUARD_KEY_MISMATCH",len(runs))
        if any(x["key64"]!=run[0]["child64"] for x in run[1:4]):
            return _hold("CHILD_KEY_MISMATCH",len(runs))
        if any(x["key64"]!=run[0]["parent64"] for x in run[4:]):
            return _hold("RETURNED_PARENT_KEY_MISMATCH",len(runs))
        if any(x["did_move"]!=1 for x in run[1:]) or any(
            x["child_entered"]!=1 for x in run[2:]):
            return _hold("SOURCE_ACTIVITY_FLAG_MISSING",len(runs))
        if run[3]["score"]!=run[4]["score"]:
            return _hold("RETURNED_SCORE_NOT_ADOPTED_IN_PARENT_CANDIDATE",len(runs))
        # score>alpha is a numeric comparison, NOT evidence alpha was written:
        # a source fail-high may break before the original alpha assignment.
        # Window relations are source-search diagnostics, never independently
        # verified chess value bounds or causal root certificates.
        assessed=run[4]
        if assessed["score"]<=assessed["alpha"]:
            counts["window_fail_low_like"]+=1
        elif assessed["score"]>=assessed["beta"]:
            counts["window_fail_high_like"]+=1
        else:
            counts["window_in_range"]+=1
        if assessed["score"]>assessed["alpha"]:
            counts["parent_value_exceeds_alpha"]+=1
        if "PARENT_BESTVALUE_ASSIGNED" in e:
            if run[4]["score"]<=run[4]["pre_best"] or run[5]["score"]!=run[4]["score"]:
                return _hold("PARENT_ASSIGNMENT_CONTRADICTED",len(runs))
            counts["parent_assignment"]+=1
            if assessed["score"]<=assessed["alpha"]:
                counts["bestvalue_only_assignments"]+=1
        else:
            if run[4]["score"]>run[4]["pre_best"]:
                return _hold("EXPECTED_ADOPTION_EVENT_ABSENT",len(runs))
        counts["full_local_spine"]+=1
    return {
        "status":"LOCAL_EXACT_GUARD_CHILD_PARENT_WITNESS_ONLY",
        "replays":len(runs),"counts":counts,
        "window_relation_is_not_a_certified_exact_score_bound":True,
        "actual_chess_value_verified":False,
        "full_ancestor_to_unrestricted_root_certified":False,
        "unique_natural_TT_mediation_certified":False,
        "source_keys_exposed":False,
        "claim_ceiling":"Observed local path, NOT a natural mediation or strategic explanation."
    }

def _hold(reason: str, n: int) -> dict:
    return {"status":"HOLD_"+reason, "replays":n,
            "full_ancestor_to_unrestricted_root_certified":False,
            "unique_natural_TT_mediation_certified":False,
            "source_keys_exposed":False}

def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--private-trace",required=True)
    p.add_argument("--public-out",required=True)
    p.add_argument("--replays",type=int,default=2)
    args=p.parse_args()
    summary=adjudicate(Path(args.private_trace).read_text(),args.replays)
    path=Path(args.public_out)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n")
    print("C3X042_R5",summary["status"])
    if summary["status"]!="LOCAL_EXACT_GUARD_CHILD_PARENT_WITNESS_ONLY":
        raise SystemExit(2)

if __name__=="__main__":
    main()
