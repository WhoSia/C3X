import copy
import unittest
from c3x_030_s4h2_r2_physical_trace_audit import verify_and_preserve,ARMS

def setup():
    masks={x:[] for x in ARMS}
    edges={x:{"records":[]} for x in ARMS}
    masks["one"]=[{"id":"17","ordinal":"0","parent":"5","key":"123","ply":"1",
                   "hit_before":"1","hit_after":"0","raw":"C3X_S4G_MASK"}]
    edges["one"]["records"]=[{"child_id":"17","parent_id":"5","probe_hit_after_mask":"0",
         "root_score":41,"child_return":-41,"root_raw_move":"100"}]
    return masks,edges

class PhysicalTraceAudit(unittest.TestCase):
    def test_authenticated_physical_parent_negamax(self):
        m,e=setup();result=verify_and_preserve(m,e,"123")
        self.assertEqual(result["one"]["verified_links"],1)
        self.assertEqual(result["one"]["physically_supported_child_root_arithmetic_links"][0]
                         ["parent_root_invocation_id"],"5")
        self.assertFalse(result["one"]["not_full_counterfactual_mediation"] is False)
    def test_wrong_key_rejected(self):
        m,e=setup();m["one"][0]["key"]="999"
        with self.assertRaisesRegex(ValueError,"NOT_ACTUAL_TARGET"):verify_and_preserve(m,e,"123")
    def test_wrong_parent_rejected(self):
        m,e=setup();e["one"]["records"][0]["parent_id"]="6"
        with self.assertRaisesRegex(ValueError,"FALSE_PARENT"):verify_and_preserve(m,e,"123")
    def test_wrong_negamax_rejected(self):
        m,e=setup();e["one"]["records"][0]["root_score"]=99
        with self.assertRaisesRegex(ValueError,"FALSE_PARENT"):verify_and_preserve(m,e,"123")
    def test_unmasked_miss_is_not_a_physical_link(self):
        m,e=setup();e["two"]["records"]=[copy.deepcopy(e["one"]["records"][0])]
        self.assertEqual(verify_and_preserve(m,e,"123")["two"]["verified_links"],0)
    def test_negative_control_contact_rejected(self):
        m,e=setup();m["sham"]=copy.deepcopy(m["one"])
        with self.assertRaisesRegex(ValueError,"MASK_IN_NEGATIVE"):verify_and_preserve(m,e,"123")
    def test_duplicate_source_event_rejected(self):
        m,e=setup();m["two"]=copy.deepcopy(m["one"])*2
        with self.assertRaisesRegex(ValueError,"DUPLICATE_PHYSICAL"):verify_and_preserve(m,e,"123")
    def test_bounded_many_log_preserves_truncation(self):
        m,e=setup()
        m["many"]=[dict(m["one"][0],id=str(i),ordinal=str(i)) for i in range(8)]
        self.assertTrue(verify_and_preserve(m,e,"123")["many"]["physical_mask_log_truncated_possible"])
if __name__=="__main__":unittest.main()
