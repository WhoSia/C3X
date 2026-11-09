"""R15 prospective factorial interaction verdict contract (synthetic, NOT native)."""
import unittest
from c3x_029_p42_r15_original_guard_plus_event33_interaction_court import adjudicate,simple_support

def reference():
    return {"status":"PASS_ACTUAL_NATIVE_C_AND_B33_SOURCE_ROOT_COMPARISON_ONLY",
            "C_guard_exact_reenable_native_source_attempts":2,
            "C_and_B33_reproduce_b3a4":True,
            "depth9_source_boundary":{"C_capture_guard_bypass":
              {"depth":9,"leader":1112,"score":-89,"average":-79}}}
def baseline():
    return [dict(key=i,ply=2,depth=4,mod4=0,old_alpha=-9,beta=1,
                 root_move=123,candidate=-1,cutoff=0) for i in range(33)]
def probemoves(move="b3a4"):
    return [dict(move=move,root_boundaries=[{"depth":j} for j in range(1,13)])
            for _ in range(2)]
def cycles(original=True):
    out=[]
    for _ in range(2):
        e=[dict(x) for x in baseline()]
        if not original:e[0]["key"]=999
        e[32]["candidate"]=0
        out.append(e)
    return out

class R15DoubleSourceTests(unittest.TestCase):
    def test_both_contacted_same_source_prefix_pass_only_interaction(self):
        x=adjudicate(reference(),probemoves(),[2,2],cycles(),baseline(),[True,True])
        self.assertEqual(x["status"],"PASS_COMBINED_PHYSICAL_SOURCE_INTERVENTIONS_ONLY")
        self.assertTrue(x["cycle_event33_same_B_preintervention_source_identity"])
        self.assertFalse(x["natural_causal_mediation_certified"])
        self.assertFalse(x["independent_chess_future_certified"])
    def test_source_prefix_changed_does_not_invent_original_b33_identity(self):
        x=adjudicate(reference(),probemoves(),[2,2],cycles(False),baseline(),[True,True])
        self.assertEqual(x["status"],"PASS_COMBINED_PHYSICAL_SOURCE_INTERVENTIONS_ONLY")
        self.assertFalse(x["cycle_event33_same_B_preintervention_source_identity"])
        self.assertTrue(all(x.startswith("HOLD_PREINTERVENTION") for x in x["matched_prefix_courts"]))
    def test_nonrestoring_combination_reported_not_selected_away(self):
        x=adjudicate(reference(),probemoves("f3f4"),[2,2],cycles(),baseline(),[True,True])
        self.assertEqual(x["status"],"PASS_COMBINED_PHYSICAL_SOURCE_INTERVENTIONS_ONLY")
        self.assertEqual(x["combined_moves"],["f3f4","f3f4"])
    def test_third_move_supported_without_binary_conclusion(self):
        x=adjudicate(reference(),probemoves("a2a3"),[2,2],cycles(),baseline(),[True,True])
        self.assertEqual(x["combined_moves"],["a2a3","a2a3"])
        self.assertFalse(x["natural_causal_mediation_certified"])
    def test_stability_required(self):
        x=adjudicate(reference(),[dict(move="b3a4"),dict(move="f3f4")],
                     [2,2],cycles(),baseline(),[True,True])
        self.assertEqual(x["status"],"HOLD_COMBINED_COLD_ROOT_INSTABILITY")
    def test_guard_target_contact_per_play_required(self):
        x=adjudicate(reference(),probemoves(),[2,1],cycles(),baseline(),[True,True])
        self.assertEqual(x["status"],"HOLD_COMBINED_GUARD_NOT_PHYSICALLY_REENABLED")
    def test_event33_must_be_executed(self):
        e=cycles();e[0]=e[0][:32]
        x=adjudicate(reference(),probemoves(),[2,2],e,baseline(),[True,True])
        self.assertEqual(x["status"],"HOLD_COMBINED_CYCLE_ORDINAL_NOT_REACHED")
    def test_targeted_event33_must_be_neutralized(self):
        e=cycles();e[1][32]["candidate"]=-1
        x=adjudicate(reference(),probemoves(),[2,2],e,baseline(),[True,True])
        self.assertEqual(x["status"],"HOLD_COMBINED_CYCLE_ORDINAL_NOT_NEUTRALIZED")
    def test_source_tt_reader_provenance_required(self):
        x=adjudicate(reference(),probemoves(),[2,2],cycles(),baseline(),[True,False])
        self.assertEqual(x["status"],"HOLD_COLD_SOURCE_EVIDENCE_MISSING")
    def test_original_guard_control_must_be_physical(self):
        r=reference();r["C_guard_exact_reenable_native_source_attempts"]=0
        x=adjudicate(r,probemoves(),[2,2],cycles(),baseline(),[True,True])
        self.assertEqual(x["status"],"HOLD_HISTORICAL_ORIGINAL_GUARD_OR_B33")
    def test_original_r14_court_must_pass(self):
        r=reference();r["status"]="HOLD"
        x=adjudicate(r,probemoves(),[2,2],cycles(),baseline(),[True,True])
        self.assertEqual(x["status"],"HOLD_ORIGINAL_R14_CONTROL_NOT_ADMITTED")
    def test_source_support_conjunction(self):
        self.assertTrue(simple_support(["PASS_ACTUAL_ONE_SOURCE_EVENT_WITH_MATCHED_PREFIX"]*2))
        self.assertFalse(simple_support(["PASS_ACTUAL_ONE_SOURCE_EVENT_WITH_MATCHED_PREFIX","HOLD_DRIFT"]))
if __name__=="__main__":
    unittest.main()
