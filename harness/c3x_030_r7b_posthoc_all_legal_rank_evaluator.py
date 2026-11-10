#!/usr/bin/env python3
"""C3X 0.30/R7-B: posthoc rank all legal Qwen moves against frozen old nominees.

Only AFTER all five blind inference score files exist and SHA-checked
source/legality inputs have been read does this program access R5 audit.
Targets are 4 existing source-nominated alternatives, NOT actual reference
puzzle solutions. Two pairs reuse original FENs, so rows are correlated.
"""
import argparse
import hashlib
import json
from pathlib import Path

from c3x_030_r6a_actual_open_decoder_blind_arm import ARMS,MODEL_ID,MODEL_REVISION
from c3x_030_r6b_posthoc_decoder_recovery_evaluator import R5_AUDIT_SHA,ARM_SHA
from c3x_030_r7a_real_qwen_all_legal_token_scorer import SCHEMA as SCORE_SCHEMA
from c3x_030_r7s_blind_all_legal_support_freeze import SCHEMA as SUPPORT_SCHEMA

SCHEMA="c3x030-r7b-posthoc-five-arm-all-legal-ranking-v1"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rank_and_grade(audit,scores,support,source_sha,support_sha):
    if source_sha!=R5_AUDIT_SHA or audit.get("schema")!="c3x030-r5-parfenova-inspired-move-hint-mask-protocol-v1":
        raise ValueError("R030_R7_HOLD_FROZEN_TRUTH_BYTES")
    if (support.get("schema")!=SUPPORT_SCHEMA or len(support.get("entries",[]))!=4
        or set(scores)!=set(ARMS)):
        raise ValueError("R030_R7_HOLD_SUPPORT_OR_ARM_COUNT")
    cases=audit.get("cases",[])
    if len(cases)!=2 or any(len(c.get("candidate_control_packets",[]))!=2 for c in cases):
        raise ValueError("R030_R7_HOLD_FOUR_NOMINATED_MOVES")
    targets=[item["root_uci_source_only_label_not_decoder_input"]
             for c in cases for item in c["candidate_control_packets"]]
    result=[]
    for arm in ARMS:
        src=scores[arm]
        if (src.get("schema")!=SCORE_SCHEMA or src.get("condition")!=arm
            or src.get("model_id")!=MODEL_ID or src.get("model_revision")!=MODEL_REVISION
            or src.get("input_blind_arm_sha256")!=ARM_SHA[arm]
            or src.get("legal_support_manifest_sha256")!=support_sha
            or src.get("source_target_and_original_reference_never_seen_during_inference") is not True
            or len(src.get("entries",[]))!=4):
            raise ValueError("R030_R7_HOLD_MODEL_PROVENANCE_OR_JUDGE_LEAK")
        details=[]
        for i,row in enumerate(src["entries"]):
            legal=support["entries"][i]["legal_move_ucis"]
            full=row["full_summed_log_probability_ranking"]
            rank_ucis=[r["uci"] for r in full]
            alt=row["full_mean_per_token_ranking_ucis"]
            if (row["ordinal"]!=i or row["legal_actions_scored"]!=len(legal)
                or len(rank_ucis)!=len(legal) or set(rank_ucis)!=set(legal)
                or len(alt)!=len(legal) or set(alt)!=set(legal)):
                raise ValueError("R030_R7_HOLD_INCOMPLETE_OR_FABRICATED_LEGAL_RANKING")
            if len(set(rank_ucis))!=len(legal) or len(set(alt))!=len(legal):
                raise ValueError("R030_R7_HOLD_DUPLICATE_RANKED_MOVES")
            if rank_ucis!=[x["uci"] for x in sorted(full,key=lambda z:(-z["summed_log_probability"],z["uci"]))]:
                raise ValueError("R030_R7_HOLD_PRIMARY_SORT_DRIFT")
            nominated=targets[i]
            if nominated not in legal:
                raise ValueError("R030_R7_HOLD_ORIGINAL_NOMINATED_NOT_LEGAL")
            rank=rank_ucis.index(nominated)+1
            rank2=alt.index(nominated)+1
            details.append({
                "ordinal":i,
                "original_source_nominated_target_uci":nominated,
                "total_legal_moves":len(legal),
                "primary_target_rank_1based":rank,
                "primary_top1_match":rank==1,
                "primary_top3_match":rank<=3,
                "per_token_mean_rank_1based_secondary":rank2,
                "secondary_top1":rank2==1,
                "secondary_top3":rank2<=3,
                "top3_primary":rank_ucis[:3],
                "top3_secondary":alt[:3],
                "true_puzzle_reference_best_move":None
            })
        result.append({
            "arm":arm,"n_nominated_targets":4,
            "primary_top1":sum(x["primary_top1_match"] for x in details),
            "primary_top3":sum(x["primary_top3_match"] for x in details),
            "secondary_mean_token_top1":sum(x["secondary_top1"] for x in details),
            "secondary_mean_token_top3":sum(x["secondary_top3"] for x in details),
            "details":details
        })
    return {
        "schema":SCHEMA,"status":"ACTUAL_MODEL_TOKEN_SCORING_HISTORICAL_NOMINEE_RANKS_ONLY",
        "owned_original_parfenova_drive_pdf":"https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view",
        "truth_read_only_after_all_five_model_score_files":True,
        "r5_truth_sha256":source_sha,"legal_support_sha256":support_sha,
        "model_id":MODEL_ID,"model_revision":MODEL_REVISION,
        "primary_metric":"sum of UCI continuation token log probabilities, no EOS",
        "secondary_metric":"per-token mean, not primary string probability",
        "source_nominees_not_llm_generated_move_or_gold_puzzle_reference":True,
        "nonindependent_four_rows_reuse_two_original_board_positions":True,
        "not_original_Parfenova_200_puzzles":True,
        "no_original_search_source_intervention":True,
        "arms":result
    }


def main():
    p=argparse.ArgumentParser()
    for x in ("audit","score-dir","legal-support","out"):
        p.add_argument("--"+x,required=True)
    a=p.parse_args()
    truthsha=digest(a.audit)
    if truthsha!=R5_AUDIT_SHA:
        raise ValueError("R030_R7_HOLD_FROZEN_AUDIT_SHA")
    scores={}
    for arm in ARMS:
        fn=Path(a.score_dir)/("R7_ALL_LEGAL_"+arm+".json")
        scores[arm]=json.loads(fn.read_text(encoding="utf-8"))
    sup=json.loads(Path(a.legal_support).read_text(encoding="utf-8"))
    audit=json.loads(Path(a.audit).read_text(encoding="utf-8"))
    out=rank_and_grade(audit,scores,sup,truthsha,digest(a.legal_support))
    dest=Path(a.out)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    for x in out["arms"]:
        print("R030_R7_FINAL_RANK",x["arm"],"top1",x["primary_top1"],"/4",
              "top3",x["primary_top3"],"/4",
              "mean-token-alt-top3",x["secondary_mean_token_top3"],"/4")
    print("R030_R7_FIVE_ARM_FINAL_SHA",digest(dest))


if __name__=="__main__":
    main()
