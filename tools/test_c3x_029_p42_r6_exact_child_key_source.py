"""P42/R6 source surgery contracts: actual child key is read AFTER do_move.

Synthetic exact-anchor fixture only. It cannot establish native engine behavior,
and must not replace pinned-source SHA, compile, historical replay or legal chess.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c3x_029_p42_r5_game14_capture_local_lineage_overlay as overlay

def synthetic_cpp_fixture():
    # The fixture is a token/anchor contract, deliberately NOT complete C++.
    return "\n".join([
        overlay.STATE_ANCHOR,
        overlay.EVENT_ANCHOR,
        overlay.MAIN_ENTRY,
        overlay.Q_ENTRY,
        overlay.MAIN_DO,
        overlay.MAIN_UNDO,
        overlay.MAIN_STOP,
        overlay.MAIN_ADOPT,
    ])+"\n"

class SourceActualKeyTests(unittest.TestCase):
    def test_exact_source_surgery_is_unique(self):
        s=overlay.patch(synthetic_cpp_fixture())
        self.assertEqual(s.count("c3x042_r5_arm(pos,ss,move);"),1)
        self.assertEqual(s.count('c3x042_r5_emit(pos,"ACTUAL_DO_MOVE");'),1)
        self.assertIn("c3x042_r5.child_key=pos.key();",s)
        self.assertNotIn("c3x042_r5.child_key=pos.key_after(move);",s)
        self.assertLess(s.index("pos.do_move(move, st, givesCheck);"),
                        s.index("c3x042_r5_after_do(pos,ss,move);"))
        self.assertIn('c3x042_r5_before_undo(pos,ss,move,int(value));',s)
    def test_parent_assessment_site_not_brittle_across_source_comments(self):
        source=synthetic_cpp_fixture().replace(
            overlay.MAIN_STOP,
            "      if (Threads.stop.load(std::memory_order_relaxed))\n"
            "          return VALUE_ZERO;\n"
            "      // actual pinned SF16 explanatory comment before root branch\n"
            + overlay.MAIN_STOP
        )
        result=overlay.patch(source)
        self.assertEqual(result.count("c3x042_r5_assess(pos,ss,move,"),1)
        self.assertLess(result.index("if (Threads.stop.load"),
                        result.index("c3x042_r5_assess(pos,ss,move,"))
        self.assertLess(result.index("c3x042_r5_assess(pos,ss,move,"),
                        result.index(overlay.MAIN_STOP))

    def test_source_contract_rejects_duplicate_root_assessment_site(self):
        source=synthetic_cpp_fixture()+overlay.MAIN_STOP+"\n"
        with self.assertRaisesRegex(ValueError,"PARENT_ASSESS_ANCHOR_COUNT_2"):
            overlay.patch(source)

    def test_duplicate_application_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"ALREADY_PATCHED"):
            overlay.patch(overlay.patch(synthetic_cpp_fixture()))
    def test_duplicate_anchor_fails_closed(self):
        bad=synthetic_cpp_fixture()+overlay.MAIN_DO+"\n"
        with self.assertRaisesRegex(ValueError,"DO_MOVE_ANCHOR_COUNT_2"):
            overlay.patch(bad)
    def test_missing_guard_bypass_fails_closed(self):
        bad=synthetic_cpp_fixture().replace(overlay.EVENT_ANCHOR,"")
        with self.assertRaisesRegex(ValueError,"EXACT_GUARD_ANCHOR_COUNT_0"):
            overlay.patch(bad)
    def test_actual_key_measured_only_at_post_move(self):
        s=overlay.patch(synthetic_cpp_fixture())
        # Pre-do native key is parent key. The first child-key write in the
        # event handler must be the observed post-do Position::key().
        pos=s.index("void c3x042_r5_after_do")
        nxt=s.index("void c3x042_r5_entry",pos)
        helper=s[pos:nxt]
        self.assertIn("c3x042_r5.child_key=pos.key();",helper)
        self.assertNotIn("pos.key_after(move)",helper.split("// Obtain actual child identity ONLY after original pos.do_move().")[-1])
        self.assertNotIn("pos.key()!=c3x042_r5.child_key",helper)
    def test_no_source_mutation_of_tt_see_or_chess_return_in_helper(self):
        # Inspect code-only lines: an observer may describe an original source
        # operation in a C++ // comment without performing that operation.
        source="\n".join(line.split("//",1)[0]
                         for line in overlay.HELPER.splitlines())
        self.assertNotIn("pos.do_move(",source)
        self.assertNotIn("pos.undo_move(",source)
        self.assertNotIn("TT.save(",source)
        self.assertNotIn("return VALUE_",source)

if __name__=="__main__":
    unittest.main()
