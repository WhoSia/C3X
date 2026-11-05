#!/usr/bin/env python3
"""P41/R3 exact legal-action cost audit before any independent value oracle."""
import argparse
import hashlib
import json
from pathlib import Path

SHA="84f037f62b86a7ee34239921f609a9015a6ea8d4cdf351f41563ef78dc6dabcf"

def audit(doc, node_budget=96000):
    if not isinstance(node_budget,int) or node_budget<=0:
        raise ValueError("BAD_NODE_BUDGET")
    if doc["game_events"]!=8 or doc["candidate_worlds"]!=16:
        raise ValueError("INVALID_ORIGINAL_DENOMINATOR")
    roots,replies,own,events=0,0,0,[]
    for case in doc["cases"]:
        row={"id":case["case_id"],"event":case["event_family"],
             "original_worlds":[]}
        for world in case["worlds"]:
            roots+=1
            rcount=len(world["branches"])
            replies+=rcount
            n=sum(branch["own_legal_reply_count"] for branch in world["branches"])
            own+=n
            if world["expanded_legal_moves"]!=1+rcount+n:
                raise ValueError("EXPANSION_COUNT_MISMATCH")
            row["original_worlds"].append({"root":world["root_uci"],
                  "legal_opponent_replies":rcount,
                  "legal_own_continuations":n,
                  "projected_full_value_nodes":n*node_budget})
        events.append(row)
    if (roots,replies,own)!=(16,644,24894):
        raise ValueError("ORIGINAL_BRANCH_LEDGER_MISMATCH")
    return {"status":"P41_R3_REQUESTED_NODE_COST_PROJECTION_NOT_NATIVE_RUN",
            "original_events":len(events),"original_roots":roots,
            "opponent_first_replies":replies,
            "own_reply_candidates":own,
            "total_legal_expansions":roots+replies+own,
            "native_nodes_requested_per_action":node_budget,
            "projected_native_nodes":own*node_budget,
            "forecast_cost_is_observed":False,
            "universal_low_regret_possible_from_sample":False,
            "single_negative_counterexample_can_refute":True,
            "events":events}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    raw=args.original.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError("SOURCE_SHA_MISMATCH")
    result=audit(json.loads(raw))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    print(result["status"],result["projected_native_nodes"])
