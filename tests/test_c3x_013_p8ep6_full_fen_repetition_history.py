"""FEN alone is not generic chess history: repeat counts can differ."""
import unittest
import chess

ONE=["g1f3","g8f6","f3g1","f6g8"]*2
TWO=["g1f3","g8f6","b1c3","b8c6","f3g1","f6g8","c3b1","c6b8"]

def replay(ucis):
    b=chess.Board()
    for x in ucis:
        m=chess.Move.from_uci(x)
        assert m in b.legal_moves
        b.push(m)
    return b

class FenHistoryCounterexample(unittest.TestCase):
    def test_full_six_field_fen_same_but_repetition_histories_differ(self):
        a,b=replay(ONE),replay(TWO)
        self.assertEqual(a.fen(en_passant="fen"),b.fen(en_passant="fen"))
        self.assertEqual(a.halfmove_clock,8)
        self.assertEqual(a.fullmove_number,5)
        self.assertTrue(a.is_repetition(3))
        self.assertFalse(b.is_repetition(3))
    def test_same_board_initial_pawn_count_both_routes(self):
        a,b=replay(ONE),replay(TWO)
        self.assertEqual(len(a.pieces(chess.PAWN,chess.WHITE)),8)
        self.assertEqual(len(b.pieces(chess.PAWN,chess.WHITE)),8)
if __name__=="__main__":
    unittest.main()
