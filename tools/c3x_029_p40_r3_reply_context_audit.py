#!/usr/bin/env python3
"""P40/R3 audit of legal response UCI strings across different chess boards."""
import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_SHA="84f037f62b86a7ee34239921f609a9015a6ea8d4cdf351f41563ef78dc6dabcf"

def audit(j):
    assert j["game_events"]==8 and j["candidate_worlds"]==16
    rows=[]
    for case in j["cases"]:
        a,b=case["worlds"]
        x={r["opponent_reply"]:r["b"] for r in a["branches"]}
        y={r["opponent_reply"]:r["b"] for r in b["branches"]}
        assert len(x)==len(a["branches"]) and len(y)==len(b["branches"])
        shared=x.keys()&y.keys()
        all_keys=x.keys()|y.keys()
        assert shared and a["root_uci"]!=b["root_uci"]
        differing=[r for r in shared if x[r]!=y[r]]
        rows.append({"case_id":case["case_id"],"event":case["event_family"],
                     "roots":[a["root_uci"],b["root_uci"]],
                     "legal_counts":[len(x),len(y)],
                     "same_uci_count":len(shared),"union_count":len(all_keys),
                     "same_uci_different_b":len(differing),
                     "examples":[{"uci":r,"first_b":x[r],"second_b":y[r]}
                                 for r in sorted(differing)[:2]]})
    shared=sum(v["same_uci_count"] for v in rows)
    changed=sum(v["same_uci_different_b"] for v in rows)
    union=sum(v["union_count"] for v in rows)
    total=sum(sum(v["legal_counts"]) for v in rows)
    assert total==shared+union
    return {"status":"RETROSPECTIVE_CONTEXT_DEPENDENCE_NOT_CHESS_VALUE",
            "events":8,"worlds":16,"reply_occurrences":total,
            "identical_uci_pairs":shared,"different_proxy_pairs":changed,
            "pooled_different_fraction":changed/shared,
            "event_macro_different_fraction":sum(
                v["same_uci_different_b"]/v["same_uci_count"] for v in rows)/8,
            "limits":"Already exposed development data, correlated replies, B is not chess value",
            "cases":rows}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    q=p.parse_args()
    data=q.source.read_bytes()
    if hashlib.sha256(data).hexdigest()!=EXPECTED_SHA:
        raise ValueError("ORIGINAL_HASH_MISMATCH")
    result=audit(json.loads(data))
    q.out.parent.mkdir(parents=True,exist_ok=True)
    q.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(result["status"],result["different_proxy_pairs"],result["identical_uci_pairs"])
