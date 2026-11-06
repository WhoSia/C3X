"""R8 native-court decision logic tests, purely synthetic.

No synthetic PASS can be promoted to engine causal effect.
"""
import unittest
from c3x_029_p42_r8_same_engine_tt_save_causal_court import judge

def report(best="b3a4",a="b3a4",b="f3f4",contacts=2):
    return {
      "baseline_bestmove":a, "TT_FIRST_bestmove":b,
      "counterfactual_bestmove":best,
      "one_event_reenable_status": "ORIGINAL_ROOT_RESTORED" if best=="b3a4" else "TREATED_ROOT_UNCHANGED",
      "counterfactual_branch_action_counts":{"EXACT_ONE_EVENT_REENABLED":contacts},
      "actual_branch_proof":True,"native_guard_one_event_contact":True
    }
def c(n, suppressed=0):
    return [{"attempts":n,"suppressed":suppressed}]*2

class R8CounterfactualTests(unittest.TestCase):
    def test_neutralization_preserves_root(self):
        a=judge(report(),report("b3a4"),c(4),c(4,4))
        self.assertIn("NOT_NECESSARY",a["status"])
        self.assertFalse(a["natural_mediation_certified"])
        self.assertFalse(a["chess_strategy_meaning_certified"])
    def test_neutralization_removes_root_restoration(self):
        a=judge(report(),report("f3f4"),c(3),c(3,3))
        self.assertIn("FUNCTIONALLY_NECESSARY",a["status"])
        self.assertFalse(a["natural_mediation_certified"])
    def test_neutralization_produces_third_move(self):
        a=judge(report(),report("c2c4"),c(3),c(3,3))
        self.assertIn("THIRD_CANDIDATE",a["status"])
    def test_no_writes_makes_experiment_uninformative(self):
        self.assertEqual(judge(report(),report(),c(0),c(0))["status"],
                         "HOLD_TARGET_TT_WRITES_NOT_PHYSICALLY_SUPPRESSED")
    def test_missing_second_cold_replay_holds(self):
        self.assertEqual(judge(report(),report(),c(5)[:1],c(5,5))["status"],
                         "HOLD_SOURCE_ATTEMPT_COUNT_INVALID")
    def test_root_control_changes_holds(self):
        self.assertEqual(judge(report(),report(a="h2h4"),c(5),c(5,5))["status"],
                         "HOLD_ROOT_CONTROL_DRIFT")
    def test_no_real_guard_contact_holds(self):
        self.assertEqual(judge(report(),report(contacts=0),c(5),c(5,5))["status"],
                         "HOLD_COUNTERFACTUAL_GUARD_CONTACT_DRIFT")
    def test_incomplete_tt_suppression_holds(self):
        self.assertEqual(judge(report(),report(),c(5),c(5,4))["status"],
                         "HOLD_TARGET_TT_WRITES_NOT_PHYSICALLY_SUPPRESSED")
    def test_original_root_not_restored_holds(self):
        self.assertEqual(judge(report("f3f4"),report(),c(5),c(5,5))["status"],
                         "HOLD_NORMAL_GUARD_RESTORATION_FAILED")

if __name__=="__main__":unittest.main()
