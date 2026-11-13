import unittest
from c3x_030_s4h2_eligibility_patch import apply
from c3x_030_p11s4e_invocation_patch import NS,ENTRY,PROBE,RET,ROOT

def original_stub():
    return "#include <algorithm>\n"+NS+"\n"+ENTRY+"\n"+PROBE+"\n"+RET+"\n"+ROOT+"\ntte->save(key);"

class TestEligibilityPatch(unittest.TestCase):
    def test_probe_before_mask_and_no_tt_assignment_in_new_logger(self):
        modified=apply(original_stub())
        probe=modified.index("tte = TT.probe(posKey, ss->ttHit);")
        hit=modified.index('C3X_S4H2_ELIGIBLE ordinal=')
        mask=modified.index("ss->ttHit = false;")
        self.assertTrue(probe < hit < mask)
        self.assertEqual(modified.count('C3X_S4H2_ELIGIBLE ordinal='),1)
        self.assertEqual(modified.count("tte = TT.probe(posKey, ss->ttHit);"),1)
        self.assertEqual(modified.count("tte->save(key);"),1)
    def test_logger_exports_no_root_score_or_pv(self):
        modified=apply(original_stub())
        block=modified.split("// C3X S4H2: outcome-blind first actual TT hit",1)[1].split("// C3X S4G:",1)[0]
        self.assertNotIn("bestmove",block)
        self.assertNotIn("root_move",block)
        self.assertNotIn(" pv=",block)
        self.assertNotIn("score=",block)
    def test_double_patch_rejected(self):
        with self.assertRaises(ValueError):apply(apply(original_stub()))
if __name__=="__main__":unittest.main()
