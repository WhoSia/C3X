import unittest
from c3x_030_s4i_tt_early_cutoff_court import cutoffs

class Tests(unittest.TestCase):
    def test_true_early_return(self):
        e=cutoffs(["C3X_S4I_TT_CUTOFF ordinal=0 id=5 parent=2 key=123 ply=1 return_value=-55"],"123")
        self.assertEqual(e["observed_cutoffs"],1)
        self.assertEqual(e["source_return_events"][0]["returned_value"],-55)
    def test_no_event_is_not_proven_absent(self):
        self.assertEqual(cutoffs([],"123")["observed_cutoffs"],0)
    def test_wrong_source_key_fails(self):
        with self.assertRaisesRegex(ValueError,"WRONG_SOURCE"):
            cutoffs(["C3X_S4I_TT_CUTOFF ordinal=0 id=5 parent=2 key=999 ply=1 return_value=-55"],"123")
    def test_false_hit_or_malformed_fail(self):
        with self.assertRaisesRegex(ValueError,"MALFORMED"):
            cutoffs(["C3X_S4I_TT_CUTOFF ordinal=0 id=5 parent=2 key=123 ply=1 value=-55"],"123")
    def test_missing_ordinal_fail(self):
        with self.assertRaisesRegex(ValueError,"WRONG_SOURCE"):
            cutoffs(["C3X_S4I_TT_CUTOFF ordinal=1 id=5 parent=2 key=123 ply=1 return_value=-55"],"123")
if __name__=="__main__":unittest.main()
