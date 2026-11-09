"""R20 source-neutral semantic labelling, no new engine/court claim."""
import unittest
from c3x_029_p42_r20_reclassify_dynamic_root_support import interpret,SCHEMA

def native():
    rows=[]
    for depth in range(1,13):
        a="e1e4" if depth<9 else "b3a4"
        b="f3f4" if depth in (9,11,12) else "e1e4"
        c="b3a4" if depth>=9 else a
        reverse=c
        if depth==9:reverse="f3f4"
        if depth==10:reverse="f3f4"
        if depth==11:reverse="b3a4"
        rows.append({"depth":depth,"A":a,"B":b,"C":c,"C_reverse":reverse})
    # Depth11 C was f3f4, while the reversed C was b3a4.
    rows[10]["C"]="f3f4"
    return {"schema":SCHEMA,
      "status":"PASS_ACTUAL_NATIVE_LEGAL_ROOT_LEADER_CANDIDATE_TRANSPORT_ONLY",
      "root_depths":rows,
      "changed_root_leader_depths":[9,10,11],
      "third_candidate_emergence_depths":[10,11]}

class R20SupportInterpretation(unittest.TestCase):
    def test_depth10_is_third_to_A_B_C_but_not_globally_new(self):
        z=interpret(native())
        self.assertEqual(z["outside_contemporaneous_A_B_C_depths"],[10])
        self.assertEqual(z["new_move_identity_across_all_original_A_B_C_depths"],[])
        self.assertEqual(z["outside_contemporaneous_B_C_depths"],[10,11])
    def test_depth9_reproduces_B_original_leader(self):
        z=interpret(native())
        self.assertTrue(z["depthwise"][0]["reverse_matches_B"])
        self.assertFalse(z["depthwise"][0]["reverse_matches_C"])
    def test_depth11_reproduces_A_not_third_globally(self):
        z=interpret(native())
        self.assertTrue(z["depthwise"][2]["reverse_matches_A"])
        self.assertFalse(z["depthwise"][2]["reverse_matches_C"])
    def test_depth12_matches_C(self):
        self.assertTrue(interpret(native())["depthwise"][3]["reverse_matches_C"])
    def test_bad_native_admission_rejected(self):
        x=native();x["status"]="HOLD"
        with self.assertRaisesRegex(ValueError,"NOT_ADMITTED"):interpret(x)
    def test_root_depth_missing_rejected(self):
        x=native();x["root_depths"].pop()
        with self.assertRaisesRegex(ValueError,"DEPTH_ORDER"):interpret(x)
    def test_source_leader_change_misreported_rejected(self):
        x=native();x["changed_root_leader_depths"]=[9]
        with self.assertRaisesRegex(ValueError,"LEADER_CHANGE"):interpret(x)
    def test_old_pair_relative_label_mismatch_rejected(self):
        x=native();x["third_candidate_emergence_depths"]=[10]
        with self.assertRaisesRegex(ValueError,"PAIR_RELATIVE"):interpret(x)
    def test_no_natural_mediation_claim(self):
        x=interpret(native())
        self.assertFalse(x["natural_root_mediation_proved"])
        self.assertFalse(x["independent_chess_strategic_value_proved"])
    def test_wholly_new_legal_move_not_ignored(self):
        x=native();x["root_depths"][9]["C_reverse"]="h2h4"
        z=interpret(x)
        self.assertEqual(z["new_move_identity_across_all_original_A_B_C_depths"],[10])

if __name__=="__main__":
    unittest.main()
