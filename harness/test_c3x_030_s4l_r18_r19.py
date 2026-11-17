"""Check legal preparation eligibility and the bounded value distinctions."""

import unittest

import chess

from c3x_030_s4l_r16_plan_oracle import balance
from c3x_030_s4l_r18_preparation_screen import requires_preparation
from c3x_030_s4l_r19_plan_material_value import compare, last_defense_value


class PreparationAndValueTests(unittest.TestCase):
    def test_pinned_pseudocapture_leaves_preparation_eligible(self):
        board = chess.Board("4r2k/8/8/8/8/8/4R2n/4K3 w - - 0 1")
        capture = chess.Move.from_uci("e2h2")
        self.assertTrue(board.is_pseudo_legal(capture))
        self.assertFalse(board.is_legal(capture))
        self.assertTrue(requires_preparation(board, chess.H2))

    def test_a_legal_immediate_target_capture_is_ineligible(self):
        board = chess.Board("7k/8/8/8/8/8/4R2n/4K3 w - - 0 1")
        self.assertFalse(requires_preparation(board, chess.H2))

    def test_last_defense_respects_en_passant_and_noncapture_promotion(self):
        for fen in ("7k/8/8/8/3Pp3/8/8/K7 b - d3 0 1",
                    "7k/8/8/8/8/K7/1p6/4R3 b - - 0 1"):
            board = chess.Board(fen)
            values = []
            for move in list(board.legal_moves):
                board.push(move)
                values.append(balance(board, chess.WHITE))
                board.pop()
            self.assertEqual(last_defense_value(board, chess.WHITE), min(values))

    def test_first_move_support_does_not_imply_plan_policy_value(self):
        values = {"a": {"open": 7, "constrained": None},
                  "b": {"open": 7, "constrained": 4},
                  "c": {"open": 6, "constrained": 2}}
        result = compare(values, ["b", "c"])
        self.assertEqual((result["V"], result["F"], result["G"]), (7, 7, 4))
        self.assertFalse(result["every_best_admits"])


if __name__ == "__main__":
    unittest.main()
