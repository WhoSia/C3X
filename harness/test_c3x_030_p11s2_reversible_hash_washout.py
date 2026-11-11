import unittest
from c3x_030_p11s2_reversible_hash_washout import phase_summary, PHASES, CLEAR_PHASES
class Washout(unittest.TestCase):
    def test_seven_phases_and_two_resets(self):
        self.assertEqual(len(PHASES),7)
        self.assertEqual(tuple(CLEAR_PHASES),("clear1","clear2"))
    def test_complete_restore_and_rebound(self):
        x={p:"e2e4" for p in PHASES}
        for p in ("warm1","warm2","postclear_warm1","postclear_warm2"):x[p]="d2d4"
        o=phase_summary(x)
        self.assertTrue(o["both_clear_phases_restore"])
        self.assertTrue(o["any_nonclear_warm_differs"])
        self.assertEqual(o["distinct_moves"],2)
    def test_absent_restore(self):
        x={p:"e2e4" for p in PHASES};x["clear2"]="d2d4"
        self.assertFalse(phase_summary(x)["both_clear_phases_restore"])
    def test_missing_phase_fail(self):
        with self.assertRaisesRegex(ValueError,"PHASE_SET"):
            phase_summary({"baseline":"e2e4"})
if __name__=="__main__":unittest.main()
