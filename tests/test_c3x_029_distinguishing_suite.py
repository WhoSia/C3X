"""Finite explanation identification court tests; no engine."""
import unittest, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from c3x_029_distinguishing_suite import court, predicates, partition, minimum_suite

class ExplanationIdentification(unittest.TestCase):
    def test_original_indistinguishable(self):
        self.assertIn(("not_g8","rank_7","rank_below_8"),
                      partition(("g7","h7","g8"),predicates()))
    def test_exact_minimality(self):
        r=court()
        self.assertEqual(r["minimum_suite_size"],2)
        self.assertEqual(len(r["minimum_suites"]),3)
        self.assertEqual(r["independently_checked_subsets"],128)
    def test_no_single_context_suffices(self):
        h=predicates()
        all_pairs=minimum_suite(("a8","g8","g7","h7","f8","a7","b8"),h)[1]
        for x in ("a8","g8","g7","h7","f8","a7","b8"):
            self.assertNotEqual(minimum_suite((x,),h)[1],all_pairs)
    def test_scope_not_native(self):
        r=court()
        self.assertFalse(r["chess_legality_verified"])
        self.assertEqual(r["native_engine_calls"],0)
if __name__=="__main__": unittest.main()
