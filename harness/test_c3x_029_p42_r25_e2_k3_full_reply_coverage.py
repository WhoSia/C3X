"""R25-E2 retrospective coverage contracts; no chess or engine imports."""
import copy
import unittest
from c3x_029_p42_r25_e2_k3_full_reply_coverage import (
    B2_SCHEMA, E1_SCHEMA, joined_coverage,
)

HASH = "3c8f2a57cefe19fcb7a00925f4434f5008195bce5adeba1e67dc84f18f084f34"


def fixtures():
    replies = ["a2a3", "b2b3", "c2c3", "d2d3"]
    scores = [30, 20, -10, -40]
    full = []
    for name, cp in zip(replies, scores):
        full.append({"opponent_reply": name, "frozen_own_move": "g1f3",
                     **{depth: {"frozen_policy": {"root_mover_cp": cp},
                                "unrestricted": {"root_mover_cp": cp + 5}}
                        for depth in ("12", "16")}})
    e1 = {
        "schema": E1_SCHEMA,
        "status": "SOURCE_ONLY_BEFORE_ANY_R25_REFEREE_ADJUDICATION",
        "independent_referee_consulted_for_ranking": False,
        "first_opponent_layer_only_not_full_Cui_tree": True,
        "original_R24_frozen_147_policy_sha256": HASH,
        "cases": [{"case_id": "synthetic", "event_family": "test", "roots": [{
            "root_uci": "e2e4", "legal_first_opponent_replies": 4,
            "ranked_replies": [
                {"opponent_reply": name, "engine_rank": i + 1,
                 "frozen_source_own_move": "g1f3"}
                for i, name in enumerate(replies[:3])]
        }]}]
    }
    b2 = {
        "schema": B2_SCHEMA, "prejudge_plan_sha256": HASH,
        "cases": [{"case_id": "synthetic", "event_family": "test", "roots": [{
            "root": "e2e4", "reply_results": full,
        }]}]
    }
    return e1, b2


class CoverageContract(unittest.TestCase):
    def test_truncated_worst_case_is_optimistic(self):
        e1, b2 = fixtures()
        row = joined_coverage(e1, b2)["cases"][0]["roots"][0]
        p = row["estimates"]["16"]["frozen_policy"]
        self.assertEqual(p["full_reply_worst_cp"], -40)
        self.assertEqual(p["source_ranked_k3_worst_cp"], -10)
        self.assertEqual(p["k3_optimism_cp"], 30)
        self.assertFalse(p["full_worst_in_k3"])

    def test_coverage_exact_when_worst_in_k3(self):
        e1, b2 = fixtures()
        b2["cases"][0]["roots"][0]["reply_results"][3]["16"]["frozen_policy"]["root_mover_cp"] = 40
        p = joined_coverage(e1, b2)["cases"][0]["roots"][0]["estimates"]["16"]["frozen_policy"]
        self.assertEqual(p["k3_optimism_cp"], 0)
        self.assertTrue(p["full_worst_in_k3"])

    def test_reject_provenance_mismatch(self):
        e1, b2 = fixtures()
        e1["independent_referee_consulted_for_ranking"] = True
        with self.assertRaisesRegex(ValueError, "PROVENANCE"):
            joined_coverage(e1, b2)

    def test_reject_duplicate_engine_rank(self):
        e1, b2 = fixtures()
        e1["cases"][0]["roots"][0]["ranked_replies"][1]["engine_rank"] = 1
        with self.assertRaisesRegex(ValueError, "SELECTION"):
            joined_coverage(e1, b2)

    def test_reject_action_drift(self):
        e1, b2 = fixtures()
        e1["cases"][0]["roots"][0]["ranked_replies"][0]["frozen_source_own_move"] = "a2a4"
        with self.assertRaisesRegex(ValueError, "DRIFT"):
            joined_coverage(e1, b2)

    def test_reject_incomplete_full_reply_set(self):
        e1, b2 = fixtures()
        b2["cases"][0]["roots"][0]["reply_results"].pop()
        with self.assertRaisesRegex(ValueError, "FULL_REPLY"):
            joined_coverage(e1, b2)

    def test_reject_unadmitted_score(self):
        e1, b2 = fixtures()
        b2["cases"][0]["roots"][0]["reply_results"][0]["16"]["frozen_policy"]["root_mover_cp"] = None
        with self.assertRaisesRegex(ValueError, "FINITE_SCORE"):
            joined_coverage(e1, b2)


if __name__ == "__main__":
    unittest.main()
