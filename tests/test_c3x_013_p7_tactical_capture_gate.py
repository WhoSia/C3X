"""P7 exact chess legality: immediate recapture hazard as a required control."""
import unittest
import chess

FEN="1r3nk1/1pp1bqp1/6pp/p7/3PNQ2/2P4P/PP3PP1/4RRK1 w - - 0 27"

def capture_hazard(fen,move_uci):
    b=chess.Board(fen)
    assert b.is_valid()
    m=chess.Move.from_uci(move_uci)
    assert m in b.legal_moves
    moving=b.piece_at(m.from_square)
    b.push(m)
    assert b.piece_at(m.to_square)==moving
    captured=[]
    for reply in b.legal_moves:
        if reply.to_square!=m.to_square or not b.is_capture(reply):continue
        aggressor=b.piece_at(reply.from_square)
        captured.append({"reply":reply.uci(),"aggressor_type":chess.piece_name(aggressor.piece_type),
                         "victim_type":chess.piece_name(moving.piece_type)})
    return sorted(captured,key=lambda x:x["reply"])

class TacticalControl(unittest.TestCase):
    def test_qxh6_pawn_can_immediately_capture_queen(self):
        danger=capture_hazard(FEN,"f4h6")
        self.assertTrue(any(z["reply"]=="g7h6" and z["aggressor_type"]=="pawn"
                            and z["victim_type"]=="queen" for z in danger))
    def test_qxc7_lacks_same_immediate_pawn_recapture(self):
        danger=capture_hazard(FEN,"f4c7")
        self.assertFalse(any(z["aggressor_type"]=="pawn" for z in danger))
    def test_tactical_signatures_differ_despite_both_capturing_pawns(self):
        b=chess.Board(FEN)
        a,c=(chess.Move.from_uci(x) for x in ("f4c7","f4h6"))
        self.assertEqual(a.from_square,c.from_square)
        self.assertTrue(b.is_capture(a) and b.is_capture(c))
        self.assertEqual(b.piece_at(a.to_square).piece_type,chess.PAWN)
        self.assertEqual(b.piece_at(c.to_square).piece_type,chess.PAWN)
        self.assertNotEqual(capture_hazard(FEN,"f4c7"),capture_hazard(FEN,"f4h6"))
    def test_initial_board_legal_pawn_push_not_immediately_captured(self):
        self.assertEqual(capture_hazard(chess.STARTING_FEN,"e2e4"),[])
if __name__=="__main__":
    unittest.main()
