import unittest
from c3x_030_p11s4g_r1_physical_mask_receipt_audit import audit,SCHEMA,ARMS,ORIGINAL_SCHEMA
def sample():
    arms={}
    for arm in ARMS:
        physical=([{"id":"5","parent":"1","ordinal":"0","hit_before":"1","hit_after":"0",
                    "key":"99","ply":"1"}] if arm=="many" else [])
        link={"child_id":"5","parent_id":"1","root_score":42,"child_return":-42,
              "probe_hit_after_mask":"0"}
        arms[arm]={"records":[link],"observed_links_with_masked_TT_hit":1}
        arms[arm]["physical"]=physical
    result={"schema":ORIGINAL_SCHEMA,"status":"PASS_SOURCE_MASK_AND_VALUE_EDGE_OBSERVATION",
           "native_searches":36,"native_actual_nodes":432459,
           "negative_controls_equal":True,"positions":{}}
    for i in range(3):
        result["positions"][str(i)]={
            "source_mask_receipts":{a:x["physical"] for a,x in arms.items()},
            "same_invocation_arithmetic_edges":{a:{"records":x["records"],
                "observed_links_with_masked_TT_hit":x["observed_links_with_masked_TT_hit"]}
                for a,x in arms.items()},
            "frozen_physical_TT_key":"99",
            "root_move_changes_vs_sham":{a:0 for a in ARMS}}
    return result
class Tests(unittest.TestCase):
    def test_true_receipt_and_false_hitzero_differ(self):
        o=audit(sample())
        self.assertEqual(o["physical_mask_link_totals"]["many"],3)
        self.assertEqual(o["old_postprobe_zero_links_totals"]["many"],3)
        self.assertEqual(o["physical_mask_link_totals"]["zero"],0)
        self.assertEqual(o["old_postprobe_zero_links_totals"]["zero"],3)
        self.assertFalse(o["proves_full_parent_root_counterfactual_mediation"])
    def test_falsified_parent_rejected(self):
        d=sample();d["positions"]["0"]["source_mask_receipts"]["many"][0]["parent"]="8"
        with self.assertRaisesRegex(ValueError,"FALSE_PHYSICAL_MASK_LINK"):audit(d)
    def test_wrong_key_rejected(self):
        d=sample();d["positions"]["0"]["source_mask_receipts"]["many"][0]["key"]="15"
        with self.assertRaisesRegex(ValueError,"WRONG_SOURCE_KEY"):audit(d)
    def test_duplicate_source_receipt_rejected(self):
        d=sample();r=d["positions"]["0"]["source_mask_receipts"]["many"]
        r.append(dict(r[0]))
        with self.assertRaisesRegex(ValueError,"DUPLICATE_PHYSICAL"):audit(d)
if __name__=="__main__":unittest.main()
