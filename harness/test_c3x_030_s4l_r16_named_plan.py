"""Guard named-victim identity, material recaptures and legal source moves."""

import unittest

import chess

from c3x_030_s4l_r16_plan_oracle import balance, finishing_move, holds_after_last_defense, solve, target_after
from c3x_030_s4l_r16_plan_source import decode, named_victim


class NamedPlanTests(unittest.TestCase):
    def test_capture_guaranteed_against_king_moves(self):
        board = chess.Board("7k/8/8/8/4n3/8/8/K3R3 w - - 0 1")
        before = board.fen()
        proof = solve(board, chess.E4)
        self.assertTrue(proof["e1e4"]["holds"])
        self.assertTrue(proof["e1e4"]["finishes"])
        self.assertFalse(proof["a1a2"]["holds"])
        self.assertEqual(board.fen(), before)

    def test_recapture_can_invalidate_a_nominal_goal(self):
        board = chess.Board("4q2k/8/8/8/4n3/8/8/K3R3 w - - 0 1")
        fail = solve(board, chess.E4)["e1e4"]
        self.assertEqual(fail, {"holds": False, "refuting_defense": "e8e4"})

    def test_named_victim_moves_in_the_reply(self):
        first = chess.Board("7k/8/5n2/8/8/8/4R3/K7 b - - 0 1")
        self.assertEqual(named_victim(first, first, ["f6e4", "e2e4"]), chess.F6)

    def test_final_defender_can_recapture(self):
        board = chess.Board("4q2k/8/8/8/4n3/8/8/K3R3 w - - 0 1")
        initial = balance(board, chess.WHITE)
        self.assertEqual(finishing_move(board, chess.E4, chess.WHITE, initial), (True, "e1e4"))
        self.assertEqual(finishing_move(board, chess.E4, chess.WHITE, initial, True), (False, None))

    def test_final_noncapture_promotion_can_change_material_balance(self):
        board = chess.Board("7k/8/8/8/8/K7/1p6/4R3 b - - 0 1")
        self.assertFalse(holds_after_last_defense(board, chess.WHITE, balance(board, chess.WHITE)))

    def test_castling_preserves_the_enemy_rook_identity(self):
        board = chess.Board("4k2r/8/8/8/8/8/8/4K3 b k - 0 1")
        castle = board.parse_uci("e8g8")
        self.assertEqual(target_after(board, castle, chess.H8), chess.F8)
        self.assertEqual(decode(board, (3 << 14) | (chess.E8 << 6) | chess.H8), "e8g8")


if __name__ == "__main__":
    unittest.main()
