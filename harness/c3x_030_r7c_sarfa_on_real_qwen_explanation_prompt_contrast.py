#!/usr/bin/env python3
"""C3X 0.30/R7-C — REAL model prompt contrast through ORIGINAL SARFA Eq1–4.

Parfenova (2026) original owned Drive PDF:
https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view
Puri et al. (2020) SARFA original owned Drive PDF:
https://drive.google.com/file/d/1C_c0AvNkEtzB2z6Nbji_NdRxlRpODgjs/view

Treated = model log-likelihood of each original legal UCI after receiving
a commentary context. Comparator = FEN ONLY. Source-selected action is
the previously nominated old chess root, *not* an independent puzzle
reference. The original SARFA kernel measures P_treated(a*)-
P_FEN(a*) and whether off-target legal-move preference changed.

Raw model log probabilities are normalized only over ALL legal actions of
the frozen source position; this is a choice-set conditional distribution,
NOT the LLM's unconstrained actual generation distribution. No raw
Stockfish search intervention or naturally generated explanation involved.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from c3x_030_r1_sarfa_logdomain import sarfa_logdomain
from c3x_030_r6a_actual_open_decoder_blind_arm import ARMS,MODEL_ID,MODEL_REVISION
from c3x_030_r6b_posthoc_decoder_recovery_evaluator import R5_AUDIT_SHA
from c3x_030_r7a_real_qwen_all_legal_token_scorer import SCHEMA as SCORER_SCHEMA

SCHEMA="c3x030-r7c-actual-qwen-prompt-sarfa-all-legal-v1"
R7_MODEL_JSON_SHA={
 "fen_only":"01d42dbee00f103dc496b21ded53e8015be6c0b3ec62b94084532a6a83770212",
 "explanation_only":"d9eed0b4fe7096893f4d791f455dcf0fca13d2c1146ff75b34063397d3f1f9ed",
 "fen_plus_unmasked":"da53c2ab45f8bc1ca326163c9b1c822b3d1448d4a196b23c37cba98081867828",
 "fen_plus_strict_masked":"13fe7b0881436e41dc6d3345d71fddbde3f9e1f63dc8cbf0dfa6af94f1370e6d",
 "fen_plus_unrelated_foil":"f7d4e2d1b8fbc2b69dd6089ccc763887b997641fc079cf6fa766b1b6693c848e",
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def vector(record):
    if (not isinstance(record,dict) or not isinstance(record.get("full_summed_log_probability_ranking"),list)
        or record.get("legal_actions_scored")!=len(record["full_summed_log_probability_ranking"])):
        raise ValueError("R030_R7C_HOLD_COMPLETE_SCORE_VECTOR")
    vec={}
    for row in record["full_summed_log_probability_ranking"]:
        if (set(row)!={"uci","summed_log_probability","mean_log_probability_per_token",
                        "continuation_tokens"} or type(row["uci"]) is not str
            or type(row["summed_log_probability"]) not in (int,float)
            or not math.isfinite(row["summed_log_probability"])):
            raise ValueError("R030_R7C_HOLD_MALFORMED_ACTUAL_SCORE")
        if row["uci"] in vec:
            raise ValueError("R030_R7C_HOLD_DUPLICATE_MOVE")
        vec[row["uci"]]=row["summed_log_probability"]
    if len(vec)<3:
        raise ValueError("R030_R7C_HOLD_TOO_FEW_CANDIDATES")
    return vec


def analyze(scores,audit,audit_sha):
    if audit_sha!=R5_AUDIT_SHA or audit.get("schema")!="c3x030-r5-parfenova-inspired-move-hint-mask-protocol-v1":
        raise ValueError("R030_R7C_HOLD_SOURCE_AUDIT_SHA")
    cases=audit.get("cases",[])
    if len(cases)!=2 or any(len(c.get("candidate_control_packets",[]))!=2 for c in cases):
        raise ValueError("R030_R7C_HOLD_EXPECTED_FOUR_ROOTS")
    targets=[{"case_id":c["case_id"],"root":i["root_uci_source_only_label_not_decoder_input"]}
             for c in cases for i in c["candidate_control_packets"]]
    if set(scores)!=set(ARMS):
        raise ValueError("R030_R7C_HOLD_FIVE_MODEL_ARMS")
    for arm,report in scores.items():
        if (report.get("schema")!=SCORER_SCHEMA or report.get("condition")!=arm
            or report.get("model_id")!=MODEL_ID or report.get("model_revision")!=MODEL_REVISION
            or report.get("source_target_and_original_reference_never_seen_during_inference") is not True
            or len(report.get("entries",[]))!=4):
            raise ValueError("R030_R7C_HOLD_ACTUAL_MODEL_PROVENANCE")
    base=scores["fen_only"]["entries"]
    results=[]
    for arm in ARMS:
        if arm=="fen_only": continue
        allrows=[]
        for idx,(original,treatment) in enumerate(zip(base,scores[arm]["entries"])):
            if original.get("ordinal")!=idx or treatment.get("ordinal")!=idx:
                raise ValueError("R030_R7C_HOLD_CROSS_ARM_ORDINAL_DRIFT")
            baseline=vector(original)
            treated=vector(treatment)
            if set(baseline)!=set(treated):
                raise ValueError("R030_R7C_HOLD_NONIDENTICAL_ALL_LEGAL_SUPPORT")
            target=targets[idx]["root"]
            if target not in baseline:
                raise ValueError("R030_R7C_HOLD_ORIGINAL_NOMINATED_TARGET")
            attribution=sarfa_logdomain(treated,baseline,target,temperature=1.0)
            allrows.append({
                "ordinal":idx,"source_case_id":targets[idx]["case_id"],
                "source_nominated_move":target,
                "number_original_legal_moves":len(baseline),
                "normalized_over_legally_valid_action_set_only":True,
                "source_chess_search_was_not_intervened":True,
                "treated_minus_fen_only_candidate_log_likelihood":treated[target]-baseline[target],
                "treated_minus_fen_only_selected_probability":attribution["specificity_delta_raw_signed"],
                "offtarget_kl":attribution["offtarget_kl_perturbed_to_original"],
                "sarfa_positive_saliency":attribution["sarfa_harmonic_saliency"],
                "preference_increase":attribution["specificity_delta_raw_signed"]>0,
            })
        results.append({
            "treated_arm":arm,"base_arm":"fen_only",
            "n_historical_source_nominees":4,
            "n_increased_target_preference":sum(x["preference_increase"] for x in allrows),
            "n_positive_sarfa":sum(x["sarfa_positive_saliency"]>0 for x in allrows),
            "measure":"original SARFA Eq1-4 applied to Qwen conditional full-legal move distribution",
            "rows":allrows
        })
    return {
        "schema":SCHEMA,
        "status":"REAL_MODEL_PROMPT_CONTRAST_NOT_CHESS_SOURCE_SEARCH_CAUSATION",
        "original_sarfa_primary_pdf":"https://drive.google.com/file/d/1C_c0AvNkEtzB2z6Nbji_NdRxlRpODgjs/view",
        "original_parfenova_primary_pdf":"https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view",
        "r5_source_audit_sha":audit_sha,"r7_model_arm_source_shas":R7_MODEL_JSON_SHA,
        "prompt_has_different_semantic_content_and_lengths_across_arms":True,
        "full_original_legal_support_fixed_within_ordinal":True,
        "not_an_internal_original_stockfish_physical_computation_intervention":True,
        "not_original_SARFA_human_evaluation":True,
        "not_Parfenova_generated_vs_reference_comparison":True,
        "n_unique_chess_positions":2,"n_paired_historical_nominee_rows":4,
        "arms":results,
    }


def main():
    p=argparse.ArgumentParser()
    for n in ("audit","scores-dir","out"):
        p.add_argument("--"+n,required=True)
    a=p.parse_args()
    if digest(a.audit)!=R5_AUDIT_SHA:
        raise ValueError("R030_R7C_HOLD_EXACT_FROZEN_AUDIT")
    reports={}
    for arm in ARMS:
        f=Path(a.scores_dir)/("R7_ALL_LEGAL_"+arm+".json")
        if digest(f)!=R7_MODEL_JSON_SHA[arm]:
            raise ValueError("R030_R7C_HOLD_REAL_MODEL_SHA_"+arm)
        reports[arm]=json.loads(f.read_text(encoding="utf-8"))
    result=analyze(reports,json.loads(Path(a.audit).read_text(encoding="utf-8")),R5_AUDIT_SHA)
    out=Path(a.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    for arm in result["arms"]:
        print("R030_R7C_ACTUAL_MODEL_SARFA",arm["treated_arm"],
              "positive_nominee_delta",arm["n_increased_target_preference"],"/4",
              "saliency",[(round(row["sarfa_positive_saliency"],6),
                           round(row["treated_minus_fen_only_selected_probability"],6))
                           for row in arm["rows"]])
    print("R030_R7C_ACTUAL_MODEL_SARFA_SHA",digest(out))


if __name__=="__main__":
    main()
