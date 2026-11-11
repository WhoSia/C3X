import unittest
from c3x_030_p11s4d_source_trace_patch import apply,ORIG_PROBE,ORIG_NS,ORIG_RETURN,ORIG_ROOT
class Test(unittest.TestCase):
    def source(self):
        return "#include <algorithm>\n"+ORIG_NS+"\n"+ORIG_PROBE+"\n"+ORIG_RETURN+"\n"+ORIG_ROOT+"\ntte->save(a);"
    def test_three_nonmutating_sites(self):
        s=apply(self.source())
        self.assertIn('kind=probe',s);self.assertIn('kind=normal_return',s)
        self.assertIn('kind=root_candidate',s)
        self.assertIn('tte->save(a);',s)
    def test_source_event_links_stack_move_to_root(self):
        s=apply(self.source())
        self.assertIn('parent_move_raw=',s)
        self.assertIn('root_move_raw=',s)
        self.assertIn('best_value=',s)
    def test_duplicate_source_anchor_hold(self):
        with self.assertRaisesRegex(ValueError,'SOURCE_ANCHOR_NOT_UNIQUE'):
            apply(self.source()+ORIG_ROOT)
    def test_double_patch_hold(self):
        with self.assertRaisesRegex(ValueError,'ALREADY_INSTRUMENTED'):apply(apply(self.source()))
if __name__=='__main__':unittest.main()
