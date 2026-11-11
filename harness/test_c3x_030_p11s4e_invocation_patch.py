import unittest
from c3x_030_p11s4e_invocation_patch import apply,NS,ENTRY,PROBE,RET,ROOT
class Test(unittest.TestCase):
    def sample(self):
        return "#include <algorithm>\n"+NS+"\n"+ENTRY+"\n"+PROBE+"\n"+RET+"\n"+ROOT+"\ntte->save(key);"
    def test_four_sites_and_unmodified_ttsave(self):
        z=apply(self.sample())
        self.assertEqual(z.count("C3X_S4E kind="),4)
        self.assertIn("tte->save(key);",z)
    def test_raii_returns_and_parent(self):
        z=apply(self.sample())
        self.assertIn("~C3XInvocationScope()",z)
        self.assertIn("parent_id",z)
        self.assertIn("child_last=",z)
        self.assertIn("value_known=0",z)
    def test_ambiguous_anchor_holds(self):
        with self.assertRaisesRegex(ValueError,"NONUNIQUE_STOCKFISH16_SOURCE_SITE"):
            apply(self.sample()+ROOT)
    def test_double_patch_holds(self):
        with self.assertRaisesRegex(ValueError,"DOUBLE_PATCH"):apply(apply(self.sample()))
if __name__=="__main__":unittest.main()
