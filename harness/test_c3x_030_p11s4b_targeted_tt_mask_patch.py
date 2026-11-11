import unittest
from c3x_030_p11s4b_targeted_tt_mask_patch import apply,ANCHOR
class Test(unittest.TestCase):
    def source(self):
        return '#include <iostream>\n'+ANCHOR+'\ntte->save(posKey, value);'
    def test_unique_target_hit_patch(self):
        result=apply(self.source())
        self.assertIn('ss->ttHit = false;',result)
        self.assertIn('ss->ply == 1',result)
        self.assertIn('C3X_S4B_MASKED',result)
        self.assertIn('tte->save(posKey, value)',result)
    def test_double_patch_rejected(self):
        with self.assertRaisesRegex(ValueError,'DOUBLE_INSTRUMENTATION'):
            apply(apply(self.source()))
    def test_ambiguous_probe_anchor_rejected(self):
        with self.assertRaisesRegex(ValueError,'SOURCE_ANCHOR'):
            apply(self.source()+ANCHOR)
    def test_original_probe_preserved(self):
        self.assertEqual(apply(self.source()).count('TT.probe('),1)
if __name__=='__main__':unittest.main()
