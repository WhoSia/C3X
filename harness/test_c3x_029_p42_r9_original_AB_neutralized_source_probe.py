"""R9 original Game14 A/B native neutral-control outcome tests (synthetic only)."""
import unittest
from c3x_029_p42_r9_original_AB_neutralized_source_probe import verify_native_arm

class R9OriginalNeutralizedABTests(unittest.TestCase):
    def test_changed_A_with_source_draw_contact_is_registered(self):
        self.assertEqual(verify_native_arm(["f3f4"]*2,["f3f4"]*2,
             {"A":[2,1],"B":[2,2]},[True,True]),
             "PASS_BROAD_VALUE_DRAW_NEUTRALIZATION_CHANGED_ACTUAL_AB_ROOT_CHOICE")
    def test_changed_B_with_source_contact_is_registered(self):
        self.assertEqual(verify_native_arm(["b3a4"]*2,["b3a4"]*2,
             {"A":[0,0],"B":[1,3]},[True,True]),
             "PASS_BROAD_VALUE_DRAW_NEUTRALIZATION_CHANGED_ACTUAL_AB_ROOT_CHOICE")
    def test_unchanged_A_B_does_not_invent_a_perturbation(self):
        self.assertEqual(verify_native_arm(["b3a4"]*2,["f3f4"]*2,
             {"A":[1,1],"B":[1,1]},[True,True]),
             "PASS_BROAD_VALUE_DRAW_NEUTRALIZATION_PRESERVED_ACTUAL_AB_ROOT_CHOICE")
    def test_zero_draw_contact_and_changed_A_is_hold(self):
        self.assertEqual(verify_native_arm(["f3f4"]*2,["f3f4"]*2,
             {"A":[0,0],"B":[2,2]},[True,True]),
             "HOLD_ROOT_CHANGE_WITHOUT_ACTUAL_VALUE_DRAW_SOURCE_CONTACT")
    def test_partial_draw_contact_and_changed_B_is_hold(self):
        self.assertEqual(verify_native_arm(["b3a4"]*2,["b3a4"]*2,
             {"A":[0,0],"B":[2,0]},[True,True]),
             "HOLD_ROOT_CHANGE_WITHOUT_ACTUAL_VALUE_DRAW_SOURCE_CONTACT")
    def test_reader_identity_missing_is_hold(self):
        self.assertEqual(verify_native_arm(["b3a4"]*2,["b3a4"]*2,
             {"A":[2,2],"B":[2,2]},[True,False]),
             "HOLD_TT_FIRST_PHYSICAL_READER_UNVERIFIED")
    def test_cold_replay_disagreement_is_hold(self):
        self.assertEqual(verify_native_arm(["b3a4","f3f4"],["f3f4"]*2,
             {"A":[2,2],"B":[2,2]},[True,True]),
             "HOLD_NEUTRALIZED_COLD_REPLAY_UNSTABLE")
    def test_missing_cold_replay_is_hold(self):
        self.assertEqual(verify_native_arm(["b3a4"],["f3f4"]*2,
             {"A":[2],"B":[2,2]},[True,True]),"HOLD_COLD_REPLAY_MISSING")

if __name__=="__main__":
    unittest.main()
