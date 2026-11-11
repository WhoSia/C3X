import unittest
from c3x_030_p11s4g_masked_invocation_patch import patch
from c3x_030_p11s4e_invocation_patch import NS,ENTRY,PROBE,RET,ROOT
class Tests(unittest.TestCase):
    def stub(self):
        return "#include <algorithm>\n"+NS+"\n"+ENTRY+"\n"+PROBE+"\n"+RET+"\n"+ROOT+"\ntte->save(key);"
    def test_one_compiled_binary_variable_dose(self):
        s=patch(self.stub())
        self.assertIn('C3X_S4G_MASK ordinal=',s)
        self.assertIn('C3X_S4G_MASK_LIMIT',s)
        self.assertIn('c3x_e_last_target',s)
        self.assertIn('tte->save(key);',s)
    def test_instance_id_in_physical_mask_record(self):
        s=patch(self.stub())
        self.assertIn('<< " id=" << c3x_e_scope.id',s)
        self.assertIn('ss->ttHit = false;',s)
    def test_double_patch_rejected(self):
        with self.assertRaisesRegex(ValueError,'ALREADY|DOUBLE'):patch(patch(self.stub()))
    def test_unmodified_stockfish_probe_site_preserved(self):
        self.assertEqual(patch(self.stub()).count('tte = TT.probe('),1)
if __name__=="__main__":unittest.main()
