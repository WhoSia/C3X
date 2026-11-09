"""R18 source-value reversal verdict tests; native claim never synthetic."""
import unittest
from c3x_029_p42_r18_source_identity_reverse_B33_in_C_court import summarize

def root():
    return [dict(depth=d,leader=1112,score=-89,average=-79)
            for d in range(1,13)]
def verdict(moves=["b3a4","b3a4"],contacts=[2,2],cutoffs=[False,False],
            readers=[True,True],depths=None,reverse=None):
    return summarize(moves,contacts,cutoffs,readers,depths or root(),
                     reverse or [root(),root()])

class R18ReverseIdentityVerdicts(unittest.TestCase):
    def test_actual_reversion_to_original_B_is_a_bounded_success(self):
        d=verdict(["f3f4"]*2)
        self.assertEqual(d["status"],"PASS_ACTUAL_ONE_REVERSED_DRAW_EVENT_REVERTS_C_ROOT_TO_B")
        self.assertFalse(d["natural_guard_cycle_mediation_certified"])
        self.assertFalse(d["independent_chess_strategy_certified"])
    def test_root_remains_C_is_valid_negative_result(self):
        d=verdict()
        self.assertEqual(d["status"],"PASS_ACTUAL_ONE_REVERSED_DRAW_EVENT_DOES_NOT_REVERT_C_ROOT")
        self.assertFalse(d["shared_crossworld_event_causation_certified"])
    def test_third_candidate_emergence_not_suppressed(self):
        d=verdict(["a2a3"]*2)
        self.assertEqual(d["status"],"PASS_ACTUAL_ONE_REVERSED_DRAW_EVENT_CREATES_THIRD_ROOT")
    def test_physical_source_contact_both_processes_required(self):
        d=verdict(contacts=[2,1])
        self.assertEqual(d["status"],"HOLD_TARGET_EXACT_SOURCE_CONTACT_PER_PROCESS")
    def test_cold_root_move_instability_holds(self):
        d=verdict(moves=["b3a4","f3f4"])
        self.assertEqual(d["status"],"HOLD_NATIVE_COLD_OUTCOME_DRIFT")
    def test_cold_cutoff_status_instability_holds(self):
        d=verdict(cutoffs=[False,True])
        self.assertEqual(d["status"],"HOLD_NATIVE_COLD_OUTCOME_DRIFT")
    def test_native_tt_reader_missing_holds(self):
        d=verdict(readers=[False,True])
        self.assertEqual(d["status"],"HOLD_NATIVE_REPLAY_OR_TT_READER")
    def test_missing_nine_to_twelve_root_support_holds(self):
        d=verdict(depths=root()[:-1])
        self.assertEqual(d["status"],"HOLD_SOURCE_ROOT_BOUNDARY_MISSING")
    def test_root_boundary_cold_state_drift_holds(self):
        r1=root();r2=root();r2[8]["score"]=-88
        d=verdict(reverse=[r1,r2])
        self.assertEqual(d["status"],"HOLD_SOURCE_ROOT_BOUNDARY_COLD_DRIFT")
    def test_first_changed_root_depth_is_reported(self):
        c=root();t=root();t[8]["leader"]=1373
        d=verdict(reverse=[t,[dict(x) for x in t]])
        self.assertEqual(d["first_C_vs_C_reverse_changed_root_depth"],9)
    def test_full_root_summary_equality_does_not_certify_mediation(self):
        d=verdict()
        self.assertIsNone(d["first_C_vs_C_reverse_changed_root_depth"])
        self.assertFalse(d["natural_guard_cycle_mediation_certified"])
    def test_score_reversal_and_cutoff_are_not_confused(self):
        d=verdict(cutoffs=[True,True])
        self.assertEqual(d["reverse_C_beta_cutoff"],[True,True])
        self.assertFalse(d["natural_guard_cycle_mediation_certified"])
if __name__=="__main__":
    unittest.main()
