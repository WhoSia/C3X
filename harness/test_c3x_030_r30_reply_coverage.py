"""Tests that event coverage is not counted as an observed treatment effect."""
import tempfile
from pathlib import Path
import unittest

from c3x_030_r30_reply_coverage import nominate, parse_ply_one, coverage


def case():
    return {"id": "T-01", "stratum": "depth-reversal", "source_attempt": 8,
            "source": {"alternative": "a2a3"}, "arms": {}, "independent_reply": "b2b3"}


class R30CoverageTests(unittest.TestCase):
    def test_producer_read_beats_earlier(self):
        rows = parse_ply_one([
            "C3X_R29_PLY1 seq=12 attempt=4 root=a2a3 hit=1 hint=g7g6 excluded=0",
            "C3X_R29_PLY1 seq=22 attempt=8 root=a2a3 hit=1 hint=c7c6 excluded=0",
            "C3X_R29_PLY1 seq=23 attempt=8 root=a2a3 hit=1 hint=h7h6 excluded=0",
        ])
        self.assertEqual(nominate(case(), rows)["seq"], "22")
        self.assertEqual(nominate(case(), rows)["hint"], "c7c6")

    def test_ignore_null_and_unrelated_root(self):
        rows = parse_ply_one([
            "C3X_R29_PLY1 seq=12 attempt=4 root=a2a3 hit=1 hint=(none) excluded=0",
            "C3X_R29_PLY1 seq=13 attempt=5 root=e2e4 hit=1 hint=c7c6 excluded=0",
            "C3X_R29_PLY1 seq=14 attempt=9 root=a2a3 hit=1 hint=h7h6 excluded=0",
        ])
        self.assertIsNone(nominate(case(), rows))

    def test_duplicate_field_rejected(self):
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            parse_ply_one(["C3X_R29_PLY1 seq=1 seq=2 attempt=3 root=a2a3 hit=1 hint=g7g6 excluded=0"])

    def test_coverage_does_not_invent_effect(self):
        c = case()
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / "T-01" / "sham"
            folder.mkdir(parents=True)
            (folder / "stderr.txt").write_text(
                "C3X_R29_PLY1 seq=22 attempt=8 root=a2a3 hit=1 hint=c7c6 excluded=0\n")
            result = coverage({"positions": [c]}, [{"case": "T-01"}], Path(root))
            self.assertEqual(result["counts"]["depth_reversal_covered"], 1)
            self.assertIsNone(result["cases"][0]["effect_observed"])
            self.assertFalse(result["cases"][0]["intervention_executed"])


if __name__ == "__main__":
    unittest.main()
