"""R25-E1 contract tests: synthetic engine reports are not native evidence."""
import unittest
from unittest.mock import Mock
import chess
from c3x_029_p42_r25_e1_engine_ranked_first_layer import rank_opponent


class RankContract(unittest.TestCase):
    def setUp(self):
        self.board = chess.Board()
        self.uci = ["e2e4", "d2d4", "g1f3"]

    def info(self, move, depth=12, nodes=100):
        return {"pv": [chess.Move.from_uci(move)], "depth": depth, "nodes": nodes}

    def engine(self, data):
        obj = Mock()
        obj.analyse.return_value = data
        return obj

    def test_engine_rank_is_preserved_not_lexicographic(self):
        obj = self.engine([self.info("g1f3"), self.info("e2e4"), self.info("d2d4")])
        ranked = rank_opponent(self.board, obj)
        self.assertEqual([r["opponent_reply"] for r in ranked],
                         ["g1f3", "e2e4", "d2d4"])
        self.assertEqual([r["engine_rank"] for r in ranked], [1, 2, 3])
        self.assertEqual(obj.analyse.call_args.kwargs["multipv"], 3)

    def test_reject_missing_multipv(self):
        with self.assertRaisesRegex(ValueError, "INCOMPLETE"):
            rank_opponent(self.board, self.engine([self.info("e2e4")]))

    def test_reject_duplicates(self):
        with self.assertRaisesRegex(ValueError, "DUPLICATE"):
            rank_opponent(self.board, self.engine([self.info("e2e4")] * 3))

    def test_reject_illegal_rank(self):
        with self.assertRaisesRegex(ValueError, "BAD_ENGINE"):
            rank_opponent(self.board, self.engine([
                self.info("e2e4"), self.info("e7e5"), self.info("g1f3")]))

    def test_reject_underdepth(self):
        with self.assertRaisesRegex(ValueError, "BAD_ENGINE"):
            rank_opponent(self.board, self.engine([
                self.info("e2e4", depth=11), self.info("d2d4"),
                self.info("g1f3")]))

    def test_reject_zero_nodes(self):
        with self.assertRaisesRegex(ValueError, "BAD_ENGINE"):
            rank_opponent(self.board, self.engine([
                self.info("e2e4", nodes=0), self.info("d2d4"),
                self.info("g1f3")]))

    def test_terminal_rejected(self):
        board = chess.Board()
        for u in ["f2f3", "e7e5", "g2g4", "d8h4"]:
            board.push_uci(u)
        with self.assertRaisesRegex(ValueError, "TERMINAL"):
            rank_opponent(board, self.engine([]))

    def test_smaller_legal_support_uses_smaller_multipv(self):
        board = chess.Board("7k/6Q1/6K1/8/8/8/8/8 b - - 0 1")
        with self.assertRaises(ValueError):
            rank_opponent(board, self.engine([]))


if __name__ == "__main__":
    unittest.main()
