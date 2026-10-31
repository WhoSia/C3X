#!/usr/bin/env python3
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p9_r15_root_bound_comparison import compare

def row(cp,kind,**kw):
    return {"cp":cp,"kind":kind,"process_id":"cold-01","root_call":3,
            "iteration_depth":12,"aspiration_attempt":2,"score_pov":"side_to_move",**kw}

class RootIntervalContract(unittest.TestCase):
    def test_nonoverlapping_bound_proves_a_greater(self):
        self.assertEqual(compare(row(18,"lower"),row(11,"upper"))["status"],"CERTIFIED_STRICT_A_GREATER_B")
    def test_nonoverlapping_bound_proves_b_greater(self):
        self.assertEqual(compare(row(4,"upper"),row(9,"lower"))["status"],"CERTIFIED_STRICT_B_GREATER_A")
    def test_overlap_abstains(self):
        self.assertEqual(compare(row(7,"lower"),row(8,"upper"))["status"],"ABSTAIN_OVERLAPPING_OR_ONE_SIDED_BOUNDS")
    def test_only_two_lowers_cannot_rank(self):
        self.assertEqual(compare(row(200,"lower"),row(-20,"lower"))["status"],"ABSTAIN_OVERLAPPING_OR_ONE_SIDED_BOUNDS")
    def test_exact_equal(self):
        self.assertEqual(compare(row(7,"exact"),row(7,"exact"))["status"],"CERTIFIED_EQUAL_EXACT")
    def test_cross_process_cannot_join(self):
        b=row(0,"exact");b["process_id"]="cold-02"
        self.assertEqual(compare(row(10,"exact"),b)["status"],"ABSTAIN_INCOMPARABLE_SOURCE_COORDINATES")
    def test_cross_aspiration_cannot_join(self):
        b=row(0,"exact");b["aspiration_attempt"]=3
        self.assertEqual(compare(row(10,"exact"),b)["status"],"ABSTAIN_INCOMPARABLE_SOURCE_COORDINATES")
    def test_untyped_score_rejected(self):
        with self.assertRaises(ValueError):compare(row(10.5,"exact"),row(0,"exact"))
if __name__=="__main__":unittest.main()
