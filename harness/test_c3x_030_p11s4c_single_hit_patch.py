import unittest
from c3x_030_p11s4c_single_hit_patch import apply,ANCHOR,NS
class Contract(unittest.TestCase):
    def template(self):
        return "#include <algorithm>\n"+NS+"\n"+ANCHOR+"\ntte->save(a,b);"
    def test_exact_site_and_once_global(self):
        x=apply(self.template())
        self.assertEqual(x.count("c3x_s4c_one_hit_claimed.exchange"),1)
        self.assertIn("std::atomic<bool> c3x_s4c_one_hit_claimed",x)
        self.assertIn("parent_move_raw=",x)
        self.assertIn("tte->save(a,b)",x)
    def test_second_patch_rejected(self):
        with self.assertRaisesRegex(ValueError,"DOUBLE_PATCH"):apply(apply(self.template()))
    def test_duplicate_anchor_rejected(self):
        with self.assertRaisesRegex(ValueError,"NONUNIQUE_ORIGINAL_ANCHOR"):apply(self.template()+ANCHOR)
    def test_original_probe_not_deleted(self):
        self.assertEqual(apply(self.template()).count("tte = TT.probe"),1)
if __name__=="__main__":unittest.main()
