"""Guard the R26 distinctions that change an empirical denominator."""
import unittest

import chess

from c3x_030_r26_tt_audit import gap_band, index_rows, pair_outcome, reference_gap, score
from c3x_030_r26_tt_cohort import position_rows
from c3x_030_r26_tt_panel import board_from_case, info_row


def row(move="g1f3", reply="g8f6", cp=14, depth=11, lowerbound=False):
    return {
        "move": move, "pv": [move, reply] if reply else [move],
        "cp": cp, "mate": None, "depth": depth,
        "lowerbound": lowerbound, "upperbound": False,
    }


class PanelTests(unittest.TestCase):
    def test_equal_score_reply_change_keeps_winner(self):
        flags = pair_outcome(row(), row(reply="d7d5"))
        self.assertEqual(flags["root_changed"], 0)
        self.assertEqual(flags["same_root_equal_score_reply_changed"], 1)

    def test_bound_drops_from_exact_score_denominator(self):
        flags = pair_outcome(row(), row(reply="d7d5", lowerbound=True))
        self.assertEqual(flags["same_root_reply_changed"], 1)
        self.assertEqual(flags["same_root_equal_score_both_replies"], 0)

    def test_stale_pv_head_loses_score_authority(self):
        base = row()
        base["pv"][0] = "e2e4"
        self.assertIsNone(score(base))
        self.assertEqual(pair_outcome(base, row())["same_root_both_replies"], 0)

    def test_reference_requires_two_distinct_exact_cp_rows_at_one_depth(self):
        base = row(cp=54)
        other = row(move="e2e4", cp=4)
        self.assertEqual(gap_band(reference_gap([base, other])), "50+cp")
        self.assertIsNone(reference_gap([base, {**other, "depth": 10}]))
        self.assertIsNone(reference_gap([base, {**other, "cp": None, "mate": 3}]))
        self.assertIsNone(reference_gap([base, base]))

    def test_admit_only_paired_complete_panel(self):
        case = {"id": "x", "game_id": "g", "ply": 30}
        cell = {"case": "x", "game": "g", "ply": 30, "arm": "upstream",
                "requested_nodes": 8000, "result": row()}
        with self.assertRaisesRegex(ValueError, "Panel mismatch"):
            index_rows([cell], {"x": case})
        with self.assertRaisesRegex(ValueError, "Duplicate cell"):
            index_rows([cell, cell], {"x": case})

    def test_board_matches_legal_replay_including_last_move(self):
        moves = ["g1f3", "g8f6", "f3g1", "f6g8"] * 7 + ["e2e4", "e7e5"]
        case, = position_rows({"id": "g", "moves": moves})
        self.assertEqual(len(board_from_case(case).move_stack), 30)
        with self.assertRaisesRegex(ValueError, "History mismatch"):
            board_from_case({**case, "legal_moves": 0})

    def test_illegal_pv_rejected(self):
        board = chess.Board()
        with self.assertRaisesRegex(ValueError, "Illegal PV"):
            info_row(board, {"pv": [chess.Move.from_uci("e2e5")]}, chess.Move.from_uci("e2e4"))


if __name__ == "__main__":
    unittest.main()
