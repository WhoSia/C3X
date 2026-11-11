import unittest
from c3x_030_p11s4g_native_paired_court import inspect_edges,native_mask_receipts,ARMS
class Tests(unittest.TestCase):
    def test_six_fixed_arms(self):
        self.assertEqual(ARMS,("original","sham","zero","one","two","many"))
    def test_good_source_mask_event(self):
        l="C3X_S4G_MASK ordinal=0 key=99 ply=1 id=5 parent=1 hit_before=1 hit_after=0"
        self.assertEqual(len(native_mask_receipts({"other_stderr":[l]})),1)
    def test_bad_source_mask_event(self):
        l="C3X_S4G_MASK ordinal=0 key=99 ply=3 id=5 parent=1 hit_before=1 hit_after=0"
        with self.assertRaisesRegex(ValueError,"BAD_ACTUAL_MASK"):native_mask_receipts({"other_stderr":[l]})
    def test_negamax_parent_edge(self):
        e=[{"kind":"probe","id":"5","parent":"1","hit":"0"},
            {"kind":"normal_return","id":"5","parent":"1","value":"-42"},
            {"kind":"root_candidate","id":"1","child_last":"5","value":"42","root_move_raw":"67"}]
        r=inspect_edges(e)
        self.assertEqual(r["observed_links_with_masked_TT_hit"],1)
        self.assertFalse(r["not_complete_mediation"] is False)
    def test_false_negamax_hold(self):
        e=[{"kind":"probe","id":"5","parent":"1","hit":"0"},
            {"kind":"normal_return","id":"5","parent":"1","value":"-42"},
            {"kind":"root_candidate","id":"1","child_last":"5","value":"43","root_move_raw":"67"}]
        with self.assertRaisesRegex(ValueError,"NEGAMAX_VALUE_NOT_PRESERVED"):inspect_edges(e)
if __name__=="__main__":unittest.main()
