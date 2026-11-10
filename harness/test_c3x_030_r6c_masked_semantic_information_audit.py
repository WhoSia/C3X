"""R6C semantic-information leakage from R5 masked factual chess comments."""
import unittest
import chess

from c3x_030_r6c_masked_semantic_information_audit import (
    features_from_text,candidate_filter,analyze,R5_AUDIT_SHA
)
from c3x_030_r5_parfenova_move_mask_control_protocol import demonstrate


class SemanticMaskedLeakageContracts(unittest.TestCase):
    def test_capture_truth_extracted_from_masked_synthetic(self):
        self.assertEqual(features_from_text(
            "Candidate move [MOVE] (SAN [MOVE]). It is a capture and gives check."),
            (True,True))
        self.assertEqual(features_from_text(
            "Candidate move [MOVE] (SAN [MOVE]). It is not a capture and does not give check."),
            (False,False))

    def test_reject_vague_or_multiple_claims(self):
        for phrase in ("This move is good.", "It is a capture and gives check. It is a capture and gives check."):
            with self.assertRaisesRegex(ValueError,"AMBIGUOUS"):
                features_from_text(phrase)

    def test_true_capture_filters_legal_actions_and_target_remains(self):
        b=chess.Board()
        for u in ("e2e4","d7d5"): b.push_uci(u)
        n=candidate_filter(b)
        captures=candidate_filter(b,True,None)
        self.assertIn("e4d5",captures)
        self.assertLess(len(captures),len(n))

    def test_true_check_filters_legal_actions_and_target_remains(self):
        b=chess.Board()
        for u in ("f2f3","e7e5","g2g4"): b.push_uci(u)
        self.assertIn("d8h4",candidate_filter(b,None,True))
        self.assertLess(len(candidate_filter(b,None,True)),len(candidate_filter(b)))

    def test_invalid_filter_schema_rejected(self):
        with self.assertRaisesRegex(ValueError,"BOARD_OR_CLAIM"):
            candidate_filter(chess.Board(),True,"True")

    def test_masked_semantic_info_may_be_zero_in_uninformative_start(self):
        worlds=[]
        for i in range(2):
            worlds.append(({"case_id":f"fixture:{i}","event_family":f"fixture:{i}"},
                           chess.Board(),[{"root":"e2e4"},{"root":"d2d4"}]))
        original=demonstrate(worlds)
        result=analyze(original,R5_AUDIT_SHA)
        self.assertEqual(result["number_exposed_root_candidates"],4)
        self.assertEqual(result["total_masked_cases_with_remaining_semantic_information"],0)
        self.assertEqual(result["mask_uniquely_identified_n"],0)

    def test_audit_sha_fail_closed(self):
        worlds=[]
        for i in range(2):
            worlds.append(({"case_id":f"fixture:{i}","event_family":f"fixture:{i}"},
                           chess.Board(),[{"root":"e2e4"},{"root":"d2d4"}]))
        with self.assertRaisesRegex(ValueError,"FROZEN"):
            analyze(demonstrate(worlds),"bad")

    def test_fake_claim_source_drift_detected(self):
        worlds=[]
        for i in range(2):
            worlds.append(({"case_id":f"fixture:{i}","event_family":f"fixture:{i}"},
                           chess.Board(),[{"root":"e2e4"},{"root":"d2d4"}]))
        archive=demonstrate(worlds)
        archive["cases"][0]["candidate_control_packets"][0]["act_eval_capture_truth"]=True
        with self.assertRaisesRegex(ValueError,"FACT_DRIFT"):
            analyze(archive,R5_AUDIT_SHA)


if __name__=="__main__":
    unittest.main()
