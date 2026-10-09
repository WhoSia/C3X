import unittest
from c3x_018_tt_physical_observer_patch import patch_tt

class TTObserverPatchTest(unittest.TestCase):
    def test_expected_source_sites(self):
        # A bounded syntactic source fixture that mirrors frozen SF16 anchors.
        s = """#include <thread>
TranspositionTable TT; // Our global transposition table
void TTEntry::save(Key k, Value v, bool pv, Bound b, Depth d, Move m, Value ev) {

  // Preserve any existing move
      eval16    = (int16_t)ev;
  }
}
          return found = (bool)tte[i].depth8, &tte[i];
  return found = false, replace;
}"""
        r=patch_tt(s)
        self.assertIn('key64=',r)
        self.assertIn('slot=',r)
        self.assertIn('kind',r)
        self.assertIn('c3x018_old_depth',r)
        self.assertIn('observed',r)
        self.assertEqual(r.count('c3x018_tt_record("probe"'),2)
        self.assertEqual(r.count('c3x018_tt_record("save"'),1)

    def test_missing_source_anchor_fails(self):
        with self.assertRaisesRegex(RuntimeError,'C3X018_TT_ANCHOR'):
            patch_tt('#include <thread>')

    def test_duplicate_source_anchor_fails(self):
        with self.assertRaisesRegex(RuntimeError,'C3X018_TT_ANCHOR_INCLUDE_2'):
            patch_tt('#include <thread>\n#include <thread>')

if __name__=='__main__':
    unittest.main()
