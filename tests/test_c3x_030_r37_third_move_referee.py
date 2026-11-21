"""R37 fixed board legality and fake-leaf fail-closed checks.

Only the external workflow, not these mocks, runs the actual Berserk referee.
"""
from copy import deepcopy
import unittest

from c3x_030_r37_third_move_referee import (
    CANDIDATES, DEPTHS, FEN, REPEATS, prepare, summarize,
)
import chess


def synthetic_cases():
    result = []
    for i, move in enumerate(CANDIDATES):
        samples = {}
        for reply in ("e7e5", "d7d6"):
            samples[reply] = {}
            for depth in DEPTHS:
                cp = (10 + i * 20) - (1 if reply == "e7e5" else 7) + depth
                item = {"type": "cp", "cp": cp, "mate": None,
                        "depth": depth, "nodes": depth * 120,
                        "pv": ["a2a4"], "completed": True}
                samples[reply][str(depth)] = [deepcopy(item) for _ in REPEATS]
        result.append({"candidate": move, "san": CANDIDATES[move],
                       "legal_replies": list(samples), "results": samples})
    return result


class R37Tests(unittest.TestCase):
    def test_actual_r30_017_board_and_three_fixed_legal_moves(self):
        plan = prepare()
        self.assertEqual([c["candidate"] for c in plan], list(CANDIDATES))
        self.assertEqual(len(plan), 3)
        self.assertEqual(chess.Board(FEN).turn, chess.WHITE)
        for c in plan:
            self.assertEqual(len(c["legal_replies"]), len(set(c["legal_replies"])))
            self.assertGreater(len(c["legal_replies"]), 10)
            child = chess.Board(FEN)
            child.push_uci(c["candidate"])
            for reply in c["legal_replies"]:
                self.assertIn(chess.Move.from_uci(reply), child.legal_moves)

    def test_mock_two_depth_order_is_only_finite(self):
        court = summarize(synthetic_cases())
        self.assertEqual(court["depth_order_status"], "FINITE_TWO_DEPTH_ORDER_STABLE")
        self.assertTrue(court["not_strategic_oracle"])
        for depth in DEPTHS:
            self.assertEqual(court["comparison"][str(depth)]["bounded_referee_ranking"],
                             ["a2a3", "e2d3", "e2f3"])

    def test_missing_reply_not_silently_dropped(self):
        rows = synthetic_cases()
        del rows[0]["results"]["e7e5"]
        with self.assertRaisesRegex(ValueError, "missing or added"):
            summarize(rows)

    def test_censored_depth_blocks_full_ranking(self):
        rows = synthetic_cases()
        rows[0]["results"]["e7e5"]["10"][1]["completed"] = False
        court = summarize(rows)
        self.assertFalse(court["comparison"]["10"]["all_candidates_finite"])
        self.assertIsNone(court["comparison"]["10"]["bounded_referee_ranking"])
        self.assertEqual(court["depth_order_status"], "HOLD_OR_DEPTH_ORDER_CHANGED")

    def test_nonidentical_cold_replay_blocks_full_ranking(self):
        rows = synthetic_cases()
        rows[2]["results"]["d7d6"]["12"][1]["nodes"] += 1
        court = summarize(rows)
        self.assertFalse(court["candidate_depth_results"]["a2a3"]["12"]["all_legal_replies_scored"])

    def test_mate_score_does_not_become_fake_centipawn(self):
        rows = synthetic_cases()
        row = rows[1]["results"]["e7e5"]["10"][0]
        row.update({"type": "mate", "cp": None, "mate": 4})
        court = summarize(rows)
        self.assertIsNone(court["comparison"]["10"]["bounded_referee_ranking"])

    def test_duplicate_reply_rejected(self):
        rows = synthetic_cases()
        rows[0]["legal_replies"].append("e7e5")
        with self.assertRaisesRegex(ValueError, "duplicate opponent reply"):
            summarize(rows)


if __name__ == "__main__":
    unittest.main()
