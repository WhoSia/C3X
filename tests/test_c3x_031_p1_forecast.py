"""C3X 0.31 P1 original-data and deliberate-tamper tests."""
from copy import deepcopy
from pathlib import Path
import unittest

from c3x_031_p1_forecast import (
    PUBLIC, SOURCE, average_precision, evaluate, load_rows, matrices,
    sha, validate,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_TABLE = ROOT / "frozen" / "C3X_031_P1_R33_128_PRETREATMENT_ROWS_20261121.tsv"


class P1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_rows(SOURCE_TABLE)
        cls.results = evaluate(cls.rows)

    def test_real_source_sha_and_full_census(self):
        self.assertEqual(sha(SOURCE_TABLE.read_bytes()),
                         "6e5cd1215ab13ac3dba3c93447b577f305c06fad1fd00c2b4a5338c71e7a63ba")
        self.assertEqual(len(self.rows), 128)
        self.assertEqual(len({row["game"] for row in self.rows}), 64)
        self.assertEqual(len({row["family"] for row in self.rows}), 16)
        self.assertEqual(sum(row["y"] for row in self.rows), 11)
        self.assertEqual(self.results["new_native_searches"], 0)

    def test_public_score_bounds_never_relabelled_exact(self):
        games = {r["game"]: r for r in self.rows if r["stratum"] == 0}
        types = [("upper" if r["public_upper_bound"] else
                  "lower" if r["public_lower_bound"] else "exact")
                 for r in games.values()]
        self.assertEqual([types.count(t) for t in ("exact", "upper", "lower")],
                         [34, 23, 7])

    def test_all_oof_predictions_and_no_game_leak(self):
        self.assertEqual(len(self.results["out_of_family_predictions"]), 128)
        self.assertEqual(
            [self.results["score"][k]["positive_count"] for k in ("m0", "m1", "m2")],
            [11, 11, 11])
        self.assertEqual(
            [self.results["source_games"], self.results["event_families"]], [64, 16])
        self.assertTrue(all(0 < r[k] < 1
                            for r in self.results["out_of_family_predictions"]
                            for k in ("m0", "m1", "m2")))

    def test_observed_brier_and_ap_match_original_local_replay(self):
        expected = {"m0": .07982292876169661, "m1": .08086903909274809,
                    "m2": .07758871404803157}
        for model, value in expected.items():
            self.assertAlmostEqual(self.results["score"][model]["brier"], value, places=11)
        self.assertAlmostEqual(self.results["score"]["m0"]["average_precision"],
                               .06872814685314685, places=11)
        self.assertAlmostEqual(self.results["score"]["m2"]["average_precision"],
                               .21258255633255632, places=11)

    def test_no_scientific_promotion_from_tiny_point_gain(self):
        self.assertEqual(self.results["verdict"], "HOLD_NO_PRETREATMENT_SOURCE_STATE_GAIN")
        for contrast in self.results["difference_95ci"].values():
            self.assertLess(contrast["observed"], .01)
            self.assertLess(contrast["bootstrap_95"][0], 0)
            self.assertGreater(contrast["bootstrap_95"][1], 0)
        for field in ("identified_mediator", "minimal_state_sufficiency_proved",
                      "prospective_game_transfer_proved", "human_value_proved"):
            self.assertIs(self.results[field], False)

    def test_tied_average_precision_is_grouped_not_label_sorted(self):
        self.assertAlmostEqual(average_precision([1, 0], [0.1, 0.1]), 0.5)
        self.assertAlmostEqual(average_precision([0, 1], [0.1, 0.1]), 0.5)

    def test_reject_post_treatment_data_leak(self):
        bad = deepcopy(self.rows)
        bad[0]["post_treatment_child_value"] = 9000
        with self.assertRaises(ValueError):
            validate(bad)

    def test_reject_game_family_overlap(self):
        bad = deepcopy(self.rows)
        bad[0]["family"] = 9 if bad[0]["family"] != 9 else 8
        with self.assertRaises(ValueError):
            validate(bad)

    def test_reject_public_bound_contradiction(self):
        bad = deepcopy(self.rows)
        bad[0]["public_upper_bound"] = 1
        bad[0]["public_lower_bound"] = 1
        with self.assertRaises(ValueError):
            validate(bad)

    def test_reject_missing_source_event(self):
        with self.assertRaises(ValueError):
            validate(self.rows[:-1])

    def test_fold_scaling_ignores_heldout_test_values(self):
        train = self.rows[:80]
        held = self.rows[80:81]
        x1, _ = matrices(train, held, PUBLIC + SOURCE)
        poisoned = deepcopy(held)
        poisoned[0]["source_progress_nodes"] = 999999999
        x2, _ = matrices(train, poisoned, PUBLIC + SOURCE)
        self.assertEqual(x1, x2)


if __name__ == "__main__":
    unittest.main()
