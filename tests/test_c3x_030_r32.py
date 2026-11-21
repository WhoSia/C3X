"""Protect the exact Bc6 join and the common-alpha root contrast."""
from io import StringIO
import json
import unittest

from c3x_030_r32_bc6 import focal, same_alpha_changes


class R32Tests(unittest.TestCase):
    def setUp(self):
        self.trace = [
            "C3X_R32_WATCH key=42",
            "C3X_R32_ENTER mode=s index=1 key=42 depth=9 alpha=1950 beta=1951",
            "C3X_R32_EXIT mode=s index=1 value=1894",
            "C3X_R32_ENTER mode=p index=1 key=42 depth=11 alpha=1706 beta=1951",
            "C3X_R32_READ mode=p ply=2 pv=1 excluded=0 key=42 parent=b5c6 depth=11 alpha=-1951 beta=-1706",
            "C3X_R32_RETURN mode=p ply=1 key=42 move=b5c6 stage=pv value=1952",
            "C3X_R32_EXIT mode=p index=1 value=1952",
        ]

    def test_exact_pv_join_excludes_scout_or_other_internal_calls(self):
        self.assertEqual(focal(self.trace)["bc6_pv_return"]["value"], "1952")
        self.trace[4] = self.trace[4].replace("excluded=0", "excluded=66")
        with self.assertRaises(ValueError):
            focal(self.trace)

    def test_window_and_value_mismatches_raise(self):
        trace = [line.replace("alpha=-1951", "alpha=-1950") for line in self.trace]
        with self.assertRaisesRegex(ValueError, "first Bc6 PV move"):
            focal(trace)
        self.trace[-1] = self.trace[-1].replace("1952", "1953")
        with self.assertRaisesRegex(ValueError, "Return does not join"):
            focal(self.trace)

    def test_comparison_requires_common_alpha_and_roundtrips_json(self):
        def root(move, alpha, value, update):
            return dict(move=move, alpha=alpha, value=value, update=update)

        control = [root("f6g7", -1951, -1952, "0"), root("f6e5", -1951, -1928, "1"),
                   root("b1b2", -1928, -1880, "1")]
        treatment = [root("f6g7", -1951, -1952, "0"), root("f6e5", -1951, -1951, "0"),
                     root("b1b2", -1951, -1951, "0")]
        delta = same_alpha_changes(control, treatment)
        self.assertEqual(delta["first_update"], [control[1], treatment[1]])
        self.assertEqual(delta, json.load(StringIO(json.dumps(delta))))
        self.assertIsNone(same_alpha_changes(control[2:], treatment[2:])["first_value"])


if __name__ == "__main__":
    unittest.main()
