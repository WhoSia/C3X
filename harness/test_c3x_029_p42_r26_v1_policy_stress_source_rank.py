"""R26-V1 synthetic contracts. Never label fake-engine outputs as native evidence."""
import unittest
from unittest.mock import Mock
import chess
import chess.engine
from c3x_029_p42_r26_v1_policy_stress_source_rank import score_after_frozen_own


class SourceStressContract(unittest.TestCase):
    def setUp(self):
        self.board = chess.Board()
        self.info = {"depth": 12, "nodes": 1234,
                     "score": chess.engine.PovScore(chess.engine.Cp(31), chess.WHITE),
                     "pv": [chess.Move.from_uci("e2e4")]}
        self.engine = Mock()

    def test_legal_finite_perspective(self):
        self.engine.analyse.return_value = dict(self.info)
        x = score_after_frozen_own(self.board, chess.WHITE, self.engine)
        self.assertEqual(x["source_policy_stress_cp"], 31)
        self.assertEqual(score_after_frozen_own(
            self.board, chess.BLACK, self.engine)["source_policy_stress_cp"], -31)

    def test_reject_undershoot(self):
        info = dict(self.info, depth=11)
        self.engine.analyse.return_value = info
        with self.assertRaisesRegex(ValueError, "SOURCE_SEARCH"):
            score_after_frozen_own(self.board, chess.WHITE, self.engine)

    def test_reject_bound(self):
        self.engine.analyse.return_value = dict(self.info, lowerbound=True)
        with self.assertRaisesRegex(ValueError, "BOUND"):
            score_after_frozen_own(self.board, chess.WHITE, self.engine)

    def test_reject_illegal_pv(self):
        self.engine.analyse.return_value = dict(
            self.info, pv=[chess.Move.from_uci("e7e5")])
        with self.assertRaisesRegex(ValueError, "PV_ILLEGAL"):
            score_after_frozen_own(self.board, chess.WHITE, self.engine)

    def test_reject_mate_score(self):
        self.engine.analyse.return_value = dict(
            self.info,
            score=chess.engine.PovScore(chess.engine.Mate(2), chess.WHITE))
        with self.assertRaisesRegex(ValueError, "MATE"):
            score_after_frozen_own(self.board, chess.WHITE, self.engine)

    def test_reject_terminal(self):
        board = chess.Board("7k/6Q1/6K1/8/8/8/8/8 b - - 0 1")
        with self.assertRaisesRegex(ValueError, "TERMINAL"):
            score_after_frozen_own(board, chess.WHITE, self.engine)


if __name__ == "__main__":
    unittest.main()
