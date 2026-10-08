"""P6-M formal chess-pawn predicates and legal move grammar counterexamples."""
import unittest
import chess
from c3x_explain.concepts import snapshot

PASSED="4k3/8/p7/2p5/P2P4/8/8/4K3 w - - 0 1"
ISOLATED="4k3/8/8/1p2p3/2PP1P2/8/8/4K3 w - - 0 1"
PROMOTION="4k3/P7/8/8/8/8/8/4K3 w - - 0 1"

def features(b):
    f=snapshot(b,chess.WHITE)
    return {
        "isolated":f["own_isolated_pawn_count"],
        "passed":f["own_passed_pawn_count"],
        "center":f["own_center_occupancy_count"],
        "own_pawn_count":len(b.pieces(chess.PAWN,chess.WHITE)),
        "enemy_pawn_count":len(b.pieces(chess.PAWN,chess.BLACK))
    }
def after(fen,move):
    b=chess.Board(fen)
    assert b.is_valid()
    m=chess.Move.from_uci(move)
    assert m in b.legal_moves,(fen,move)
    b.push(m)
    assert b.is_valid()
    return b

class P6PawnGeometry(unittest.TestCase):
    def test_ordinary_push_changes_passed_not_isolation(self):
        b=chess.Board(PASSED)
        self.assertEqual((features(b)["isolated"],features(b)["passed"]),(2,0))
        target=after(PASSED,"d4d5")
        control=after(PASSED,"a4a5")
        self.assertEqual(features(target)["passed"],1)
        self.assertEqual(features(control)["passed"],0)
        self.assertEqual(features(target)["isolated"],features(control)["isolated"])
        self.assertEqual(features(target)["center"],features(control)["center"])
        self.assertEqual(features(target)["own_pawn_count"],features(control)["own_pawn_count"])
        self.assertEqual(features(target)["enemy_pawn_count"],features(control)["enemy_pawn_count"])
    def test_two_legal_captures_change_isolation_differently(self):
        b=chess.Board(ISOLATED)
        self.assertEqual(features(b)["isolated"],1)
        target=after(ISOLATED,"c4b5")
        control=after(ISOLATED,"d4e5")
        self.assertEqual(features(target)["isolated"],3)
        self.assertEqual(features(control)["isolated"],1)
        self.assertEqual(features(target)["enemy_pawn_count"],1)
        self.assertEqual(features(control)["enemy_pawn_count"],1)
        self.assertEqual(features(target)["own_pawn_count"],3)
        self.assertEqual(features(control)["own_pawn_count"],3)
    def test_promotion_exception_to_unqualified_file_invariance(self):
        b=chess.Board(PROMOTION)
        self.assertEqual((features(b)["isolated"],features(b)["passed"]),(1,1))
        q=after(PROMOTION,"a7a8q")
        self.assertEqual((features(q)["isolated"],features(q)["passed"]),(0,0))
        self.assertEqual(features(q)["own_pawn_count"],0)
    def test_forward_push_isolation_invariant_only_without_promotion(self):
        for fen,move in ((PASSED,"d4d5"),(PASSED,"a4a5")):
            b=chess.Board(fen)
            self.assertFalse(chess.Move.from_uci(move).promotion)
            self.assertEqual(features(b)["isolated"],features(after(fen,move))["isolated"])
    def test_own_file_adjacency_counting_multiple_pawns(self):
        b=chess.Board("4k3/8/8/P7/P7/8/8/4K3 w - - 0 1")
        self.assertTrue(b.is_valid())
        self.assertEqual(features(b)["isolated"],2)
    def test_legal_moves_not_equivalent_to_legal_board_edits(self):
        b=chess.Board(ISOLATED)
        fake=chess.Move.from_uci("c4b4")
        self.assertNotIn(fake,b.legal_moves)
        q=b.copy(stack=False)
        q.remove_piece_at(chess.C4)
        q.set_piece_at(chess.B4,chess.Piece(chess.PAWN,chess.WHITE))
        self.assertTrue(q.is_valid())
if __name__=="__main__":
    unittest.main()
