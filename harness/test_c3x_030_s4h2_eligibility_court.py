import unittest
from c3x_030_s4h2_eligibility_court import choose

class EligibilitySourceOnlyTests(unittest.TestCase):
    def test_first_physical_hit_key_frozen(self):
        rows=["C3X_S4H2_ELIGIBLE ordinal=0 key=123 ply=1 hit_before=1",
              "C3X_S4H2_ELIGIBLE ordinal=1 key=456 ply=1 hit_before=1"]
        x=choose(rows)
        self.assertEqual(x["frozen_key"],"123")
        self.assertEqual(x["source_hit_events_logged"],2)
    def test_no_hit_is_preserved_as_ineligible(self):
        self.assertEqual(choose([])["eligible"],False)
        self.assertIsNone(choose([])["frozen_key"])
    def test_malformed_source_rejected(self):
        with self.assertRaisesRegex(ValueError,"MALFORMED"):
            choose(["C3X_S4H2_ELIGIBLE ordinal=0 key=123 ply=1 hit_before=0"])
    def test_source_event_gap_rejected(self):
        with self.assertRaisesRegex(ValueError,"GAP"):
            choose(["C3X_S4H2_ELIGIBLE ordinal=1 key=123 ply=1 hit_before=1"])
    def test_duplicate_ordinal_rejected(self):
        with self.assertRaisesRegex(ValueError,"GAP"):
            choose(["C3X_S4H2_ELIGIBLE ordinal=0 key=123 ply=1 hit_before=1",
                    "C3X_S4H2_ELIGIBLE ordinal=0 key=123 ply=1 hit_before=1"])
    def test_out_of_range_key_rejected(self):
        with self.assertRaisesRegex(ValueError,"BAD_ORDINAL_OR_KEY"):
            choose(["C3X_S4H2_ELIGIBLE ordinal=0 key=18446744073709551616 ply=1 hit_before=1"])
    def test_outcome_lines_not_accepted_as_source(self):
        with self.assertRaisesRegex(ValueError,"MALFORMED"):
            choose(["C3X_S4H2_ELIGIBLE score=4 bestmove=e2e4"])
if __name__=="__main__":unittest.main()
