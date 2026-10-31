#!/usr/bin/env python3
"""Cross-receipt evidence type checks; NEVER joins different native processes."""
import argparse,json
from pathlib import Path

def audit(t3,r2,r3):
    if not t3.get("schema","").startswith("c3x023-P1-R2-T3-"):
        raise ValueError("T3_SCHEMA")
    if not r2.get("schema","").startswith("c3x024-P2-R2-"):
        raise ValueError("R2_SCHEMA")
    if not r3.get("schema","").startswith("c3x024-P2-R3-"):
        raise ValueError("R3_SCHEMA")
    x=r2["source_certificates"]
    y=r3["classification"]
    if (x["full_ancestor_root_arms"],x["partial_or_diverged_arms"],x["actual_continue_arms"])!=(2,2,4):
        raise ValueError("R2_COUNTS_CHANGED")
    if (y["full_C3b_root_candidate_reached_but_not_final_bestmove_arms"],
        y["partial_C3b_root_status_HOLD_arms"],y["actual_SEE_guard_continue_arms"],
        y["root_candidate_reached_and_final_bestmove_arms"])!=(2,2,4,0):
        raise ValueError("R3_COUNTS_CHANGED")
    t3cases={x["game_id"]:x for x in t3["root_cases"]}
    if set(t3cases)!={2,11}:raise ValueError("WRONG_DEVELOPMENT_GAMES")
    two=t3cases[2]["arms"]
    if [two[k]["bestmove"] for k in ("TT0_SEE_SHAM","TT1_SEE_SHAM","TT0_SEE_FLIP","TT1_SEE_FLIP")]!=["e1g1","e1g1","e1g1","b1b4"]:
        raise ValueError("T3_JOINT_ONLY_DRIFT")
    return {"schema":"c3x029-P9-R14-archived-certificate-type-audit-v1",
      "authority":"ARCHIVAL_CROSS_RECEIPT_CONSISTENCY_NOT_SAME_PROCESS_JOIN",
      "game2_joint_selected":"b1b4",
      "game2_source_guard_full_chain_is_joint_arm":False,
      "full_source_to_root_candidates_reached_but_lost":2,
      "joint_arm_target_guard_status":"ACTUAL_CONTINUE",
      "May11_partial_ancestor_not_promoted":True,
      "complete_causal_mediation":"NOT_IDENTIFIED"}

def main():
    p=argparse.ArgumentParser()
    for n in ("t3","r2","r3","out"):p.add_argument("--"+n,required=True)
    a=p.parse_args()
    d=audit(*[json.loads(Path(getattr(a,n)).read_text()) for n in ("t3","r2","r3")])
    Path(a.out).write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("R14_ARCHIVAL_TYPE_AUDIT",d["authority"])

if __name__=="__main__": main()
