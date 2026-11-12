import copy
import unittest
from c3x_030_f2_blind_game_manifest import manifest
from c3x_030_s4h1_cohort_firewall import audit

class CohortFirewall(unittest.TestCase):
    def setUp(self):
        self.m = manifest()

    def test_frozen_cohort_is_legal_but_not_random(self):
        r = audit(self.m)
        self.assertEqual((r["development_games"], r["holdout_games"]), (4, 8))
        self.assertFalse(r["causal_effect_or_superiority_tested"])
        self.assertEqual(r["verdict"], "PASS_IDENTITY_FIREWALL_ONLY")

    def test_fen_forgery_rejected(self):
        self.m["entries"][0]["fen"] = self.m["entries"][1]["fen"]
        with self.assertRaisesRegex(ValueError, "FEN_RECONSTRUCTION|DUPLICATE_FEN"):
            audit(self.m)

    def test_illegal_move_rejected(self):
        self.m["entries"][0]["history_uci"][0] = "e2e5"
        with self.assertRaisesRegex(ValueError, "ILLEGAL_HISTORY"):
            audit(self.m)

    def test_prefix_mismatch_rejected(self):
        a, b = self.m["entries"][0], self.m["entries"][1]
        # Disturb the 8-ply snapshot without changing 10-ply history.
        # A valid position from another game still cannot share its lineage.
        a["history_uci"] = self.m["entries"][2]["history_uci"][:]
        with self.assertRaises(ValueError):
            audit(self.m)

    def test_outcome_leak_rejected_in_development_too(self):
        self.m["development_entries"][0]["label"] = 1
        with self.assertRaisesRegex(ValueError, "OUTCOME_LEAK"):
            audit(self.m)

    def test_holdout_game_collision_rejected(self):
        self.m["entries"][0]["game_id"] = self.m["development_entries"][0]["game_id"]
        with self.assertRaises(ValueError):
            audit(self.m)

    def test_missing_game_snapshot_rejected(self):
        self.m["entries"].pop()
        with self.assertRaisesRegex(ValueError, "SPLIT_CASE_COUNT"):
            audit(self.m)

    def test_fake_random_sample_rejected(self):
        self.m["random_population_sample"] = True
        with self.assertRaisesRegex(ValueError, "SAMPLING_SCOPE"):
            audit(self.m)

if __name__ == "__main__":
    unittest.main()
