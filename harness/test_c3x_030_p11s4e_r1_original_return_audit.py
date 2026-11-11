import unittest
from c3x_030_p11s4e_r1_original_return_audit import exact_edges
def probe():return {"kind":"probe","id":"5","parent":"1","key":"99","ply":"1","hit":"1"}
def ret():return {"kind":"normal_return","id":"5","parent":"1","ply":"1","value":"-37"}
def root():return {"kind":"root_candidate","id":"1","child_last":"5","value":"37"}
class Test(unittest.TestCase):
    def test_true_same_parent_negamax(self):
        v=exact_edges([probe(),ret(),root()])
        self.assertEqual(v["root_edges_with_same_id_parent_time_and_negated_value"],1)
        self.assertFalse(v["edges"][0]["TT_hit_caused_return_value"])
    def test_inconsistent_parent_holds(self):
        x=ret();x["parent"]="2"
        with self.assertRaisesRegex(ValueError,"PARENT_INVOCATION_MISMATCH"):exact_edges([probe(),x,root()])
    def test_value_mismatch_holds(self):
        x=root();x["value"]="30"
        with self.assertRaisesRegex(ValueError,"NEGAMAX_CHILD_ROOT"):exact_edges([probe(),ret(),x])
    def test_temporal_reordering_does_not_fake_edge(self):
        v=exact_edges([root(),probe(),ret()])
        self.assertEqual(v["root_edges_with_same_id_parent_time_and_negated_value"],0)
    def test_non_hit_holds(self):
        x=probe();x["hit"]="0"
        with self.assertRaisesRegex(ValueError,"NOT_REAL_TT_HIT"):exact_edges([x,ret(),root()])
if __name__=="__main__":unittest.main()
