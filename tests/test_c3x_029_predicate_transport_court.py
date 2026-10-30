"""C3X 0.29 P1 finite restricted-KRK explanation transport tests."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from c3x_029_predicate_transport_court import (
    court,legal_krk_black_to_move,pred_rank7,pred_not_g8
)

class PredicateTransportCourt(unittest.TestCase):
    def test_explicit_off_support_legal_context(self):
        r=court()
        self.assertEqual(r["legal_black_king_states"],43)
        self.assertEqual(r["predicate_disagreement_legal_states"],37)
        self.assertEqual(r["first_disagreement_square"],"a8")
        self.assertEqual(r["example_fen"],"k7/8/2K5/8/8/8/8/1R6 b - - 0 1")

    def test_predicates_separate_at_a8(self):
        self.assertTrue(legal_krk_black_to_move((0,7)))
        self.assertFalse(pred_rank7((0,7)))
        self.assertTrue(pred_not_g8((0,7)))

    def test_proof_scope_is_explicit(self):
        r=court()
        self.assertFalse(r["full_chess_rules_verified"])
        self.assertFalse(r["original_KRK1_reply_reachability_claim"])
        self.assertEqual(r["native_stockfish_calls"],0)

if __name__=="__main__":
    unittest.main()
