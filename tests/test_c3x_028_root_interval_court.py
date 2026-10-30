"""C3X 0.28 independent finite oracle, no Stockfish/WSL requirements."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from c3x_028_root_interval_court import (
    Interval, winner, logically_possible_winners, guaranteed_winner,
    exhaustive_possible, two_ply_root, enumerate_single_leaf_counterexamples,
    self_court,
)


class RootBoundsCourt(unittest.TestCase):
    def test_tie_priority_is_stable(self):
        c = [Interval('A', 2, 2), Interval('B', 2, 2)]
        self.assertEqual(winner((2, 2)), 0)
        self.assertEqual(logically_possible_winners(c), ['A'])
        self.assertEqual(guaranteed_winner(c), 'A')
        self.assertEqual(exhaustive_possible(c), {'A'})

    def test_intervals_that_overlap_are_ambiguous(self):
        c = [Interval('A', 2, 4), Interval('B', 3, 5)]
        self.assertEqual(set(logically_possible_winners(c)), {'A', 'B'})
        self.assertIsNone(guaranteed_winner(c))

    def test_strict_upper_gap_is_guaranteed(self):
        self.assertEqual(guaranteed_winner([
            Interval('A', 4, 7), Interval('B', 2, 3)]), 'A')

    def test_minimax_hypotheses_have_counterexamples(self):
        self.assertEqual(two_ply_root((8, 7, 6, 9)), (7, 6, 'A'))
        self.assertEqual(two_ply_root((8, 7, 7, 9)), (7, 7, 'A'))
        self.assertEqual(two_ply_root((8, 7, 8, 9)), (7, 8, 'B'))
        result = enumerate_single_leaf_counterexamples()
        self.assertEqual(result['counts']['root_changed_without_parent_change'], 0)
        self.assertTrue(all(result['counts'][key] for key in
                            ('child_change_parent_same', 'parent_change_root_same', 'root_choice_changed')))

    def test_independent_oracle_exhaustive(self):
        self.assertEqual(self_court()['interval_triples_exhaustively_compared'], 216)


if __name__ == '__main__':
    unittest.main()
