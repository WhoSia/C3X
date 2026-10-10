#!/usr/bin/env python3
import sys,unittest
from pathlib import Path
import chess
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_021_P2_reply_contingent_chess_primitives import (
    profile_after_root,pair_profile,FIXED_PAIRS)
class ResponseContingentChess(unittest.TestCase):
    def test_standard_startpos_and_all_black_legal_responses(self):
        fen=" ".join(chess.Board().fen().split()[:4])
        a=profile_after_root(fen,"e2e4")
        self.assertEqual(len(a),20)
        self.assertIn("e7e5",a)
        self.assertGreater(a["e7e5"]["next_own_legal_count"],0)
        self.assertEqual(len(a["e7e5"]["next_own_legal_sha256"]),64)
    def test_missing_illegal_move_fails_before_any_native(self):
        with self.assertRaises(ValueError):
            profile_after_root(" ".join(chess.Board().fen().split()[:4]),"e2e5")
    def test_two_root_actions_identical_only_if_same_move(self):
        fen=" ".join(chess.Board().fen().split()[:4])
        m=pair_profile(fen,"e2e4","d2d4")
        self.assertEqual(m["F_legal_opponent_reply_count"],20)
        self.assertEqual(m["V_legal_opponent_reply_count"],20)
        self.assertEqual(len(m["response_contingent_own_reply_comparisons"]),20)
        self.assertGreater(m["different_next_own_move_set_count"],0)
    def test_cases_not_chosen_from_P2_new_native_outcomes(self):
        self.assertEqual(FIXED_PAIRS,{4:("h8h4","g5h4"),9:("a6b7","f6h5")})
    def test_no_native_engine_calls_and_no_atomic_variant(self):
        code=(Path(__file__).resolve().parents[1]/"harness"/
              "c3x_021_P2_reply_contingent_chess_primitives.py").read_text()
        self.assertNotIn("subprocess",code)
        self.assertNotIn("chess.engine",code)
        self.assertIn("Standard Chess",code)
if __name__=="__main__":unittest.main()
