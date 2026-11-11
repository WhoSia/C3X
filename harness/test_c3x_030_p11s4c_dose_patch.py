import unittest
from c3x_030_p11s4c_dose_patch import apply
from c3x_030_p11s4c_single_hit_patch import ANCHOR,NS
class Test(unittest.TestCase):
    def source(self):
        return "#include <algorithm>\n"+NS+"\n"+ANCHOR+"\ntte->save(foo);"
    def test_original_probe_save_survive(self):
        r=apply(self.source())
        self.assertEqual(r.count("tte = TT.probe"),1)
        self.assertEqual(r.count("tte->save(foo)"),1)
        self.assertIn("C3X_S4C2_LIMIT",r)
    def test_single_process_global_counter(self):
        r=apply(self.source())
        self.assertIn("static std::atomic<unsigned> c3x_s4c2_matching_hits",r)
        self.assertEqual(r.count("matching_hits.fetch_add"),1)
    def test_doubly_patched_rejected(self):
        with self.assertRaisesRegex(ValueError,"DOUBLE_PATCH"):
            apply(apply(self.source()))
    def test_mismatched_anchor_hold(self):
        with self.assertRaisesRegex(ValueError,"NONUNIQUE_SOURCE_ANCHOR"):
            apply(self.source()+ANCHOR)
if __name__=="__main__":unittest.main()
