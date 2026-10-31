#!/usr/bin/env python3
"""C3X P9: evidence-safe adjudication of a published T3 factorial receipt.

No engine run, source move reconstruction, or natural mediation claim.
"""
import argparse
import json
from pathlib import Path

ARMS=("TT0_SEE_SHAM","TT1_SEE_SHAM","TT0_SEE_FLIP","TT1_SEE_FLIP")
EXPECTED={"engine":"Stockfish16","positions":2}

def evaluate(receipt):
    if receipt.get("schema")!="c3x023-P1-R2-T3-two-preregistered-SEE-pruning-events-cross-real-physical-TT-first-v1":
        raise ValueError("UNEXPECTED_T3_SCHEMA")
    if receipt.get("treatment_validation",{}).get("number_distinct_preselected_chess_positions")!=2:
        raise ValueError("UNEXPECTED_POSITION_DENOMINATOR")
    cases=receipt.get("root_cases",[])
    if len(cases)!=2 or len({x["game_id"] for x in cases})!=2:
        raise ValueError("DUPLICATE_OR_MISSING_GAME")
    result=[]
    for c in cases:
        arms=c["arms"]
        if set(arms)!=set(ARMS):
            raise ValueError("FACTORIAL_ARMS_INCOMPLETE")
        for a in arms.values():
            if not isinstance(a["bestmove"],str) or len(a["bestmove"]) not in (4,5):
                raise ValueError("INVALID_UCI_SHAPE")
            if not isinstance(a["score_cp"],int) or not isinstance(a["nodes"],int) or a["nodes"]<=0:
                raise ValueError("INVALID_NATIVE_OUTCOME")
        moves=[arms[k]["bestmove"] for k in ARMS]
        joint_unique=moves[3] not in moves[:3]
        joint_indicator=[int(m==moves[3]) for m in moves]
        interaction=joint_indicator[3]-joint_indicator[1]-joint_indicator[2]+joint_indicator[0]
        result.append({"game_id":c["game_id"],"arm_bestmoves":dict(zip(ARMS,moves)),
                       "joint_only_new_candidate":joint_unique,
                       "joint_candidate_indicator_interaction":interaction,
                       "reported_final_scores_are_candidate_margins":False,
                       "per_candidate_score_margin_status":"NOT_IDENTIFIED",
                       "natural_mediation_status":"NOT_IDENTIFIED"})
    return {"schema":"c3x029-p9-r11-T3-public-aggregate-adjudication-v1",
            "scope":"POSTSELECTED_TWO_DEVELOPMENT_CHESS_POSITIONS",
            "source_run":"HISTORICAL_NO_NATIVE_EXECUTION","cases":result,
            "count_joint_only":sum(x["joint_only_new_candidate"] for x in result),
            "count_independent_chess_positions":len(result),
            "robustness_beyond_pinned_depth12":"UNMEASURED",
            "candidate_specific_margin":"NOT_IDENTIFIED"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--receipt",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    output=evaluate(json.loads(Path(args.receipt).read_text()))
    Path(args.out).write_text(json.dumps(output,sort_keys=True,indent=2)+"\n")
    print("C3X_P9_R11_PUBLIC_AGGREGATE",output["count_joint_only"],
          output["count_independent_chess_positions"])

if __name__=="__main__":
    main()
