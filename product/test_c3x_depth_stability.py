"""T04-d pure finite-depth evidence tests, no engine required."""
import unittest
from c3x_depth_stability import assess,depth_profile

def rows(gaps,profile="audit",*,bound=None,missing=None):
    out=[{"forced_root_evaluations":{}},{"forced_root_evaluations":{}}]
    for d,g in zip(depth_profile(profile),gaps):
        if d==missing:continue
        for i,v in enumerate((g,0)):
            out[i]["forced_root_evaluations"][str(d)]={"depth":d,"mover_cp_or_null_if_mate":v,
                "bound":(bound or "none") if i==0 and d==14 else "none"}
    return out
class Stability(unittest.TestCase):
    def test_shallow_large_gap_still_unresolved(self):
        p=assess(rows([-25,-43],"quick"),"quick")
        self.assertEqual(p["status"],"UNRESOLVED")
        self.assertIn("SHALLOW_ONLY",p["reasons"])
        self.assertFalse(p["draw_proven"])
    def test_deep_reversal(self):
        p=assess(rows([-25,-43,-8,4,15]),"audit")
        self.assertIn("DEPTH_SIGN_REVERSAL",p["reasons"])
        self.assertIn("SMALL_GAP",p["reasons"])
        self.assertEqual(p["finite_observed_range_cp"],[-43,15])
        self.assertEqual(p["status"],"UNRESOLVED")
    def test_consistent(self):
        for g,expected in ((21,"SAMPLED_A_PREFERENCE"),(-21,"SAMPLED_B_PREFERENCE")):
            p=assess(rows([g]*5),"audit")
            self.assertEqual(p["status"],expected)
            self.assertFalse(p["global_best_proven"])
            self.assertFalse(p["confidence_interval"])
    def test_threshold_boundary(self):
        p=assess(rows([21,30,20,50,60]),"audit")
        self.assertEqual(p["status"],"UNRESOLVED")
        self.assertIn("SMALL_GAP",p["reasons"])
    def test_bound_and_mate_and_missing(self):
        for kw,gaps,reason in (({"bound":"lower"},[40]*5,"BOUND_ONLY"),
                               ({},[40,40,None,40,40],"MATE_OR_NONFINITE"),
                               ({"missing":14},[40]*5,"INCOMPLETE")):
            p=assess(rows(gaps,**kw),"audit")
            self.assertEqual(p["status"],"UNRESOLVED")
            self.assertIn(reason,p["reasons"])
            self.assertIsNone(p["gaps_cp"]["14"])
    def test_order_reversal(self):
        r=rows([30,40,35,29,23]);a=assess(r,"audit");b=assess(r[::-1],"audit")
        self.assertEqual(a["status"],"SAMPLED_A_PREFERENCE")
        self.assertEqual(b["status"],"SAMPLED_B_PREFERENCE")
        self.assertEqual(b["finite_observed_range_cp"],[-40,-23])
if __name__=="__main__":unittest.main()
