"""R27 actual two-opponent-layer tree shape, provenance, and fail-closed tests.

Synthetic chess engines used here are NOT scientific engine observations.
"""
import unittest
from unittest.mock import Mock
import chess
import chess.engine

from c3x_029_p42_r27_cui_recursive_k3_tree import (
    best_player, build_two_layer, AFTER_ROOT_PLIES)


class TwoLayerContract(unittest.TestCase):
    def setUp(self):
        self.board = chess.Board()
        self.child = self.board.copy(stack=True)
        self.child.push_uci("e2e4")

    def fake_engine(self):
        obj = Mock()

        def analysis(board, _limit, **kwargs):
            legal = list(board.legal_moves)
            if "multipv" in kwargs:
                n = kwargs["multipv"]
                return [{"pv": [legal[i]], "depth": 12,
                         "nodes": 500 + 100 * i}
                        for i in range(n)]
            return {"pv": [legal[0]], "depth": 12, "nodes": 1000}

        obj.analyse.side_effect = analysis
        return obj

    def test_real_structure_two_opponent_layers(self):
        eng = self.fake_engine()
        tree = build_two_layer(self.child, eng)
        self.assertEqual(tree["leaf_paths"], 9)
        self.assertEqual(tree["continuation_plies_after_root"], AFTER_ROOT_PLIES)
        self.assertEqual(len(tree["first_layer"]), 3)
        self.assertEqual(
            [len(x["next_opponent_branches"]) for x in tree["first_layer"]],
            [3, 3, 3])
        self.assertEqual(tree["physical_search_accounting"]["opponent_engine_queries"], 4)
        self.assertEqual(tree["physical_search_accounting"]["player_engine_queries"], 12)
        self.assertEqual(eng.analyse.call_count, 16)
        self.assertEqual(tree["physical_search_accounting"]["opponent_multipv_nodes_reported"], 4 * 700)

    def test_k1_still_recursively_expands(self):
        eng = self.fake_engine()
        tree = build_two_layer(self.child, eng, k=1)
        self.assertEqual(tree["leaf_paths"], 1)
        self.assertEqual(tree["physical_search_accounting"]["opponent_engine_queries"], 2)
        self.assertEqual(tree["physical_search_accounting"]["player_engine_queries"], 2)

    def test_illegal_player_pv_fails(self):
        eng = Mock()
        eng.analyse.return_value = {"pv": [chess.Move.from_uci("e7e5")],
                                    "depth": 12, "nodes": 100}
        with self.assertRaisesRegex(ValueError, "PLAYER_BEST"):
            best_player(chess.Board(), eng)

    def test_no_shallow_player_depth(self):
        eng = Mock()
        eng.analyse.return_value = {"pv": [chess.Move.from_uci("e2e4")],
                                    "depth": 11, "nodes": 100}
        with self.assertRaisesRegex(ValueError, "PLAYER_BEST"):
            best_player(chess.Board(), eng)

    def test_terminal_root_rejected(self):
        board = chess.Board("7k/6Q1/6K1/8/8/8/8/8 b - - 0 1")
        with self.assertRaisesRegex(ValueError, "TERMINAL"):
            build_two_layer(board, self.fake_engine())

    def test_k_more_than_three_rejected(self):
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED"):
            build_two_layer(self.child, self.fake_engine(), k=4)


if __name__ == "__main__":
    unittest.main()
