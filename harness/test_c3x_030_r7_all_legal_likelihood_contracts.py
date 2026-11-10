"""C3X 0.30/R7 deterministic source-blind action support and rank scoring tests.

All candidate score numbers are synthetic here, NOT Qwen model results.
Genuine Qwen model must execute in a distinct pinned read-only workflow.
"""
import math
import unittest

import chess

from c3x_030_r7s_blind_all_legal_support_freeze import support,FEN_SHA,SCHEMA as SUPPORT_SCHEMA
from c3x_030_r7a_real_qwen_all_legal_token_scorer import (
    validate_arm_and_support,choose_ranking,SCHEMA as SCORE_SCHEMA
)
from c3x_030_r7b_posthoc_all_legal_rank_evaluator import (
    rank_and_grade
)
from c3x_030_r6a_actual_open_decoder_blind_arm import (
    ARMS,R5_SCHEMA,MODEL_ID,MODEL_REVISION
)
from c3x_030_r6b_posthoc_decoder_recovery_evaluator import ARM_SHA,R5_AUDIT_SHA


def example_support():
    fen=chess.Board().fen(en_passant="fen")
    d={"schema":R5_SCHEMA,"condition":"fen_only",
       "entries":[{"fen":fen,"explanation":None} for _ in range(4)],
       "no_target_labels_or_cross_arm_case_identifiers":True,
       "requires_isolated_decoder_context_no_cross_arm_visibility":True,
       "no_decoder_executed":True}
    return support(d,FEN_SHA)


def fixture_for_arm(arm):
    fen=chess.Board().fen(en_passant="fen")
    return {
        "schema":R5_SCHEMA,"condition":arm,
        "entries":[{
            "fen":None if arm=="explanation_only" else fen,
            "explanation":None if arm=="fen_only" else "A generic chess plan."
        } for _ in range(4)],
        "no_target_labels_or_cross_arm_case_identifiers":True,
        "requires_isolated_decoder_context_no_cross_arm_visibility":True,
        "no_decoder_executed":True
    }


class R7EvidenceContracts(unittest.TestCase):
    def test_full_support_all_legal_and_only_legal(self):
        d=example_support()
        self.assertEqual(len(d["entries"]),4)
        self.assertEqual([len(x["legal_move_ucis"]) for x in d["entries"]],[20]*4)
        self.assertNotIn(chess.Board().fen(en_passant="fen"),repr(d))
        self.assertNotIn("root_uci_source_only_label",repr(d))
        self.assertIn("e2e4",d["entries"][0]["legal_move_ucis"])

    def test_reject_source_sha(self):
        with self.assertRaisesRegex(ValueError,"FROZEN"):
            support(fixture_for_arm("fen_only"),"made-up")

    def test_every_fen_condition_matches_exact_support(self):
        for arm in ARMS:
            entries, actions=validate_arm_and_support(fixture_for_arm(arm),arm,example_support())
            self.assertEqual(len(entries),4)
            self.assertEqual(len(actions[0]),20)

    def test_explanation_only_model_prompt_must_not_contain_fen(self):
        entry=fixture_for_arm("explanation_only")["entries"][0]
        self.assertIsNone(entry["fen"])

    def test_manifest_extra_target_field_is_fatal(self):
        x=example_support()
        x["candidate_label"]="e2e4"
        with self.assertRaisesRegex(ValueError,"PROVENANCE"):
            validate_arm_and_support(fixture_for_arm("fen_only"),"fen_only",x)

    def test_invalid_support_move_is_fatal(self):
        x=example_support()
        x["entries"][0]["legal_move_ucis"][0]="a1a1"
        with self.assertRaisesRegex(ValueError,"SORTED_EXACT_LEGAL_SUPPORT|BOARD_ACTION_DRIFT"):
            validate_arm_and_support(fixture_for_arm("fen_only"),"fen_only",x)

    def test_summed_score_primary_and_average_secondary_diverge(self):
        rows=[
          {"uci":"a2a3","summed_log_probability":-3.0,
           "mean_log_probability_per_token":-1.5,"continuation_tokens":2},
          {"uci":"a2a4","summed_log_probability":-2.0,
           "mean_log_probability_per_token":-2.0,"continuation_tokens":1}
        ]
        self.assertEqual(choose_ranking(rows)[0]["uci"],"a2a4")
        self.assertEqual(choose_ranking(rows,"mean_log_probability_per_token")[0]["uci"],"a2a3")

    def test_tie_lexicographic(self):
        rows=[{"uci":u,"summed_log_probability":-4.,
               "mean_log_probability_per_token":-2.,
               "continuation_tokens":2} for u in ("d2d4","e2e4")]
        self.assertEqual(choose_ranking(rows)[0]["uci"],"d2d4")

    def test_nonfinite_score_hard_reject(self):
        rows=[{"uci":"a2a3","summed_log_probability":math.nan,
               "mean_log_probability_per_token":0.0,
               "continuation_tokens":2}]
        with self.assertRaisesRegex(ValueError,"NONFINITE"):
            choose_ranking(rows)

    def test_evaluation_joins_only_after_all_five_sealed(self):
        sup=example_support()
        target="e2e4"
        truth={"schema":"c3x030-r5-parfenova-inspired-move-hint-mask-protocol-v1",
               "cases":[{"candidate_control_packets":[
                 {"root_uci_source_only_label_not_decoder_input":target},
                 {"root_uci_source_only_label_not_decoder_input":target}
               ]} for _ in range(2)]}
        support_sha="test-support-sha"
        models={}
        for arm in ARMS:
            rs=[]
            for i in range(4):
                legal=sup["entries"][i]["legal_move_ucis"]
                scored=[{"uci":u,"summed_log_probability":float(-idx),
                         "mean_log_probability_per_token":float(-idx),
                         "continuation_tokens":1} for idx,u in enumerate(legal)]
                rs.append({"ordinal":i,"legal_actions_scored":len(legal),
                           "full_summed_log_probability_ranking":scored,
                           "full_mean_per_token_ranking_ucis":legal})
            models[arm]={"schema":SCORE_SCHEMA,"condition":arm,
                         "model_id":MODEL_ID,"model_revision":MODEL_REVISION,
                         "input_blind_arm_sha256":ARM_SHA[arm],
                         "legal_support_manifest_sha256":support_sha,
                         "source_target_and_original_reference_never_seen_during_inference":True,
                         "entries":rs}
        out=rank_and_grade(truth,models,sup,R5_AUDIT_SHA,support_sha)
        self.assertEqual(len(out["arms"]),5)
        self.assertEqual(out["arms"][0]["primary_top1"],0)
        self.assertTrue(out["source_nominees_not_llm_generated_move_or_gold_puzzle_reference"])
        models["fen_only"]["entries"][0]["full_summed_log_probability_ranking"].pop()
        with self.assertRaisesRegex(ValueError,"INCOMPLETE"):
            rank_and_grade(truth,models,sup,R5_AUDIT_SHA,support_sha)


if __name__=="__main__":
    unittest.main()
