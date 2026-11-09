"""R16 exact source-state support tests (synthetic, not native)."""
import unittest
from c3x_029_p42_r16_original_event33_crossworld_source_support import (
 audit,match_indices,first_difference,BOARD,WINDOW,SCORE)

def event(i,**kwargs):
    x=dict(key=i,ply=3,depth=6,root_move=88,
           old_alpha=-8,beta=1,mod4=2)
    x.update(kwargs)
    return x
def states():
    b=[event(i) for i in range(40)]
    c=[dict(x) for x in b]
    joint=[dict(x) for x in b]
    return b,c,joint
def roots():
    return [dict(depth=d,leader=1112,score=-89,average=-80) for d in range(1,13)]

class R16SupportTests(unittest.TestCase):
    def test_all_three_same_full_source_signature(self):
        b,c,j=states()
        r=audit(b,c,j,roots(),roots())
        self.assertEqual(r["crossworld_source_support"]["capture_guard_C"]["exact_source_computation"],1)
        self.assertTrue(r["original_B_event33_full_source_signature_in_C"])
        self.assertFalse(r["natural_common_mediator_certified"])
    def test_no_original_B_event33_board_key_in_C(self):
        b,c,j=states();c[32]["key"]=999
        r=audit(b,c,j,roots(),roots())
        self.assertFalse(r["original_B_event33_same_board_context_in_C"])
        self.assertEqual(r["crossworld_source_support"]["capture_guard_C"]["board_context"],0)
    def test_same_board_but_different_window(self):
        b,c,j=states();c[32]["beta"]=2
        r=audit(b,c,j,roots(),roots())
        self.assertTrue(r["original_B_event33_same_board_context_in_C"])
        self.assertFalse(r["original_B_event33_same_window_and_board_in_C"])
    def test_same_window_but_different_node_bit(self):
        b,c,j=states();c[32]["mod4"]=3
        r=audit(b,c,j,roots(),roots())
        self.assertTrue(r["original_B_event33_same_window_and_board_in_C"])
        self.assertFalse(r["original_B_event33_full_source_signature_in_C"])
    def test_source_call_ordinal_is_not_source_event_identity(self):
        b,c,j=states()
        matching=c.pop(32)
        c.insert(39,matching)
        r=audit(b,c,j,roots(),roots())
        self.assertTrue(r["original_B_event33_full_source_signature_in_C"])
        self.assertEqual(r["first_native_event_identity_difference"]["B_vs_C"],33)
    def test_exact_source_signature_duplicate_count_is_not_one_mediator(self):
        b,c,j=states();c.append(dict(c[32]))
        r=audit(b,c,j,roots(),roots())
        self.assertEqual(r["crossworld_source_support"]["capture_guard_C"]["exact_source_computation"],2)
        self.assertFalse(r["causal_reachability_of_B33_in_C_established"])
    def test_matching_root_summaries_do_not_certify_state_identity(self):
        b,c,j=states();c[32]["key"]=99
        r=audit(b,c,j,roots(),roots())
        self.assertEqual(len(r["C_vs_combined_full_root_summary_matching_depths"]),12)
        self.assertFalse(r["natural_common_mediator_certified"])
    def test_root_depth_support_difference_holds(self):
        b,c,j=states()
        r=audit(b,c,j,roots(),roots()[:-1])
        self.assertEqual(r["status"],"HOLD_DIFFERENT_ROOT_DEPTH_SUPPORT")
    def test_original_B_signature_may_be_absent_in_combined(self):
        b,c,j=states();j[32]["key"]=999
        r=audit(b,c,j,roots(),roots())
        self.assertEqual(r["crossworld_source_support"]["combined_C_plus_B33"]["exact_source_computation"],0)
    def test_first_difference_when_one_trace_shorter(self):
        a=[event(1),event(2)];b=[event(1)]
        self.assertEqual(first_difference(a,b,BOARD),2)
    def test_first_difference_on_equal_native_traces_is_none(self):
        a=[event(1),event(2)]
        self.assertIsNone(first_difference(a,[dict(x) for x in a],SCORE))
    def test_private_key_never_appears_in_public_result(self):
        b,c,j=states();b[32]["key"]=4820203130129876543
        x=audit(b,c,j,roots(),roots())
        self.assertNotIn("4820203130129876543",str(x))
        self.assertFalse(x["source_key_or_score_values_disclosed"])
    def test_root_mean_difference_detected_but_leader_score_same(self):
        b,c,j=states();x=roots();y=roots();y[8]["average"]=-79
        r=audit(b,c,j,x,y)
        self.assertIn(9,r["C_vs_combined_root_leader_score_matching_depths"])
        self.assertNotIn(9,r["C_vs_combined_full_root_summary_matching_depths"])

if __name__=="__main__":
    unittest.main()
