"""P40/R2: original archived baseline audit (tests skip without authentic bytes)."""
import copy
import os
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from c3x_029_p40_r2_original_baseline_court import (
    read_original, compare_originals, certified_preference_from_search_bounds, W_SHA, REF_SHA
)


class HistoricalScoreAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        w = os.environ.get("C3X_P40_W")
        ref = os.environ.get("C3X_P40_REF")
        if not w or not ref:
            raise unittest.SkipTest("exact historical JSON member files required, no synthetic PASS")
        cls.w = read_original(Path(w),W_SHA)
        cls.ref = read_original(Path(ref),REF_SHA)

    def test_exact_original_counts_no_hindsight_selection(self):
        report = compare_originals(self.w,self.ref)
        self.assertEqual(report["original_games"],8)
        self.assertEqual(report["96k_bounds_identified_cases"],5)
        self.assertEqual(report["96k_bounds_censored_cases"],3)
        self.assertEqual(report["mobility_chose"],5)
        self.assertEqual(report["mobility_chose_with_identified_reference"],3)
        self.assertEqual(report["mobility_hits_when_chosen"],2)
        self.assertEqual(report["24k_first_root_hits_all"],5)
        self.assertEqual(report["24k_first_root_hits_on_mobility_decisions"],3)

    def test_score_bounds_do_not_become_artificial_point_values(self):
        upper = {"root_side_cp":53,"upperbound":True,"lowerbound":False,"root_side_mate":None}
        exact = {"root_side_cp":50,"upperbound":False,"lowerbound":False,"root_side_mate":None}
        winner, intervals = certified_preference_from_search_bounds(exact,upper)
        self.assertIsNone(winner)
        self.assertEqual(intervals,[(50,50),(None,53)])
        lower = {"root_side_cp":-18,"upperbound":False,"lowerbound":True,"root_side_mate":None}
        self.assertIsNone(certified_preference_from_search_bounds(
            {"root_side_cp":11,"upperbound":False,"lowerbound":False,"root_side_mate":None},
            lower)[0])
        upper_loser = {"root_side_cp":-54,"upperbound":True,"lowerbound":False,"root_side_mate":None}
        self.assertEqual(certified_preference_from_search_bounds(
            {"root_side_cp":0,"upperbound":False,"lowerbound":False,"root_side_mate":None},
            upper_loser)[0],0)

    def test_swapped_case_refuses_alignment(self):
        f=copy.deepcopy(self.ref)
        f["cases"][0],f["cases"][1]=f["cases"][1],f["cases"][0]
        with self.assertRaisesRegex(ValueError,"CASE_ALIGNMENT"):
            compare_originals(self.w,f)

    def test_modified_candidate_refuses(self):
        w=copy.deepcopy(self.w)
        w["cases"][0]["worlds"][0]["root_uci"]="a1a8"
        with self.assertRaisesRegex(ValueError,"MOVE_ALIGNMENT"):
            compare_originals(w,self.ref)

    def test_censored_mate_not_imputed_as_centipawn(self):
        f=copy.deepcopy(self.ref)
        f["cases"][0]["scored_candidate_predictions"][0]["reference_96k"]["reference"]["root_side_mate"]=1
        with self.assertRaisesRegex(ValueError,"MATE_SCORE"):
            compare_originals(self.w,f)


if __name__=="__main__":
    unittest.main()
