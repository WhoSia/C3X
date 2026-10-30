"""Finite first-divergence negative-control court: no live engine inputs."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from c3x_028_no_contact_parity_court import run, court


class FirstDivergenceCourt(unittest.TestCase):
    def test_no_contact_prevents_difference(self):
        b, events = run((1,1,2), 0, {2})
        c, _ = run((1,1,2), 0, {2}, (2,2,0))
        self.assertFalse(events)
        self.assertEqual(b, c)

    def test_guard_contact_can_cause_difference(self):
        b, events = run((1,1,2), 0, {1})
        c, _ = run((1,1,2), 0, {1}, (1,2,2))
        self.assertTrue(events)
        self.assertNotEqual(b,c)

    def test_pre_guard_side_effect_breaks_assumptions(self):
        b, contacts = run((1,1,2), 0, {2})
        other, _ = run((2,1,2), 0, {2})
        self.assertFalse(contacts)
        self.assertNotEqual(b,other)

    def test_exhaustive_court(self):
        r=court()
        self.assertEqual(r['exhaustively_compared'], 3**3 * 3**3 * 8 * 3)
        self.assertEqual(r['no_contact_parity_failures'], 0)


if __name__ == '__main__':
    unittest.main()
