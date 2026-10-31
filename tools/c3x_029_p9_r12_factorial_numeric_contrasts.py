#!/usr/bin/env python3
"""C3X P9-R12: descriptive four-arm numeric contrasts; not identified mediation."""
import argparse,json
from pathlib import Path
ARMS=("TT0_SEE_SHAM","TT1_SEE_SHAM","TT0_SEE_FLIP","TT1_SEE_FLIP")

def analyze(receipt):
    if receipt.get("schema")!="c3x023-P1-R2-T3-two-preregistered-SEE-pruning-events-cross-real-physical-TT-first-v1":
        raise ValueError("UNTRUSTED_SCHEMA")
    cases=receipt.get("root_cases",[])
    if len(cases)!=2 or len({c["game_id"] for c in cases})!=2:
        raise ValueError("EXPECTED_TWO_DISTINCT_GAMES")
    out=[]
    for c in cases:
        if set(c["arms"])!=set(ARMS):raise ValueError("INCOMPLETE_FACTORIAL")
        a=[c["arms"][k] for k in ARMS]
        if any(type(x["nodes"]) is not int or x["nodes"]<=0 or type(x["score_cp"]) is not int for x in a):
            raise ValueError("INVALID_SCALAR")
        nodes=[x["nodes"] for x in a]; scores=[x["score_cp"] for x in a]
        moves=[x["bestmove"] for x in a]
        out.append({"game_id":c["game_id"],
                    "nodes_four_arm_contrast":nodes[3]-nodes[1]-nodes[2]+nodes[0],
                    "reported_root_cp_four_arm_arithmetic_contrast":scores[3]-scores[1]-scores[2]+scores[0],
                    "root_cp_contrast_is_candidate_margin":False,
                    "root_cp_contrast_is_chess_value_effect":False,
                    "selection_indicator_contrast":int(moves[3]==moves[3])-int(moves[1]==moves[3])-int(moves[2]==moves[3])+int(moves[0]==moves[3]),
                    "unique_joint_candidate":moves[3] not in moves[:3],
                    "per_candidate_score_status":"UNMEASURED"})
    return {"schema":"c3x029-P9-R12-descriptive-factorial-numeric-v1",
            "source":"HISTORIC_PUBLISHED_AGGREGATE","independent_positions":2,
            "terms":"DESCRIPTIVE_WITHIN_POSTSELECTED_CASES_NOT_NATURAL_MEDIATION",
            "cases":out}

def main():
    p=argparse.ArgumentParser();p.add_argument("--receipt",required=True);p.add_argument("--out",required=True)
    args=p.parse_args();d=analyze(json.loads(Path(args.receipt).read_text()))
    Path(args.out).write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("C3X029_R12",[(x["game_id"],x["nodes_four_arm_contrast"]) for x in d["cases"]])

if __name__=="__main__":main()
