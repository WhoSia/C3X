"""0.31/P2 original 576-run science gate plus deliberately corrupted fixtures."""
import json
import os
from pathlib import Path
from copy import deepcopy
import unittest

from c3x_031_p2_independent_court import verify

SOURCE=Path(os.environ.get("C3X_P2_SOURCE","/tmp/p2-precontact/C3X_031_P2_PHYSICAL_EVENT_AND_FORECAST_PRETREATMENT.json"))
TREATED=Path(os.environ.get("C3X_P2_TREATED","/tmp/p2-treated/C3X_031_P2_TWIC1670_TREATED_NATIVE_ALL_EVENTS.json"))
LOGS=Path(os.environ.get("C3X_P2_LOGS","/tmp/p2-native-logs"))


class P2OriginalCourt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads(SOURCE.read_text())
        cls.treated=json.loads(TREATED.read_text())
        cls.court=verify(cls.source,cls.treated,LOGS)

    def test_original_full_source_search_denominator(self):
        self.assertEqual(self.court["verified_original_treatment_and_sham_searches"],576)
        self.assertEqual(self.court["original_verified_raw_stderr_and_UCI_files"],1152)
        self.assertEqual(self.court["event_outcome_counts"]["sham_verified"],64)
        self.assertEqual(self.court["event_outcome_counts"]["treated_native_runs_verified"],512)

    def test_predictor_transport_is_real_negative(self):
        self.assertEqual(self.court["P2_science_verdict"],"NEGATIVE_PROSPECTIVE_TRANSPORT")
        s=self.court["predictor_metrics_recomputed_from_original_raw"]
        self.assertAlmostEqual(s["m0"]["brier"],.05288425425154738,places=13)
        self.assertAlmostEqual(s["m1"]["brier"],.05493915369453629,places=13)
        self.assertAlmostEqual(s["m2"]["brier"],.06216502489971843,places=13)
        self.assertEqual(s["m2"]["predicted_positive"],4)
        self.assertEqual(s["m2"]["true_positive_at_0_5"],0)

    def test_actual_7_flips_and_depth_censor(self):
        rows=self.court["actual_root_choice_flips"]
        self.assertEqual(len(rows),7)
        self.assertEqual(len({x["event"] for x in rows}),7)
        self.assertEqual(
            self.court["event_outcome_counts"]["root_flip_with_same_completed_depth"],1)
        self.assertEqual(
            self.court["event_outcome_counts"]["root_flip_with_different_completed_depth"],6)
        self.assertEqual(
            self.court["event_outcome_counts"]["futility_only_flip_g1"],0)
        self.assertEqual(
            self.court["event_outcome_counts"]["root_flip_g1"],4)
        self.assertEqual(
            self.court["event_outcome_counts"]["root_flip_g0"],3)

    def test_prespecified_macro_family_sensitivity_separate(self):
        self.assertEqual(self.court["event_family_groups"],17)
        self.assertEqual(self.court["predeclared_macro_group_sensitivity"],12)
        self.assertEqual(
            self.court["new_native_searches_in_this_court"],0)

    def test_reject_rewritten_frozen_prediction(self):
        damaged=deepcopy(self.treated)
        damaged["cases"][0]["targets"]["0"]["frozen_predictions"]["m2"]=.999
        with self.assertRaisesRegex(ValueError,"forecast"):
            verify(self.source,damaged,LOGS)

    def test_reject_reported_sham_flip(self):
        damaged=deepcopy(self.treated)
        damaged["cases"][0]["sham_result"]="a1a8"
        with self.assertRaisesRegex(ValueError,"sham"):
            verify(self.source,damaged,LOGS)

    def test_reject_treatment_target_contact_fabrication(self):
        damaged=deepcopy(self.treated)
        damaged["cases"][0]["targets"]["0"]["arms"]["both_off"]["full_repeats"][0]["event"]["open"]["root"]="a1a8"
        with self.assertRaisesRegex(ValueError,"signature"):
            verify(self.source,damaged,LOGS)

    def test_reject_downstream_model_retraining(self):
        damaged=deepcopy(self.treated)
        damaged["original_p1_train_model_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"model/source"):
            verify(self.source,damaged,LOGS)


if __name__=="__main__":
    unittest.main()
