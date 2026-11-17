"""Verify the bounded mate results for the published pair of diagrams."""

import unittest

from c3x_030_s4m_r2_wilkins_countercausal import replay


class WilkinsCountercausalTest(unittest.TestCase):
    def test_only_e5_breaks_the_second_diagrams_bounded_mate(self):
        figures = replay()["figures"]
        self.assertEqual(
            {move: row["mate_plies_after_black_move"]
             for move, row in figures["1"]["rook_alternatives"].items()},
            {"Rc5": 3, "Rd5": 3, "Re5": 3, "Rf5": 3},
        )
        two = figures["2"]["rook_alternatives"]
        self.assertEqual(
            {move: row["mate_plies_after_black_move"] for move, row in two.items()},
            {"Rc5": 5, "Rd5": 5, "Re5": None, "Rf5": 5},
        )
        self.assertEqual(two["Re5"]["mate_plies_after_each_defense"],
                         {"Be8": None, "Re8": None})
        self.assertEqual(two["Rc5"]["mate_plies_after_each_defense"],
                         {"Be8": 1, "Rc8": 3})


if __name__ == "__main__":
    unittest.main()
