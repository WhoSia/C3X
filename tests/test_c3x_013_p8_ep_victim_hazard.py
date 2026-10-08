"""P8-EP1: legal en passant captures the just moved pawn on a DIFFERENT square."""
import unittest
import chess
from harness.c3x_013_p7r1_tactical_support import hazard

EP_FEN="4k3/8/8/8/3p4/8/4P3/4K3 w - - 0 1"
QUEEN_FEN="1r3nk1/1pp1bqp1/6pp/p7/3PNQ2/2P4P/PP3PP1/4RRK1 w - - 0 27"

class EnPassantVictimTacticalTests(unittest.TestCase):
    def test_double_pushed_pawn_is_capture_victim_on_other_square(self):
        b=chess.Board(EP_FEN)
        self.assertTrue(b.is_valid())
        m=chess.Move.from_uci("e2e4")
        self.assertIn(m,b.legal_moves)
        b.push(m)
        r=chess.Move.from_uci("d4e3")
        self.assertIn(r,b.legal_moves)
        self.assertTrue(b.is_en_passant(r))
        self.assertTrue(b.is_capture(r))
        self.assertNotEqual(r.to_square,chess.E4)
        self.assertEqual(b.piece_at(chess.E4),chess.Piece(chess.PAWN,chess.WHITE))
    def test_tactical_gate_counts_en_passant_recapture_of_root_pawn(self):
        b=chess.Board(EP_FEN)
        sig=hazard(b,chess.Move.from_uci("e2e4"))
        self.assertEqual(sig["mover"],"pawn")
        self.assertEqual(sig["captured"],"NONE")
        self.assertEqual(sig["recapture_types"],["pawn"])
    def test_initial_position_no_en_passant_opponent(self):
        b=chess.Board()
        sig=hazard(b,chess.Move.from_uci("e2e4"))
        self.assertEqual(sig["recapture_types"],[])
    def test_queen_regular_pawn_capture_still_counted(self):
        b=chess.Board(QUEEN_FEN)
        sig=hazard(b,chess.Move.from_uci("f4h6"))
        self.assertIn("pawn",sig["recapture_types"])
    def test_one_step_e3_direct_pawn_capture(self):
        b=chess.Board(EP_FEN)
        sig=hazard(b,chess.Move.from_uci("e2e3"))
        self.assertEqual(sig["recapture_types"],["pawn"])
    def test_en_passant_reply_is_not_misclassified_as_any_square_capture(self):
        b=chess.Board(EP_FEN)
        no=hazard(b,chess.Move.from_uci("e1d2"))
        self.assertEqual(no["recapture_types"],[])
if __name__=="__main__":
    unittest.main()
