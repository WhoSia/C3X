import unittest
from c3x_030_p11s4b_exact_key_mask_court import first_hit_ply1,evaluate,SHAM_KEY
class Test(unittest.TestCase):
    def test_first_valid_hit_rule_prevents_postselection(self):
        e=[{"kind":"probe","ply":0,"key":"99","raw":"hit=1 "},
           {"kind":"probe","ply":1,"key":"11","raw":"hit=0 "},
           {"kind":"probe","ply":1,"key":"22","raw":"x hit=1 y"},
           {"kind":"probe","ply":1,"key":"33","raw":"x hit=1 y"}]
        self.assertEqual(first_hit_ply1(e),"22")
    def test_no_source_hit_holds(self):
        with self.assertRaisesRegex(ValueError,"NO_SOURCE_PLY1_HIT"):first_hit_ply1([])
    def test_sham_key_collision_holds(self):
        with self.assertRaisesRegex(ValueError,"SHAM_COLLISION"):
            first_hit_ply1([{"kind":"probe","ply":1,"key":SHAM_KEY,"raw":"x hit=1 y"}])
    def test_native_sham_and_target_results_independent(self):
        r=lambda m:{"trials":[{"bestmove":m,"depth":9,"nodes":12000,"score":("cp",12),"pv":[m]}]}
        x=evaluate(r("e2e4"),r("e2e4"),r("d2d4"))
        self.assertTrue(x["baseline_matches_sham"])
        self.assertEqual(x["target_changed_bestmove_trials"],1)
    def test_original_drift_detected(self):
        r=lambda m:{"trials":[{"bestmove":m,"depth":9,"nodes":12000,"score":("cp",12),"pv":[m]}]}
        self.assertFalse(evaluate(r("e2e4"),r("d2d4"),r("d2d4"))["baseline_matches_sham"])
if __name__=="__main__":unittest.main()
