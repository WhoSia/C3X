"""Synthetic original R12 source contract, not a native behavioral claim."""
import unittest
from c3x_029_p42_r12_single_cycle_event_intervention import patch,ANCHOR,STATE_ANCHOR
def fixture():
    return STATE_ANCHOR+'\\n'+ANCHOR

class R12SourceTests(unittest.TestCase):
    def test_exact_single_source_cycle_site(self):
        s=patch('A\n'+ANCHOR+'\nB')
        self.assertEqual(s.count('++c3x042_r12_ordinal;'),1)
        self.assertIn('const Value c3x042_r12_native',s)
        self.assertIn('const Value c3x042_r11_candidate',s)
    def test_only_original_chosen_call_modified(self):
        s=patch(fixture())
        self.assertIn('c3x042_r12_ordinal == c3x042_r12_selected',s)
        self.assertIn('c3x042_r12_hit ? VALUE_DRAW : c3x042_r12_native',s)
    def test_missing_source_match_holds(self):
        with self.assertRaisesRegex(ValueError,'ANCHOR_COUNT_0'):
            patch('empty')
    def test_duplicate_source_site_holds(self):
        with self.assertRaisesRegex(ValueError,'ANCHOR_COUNT_2'):
            patch(ANCHOR+'\n'+ANCHOR)
    def test_duplicate_application_holds(self):
        with self.assertRaisesRegex(ValueError,'ALREADY_PATCHED'):
            patch(patch(fixture()))
    def test_original_value_always_physically_computed(self):
        self.assertIn('c3x042_r10_draw_site(pos.this_thread(),1,ss->ply)',patch(fixture()))
    def test_no_direct_root_override(self):
        s=patch(fixture())
        for bad in ('rootMoves.front(', 'TT.save(', 'pos.do_move(', 'pos.undo_move('):
            self.assertNotIn(bad,s)
    def test_no_silent_default_intervention(self):
        self.assertIn('c3x042_r12_selected != 0',patch(fixture()))
    def test_per_thread_counter_declaration(self):
        self.assertIn('thread_local unsigned long long c3x042_r12_ordinal=0;',patch(fixture()))
if __name__=='__main__':
    unittest.main()
