"""P2-L1 original R26/P2 source-family collision and negative-result check.

Reads actual signed source files from prior immutable workflow artifacts.
Mutated fixtures test fail-closed behavior only; never count as chess games.
"""
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from c3x_031_p2_l1_historical_family_audit import (
    SOURCE_ZIP_SHA, P2_GAME_SHA, P2_TREATMENT_SHA,
    audit, brier, norm, read_publisher, require,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get("C3X_P2_L1_SOURCE", "/tmp/c3x-p2-l1/source/twic1670g.zip"))
GAMES = Path(os.environ.get("C3X_P2_L1_GAMES", "/tmp/c3x-p2-l1/games/C3X_031_P2_TWIC1670_GAME_FREEZE_FULL_HISTORIES.json"))
TREATMENT = Path(os.environ.get("C3X_P2_L1_TREATMENT", "/tmp/c3x-p2-l1/treatment/C3X_031_P2_TWIC1670_TREATED_NATIVE_ALL_EVENTS.json"))
R26 = ROOT / "receipts/C3X_030_R26_TT_PREOUTCOME_20261117.json"


class P2LineageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = audit(SOURCE, R26, GAMES, TREATMENT)

    def test_real_source_and_complete_game_census(self):
        self.assertEqual(len(read_publisher(SOURCE)), 8391)
        self.assertEqual(self.result["original_P2"]["games"], 64)
        self.assertEqual(self.result["original_P2"]["events"], 128)
        self.assertEqual(self.result["original_P2"]["root_flips"], 7)
        self.assertEqual(self.result["new_native_engine_searches"], 0)

    def test_actual_R26_family_overlap_not_game_identity(self):
        self.assertEqual(self.result["R26_and_P2_shared_tournament_families"], [
            "fide world open u20 rapid", "world girls u20 blitz"])
        self.assertEqual(self.result["original_R26_game_history_count"], 16)
        self.assertEqual(self.result["original_R26_distinct_source_event_families"], 12)
        self.assertEqual(self.result["R26_and_P2_identical_full_game_histories"], 0)

    def test_exact_posthoc_loss_of_16_events_and_zero_flips(self):
        group = self.result["P2_R26_shared_family_subset"]
        self.assertEqual((group["games"], group["events"], group["root_flips"]), (8, 16, 0))
        self.assertEqual(sorted({s.rsplit("-",1)[0] for s in group["event_ids"]}),
                         ["P2-003", "P2-013", "P2-020", "P2-030",
                          "P2-037", "P2-047", "P2-054", "P2-064"])

    def test_112_preserved_events_and_all_seven_root_flips(self):
        kept = self.result["P2_excluding_R26_shared_families_POSTHOC"]
        self.assertEqual((kept["games"], kept["events"], kept["families"],
                          kept["root_flips"]), (56, 112, 15, 7))
        self.assertTrue(kept["all_original_7_chess_move_switches_retained"])
        self.assertEqual(kept["predictive_result"], "NEGATIVE_TRANSFER_REMAINS")

    def test_original_full_metrics_reproduced(self):
        s = self.result["original_P2"]["scores"]
        for key, expected in (("m0", 0.05288425425154738),
                              ("m1", 0.05493915369453629),
                              ("m2", 0.06216502489971843)):
            self.assertAlmostEqual(s[key]["brier"], expected, places=13)

    def test_posthoc_metrics_negative_and_bounded(self):
        s = self.result["P2_excluding_R26_shared_families_POSTHOC"]["scores"]
        for key, expected in (("m0", 0.059303827894958236),
                              ("m1", 0.05891931995816267),
                              ("m2", 0.06015073308975114)):
            self.assertAlmostEqual(s[key]["brier"], expected, places=13)
        u = self.result["P2_excluding_R26_shared_families_POSTHOC"]["brier_difference_95ci"]
        self.assertAlmostEqual(u["m1_minus_m2"]["gain"], -0.00123141313158847, places=13)
        self.assertAlmostEqual(u["m0_minus_m2"]["gain"], -0.000846905194792906, places=13)
        for v in u.values():
            self.assertLess(v["family_bootstrap_95"][0], 0)
            self.assertGreater(v["family_bootstrap_95"][1], 0)

    def test_no_retroactive_unseen_family_claim(self):
        self.assertFalse(self.result["original_P2_primary_analysis_modified"])
        self.assertEqual(self.result["classification"],
                         "POSTOUTCOME_HISTORICAL_EXPOSURE_SENSITIVITY")
        self.assertTrue(any("not fully" in x for x in self.result["scientific_corrections"]))

    def test_normalization_cannot_hide_case_only_overlap(self):
        self.assertEqual(norm(" FIDE World Open U20 Rapid "), "fide world open u20 rapid")
        self.assertEqual(norm("WORLD GIRLS U20 BLITZ"), "world girls u20 blitz")

    def test_reject_unsealed_P2_treatment_modification(self):
        obj = json.loads(TREATMENT.read_text())
        obj["cases"][0]["targets"]["0"]["treatment_bestmove_changed"] = True
        with tempfile.TemporaryDirectory() as folder:
            altered = Path(folder) / "treated.json"
            altered.write_text(json.dumps(obj))
            with self.assertRaisesRegex(ValueError, "SHA changed"):
                audit(SOURCE, R26, GAMES, altered)

    def test_reject_unsealed_P2_source_sample_modification(self):
        obj = json.loads(GAMES.read_text())
        obj["sample"][0]["family"] = "invented-other-source"
        with tempfile.TemporaryDirectory() as folder:
            altered = Path(folder) / "freeze.json"
            altered.write_text(json.dumps(obj))
            with self.assertRaisesRegex(ValueError, "SHA changed"):
                audit(SOURCE, R26, altered, TREATMENT)

    def test_reject_prior_R26_selected_history_relabelling(self):
        obj = json.loads(R26.read_text())
        obj["game_history_hashes"][0]["ordinal"] = 0
        with tempfile.TemporaryDirectory() as folder:
            altered = Path(folder) / "r26.json"
            altered.write_text(json.dumps(obj))
            with self.assertRaisesRegex(ValueError, "invalid original R26"):
                audit(SOURCE, altered, GAMES, TREATMENT)


if __name__ == "__main__":
    unittest.main()
