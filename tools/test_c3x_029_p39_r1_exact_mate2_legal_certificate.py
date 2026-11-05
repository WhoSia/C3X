"""P39/R1 rule-complete chess mate certificate tests; no model or oracle."""
import unittest
import chess
from c3x_029_p39_r1_exact_mate2_legal_certificate import calculate_q,verify_q_certificate

class LegalCertificateTest(unittest.TestCase):
    def test_known_fools_mate_immediate_positive(self):
        board=chess.Board()
        for u in ("f2f3","e7e5","g2g4"):
            board.push_uci(u)
        result=calculate_q(board,"d8h4")
        self.assertEqual((result["verdict"],result["kind"]),("TRUE","IMMEDIATE_MATE"))
        self.assertTrue(verify_q_certificate(board,"d8h4",result))

    def test_starting_position_nonmate_has_complete_counterexample(self):
        board=chess.Board()
        result=calculate_q(board,"e2e4")
        self.assertEqual((result["verdict"],result["kind"]),("FALSE","OPPONENT_COUNTEREXAMPLE"))
        self.assertTrue(verify_q_certificate(board,"e2e4",result))
        self.assertEqual(len(result["counterexample"]["all_own_legal_moves"]),20)

    def test_false_negative_counterproof_cannot_omit_legal_response(self):
        board=chess.Board()
        result=calculate_q(board,"e2e4")
        result["counterexample"]["all_own_legal_moves"].pop()
        with self.assertRaisesRegex(ValueError,"CERT_INCOMPLETE_OWN_MOVES"):
            verify_q_certificate(board,"e2e4",result)

    def test_false_positive_missing_universal_replies_rejected(self):
        board=chess.Board()
        fake={"verdict":"TRUE","kind":"FORCED_MATE_ON_SECOND_TURN",
              "opponent_reply_count":20,"all_reply_mating_witnesses":{}}
        with self.assertRaisesRegex(ValueError,"CERT_MISSING_OPPONENT_REPLY"):
            verify_q_certificate(board,"e2e4",fake)

    def test_invalid_root_rejected(self):
        with self.assertRaisesRegex(ValueError,"ILLEGAL_ROOT"):
            calculate_q(chess.Board(),"e7e5")

    def test_expansion_limit_is_hold_not_false(self):
        with self.assertRaisesRegex(ValueError,"COMPUTE_CAP"):
            calculate_q(chess.Board(),"e2e4",cap=1)

if __name__=="__main__":
    unittest.main()
