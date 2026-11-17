import unittest

import chess

from c3x_030_r22_menu_score import minimum, rank
from c3x_030_r22_reply_menus import make_menus
from c3x_030_r22_window_audit import attempt, encode, order


def candidate(move, number, value, depth=8):
    return {"iteration": 8, "depth": depth, "alpha": 30, "beta": 62,
            "root_move_raw": move, "move_count": number, "value": value}


class WindowAuditTest(unittest.TestCase):
    def test_partial_fail_low_abstains_but_beta_cutoff_does_not_need_all_moves(self):
        legal = {20, 30}
        self.assertEqual(attempt([candidate(20, 1, 17)], legal)[1], "no_certifiable_threshold")
        self.assertEqual(attempt([candidate(20, 1, 17), candidate(30, 2, 30)], legal)[0],
                         ("upper", 9))
        self.assertEqual(attempt([candidate(20, 1, 70)], legal)[0], ("lower", 18))

    def test_reduced_depth_and_repeated_move_cannot_certify_root(self):
        self.assertEqual(attempt([candidate(20, 1, 70, depth=7)], {20})[1], "effective_depth")
        self.assertEqual(attempt([candidate(20, 1, 17), candidate(20, 2, 20)], {20, 30})[1],
                         "invalid_move_coverage")
        self.assertIsNone(order(((10, None), (None, 10))))
        self.assertEqual(order(((11, None), (None, 10))), 1)

    def test_stockfish_native_encoding_special_moves(self):
        castles = chess.Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
        self.assertEqual(encode(castles, castles.parse_san("O-O")), (3 << 14) | (4 << 6) | 7)
        en_passant = chess.Board("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1")
        self.assertEqual(encode(en_passant, en_passant.parse_san("exd6")), (2 << 14) | (36 << 6) | 43)
        promotion = chess.Board("4k3/P7/8/8/8/8/8/4K3 w - - 0 1")
        self.assertEqual(encode(promotion, promotion.parse_san("a8=Q")), (1 << 14) | (3 << 12) | (48 << 6) | 56)


class ReplyMenuTest(unittest.TestCase):
    def test_differential_capture_gets_third_slot(self):
        boards = [chess.Board("4k3/8/8/8/r7/8/P7/4K3 b - - 0 1"),
                  chess.Board("4k3/8/8/8/r7/8/8/4K3 b - - 0 1")]
        common = ["e8d8", "e8f8", "a4a2", "a4a3"]
        menus, tactical = make_menus(boards, common, [common, common[1:] + common[:1]])
        self.assertEqual(menus["mixed"], ["e8d8", "e8f8", "a4a2"])
        self.assertEqual(list(tactical), ["a4a2"])

    def test_minimum_keeps_ties_and_does_not_ignore_unknown_replies(self):
        rows = {"a": [2, 5], "b": [2, 3], "c": [4, None]}
        self.assertEqual(minimum(rows, rows, 0), {"cp": 2, "moves": ["a", "b"]})
        self.assertIsNone(minimum(rows, rows, 1))
        self.assertIsNone(rank([minimum(rows, rows, 0), None]))


if __name__ == "__main__":
    unittest.main()
