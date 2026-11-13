import copy
import unittest
from c3x_030_s4h2_r3_archived_receipt_court import inspect_arm

def record():
    mask={"id":"14","ordinal":"0","parent":"3","key":"123","ply":"1",
          "hit_before":"1","hit_after":"0","raw":"C3X_S4G_MASK"}
    edge={"child_invocation_id":"14","parent_root_invocation_id":"3",
          "physical_tt_key":"123","physical_mask_ordinal":0,
          "child_return_value":-37,"observed_root_candidate_value":37,
          "root_move_raw":"400"}
    return {"mask_receipts":[mask],
            "physically_supported_child_root_arithmetic_links":[edge],
            "bounded_mask_count":1,"verified_links":1,
            "not_full_counterfactual_mediation":True}

class Audit(unittest.TestCase):
    def test_true_source_link(self):
        a=inspect_arm("one",record(),"123")
        self.assertEqual(a["physically_supported_links"],1)
    def test_parent_mismatch_rejected(self):
        a=record();a["physically_supported_child_root_arithmetic_links"][0]["parent_root_invocation_id"]="9"
        with self.assertRaisesRegex(ValueError,"PARENT_OR_VALUE"):inspect_arm("one",a,"123")
    def test_unphysical_link_rejected(self):
        a=record();a["mask_receipts"].clear();a["bounded_mask_count"]=0
        with self.assertRaisesRegex(ValueError,"NONPHYSICAL"):inspect_arm("one",a,"123")
    def test_negamax_failure_rejected(self):
        a=record();a["physically_supported_child_root_arithmetic_links"][0]["observed_root_candidate_value"]=38
        with self.assertRaisesRegex(ValueError,"PARENT_OR_VALUE"):inspect_arm("one",a,"123")
    def test_sham_mask_rejected(self):
        with self.assertRaisesRegex(ValueError,"CONTROL_MASK"):inspect_arm("sham",record(),"123")
    def test_out_of_dose_rejected(self):
        a=record();a["mask_receipts"].append(dict(a["mask_receipts"][0],id="15",ordinal="1"))
        with self.assertRaisesRegex(ValueError,"MASK_BOUNDED"):inspect_arm("one",a,"123")
    def test_postprobe_miss_with_no_real_mask_cannot_count(self):
        a=record();a["mask_receipts"].clear()
        a["physically_supported_child_root_arithmetic_links"].clear()
        a["bounded_mask_count"]=0;a["verified_links"]=0
        self.assertEqual(inspect_arm("two",a,"123")["physically_supported_links"],0)
if __name__=="__main__":unittest.main()
