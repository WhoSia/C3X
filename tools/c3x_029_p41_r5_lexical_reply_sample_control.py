"""Retrospective lexical-k3 truncation on original P39 chess-law proxy branches.

Never use as evidence against Cui's ENGINE-RANKED top-k partial tree or as
chess VALUE. Exact historical eight-game original digest required.
"""
import argparse
import hashlib
import json
from pathlib import Path

ORIGINAL_SHA="84f037f62b86a7ee34239921f609a9015a6ea8d4cdf351f41563ef78dc6dabcf"


def source(path):
    b=Path(path).read_bytes()
    if hashlib.sha256(b).hexdigest()!=ORIGINAL_SHA:
        raise ValueError("HOLD_ORIGINAL_SHA")
    return json.loads(b)


def audit(original,k=3):
    if original["game_events"]!=8 or original["candidate_worlds"]!=16 or k<1:
        raise ValueError("HOLD_SOURCE_AND_K")
    records=[]
    for case in original["cases"]:
        for world in case["worlds"]:
            branches=world["branches"]
            if not branches:
                raise ValueError("HOLD_NO_BRANCHES")
            if len(set(row["opponent_reply"] for row in branches))!=len(branches):
                raise ValueError("HOLD_DUPLICATE_LEGAL_REPLY")
            full=max(row["b"] for row in branches)
            if full!=world["w"]:
                raise ValueError("HOLD_ARCHIVED_FULL_W_INCONSISTENT")
            chosen=sorted(branches,key=lambda row:row["opponent_reply"])[:k]
            limited=max(row["b"] for row in chosen)
            if limited>full:
                raise ValueError("HOLD_SET_MONOTONICITY")
            records.append({
                "case_id":case["case_id"],
                "event_family":case["event_family"],
                "root_uci":world["root_uci"],
                "complete_reply_count":len(branches),
                "sampled_reply_count":len(chosen),
                "true_w_full_proxy":full,
                "lexical_k_w_proxy":limited,
                "missed_w_gap":full-limited})
    if len(records)!=16:
        raise ValueError("HOLD_NOT_SIXTEEN")
    return {"status":"P41_R5_POSTHOC_LEXICAL_REPLY_SAMPLE_CONTROL_NOT_CHESS_VALUE",
            "root_worlds":16,"source_events":8,"lexical_k":k,
            "worlds_missing_worst":sum(item["missed_w_gap"]>0 for item in records),
            "sum_missed_w_gap":sum(item["missed_w_gap"] for item in records),
            "max_missed_w_gap":max(item["missed_w_gap"] for item in records),
            "limits":["source-exposed historical sample",
                      "lexical k is NOT Cui engine-ranked top k",
                      "response mobility is NOT chess value",
                      "not independent chess evidence"],
            "cases":records}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    result=audit(source(a.source))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("P41_R5_POSTHOC",result["worlds_missing_worst"],"/16")
