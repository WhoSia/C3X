"""P39/R2 exact legal minmax counterplay certificate, source-independent fixtures."""
import copy
import unittest
import chess
from c3x_029_p39_r2_adversarial_mobility import compute_world, verify_world, DRAW_PENALTY

class RobustOptionValueTest(unittest.TestCase):
    def test_startboard_after_e4_full_reply_universe(self):
        b = chess.Board()
        receipt = compute_world(b, "e2e4")
        post = b.copy(stack=True)
        post.push_uci("e2e4")
        self.assertEqual(len(receipt["branches"]),post.legal_moves.count())
        self.assertTrue(verify_world(b,receipt))
        self.assertEqual(receipt["w"],max(x["b"] for x in receipt["branches"]))

    def test_immediate_checkmate_value_zero(self):
        b=chess.Board()
        for move in ("f2f3","e7e5","g2g4"):b.push_uci(move)
        receipt=compute_world(b,"d8h4")
        self.assertEqual(receipt["w"],0)
        self.assertEqual(receipt["kind"],"IMMEDIATE_MATE")
        self.assertTrue(verify_world(b,receipt))

    def test_invalid_root_holds(self):
        with self.assertRaisesRegex(ValueError,"ROOT_ILLEGAL"):
            compute_world(chess.Board(),"e7e5")

    def test_cost_cap_holds_not_imputed_value(self):
        with self.assertRaisesRegex(ValueError,"EXPANSION_CAP"):
            compute_world(chess.Board(),"e2e4",cap=1)

    def test_tampered_opponent_branch_rejected(self):
        b=chess.Board()
        receipt=compute_world(b,"e2e4")
        fake=copy.deepcopy(receipt)
        fake["branches"][0]["b"]+=1
        with self.assertRaisesRegex(ValueError,"MOBILITY_CERT_MISMATCH"):
            verify_world(b,fake)

    def test_tampered_best_own_reply_rejected(self):
        b=chess.Board()
        receipt=compute_world(b,"e2e4")
        fake=copy.deepcopy(receipt)
        fake["branches"][0]["best_own_reply"]="a1a8"
        with self.assertRaisesRegex(ValueError,"MOBILITY_CERT_MISMATCH"):
            verify_world(b,fake)

if __name__=="__main__":
    unittest.main()
