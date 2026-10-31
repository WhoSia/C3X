#!/usr/bin/env python3
"""Bound-sound root candidate pair comparisons within ONE matching native attempt.

This is mathematical source-independent contract logic, not a Stockfish native observer.
"""
import argparse,json
from pathlib import Path
KINDS={"exact","lower","upper"}

def interval(entry):
    if entry.get("kind") not in KINDS or type(entry.get("cp")) is not int:
        raise ValueError("INVALID_SCORE_BOUND")
    v=entry["cp"];k=entry["kind"]
    return (v if k!="upper" else None,v if k!="lower" else None)

def compare(a,b):
    required=("engine_sha256","process_id","treatment_arm","root_call","iteration_depth","aspiration_attempt","score_pov")
    if any(a.get(k)!=b.get(k) or a.get(k) is None for k in required):
        return {"status":"ABSTAIN_INCOMPARABLE_SOURCE_COORDINATES"}
    if a.get("score_pov") not in ("white","black","side_to_move"):
        return {"status":"ABSTAIN_SCORE_POV_UNKNOWN"}
    if not a.get("completed") or not b.get("completed"):
        return {"status":"ABSTAIN_INCOMPLETE_CANDIDATE_SEARCH"}
    if not a.get("candidate_uci") or not b.get("candidate_uci") or a["candidate_uci"]==b["candidate_uci"]:
        return {"status":"ABSTAIN_MISSING_OR_DUPLICATE_CANDIDATES"}
    lo_a,hi_a=interval(a);lo_b,hi_b=interval(b)
    if lo_a is not None and hi_b is not None and lo_a>hi_b:
        return {"status":"CERTIFIED_STRICT_A_GREATER_B"}
    if lo_b is not None and hi_a is not None and lo_b>hi_a:
        return {"status":"CERTIFIED_STRICT_B_GREATER_A"}
    if lo_a is not None and hi_a is not None and lo_b is not None and hi_b is not None and lo_a==hi_a==lo_b==hi_b:
        return {"status":"CERTIFIED_EQUAL_EXACT"}
    return {"status":"ABSTAIN_OVERLAPPING_OR_ONE_SIDED_BOUNDS"}

def main():
    p=argparse.ArgumentParser();p.add_argument("--input",required=True)
    d=json.loads(Path(p.parse_args().input).read_text())
    print(json.dumps(compare(d["a"],d["b"]),sort_keys=True))

if __name__=="__main__":main()
