"""Counterexamples and incomplete-evidence checks for the reply-scope audit."""

import unittest

from c3x_030_s4l_r10_reply_transport import board_at
from c3x_030_s4l_r13_reply_scope import partition, read_points


class ReplyScopeTests(unittest.TestCase):
    def test_an_exclusive_refutation_can_reverse_shared_dominance(self):
        verdict = partition({"common": 5, "exclusive": -9}, {"common": 0})
        self.assertEqual(verdict["reply_deltas"], {"common": 5})
        self.assertEqual(verdict["shared_minima_gap"], 5)
        self.assertEqual(verdict["full_gap"], -9)
        self.assertEqual(verdict["roots"][0]["minimizers"], ["exclusive"])

    def test_one_favorable_reply_can_hide_a_flip_in_the_common_set(self):
        verdict = partition({"x": 8, "y": -3}, {"x": 2, "y": 0})
        self.assertEqual(verdict["directions"], {"-1": 1, "0": 0, "1": 1})
        self.assertEqual(verdict["shared_minima_gap"], -3)

    def test_missing_points_do_not_create_minima(self):
        result = partition({"yes": 4, "pending": None}, {"yes": 2, "pending": 0})
        self.assertEqual(result["reply_deltas"], {"pending": None, "yes": 2})
        self.assertIsNone(result["full_gap"])
        self.assertIsNone(result["shared_minima_gap"])

    def test_abstain_on_falsely_terminal_and_stale_depth_receipts(self):
        board = board_at(["e2e4"])
        replies = {m.uci(): {"point": None} for m in board.legal_moves}
        replies["e7e5"]["point"] = {"depth": 0, "nodes": 0, "pv": [], "bound": False}
        replies["c7c5"]["point"] = {"depth": 12, "ordered": 30, "bound": False}
        self.assertIsNone(read_points(board, replies, 14)["e7e5"])
        self.assertIsNone(read_points(board, replies, 14)["c7c5"])
        self.assertEqual(read_points(board, replies, 12)["c7c5"], 30)

    def test_illegal_reply_inventory_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "legal replies"):
            read_points(board_at(["e2e4"]), {}, 12)


if __name__ == "__main__":
    unittest.main()
