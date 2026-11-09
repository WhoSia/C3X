"""R18 source-patch contract, synthetic source fixture only."""
import unittest
from c3x_029_p42_r18_source_identity_reverse_B33_in_C_overlay import (
    patch,ANCHOR,STATE)

def fixture():return "namespace Stockfish {\n"+STATE+"\n"+ANCHOR+"\n}\n"
class R18IdentityPatchTests(unittest.TestCase):
    def test_exact_original_B_source_ID_only(self):
        x=patch(fixture())
        for k in ("KEY","PLY","DEPTH","ROOT_MOVE","ALPHA","BETA"):
            self.assertIn("C3X042_R18_TARGET_"+k,x)
        self.assertIn("pos.key()",x)
        self.assertIn("c3x042_r11_old_alpha",x)
    def test_does_not_match_node_mod4_because_causal_input_is_varied(self):
        x=patch(fixture())
        selected=x.split("const bool r18_eligible =",1)[1].split("if (r18_eligible)",1)[0]
        self.assertNotIn("nodes & 3",selected)
    def test_exact_reverse_return_is_minus_one(self):
        x=patch(fixture())
        self.assertIn("r18_apply ? Value(-1)",x)
        self.assertIn("c3x042_r12_hit ? VALUE_DRAW : c3x042_r12_native",x)
    def test_idempotent_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"ALREADY_PATCHED"):
            patch(patch(fixture()))
    def test_missing_anchor_fails(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_ANCHOR_DRIFT"):
            patch(fixture().replace(ANCHOR,"return VALUE_DRAW;"))
    def test_duplicate_original_branch_fails(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_ANCHOR_DRIFT"):
            patch(fixture()+ANCHOR)
    def test_source_state_initialized_per_real_engine_process(self):
        x=patch(fixture())
        self.assertIn("thread_local unsigned long long c3x042_r18_matching_calls=0",x)
        self.assertIn("c3x042_r18_matching_calls == 1",x)
    def test_private_hit_log_only_when_source_matches(self):
        x=patch(fixture())
        self.assertIn('if (r18_eligible) {',x)
        self.assertIn("C3X042_R18_PRIVATE_HIT_LOG",x)
    def test_no_new_chess_move_or_tt_write(self):
        code="\n".join(line.split("//",1)[0] for line in patch(fixture()).splitlines())
        for forbidden in ("TT.save(", "pos.do_move(", "pos.undo_move(", "rootMoves.front()"):
            self.assertNotIn(forbidden,code)
if __name__=="__main__":
    unittest.main()
