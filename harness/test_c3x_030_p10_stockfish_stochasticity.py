import unittest
from c3x_030_p10_stockfish_stochasticity import summarize, board_for, POSITIONS

class TestP10(unittest.TestCase):
    def test_counts_stable(self):
        data=[{"bestmove_uci":"e2e4","actual_nodes":12,"completed_depth":3} for _ in range(4)]
        r=summarize(data)
        self.assertEqual(r["distinct_best_moves"],1)
        self.assertFalse(r["best_move_changed_across_trials"])
        self.assertEqual(r["actual_native_nodes"],48)
    def test_counts_variable(self):
        rows=[{"bestmove_uci":m,"actual_nodes":12,"completed_depth":3} for m in ("e2e4","d2d4","e2e4")]
        r=summarize(rows)
        self.assertTrue(r["best_move_changed_across_trials"])
        self.assertEqual(r["best_move_counts"]["e2e4"],2)
    def test_source_positions_legal(self):
        for moves in POSITIONS.values():
            self.assertTrue(board_for(moves).is_valid())
    def test_invalid_history_hold(self):
        with self.assertRaisesRegex(ValueError,"INVALID_PIECE_HISTORY"):
            board_for(["e2e5"])
    def test_empty_trial_hold(self):
        with self.assertRaisesRegex(ValueError,"NO_TRIALS"):
            summarize([])
if __name__=="__main__":
    unittest.main()
