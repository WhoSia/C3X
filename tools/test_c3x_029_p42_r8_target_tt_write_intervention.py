"""R8 test: write-path intervention is source-scoped and fails on anchor drift.

Pure synthetic patch contract, not a native Stockfish result.
"""
import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import c3x_029_p42_r8_guard_descendant_tt_save_intervention as p
import c3x_029_p42_r5_game14_capture_local_lineage_overlay as r5

SEARCH="\n".join([
    r5.STATE_ANCHOR,r5.EVENT_ANCHOR,r5.MAIN_ENTRY,r5.Q_ENTRY,
    r5.MAIN_DO,r5.MAIN_UNDO,r5.MAIN_STOP,r5.MAIN_ADOPT])+"\n"

def search_fixture():
    return r5.patch(SEARCH)

def tt_fixture():
    return '#include "tt.h"\nnamespace Stockfish {\n'+p.TT_ANCHOR+'\n}\n'

class TTWriteContract(unittest.TestCase):
    def test_changes_only_explicit_tagged_descendant(self):
        s=p.patch_search(search_fixture())
        self.assertEqual(s.count("c3x042_r8_target_descendant=true;"),1)
        self.assertEqual(s.count("c3x042_r5.child_returned=true;\n  c3x042_r8_target_descendant=false;"),1)
        self.assertLess(s.index("c3x042_r5.did_move=true;"),
                        s.index("c3x042_r8_target_descendant=true;"))
        return_site=s.index("c3x042_r5.child_returned=true;")
        self.assertLess(return_site,
                        s.index("c3x042_r8_target_descendant=false;",return_site))
    def test_control_is_non_mutating_when_env_unset(self):
        t=p.patch_tt(tt_fixture())
        self.assertIn('drop && drop[0]==\'1\' && drop[1]==\'\\0\'',t)
        self.assertIn('if (c3x042_r8_target_descendant)',t)
    def test_tt_anchor_is_unique(self):
        self.assertEqual(p.patch_tt(tt_fixture()).count("extern thread_local unsigned long long c3x042_r8_tt_attempts;"),1)
    def test_double_search_patch_refused(self):
        with self.assertRaisesRegex(ValueError,"ALREADY_PATCHED_SEARCH"):
            p.patch_search(p.patch_search(search_fixture()))
    def test_double_tt_patch_refused(self):
        with self.assertRaisesRegex(ValueError,"ALREADY_PATCHED_TT"):
            p.patch_tt(p.patch_tt(tt_fixture()))
    def test_missing_target_site_refused(self):
        bad=search_fixture().replace(p.AFTER_DO,"")
        with self.assertRaisesRegex(ValueError,"AFTER_DO_ANCHOR_COUNT_0"):
            p.patch_search(bad)
    def test_duplicate_tt_source_site_refused(self):
        with self.assertRaisesRegex(ValueError,"TTENTRY_SAVE_ANCHOR_COUNT_2"):
            p.patch_tt(tt_fixture()+p.TT_ANCHOR)
    def test_source_scope_does_not_change_original_guard_policy(self):
        s=p.patch_search(search_fixture())
        self.assertIn(r5.EVENT_ANCHOR,s)
        self.assertIn("c3x042_r5_arm(pos,ss,move);",s)

if __name__=="__main__":unittest.main()
