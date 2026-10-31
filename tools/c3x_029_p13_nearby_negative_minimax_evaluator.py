#!/usr/bin/env python3
"""C3X P13: evaluate precomputed, independently verified binary chess concepts.

Evaluation ONLY. Source-position construction, engine scores, and chess legality
must be independently verified before this tool's numbers have empirical authority.
"""
import json
import argparse
from pathlib import Path

GROUPS=("positive","negative","nearby_negative")

def evaluate(rows, expected_groups=GROUPS):
    if not rows: raise ValueError("EMPTY_INPUT")
    ids=[r.get("case_id") for r in rows]
    if any(not isinstance(i,str) or not i for i in ids) or len(set(ids))!=len(ids):
        raise ValueError("INVALID_OR_DUPLICATED_CASE_ID")
    got={r.get("group") for r in rows}
    if got!=set(expected_groups): raise ValueError("INCOMPLETE_OR_UNKNOWN_GROUPS")
    if any(type(r.get("predicted")) is not bool for r in rows):
        raise ValueError("PREDICTION_NOT_BINARY")
    if any(not isinstance(r.get("game_id"),str) or not r["game_id"] for r in rows):
        raise ValueError("MISSING_GAME_CLUSTER")
    by={}
    for g in expected_groups:
        subset=[r for r in rows if r["group"]==g]
        if not subset: raise ValueError("EMPTY_GROUP")
        correct=sum(r["predicted"]==(g=="positive") for r in subset)
        by[g]={"correct":correct,"total":len(subset),"accuracy":correct/len(subset)}
    scores={k:by[k]["accuracy"] for k in expected_groups}
    return {"status":"SYNTACTIC_EVALUATION_ONLY","worst_group_accuracy":min(scores.values()),
            "accuracy_by_group":by,"distinct_game_clusters":len({r["game_id"] for r in rows}),
            "caution":"HOLD until game-disjoint provenance and legal/engine-label replay validated"}

def main():
    a=argparse.ArgumentParser();a.add_argument("--input",required=True);a.add_argument("--output",required=True)
    x=a.parse_args()
    rows=json.loads(Path(x.input).read_text())
    Path(x.output).write_text(json.dumps(evaluate(rows),ensure_ascii=False,indent=2)+"\n")

if __name__=="__main__":main()
