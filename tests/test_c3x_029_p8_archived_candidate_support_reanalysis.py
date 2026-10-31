"""C3X 0.29 P8 original frozen-forecast / native-receipt regression tests."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1] / "tools"))
from c3x_029_p8_archived_candidate_support_reanalysis import analyze

class SourceRiskAndThirdCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=analyze()
        cls.t=cls.r["twic"]
    def test_games_not_roles_are_independent_units(self):
        self.assertEqual(self.t["source_games"],16)
        self.assertEqual(self.t["eligible_role_cells"],64)
        self.assertEqual(self.t["actually_flipped_game_ids"],[1,4,7,10])
        self.assertEqual(self.t["disagreed_but_not_flipped_games"],[3,12,13,14])
    def test_three_outcome_classes_are_exhaustive(self):
        c=self.t["class_distribution"]
        self.assertEqual(c,{"unchanged":54,"changed_to_other_baseline_move":6,"changed_to_third_move":4})
        self.assertEqual(sum(c.values()),64)
    def test_candidate_support_ceiling_and_baselines(self):
        self.assertEqual(self.t["two_baseline_output_oracle_accuracy_ceiling_in_this_sample"],60/64)
        self.assertEqual(self.t["exact_old_forecast_accuracy"],38/64)
        self.assertEqual(self.t["always_nochange_accuracy"],54/64)
        self.assertEqual(self.t["binary_flip_accuracy"],42/64)
    def test_selective_easy_subset_is_not_positive_causal_explanation(self):
        self.assertEqual(self.t["risk_marker_agreement_only_coverage"],0.5)
        self.assertEqual(self.t["agreement_only_observed_exact_accuracy"],1)
        self.assertEqual(self.r["puzzles"]["actual_flips"],0)
        self.assertFalse(self.r["puzzles"]["positive_flip_prediction_validated"])
if __name__=="__main__":
    unittest.main()
