"""R6 isolated decoder-and-posthoc evaluator contracts; fake outputs are NOT model results."""
import unittest
import chess

from c3x_030_r6a_actual_open_decoder_blind_arm import (
    prompt_for,input_arm,parse_strict_uci,ARMS,SCHEMA,R5_SCHEMA,MODEL_ID,MODEL_REVISION
)
from c3x_030_r6b_posthoc_decoder_recovery_evaluator import evaluate,ARM_SHA


def fixtures():
    source_cases=[]
    for case_idx in range(2):
        b=chess.Board()
        targets=["e2e4","d2d4"]
        records=[]
        for u in targets:
            condition={arm:{"fen":b.fen(en_passant="fen"),"explanation":"[MOVE]"} for arm in ARMS}
            condition["explanation_only"]["fen"]=None
            condition["fen_only"]["explanation"]=None
            condition["fen_plus_unmasked"]["explanation"]="Candidate move "+u
            records.append({"root_uci_source_only_label_not_decoder_input":u,
                            "conditions":condition})
        source_cases.append({"event_family":f"mock:{case_idx}","candidate_control_packets":records})
    truth={"schema":"c3x030-r5-parfenova-inspired-move-hint-mask-protocol-v1",
           "cases":source_cases}
    reps={}
    for arm in ARMS:
        reps[arm]={"schema":SCHEMA,"arm":arm,"model_id":MODEL_ID,
                   "model_revision":MODEL_REVISION,
                   "input_blind_arm_sha256":ARM_SHA[arm],
                   "no_truth_manifest_access_in_decoder":True,
                   "isolated_chat_context_every_entry":True,
                   "results":[{"ordinal":i,"parsed_uci_or_null":("e2e4" if i%2==0 else "d2d4")}
                              for i in range(4)]}
    return truth,reps


class OpenDecoderAndBlindEvaluation(unittest.TestCase):
    def test_strict_UCI_no_posthoc_cherry_pick(self):
        self.assertEqual(parse_strict_uci("e2e4"),"e2e4")
        self.assertEqual(parse_strict_uci("Best move: d2d4"),"d2d4")
        self.assertIsNone(parse_strict_uci("I think e2e4 should work"))
        self.assertIsNone(parse_strict_uci("not a move"))
        self.assertIsNone(parse_strict_uci("e2e4foo"))

    def test_prompt_no_truth_headers(self):
        p=prompt_for({"fen":chess.Board().fen(),"explanation":"[MOVE] gives check."})
        self.assertIn("Position (FEN):",p)
        self.assertIn("Explanation:",p)
        self.assertNotIn("root_uci_source_only_label",p)

    def test_refuse_extra_candidate_field(self):
        with self.assertRaisesRegex(ValueError,"NONBLIND"):
            prompt_for({"fen":"a","explanation":"b","target":"e2e4"})

    def test_correct_arm_schema_and_count(self):
        data={"schema":R5_SCHEMA,"condition":"fen_only",
              "entries":[{"fen":chess.Board().fen(),"explanation":None}]*4,
              "no_target_labels_or_cross_arm_case_identifiers":True,
              "requires_isolated_decoder_context_no_cross_arm_visibility":True,
              "no_decoder_executed":True}
        self.assertEqual(len(input_arm(data,"fen_only")),4)

    def test_reject_cross_arm_info(self):
        data={"schema":R5_SCHEMA,"condition":"fen_only","entries":[],
              "no_target_labels_or_cross_arm_case_identifiers":True,
              "requires_isolated_decoder_context_no_cross_arm_visibility":True,
              "no_decoder_executed":True,"leaked":"e2e4"}
        with self.assertRaisesRegex(ValueError,"TARGET_LEAK"):
            input_arm(data,"fen_only")

    def test_evaluate_four_nominated_targets_only_after_join(self):
        truth,reps=fixtures()
        result=evaluate(truth,reps,"fixture-audit-sha",expected_audit_sha="fixture-audit-sha")
        self.assertEqual(result["arms"][0]["nominated_target_recovered"],4)
        self.assertTrue(result["reference_best_move_comparison_not_available"])
        self.assertEqual(len(result["arms"]),5)

    def test_reject_bad_decoded_pinned_revision(self):
        truth,reps=fixtures()
        reps["fen_only"]["model_revision"]="main"
        with self.assertRaisesRegex(ValueError,"PROVENANCE"):
            evaluate(truth,reps,"fixture",expected_audit_sha="fixture")

    def test_reject_audit_sha_mismatch(self):
        truth,reps=fixtures()
        with self.assertRaisesRegex(ValueError,"AUDIT_SHA"):
            evaluate(truth,reps,"invalid",expected_audit_sha="frozen")

    def test_reject_missing_condition(self):
        truth,reps=fixtures()
        del reps["fen_only"]
        with self.assertRaisesRegex(ValueError,"MISSING_DECODER_ARM"):
            evaluate(truth,reps,"fixture",expected_audit_sha="fixture")

    def test_no_grade_for_missing_response(self):
        truth,reps=fixtures()
        reps["fen_only"]["results"][0]["parsed_uci_or_null"]=None
        result=evaluate(truth,reps,"fixture",expected_audit_sha="fixture")
        self.assertEqual(result["arms"][0]["nominated_target_recovered"],3)
        self.assertEqual(result["arms"][0]["parsed_count"],3)


if __name__=="__main__":
    unittest.main()
