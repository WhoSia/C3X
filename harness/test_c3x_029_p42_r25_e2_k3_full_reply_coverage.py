"""R25-E2: native 48-search replacement tests (synthetic, NOT evidence)."""
import unittest
import chess
from c3x_029_p42_r25_e2_k3_full_reply_coverage import (
    B2_SCHEMA, E1_SCHEMA, compare_minima, validate_join,
)

HASH = "3c8f2a57cefe19fcb7a00925f4434f5008195bce5adeba1e67dc84f18f084f34"


def fixtures():
    board = chess.Board()
    child = board.copy(stack=True)
    child.push_uci("e2e4")
    universe = sorted(x.uci() for x in child.legal_moves)
    names = ["e7e5", "c7c5", "e7e6"]
    e1 = {
        "schema": E1_SCHEMA,
        "status": "SOURCE_ONLY_BEFORE_ANY_R25_REFEREE_ADJUDICATION",
        "independent_referee_consulted_for_ranking": False,
        "first_opponent_layer_only_not_full_Cui_tree": True,
        "original_R24_frozen_147_policy_sha256": HASH,
        "cases": [{"case_id": "synthetic", "event_family": "test", "roots": [{
            "root_uci": "e2e4", "legal_first_opponent_replies": len(universe),
            "ranked_replies": [{"opponent_reply": u, "engine_rank": i + 1,
                                "frozen_source_own_move": "g1f3"}
                               for i, u in enumerate(names)]
        }]}]}
    b2 = {
        "schema": B2_SCHEMA, "prejudge_plan_sha256": HASH,
        "cases": [{"case_id": "synthetic", "event_family": "test", "roots": [{
            "root_uci": "e2e4", "source_legal_reply_count": len(universe),
            "depth_evaluations": {"12": {"all_legal_reply_plan_scores_finite": True},
                                  "16": {"all_legal_reply_plan_scores_finite": True}},
        }]}]
    }
    worlds = [({"case_id": "synthetic", "event_family": "test"},
               board, [{"root": "e2e4", "replies": universe}])]
    return e1, b2, worlds


class NativeJoinContract(unittest.TestCase):
    def test_join_preserves_ranked_legal_replies(self):
        e1, b2, worlds = fixtures()
        tasks = validate_join(e1, b2, worlds)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0][2][0][1]["ranked_replies"][0]["opponent_reply"], "e7e5")

    def test_reject_judge_leakage(self):
        e1, b2, worlds = fixtures()
        e1["independent_referee_consulted_for_ranking"] = True
        with self.assertRaisesRegex(ValueError, "PROVENANCE"):
            validate_join(e1, b2, worlds)

    def test_reject_rank_duplicate(self):
        e1, b2, worlds = fixtures()
        e1["cases"][0]["roots"][0]["ranked_replies"][1]["engine_rank"] = 1
        with self.assertRaisesRegex(ValueError, "SELECTION"):
            validate_join(e1, b2, worlds)

    def test_reject_illegal_frozen_own_move(self):
        e1, b2, worlds = fixtures()
        e1["cases"][0]["roots"][0]["ranked_replies"][0]["frozen_source_own_move"] = "e7e5"
        with self.assertRaisesRegex(ValueError, "ILLEGAL"):
            validate_join(e1, b2, worlds)

    def test_reject_incomplete_original_support(self):
        e1, b2, worlds = fixtures()
        b2["cases"][0]["roots"][0]["source_legal_reply_count"] = 3
        with self.assertRaisesRegex(ValueError, "SUPPORT"):
            validate_join(e1, b2, worlds)

    def test_subset_minima_consistency(self):
        ok = compare_minima(-10, -40)
        self.assertEqual(ok["delta_k3_minus_full_cp"], 30)
        self.assertTrue(ok["valid_subset_minimum_if_replay_consistent"])
        bad = compare_minima(-50, -40)
        self.assertFalse(bad["valid_subset_minimum_if_replay_consistent"])
        self.assertIn("HOLD", bad["interpretation"])

    def test_reject_nonfinite(self):
        with self.assertRaisesRegex(ValueError, "NONFINITE"):
            compare_minima(None, 5)


if __name__ == "__main__":
    unittest.main()
