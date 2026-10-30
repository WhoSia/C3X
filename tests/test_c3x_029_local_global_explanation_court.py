"""0.29 exact local/global explanation nonidentifiability test."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from c3x_029_local_global_explanation_court import court

class LocalGlobalCourt(unittest.TestCase):
    def test_true_on_support_not_global_unique(self):
        result=court()
        self.assertEqual(result["permitted_predicate_assignments_on_support"],[("g7","h7")])
        self.assertEqual(result["number_of_global_boolean_extensions"],2**61)
        self.assertTrue(result["pair_equivalent_on_reachable_support"])
        self.assertTrue(result["pair_distinct_outside_reachable_support"])
        self.assertEqual(result["illustrative_disagreement_square"], "a8")
        self.assertFalse(result["new_native_engine_data"])

if __name__=="__main__":
    unittest.main()
