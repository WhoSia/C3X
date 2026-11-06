"""P42/R9 synthetic contract checks; does not establish native Game14 contact."""
import unittest
from c3x_029_p42_r9_original_value_draw_node_parity_intervention import (
    patch, ANCHOR, FUNCTION
)

def fixture():
    return "namespace Stockfish {\n" + FUNCTION + "\n" + ANCHOR + "\n  }\n}"

class R9DrawPatchTests(unittest.TestCase):
    def test_exact_single_actual_original_callsite(self):
        new=patch(fixture())
        self.assertEqual(new.count("c3x042_r9_native ="),1)
        self.assertIn("C3X042_R9_DRAW_TRACE",new)
        self.assertIn("C3X042_R9_DRAW_PARITY_NEUTRAL",new)
        self.assertIn("thisThread->nodes & 0x2",new)
    def test_no_mutation_of_other_source(self):
        sentinel="\nvoid unrelated() { int x = 9; }\n"
        new=patch(fixture()+sentinel)
        self.assertTrue(new.endswith(sentinel))
    def test_duplicate_source_anchor_rejected(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_ANCHOR_NOT_UNIQUE"):
            patch(fixture()+"\n"+ANCHOR)
    def test_missing_original_return_rejected(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_ANCHOR_NOT_UNIQUE"):
            patch(fixture().replace(ANCHOR,"return VALUE_DRAW;"))
    def test_no_second_source_patch(self):
        with self.assertRaisesRegex(ValueError,"ALREADY_INSTRUMENTED"):
            patch(patch(fixture()))
    def test_nonadjacent_function_must_hold(self):
        x=fixture().replace(ANCHOR,"/*"+("long filler"*60)+"*/\n"+ANCHOR)
        with self.assertRaisesRegex(ValueError,"FUNCTION_AND_RETURN_NOT_ADJACENT"):
            patch(x)
    def test_observation_is_passive_when_neutral_off(self):
        s=patch(fixture())
        self.assertIn("return c3x042_r9_neutral ? VALUE_DRAW : c3x042_r9_native;",s)
    def test_no_engine_choice_write_in_source_patch(self):
        s=patch(fixture())
        code="\n".join(line.split("//",1)[0] for line in s.splitlines())
        self.assertNotIn("rootMoves.front().score",code)
        self.assertNotIn("TT.save(",code)
        self.assertNotIn("bestMove =",code)

if __name__=="__main__":
    unittest.main()
