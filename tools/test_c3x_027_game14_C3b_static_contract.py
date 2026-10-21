#!/usr/bin/env python3
"""Static regression gates for C3X 0.27 C3b emitted C++ (not a native build receipt)."""
import unittest
from tools.c3x_027_game14_C3b_passive_ancestor_overlay import HELPER, patch


class C3bStaticContract(unittest.TestCase):
    def test_fprintf_argument_is_valid_cpp_line_break(self):
        self.assertIn("int(move),value,\n    (unsigned long long)", HELPER)
        self.assertNotIn("int(move),value,\\n", HELPER)

    def test_anchor_missing_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "C3X027_C3B_ANCHOR_HELPERS_0"):
            patch("not a native search.cpp")

    def test_first_parent_and_post_undo_are_separate_sites(self):
        s = '''void c3x027_lineage_arm(const Position& pos,Search::Stack* ss,Move move) {
c3x027_lineage_emit("GUARD_REENABLED",pos,ss->ply);
c3x027_lineage_emit("CHILD_VALUE_RETURNED",pos,ss->ply,value,alpha,beta);
c3x027_lineage_emit("PARENT_CANDIDATE_VALUE",pos,ss->ply,value,alpha,beta);
      // Step 19. Undo move
      pos.undo_move(move);
    return bestValue;
  }


  // qsearch() is the quiescence search function
    return bestValue;
  }


  // value_to_tt() adjusts a mate or TB score'''
        patched = patch(s)
        self.assertEqual(patched.count('c3x027_c3b_candidate(pos,ss,move'), 2)
        self.assertIn('c3x027_c3b_frame_return(pos,ss,int(bestValue));', patched)
        self.assertIn('struct C3X027_C3b', patched)


if __name__ == "__main__":
    unittest.main()
