"""R11 strict source surgery tests, not a claim of native execution."""
import unittest
from c3x_029_p42_r11_original_cycle_window_event_overlay import OLD, NEW, patch

class R11WindowSourceTests(unittest.TestCase):
    def test_original_cycle_branch_surgery_once(self):
        s=patch('before\n'+OLD+'\nafter')
        self.assertIn('c3x042_r11_old_alpha',s)
        self.assertEqual(s.count('c3x042_r11_cut ='),1)
        self.assertEqual(s.count('if (c3x042_r11_cut)'),1)
        self.assertIn('root_move=%d',s)
        self.assertIn('key64=%llu',s)
    def test_no_fictitious_score_bound(self):
        s=patch(OLD)
        self.assertIn('alpha = c3x042_r11_candidate;',s)
        self.assertIn('alpha >= beta',s)
        self.assertIn('old_alpha=%d beta=%d candidate=%d',s)
    def test_no_spurious_move_mutation(self):
        s=patch(OLD)
        for invalid in ('pos.do_move(', 'pos.undo_move(', 'TT.save(', 'rootMoves.front().score='):
            self.assertNotIn(invalid,s)
    def test_missing_original_site_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'ANCHOR_COUNT_0'):
            patch('other')
    def test_duplicate_source_site_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'ANCHOR_COUNT_2'):
            patch(OLD+'\n'+OLD)
    def test_double_patching_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'ALREADY_INSTRUMENTED'):
            patch(patch(OLD))
    def test_trace_path_gated(self):
        s=patch(OLD)
        self.assertIn('std::getenv("C3X042_R11_CYCLE_WINDOW_TRACE")',s)
        self.assertIn('if (*c3x042_r11_path)',s)
    def test_preserves_neighboring_original_source(self):
        s='sentinel_before\n'+OLD+'\nsentinel_after'
        got=patch(s)
        self.assertTrue(got.startswith('sentinel_before\n'))
        self.assertTrue(got.endswith('\nsentinel_after'))
    def test_logs_native_cutoff_not_causal_claim(self):
        self.assertIn('int(c3x042_r11_cut)',patch(OLD))
        self.assertIn('return alpha;',patch(OLD))
if __name__=='__main__':
    unittest.main()
