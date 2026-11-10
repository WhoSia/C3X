"""R30-B: distinguish computed preferred action, final score, actual choice."""
import unittest
from c3x_029_p42_r30_source_stage_override_diagnostic import audit


def fixture():
    return {
        "state_key": "synthetic:position:1",
        "source_engine": "synthetic-test-only", "depth": 12,
        "observed_candidate_support": ["a", "b", "c"],
        "intermediate_candidate_scores": {"a": 100, "b": 90, "c": 0},
        "final_candidate_scores": {"a": 50, "b": 60, "c": 0},
        "final_action": "b",
    }


class OverrideContract(unittest.TestCase):
    def test_override_detected(self):
        x = audit(fixture())
        self.assertTrue(x["intermediate_vs_final_score_override"])
        self.assertTrue(x["intermediate_vs_actual_final_action"])
        self.assertFalse(x["score_argmax_vs_actual_action_inconsistent"])
        self.assertEqual(x["intermediate_preference_margin"], 10)
        self.assertEqual(x["final_action_score_disadvantage_to_best_in_final_snapshot"], 0)

    def test_stable_unchanged(self):
        x = fixture()
        x["final_candidate_scores"] = dict(x["intermediate_candidate_scores"])
        x["final_action"] = "a"
        self.assertFalse(audit(x)["intermediate_vs_actual_final_action"])

    def test_detect_snapshot_action_inconsistency(self):
        x = fixture()
        x["final_action"] = "c"
        self.assertTrue(audit(x)["score_argmax_vs_actual_action_inconsistent"])

    def test_reject_different_action_support(self):
        x = fixture()
        x["final_candidate_scores"]["d"] = 3
        with self.assertRaisesRegex(ValueError, "SUPPORT"):
            audit(x)

    def test_require_actual_action_in_vector(self):
        x = fixture()
        x["final_action"] = "unknown"
        with self.assertRaisesRegex(ValueError, "SUPPORT"):
            audit(x)

    def test_tie_break_deterministic(self):
        x = fixture()
        x["intermediate_candidate_scores"] = {"c": 5, "b": 5, "a": 5}
        self.assertEqual(audit(x)["intermediate_preferred"], "a")

    def test_reject_nan(self):
        x = fixture()
        x["intermediate_candidate_scores"]["a"] = float("nan")
        with self.assertRaisesRegex(ValueError, "INVALID"):
            audit(x)

    def test_reject_invalid_depth(self):
        x = fixture()
        x["depth"] = 0
        with self.assertRaisesRegex(ValueError, "PROVENANCE"):
            audit(x)


if __name__ == "__main__":
    unittest.main()
