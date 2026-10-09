#!/usr/bin/env python3
"""C3X 0.17: independently audit historical depth>=8 root event source-native JSON.
Order-dependent sequence alignment is only a retained event comparison; not causal mediation.
"""
import argparse, hashlib, json
from collections import Counter
from pathlib import Path
SCHEMA="c3x017-depth8-first-retained-semantic-event-audit-v2"
INPUT_SHA="0c25ff11f28ced23e8d3ead2219861f350d8ba27d93ba457617abe65347da564"
def cls(x,y):
    if x["kind"]!=y["kind"] or x["depth"]!=y["depth"]:
        return "EVENT_ALIGNMENT_AMBIGUOUS_KIND_DEPTH"
    if x["kind"]=="candidate" and (x.get("move"),x.get("index"))!=(y.get("move"),y.get("index")):
        return "EVENT_ALIGNMENT_AMBIGUOUS_CANDIDATE"
    if (x.get("alpha"),x.get("beta"))!=(y.get("alpha"),y.get("beta")):
        return "ALPHA_BETA_WINDOW_DIFFERENT"
    if x.get("child_return")!=y.get("child_return"):
        return "CHILD_RETURN_DIFFERENT"
    if (x.get("before"),x.get("after"))!=(y.get("before"),y.get("after")):
        return "ROOT_SCORE_STORAGE_DIFFERENT"
    if x.get("value")!=y.get("value"):
        return "WINDOW_RETURN_VALUE_DIFFERENT"
    if x.get("first_move")!=y.get("first_move"):
        return "FIRST_RANKED_MOVE_DIFFERENT"
    if x.get("first_score")!=y.get("first_score"):
        return "FIRST_RANKED_SCORE_DIFFERENT"
    return None
def audit(src):
    rows=[]
    assert src["new_native_processes"]==72 and len(src["worlds"])==12
    for w in src["worlds"]:
        a=w["cells"]["O"]["passive_root_events"]
        b=w["cells"]["F"]["passive_root_events"]
        first=None
        for i,(x,y) in enumerate(zip(a,b)):
            if (kind:=cls(x,y)):
                first={"index_zero_based":i,"classification":kind,
                       "depth_reference":x["depth"],"depth_intervention":y["depth"],
                       "reference":x,"intervention":y}
                break
        if first is None and len(a)!=len(b):
            first={"index_zero_based":min(len(a),len(b)),
                   "classification":"EVENT_ALIGNMENT_AMBIGUOUS_LENGTH"}
        rows.append({"id":w["id"],"geometry_stratum":w["candidate_stratum"],
                     "categorical_bestmove_changed":w["contrasts"]["categorical_bestmove_changed"],
                     "event_count_O":len(a),"event_count_F":len(b),
                     "trace_truncated_O":w["cells"]["O"]["trace_censored"],
                     "trace_truncated_F":w["cells"]["F"]["trace_censored"],
                     "first_retained_difference":first})
    return {"schema":SCHEMA,"input_json_sha256":INPUT_SHA,
        "source_run":37951814506,"count":len(rows),
        "categories":dict(Counter((w["first_retained_difference"] or {"classification":"NONE"})["classification"] for w in rows)),
        "cases":rows,
        "limits":["depth8+ only: no claim about first physical divergence at depths1..7",
                  "index event alignment is ambiguous after a move-order mismatch",
                  "root nodes alone are not operator-identity signatures",
                  "no observed physical TT writer/reader: natural mediation HOLD",
                  "no claim about named tactic semantic cause or engine latent concepts"]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--native-json",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    b=Path(a.native_json).read_bytes()
    if hashlib.sha256(b).hexdigest()!=INPUT_SHA:
        raise RuntimeError("C3X017_ORIGINAL_NATIVE_BYTES_DRIFT")
    j=audit(json.loads(b))
    if j["categories"]!={"CHILD_RETURN_DIFFERENT":3,"ALPHA_BETA_WINDOW_DIFFERENT":7,"NONE":2}:
        raise RuntimeError("C3X017_SOURCE_EVENT_COURT_DRIFT")
    Path(a.out).write_text(json.dumps(j,indent=2,sort_keys=True)+"\n")
    print("C3X017_DEPTH8_TWELVE_SOURCE_EVENT_INDEPENDENT_SCOPED_PASS",j["categories"])
if __name__=="__main__":main()
