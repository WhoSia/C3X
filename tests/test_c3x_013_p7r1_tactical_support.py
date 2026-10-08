"""P7-R1: immediate-recapture matching cannot be inferred from capture class."""
import unittest
import chess
from harness.c3x_013_p7r1_tactical_support import hazard,census

FAIL_FEN="1r3nk1/1pp1bqp1/6pp/p7/3PNQ2/2P4P/PP3PP1/4RRK1 w - - 0 27"
def classes_equal(a,b):
    core=("mover","captured","gives_check","promotion","castling")
    return all(a[k]==b[k] for k in core)

class P7TacticalPairTests(unittest.TestCase):
    def test_real_pawn_capture_counterexample_rejected(self):
        b=chess.Board(FAIL_FEN)
        a,c=hazard(b,chess.Move.from_uci("f4c7")),hazard(b,chess.Move.from_uci("f4h6"))
        self.assertEqual(a["mover"],"queen")
        self.assertEqual(a["captured"],c["captured"])
        self.assertEqual(c["captured"],"pawn")
        self.assertNotEqual(a["recapture_types"],c["recapture_types"])
        self.assertIn("pawn",c["recapture_types"])
    def test_starting_knight_same_origin_tactical_signature(self):
        b=chess.Board()
        a,c=hazard(b,chess.Move.from_uci("b1a3")),hazard(b,chess.Move.from_uci("b1c3"))
        self.assertTrue(classes_equal(a,c))
        self.assertEqual(a["recapture_types"],c["recapture_types"])
        result=census(b)
        self.assertGreater(result["counts"]["matched_and_same_origin"],0)
    def test_census_gates_nested(self):
        x=census(chess.Board())["counts"]
        self.assertGreater(x["all_legal_pairs"],0)
        self.assertGreaterEqual(x["same_class_capture_check_promotion"],
                                x["matched_legal_immediate_recapture"])
        self.assertGreaterEqual(x["matched_legal_immediate_recapture"],
                                x["matched_and_same_origin"])
        self.assertGreaterEqual(x["matched_and_same_origin"],
                                x["passed_birth_toggling_in_strict"])
    def test_no_hazard_when_starting_e4_d4(self):
        b=chess.Board()
        self.assertEqual(hazard(b,chess.Move.from_uci("e2e4"))["recapture_types"],[])
        self.assertEqual(hazard(b,chess.Move.from_uci("d2d4"))["recapture_types"],[])
if __name__=="__main__":
    unittest.main()
