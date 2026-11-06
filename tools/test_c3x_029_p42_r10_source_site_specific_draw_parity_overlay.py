"""R10 actual original source callsite surgery contracts (synthetic)."""
import unittest
from c3x_029_p42_r10_source_site_specific_draw_parity_overlay import (
    patch,FUNCTION_TAIL,CYCLE,TERMINAL
)

def source():
    return FUNCTION_TAIL+"\n"+"void search() {\n"+CYCLE+"\n"+TERMINAL+"\n}"

class R10Sites(unittest.TestCase):
    def test_two_original_sites_replaced_independently(self):
        z=patch(source())
        self.assertIn("c3x042_r10_draw_site(pos.this_thread(),1,ss->ply);",z)
        self.assertIn("c3x042_r10_draw_site(pos.this_thread(),2,ss->ply);",z)
        self.assertIn("site 1=cycle-alpha, site 2=terminal draw",z)
    def test_existing_r9_source_preserved(self):
        z=patch(source())
        self.assertEqual(z.count(FUNCTION_TAIL),1)
    def test_double_patch_fails(self):
        with self.assertRaisesRegex(ValueError,"ALREADY_PATCHED"):
            patch(patch(source()))
    def test_missing_cycle_caller_fails(self):
        with self.assertRaisesRegex(ValueError,"CYCLE_ANCHOR_COUNT_0"):
            patch(source().replace(CYCLE,"value = 123;"))
    def test_duplicated_terminal_caller_fails(self):
        with self.assertRaisesRegex(ValueError,"TERMINAL_ANCHOR_COUNT_2"):
            patch(source()+TERMINAL)
    def test_missing_original_r9_source_fails(self):
        with self.assertRaisesRegex(ValueError,"R9_ANCHOR_COUNT_0"):
            patch(source().replace(FUNCTION_TAIL,"return VALUE_DRAW;"))
    def test_both_and_individual_selection_are_explicit(self):
        z=patch(source())
        for code in ("code == '1' && site == 1","code == '2' && site == 2","code == '3'"):
            self.assertIn(code,z)
    def test_original_native_function_is_always_called(self):
        z=patch(source())
        self.assertIn("const Value original = value_draw(thread);",z)
    def test_no_root_or_tt_mutation_in_helper(self):
        z=patch(source())
        helper=z.split("  // R10 independent site challenge.",1)[1].split("void search()",1)[0]
        for invalid in ("pos.do_move(", "TT.save(", "rootMoves.front(", "bestMove ="):
            self.assertNotIn(invalid,helper)

if __name__=="__main__":
    unittest.main()
