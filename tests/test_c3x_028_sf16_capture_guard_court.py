"""A tiny finite source-logic court for Stockfish16 post-SEE pruning."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from c3x_028_sf16_capture_guard_court import post_see_prunes, finite_court


class SF16PostSeeCourt(unittest.TestCase):
    def test_see_true_is_not_post_see_prune(self):
        for depth in (-1, 0, 1, 2):
            for capture in (False, True):
                for retained in (False, True):
                    self.assertFalse(post_see_prunes(see_ge=True, depth=depth,
                        capture=capture, discovered_attack_retains=retained))

    def test_see_false_not_sufficient_for_prune(self):
        self.assertFalse(post_see_prunes(see_ge=False, depth=2,
            capture=True, discovered_attack_retains=True))
        self.assertTrue(post_see_prunes(see_ge=False, depth=2,
            capture=True, discovered_attack_retains=False))

    def test_depth_priority_over_discovered_attack(self):
        self.assertTrue(post_see_prunes(see_ge=False, depth=0,
            capture=True, discovered_attack_retains=True))

    def test_exhaustive_boolean_tally(self):
        r=finite_court()
        self.assertEqual(r['examined_boolean_combinations'], 32)
        self.assertEqual(r['see_ge_false_combinations'], 16)
        self.assertEqual(r['see_ge_false_but_not_pruned'] + r['see_ge_false_and_pruned'], 16)
        self.assertGreater(r['see_ge_false_but_not_pruned'], 0)


if __name__=='__main__':
    unittest.main()
