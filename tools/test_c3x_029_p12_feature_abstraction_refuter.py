import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p12_feature_abstraction_refuter import audit_feature_sufficiency as audit
class FeatureRefuter(unittest.TestCase):
    def test_disjoint_pair(self):
        a=audit({"check":["a"],"capture":["b"]},{"check":"forcing","capture":"forcing"})
        self.assertEqual(a["status"],"REFUTED_FEATURE_SUFFICIENCY")
        self.assertEqual(a["collision_pair"],["check","capture"])
    def test_common_label(self):
        a=audit({"check":["a","b"],"capture":["b"]},{"check":"forcing","capture":"forcing"})
        self.assertEqual(a["status"],"CERTIFIED_FINITE_ACTION_SCHEMA_ONLY")
        self.assertEqual(a["policy"]["forcing"],"b")
    def test_pairwise_overlap_but_triple_empty(self):
        a=audit({"r1":["a","b"],"r2":["b","c"],"r3":["a","c"]},
            {"r1":"same","r2":"same","r3":"same"})
        self.assertEqual(a["status"],"REFUTED_FEATURE_SUFFICIENCY")
        self.assertIsNone(a["collision_pair"])
        self.assertEqual(a["cell_reply_count"],3)
    def test_empty_domain(self):
        self.assertEqual(audit({}, {})["status"],"ABSTAIN_EMPTY_REPLY_DOMAIN")
    def test_incomplete_feature(self):
        self.assertEqual(audit({"r":["a"]}, {})["status"],"HOLD_FEATURE_DOMAIN_MISMATCH")
if __name__=="__main__":unittest.main()
