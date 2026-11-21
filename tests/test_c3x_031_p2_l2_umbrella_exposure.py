"""P2-L2 source-original event macro grouping regressions and deliberate negatives.

Requires original TWIC 1670 PGN, 64-game pre-treatment freeze and true P2
native treatment JSON. Synthetic input edits count ONLY as failed integrity
tests, not as new source search results.
"""
import json
import os
from pathlib import Path
import tempfile
import unittest

from c3x_031_p2_l2_umbrella_exposure import (
    ORIGINAL_EXPECTED_MACRO, audit, frozen_original_macro, require,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get("C3X_P2_L1_SOURCE", "/tmp/c3x-p2-l1/source/twic1670g.zip"))
GAMES = Path(os.environ.get("C3X_P2_L1_GAMES", "/tmp/c3x-p2-l1/games/C3X_031_P2_TWIC1670_GAME_FREEZE_FULL_HISTORIES.json"))
TREATMENT = Path(os.environ.get("C3X_P2_L1_TREATMENT", "/tmp/c3x-p2-l1/treatment/C3X_031_P2_TWIC1670_TREATED_NATIVE_ALL_EVENTS.json"))
R26 = ROOT / "receipts/C3X_030_R26_TT_PREOUTCOME_20261117.json"
COURT = ROOT / "harness/c3x_031_p2_independent_court.py"


class MacroLineageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = audit(SOURCE, R26, GAMES, TREATMENT, COURT)

    def test_original_macro_map_reused_exactly(self):
        self.assertEqual(frozen_original_macro(COURT), ORIGINAL_EXPECTED_MACRO)
        self.assertTrue(self.results["original_macro_mapping_exactly_matches_source"])

    def test_primary_outcomes_and_model_not_reselected(self):
        self.assertEqual(self.results["P2_original_native_source_events_untouched"], 128)
        self.assertEqual(self.results["P2_original_root_flips_untouched"], 7)
        self.assertFalse(self.results["model_retrained"])
        self.assertEqual(self.results["new_engine_searches"], 0)
        self.assertEqual(self.results["primary_P2_scientific_gate"],
                         "NEGATIVE_PROSPECTIVE_TRANSPORT")

    def test_exact_literal_replicates_separate_l1_evidence(self):
        strict = self.results["literal_exact"]
        self.assertEqual((strict["removed_game_count"], strict["removed_event_count"],
                          strict["retained_events"], strict["retained_true_root_flips"]),
                         (8, 16, 112, 7))
        self.assertAlmostEqual(strict["scores"]["m2"]["brier"],
                               0.06015073308975114, places=13)

    def test_original_predeclared_macro_removes_p2_028_flip(self):
        macro = self.results["predeclared_macro_names"]
        self.assertEqual((macro["removed_game_count"], macro["removed_event_count"],
                          macro["retained_events"], macro["retained_true_root_flips"]),
                         (16, 32, 96, 6))
        self.assertEqual(macro["retained_macro_event_families"], 10)
        self.assertEqual(macro["removed_true_flip_events"], ["P2-028-0"])
        self.assertEqual(len(macro["overlap_p2_exact_families"]), 4)
        self.assertEqual(macro["evidence_class"],
                         "POSTOUTCOME_PRIOR_REGISTERED_MACRO_FAMILY_SENSITIVITY")

    def test_macro_brier_gain_changes_sign_but_not_frozen_gate(self):
        m = self.results["predeclared_macro_names"]
        self.assertAlmostEqual(m["scores"]["m0"]["brier"], 0.059303827894958236, places=13)
        self.assertAlmostEqual(m["scores"]["m1"]["brier"], 0.05646047308975103, places=10)
        self.assertAlmostEqual(m["scores"]["m2"]["brier"], 0.05503847463871406, places=10)
        self.assertAlmostEqual(m["differences"]["m1_minus_m2"]["gain"],
                               0.0014219984510369654, places=12)
        self.assertEqual(m["source_gain_gate"], "NO_VALIDATED_M2_BRIER_ADVANTAGE")

    def test_recheck_macro_uncertainty_not_only_point_estimate(self):
        c = self.results["predeclared_macro_names"]["differences"]
        for v in c.values():
            self.assertLess(v["macro_family_bootstrap95"][0], 0)
            self.assertGreater(v["macro_family_bootstrap95"][1], 0)
            self.assertLess(v["gain"], 0.01)

    def test_later_alias_scenario_is_not_precommitted_or_proven(self):
        x = self.results["later_conservative_name_alias_scenario_NOT_VERIFIED"]
        self.assertEqual(x["evidence_class"],
                         "LATER_HYPOTHETICAL_UMBRELLA_NAME_ALIAS_SCENARIO")
        self.assertEqual((x["removed_game_count"], x["removed_event_count"],
                          x["retained_events"], x["retained_true_root_flips"]),
                         (26, 52, 76, 5))
        self.assertEqual(x["removed_true_flip_events"], ["P2-028-0", "P2-055-0"])
        self.assertEqual(x["retained_macro_event_families"], 8)
        self.assertEqual(x["source_gain_gate"], "NO_VALIDATED_M2_BRIER_ADVANTAGE")

    def test_source_p2_028_priority_is_originally_macro_exposed(self):
        x = self.results["priority_P2_D1_original_pair_P2_028"]
        self.assertTrue(x["same_PREDECLARED_macro_event_family_as_R26"])
        self.assertFalse(x["selected_original_history_is_R26_duplicate"])
        self.assertFalse(x["same_literal_R26_event_header"])

    def test_cannot_promote_any_exposure_sensitivity_to_blind_new_study(self):
        # No source-state mediator has been claimed by this audit.
        self.assertTrue(self.results["no_causal_TT_or_history_mediator_claim"])
        self.assertTrue(self.results["no_chess_strategy_claim"])
        for key in ("literal_exact", "predeclared_macro_names",
                    "later_conservative_name_alias_scenario_NOT_VERIFIED"):
            self.assertLess(self.results[key]["differences"]["m1_minus_m2"]["gain"], 0.01)

    def test_mutated_predeclared_macro_map_is_rejected(self):
        source = COURT.read_text(encoding="utf8")
        poisoned = source.replace(
            '"fide world open u20 rapid": "fide world open u20"',
            '"fide world open u20 rapid": "not-the-original-family"',
        )
        self.assertNotEqual(source, poisoned)
        with tempfile.TemporaryDirectory() as folder:
            f = Path(folder) / "prior_macro.py"
            f.write_text(poisoned, encoding="utf8")
            with self.assertRaisesRegex(ValueError, "has drifted"):
                frozen_original_macro(f)


if __name__ == "__main__":
    unittest.main()
