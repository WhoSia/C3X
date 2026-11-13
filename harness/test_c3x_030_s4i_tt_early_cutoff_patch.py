import unittest
from c3x_030_s4i_tt_early_cutoff_patch import patch,TT_CUTOFF
from c3x_030_p11s4e_invocation_patch import NS,ENTRY,PROBE,RET,ROOT

def original():
    return "#include <algorithm>\n"+NS+"\n"+ENTRY+"\n"+PROBE+"\n"+TT_CUTOFF+"\n"+RET+"\n"+ROOT+"\ntte->save(key);"

class TestCutoff(unittest.TestCase):
    def test_only_true_return_path_instrumented(self):
        s=patch(original())
        self.assertEqual(s.count("return ttValue;"),1)
        self.assertEqual(s.count("C3X_S4I_TT_CUTOFF ordinal="),1)
        self.assertIn("if (c3x_e_scope.interested)",s)
        self.assertEqual(s.count("tte = TT.probe(posKey, ss->ttHit);"),1)
        self.assertIn("ss->ttHit = false;",s)
    def test_global_cutoff_counter(self):
        s=patch(original())
        self.assertEqual(s.count("static std::atomic<unsigned> c3x_i_logged_cutoffs{0};"),1)
        self.assertEqual(s.count("c3x_i_logged_cutoffs.fetch_add"),1)
    def test_double_patch_fails_closed(self):
        with self.assertRaises(ValueError):patch(patch(original()))
    def test_no_state_changed_before_return(self):
        s=patch(original())
        b=s[s.index("// S4-I: observe only actual TT short-circuit"):s.index("return ttValue;")]
        self.assertNotIn("ss->ttHit = false;",b)
        self.assertNotIn("alpha =",b)
        self.assertNotIn("beta =",b)
if __name__=="__main__":unittest.main()
