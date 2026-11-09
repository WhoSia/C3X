"""R17 source semantics counterexamples: dynamic C event != original B event."""
import unittest
from c3x_029_p42_r17_actual_C_event33_local_window_effect import test_dynamic_effect

def source_events(candidate=-1,beta=0):
    out=[dict(key=i,ply=2,depth=4,mod4=0,old_alpha=-3,beta=5,
              root_move=1112,candidate=-1,cutoff=0) for i in range(50)]
    out[32].update(candidate=candidate,beta=beta,
                  cutoff=int(candidate>=beta),mod4=0 if candidate==-1 else 2)
    return out

def matched_pair(candidate=-1,beta=0):
    original=source_events(candidate,beta)
    changed=[dict(x) for x in original]
    changed[32]["candidate"]=0
    changed[32]["cutoff"]=int(0>=beta)
    return original,changed

class ActualCWindowTests(unittest.TestCase):
    def test_value_changes_without_immediate_cutoff_change(self):
        a,b=matched_pair(-1,2)
        z=test_dynamic_effect(a,b)
        self.assertEqual(z["status"],"PASS_ONE_ACTUAL_C_EVENT_VALUE_CHANGE_WITH_PRESERVED_SOURCE_CONTEXT")
        self.assertFalse(z["immediate_cutoff_changed"])
        self.assertEqual(z["actual_return_delta"],1)
        self.assertFalse(z["natural_B33_source_mediation_identified"])
    def test_value_change_with_immediate_cutoff_change(self):
        a,b=matched_pair(-1,0)
        z=test_dynamic_effect(a,b)
        self.assertTrue(z["immediate_cutoff_changed"])
        self.assertFalse(z["unmeasured_search_state_equality_certified"])
    def test_positive_native_draw_return_downward_modification(self):
        a,b=matched_pair(1,2)
        z=test_dynamic_effect(a,b)
        self.assertEqual(z["actual_return_delta"],-1)
    def test_missing_event33_holds(self):
        a,b=matched_pair()
        self.assertEqual(test_dynamic_effect(a[:32],b)["status"],
                         "HOLD_EVENT33_NOT_IN_BOTH_NATIVE_EXECUTIONS")
    def test_dynamic_event_count_shift_holds(self):
        a,b=matched_pair();b.append(dict(b[-1]))
        self.assertEqual(test_dynamic_effect(a,b)["status"],
                         "HOLD_NATIVE_EVENT_SUPPORT_LENGTH_CHANGED")
    def test_native_board_context_drift_holds(self):
        a,b=matched_pair();b[32]["key"]=12345
        self.assertEqual(test_dynamic_effect(a,b)["status"],
                         "HOLD_PRE_SCORE_NATIVE_SOURCE_CONTEXT_DRIFT")
    def test_beta_window_drift_holds(self):
        a,b=matched_pair();b[32]["beta"]=42
        self.assertEqual(test_dynamic_effect(a,b)["status"],
                         "HOLD_PRE_SCORE_NATIVE_SOURCE_CONTEXT_DRIFT")
    def test_mod4_drift_holds(self):
        a,b=matched_pair();b[32]["mod4"]=3
        self.assertEqual(test_dynamic_effect(a,b)["status"],
                         "HOLD_PRE_SCORE_NATIVE_SOURCE_CONTEXT_DRIFT")
    def test_unexpected_second_actual_score_change_holds(self):
        a,b=matched_pair();b[40]["candidate"]=0
        self.assertEqual(test_dynamic_effect(a,b)["status"],
                         "HOLD_UNEXPECTED_NUMBER_OR_LOCATION_OF_DRAW_VALUE_CHANGES")
    def test_no_actual_intervention_holds(self):
        a,b=matched_pair();b[32]["candidate"]=a[32]["candidate"];b[32]["cutoff"]=a[32]["cutoff"]
        self.assertEqual(test_dynamic_effect(a,b)["status"],
                         "HOLD_UNEXPECTED_NUMBER_OR_LOCATION_OF_DRAW_VALUE_CHANGES")
    def test_original_unphysical_score_holds(self):
        a,b=matched_pair();a[32]["candidate"]=20
        self.assertEqual(test_dynamic_effect(a,b)["status"],
                         "HOLD_ORIGINAL_OR_NEUTRALIZED_DRAW_VALUE_UNEXPECTED")
    def test_actual_cutoff_inconsistent_holds(self):
        a,b=matched_pair(-1,0);a[32]["cutoff"]=1
        self.assertEqual(test_dynamic_effect(a,b)["status"],
                         "HOLD_NATIVE_IMMEDIATE_CUTOFF_INCONSISTENT")

if __name__=="__main__":
    unittest.main()
