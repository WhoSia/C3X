import unittest
from c3x_018_tt_consumer_source_patch import patch

HEADER = "#include <cstring>   // For std::memset\nnamespace Stockfish {\n"
MAIN = """    // At non-PV nodes we check for an early TT cutoff
    if (  !PvNode
        && !excludedMove
        && tte->depth() > depth - (tte->bound() == BOUND_EXACT)
        && ttValue != VALUE_NONE // Possible in case of TT access race or if !ttHit
        && (tte->bound() & (ttValue >= beta ? BOUND_LOWER : BOUND_UPPER)))
    {"""
QS = """    // At non-PV nodes we check for an early TT cutoff
    if (  !PvNode
        && tte->depth() >= ttDepth
        && ttValue != VALUE_NONE // Only in case of TT access race or if !ttHit
        && (tte->bound() & (ttValue >= beta ? BOUND_LOWER : BOUND_UPPER)))
        return ttValue;"""

class C3X018ConsumerAnchors(unittest.TestCase):
    def test_both_native_branches(self):
        patched=patch(HEADER+MAIN+"\n"+QS)
        self.assertEqual(patched.count('c3x018_report_tt_cutoff("main"'),1)
        self.assertEqual(patched.count('c3x018_report_tt_cutoff("qsearch"'),1)
        self.assertIn("#include <cstdlib>",patched)

    def test_missing_qsearch_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError,"C3X018_TT_CONSUME_QSEARCH_ANCHOR_0"):
            patch(HEADER+MAIN)

    def test_duplicate_main_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError,"C3X018_TT_CONSUME_MAIN_ANCHOR_2"):
            patch(HEADER+MAIN+MAIN+QS)

if __name__=="__main__": unittest.main()
