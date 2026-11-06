"""P42/R9 causal verdict tests: count actual source calls, not invented parity."""
import unittest
from c3x_029_p42_r9_native_value_draw_court import inspect,decide

ABC={"A":"b3a4","B":"f3f4","C":"b3a4"}
def court(d="b3a4"):
    return {"status":"PASS_SOURCE_EXACT_TARGET_TT_SAVE_INTERVENTION_TT_WRITES_NOT_NECESSARY_FOR_THIS_RESTORATION_UNDER_TESTED_INTERVENTION",
            "control_three_arm_choices":dict(ABC),"intervention_D_choice":d}
def rows(n=0):
    return {"actual_value_draw_calls":n,"node_mod4_histogram":{"0":n,"1":0,"2":0,"3":0}}

class R9DrawCausalCourt(unittest.TestCase):
    def test_no_source_call_rejects_node_draw_mediation(self):
        r=decide(rows(),rows(),court(),court(),0,0)
        self.assertEqual(r["status"],"PASS_ACTUAL_NO_VALUE_DRAW_CONTACT_IN_TESTED_SOURCE_EXECUTIONS")
        self.assertFalse(r["natural_TT_mediation_certified"])
    def test_neutralized_contact_but_same_root(self):
        r=decide(rows(4),rows(4),court(),court(),0,0)
        self.assertEqual(r["status"],"PASS_GLOBAL_DRAW_PARITY_NEUTRALIZATION_ROOT_UNCHANGED")
        self.assertFalse(r["prospective_heldout_chess_certified"])
    def test_neutralized_contact_changes_root(self):
        r=decide(rows(1),rows(1),court(),court("f3f4"),0,0)
        self.assertEqual(r["status"],"PASS_GLOBAL_DRAW_PARITY_NEUTRALIZATION_ROOT_CHANGED")
        self.assertFalse(r["independent_chess_strategic_meaning_certified"])
    def test_asymmetric_real_calls_hold(self):
        self.assertEqual(decide(rows(0),rows(2),court(),court(),0,0)["status"],
                         "HOLD_ASYMMETRIC_DRAW_CONTACT")
    def test_earlier_native_failure_holds(self):
        self.assertEqual(decide(rows(),rows(),court(),court(),2,0)["status"],
                         "HOLD_NATIVE_FOUR_ARM_REPLAY_OR_CONTROL_DRIFT")
    def test_original_threearm_drift_holds(self):
        other=court();other["control_three_arm_choices"]["B"]="b3a4"
        self.assertEqual(decide(rows(),rows(),court(),other,0,0)["status"],
                         "HOLD_ORIGINAL_THREE_ARM_CHOICES_DRIFT")
    def test_zero_calls_expected_when_empty_log(self):
        self.assertEqual(inspect("",False)["actual_value_draw_calls"],0)
    def test_actual_draw_parity_math_uses_source_return(self):
        raw=("c3x042_r9_draw call=1 node_mod4=0 original=-1 neutral=0 return=-1\n"
             "c3x042_r9_draw call=1 node_mod4=2 original=1 neutral=0 return=1\n")
        v=inspect(raw,False)
        self.assertEqual(v["actual_value_draw_calls"],2)
        self.assertEqual(v["node_mod4_histogram"]["2"],1)
    def test_true_neutral_changes_parity_return(self):
        raw="c3x042_r9_draw call=1 node_mod4=2 original=1 neutral=1 return=0\n"
        self.assertEqual(inspect(raw,True)["actual_value_draw_calls"],1)
    def test_wrong_mode_holds(self):
        with self.assertRaisesRegex(ValueError,"MODE_MISMATCH"):
            inspect("c3x042_r9_draw call=1 node_mod4=2 original=1 neutral=0 return=1",True)
    def test_invalid_original_value_holds(self):
        with self.assertRaisesRegex(ValueError,"RETURN_MISMATCH"):
            inspect("c3x042_r9_draw call=1 node_mod4=2 original=-1 neutral=0 return=-1",False)
    def test_malformed_native_source_event_holds(self):
        with self.assertRaisesRegex(ValueError,"MALFORMED"):
            inspect("c3x042_r9_draw not_an_actual_event",False)

if __name__=="__main__":
    unittest.main()
