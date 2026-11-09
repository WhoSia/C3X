"""R19 synthetic court exercises strict source-root distinctness.

Not a native chess experiment; actual source selection is checked separately
by re-running unchanged R18 original Game14 native court before R19 admission.
"""
import unittest
from c3x_029_p42_r19_native_R18_root_depth_propagation import classify

def history():
    return [{"depth":i,"leader":1 if i<9 else 2,"score":-10-i,"average":-20-i}
            for i in range(1,13)]
def other(root):
    return [dict(x) for x in root]

class R19CausalDepth(unittest.TestCase):
    def test_changed_intermediate_leader_but_not_final(self):
        base=history()
        mod=other(base);mod[8]["leader"]=7
        out=classify(base,[mod,other(mod)])
        self.assertEqual(out["status"],"PASS_NATIVE_SOURCE_REVERSAL_CHANGED_INTERMEDIATE_ROOT_LEADER")
        self.assertEqual(out["changed_depths"],[9])
        self.assertEqual(out["leader_changed_depths"],[9])
        self.assertTrue(out["final_depth_summary_equals_original"])
        self.assertTrue(out["intermediate_choice_causal_sensitivity_certified"])
        self.assertFalse(out["natural_guard_cycle_mediation_certified"])
    def test_only_root_scores_different(self):
        base=history();mod=other(base);mod[8]["score"]+=4
        out=classify(base,[mod,other(mod)])
        self.assertEqual(out["status"],"PASS_NATIVE_SOURCE_REVERSAL_CHANGED_ROOT_SCORES_ONLY")
        self.assertFalse(out["intermediate_choice_causal_sensitivity_certified"])
        self.assertEqual(out["depth_delta_aggregates"][8]["score_delta"],4)
    def test_all_boundaries_equal(self):
        root=history();r=classify(root,[root,other(root)])
        self.assertEqual(r["status"],"PASS_NO_OBSERVED_INTERMEDIATE_ROOT_DEPTH_DIFFERENCE")
        self.assertIsNone(r["first_changed_depth"])
    def test_source_depth_cold_replay_drift_hold(self):
        a=history();b=other(a);b[8]["average"]+=1
        self.assertEqual(classify(a,[a,b])["status"],"HOLD_COUNTERFACTUAL_COLD_BOUNDARY_DRIFT")
    def test_missing_depth_hold(self):
        a=history()
        self.assertEqual(classify(a[:11],[a,a])["status"],"HOLD_ROOT_DEPTH_PROVENANCE")
    def test_missing_second_real_cold_hold(self):
        a=history()
        self.assertEqual(classify(a,[a])["status"],"HOLD_ROOT_DEPTH_PROVENANCE")
    def test_mismatched_depth_ids_hold(self):
        a=history();b=other(a);b[8]["depth"]=19
        self.assertEqual(classify(a,[b,other(b)])["status"],"HOLD_DEPTH_IDENTITY_DRIFT")
    def test_final_root_not_equal_is_reported_not_suppressed(self):
        a=history();b=other(a);b[-1]["leader"]+=1
        r=classify(a,[b,other(b)])
        self.assertFalse(r["final_depth_summary_equals_original"])
        self.assertEqual(r["last_changed_depth"],12)
    def test_no_private_source_ids_are_leaked(self):
        a=history();b=other(a);b[3]["average"]+=1
        r=classify(a,[b,other(b)])
        self.assertFalse(r["reveals_source_keys"])
        self.assertNotIn("position_key",repr(r))
        self.assertFalse(r["true_chess_strategic_meaning_certified"])

if __name__=="__main__":
    unittest.main()
