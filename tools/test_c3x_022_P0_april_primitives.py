#!/usr/bin/env python3
import sys,unittest
from pathlib import Path
import chess
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_022_P0_april_chess_decision_primitives import build,APRIL_SHA
class AprilPrimitives(unittest.TestCase):
    def test_frozen_sha(self):
        self.assertEqual(APRIL_SHA,"0e5516fc0cd49203bf7cc366f4133d6c9b20a2f21de0667468f121e398d2fa93")
    def test_sixteen_source_required(self):
        with self.assertRaises(ValueError):
            build({"phase":"SOURCE_ONLY_BEFORE_APRIL_NATIVE_OUTCOMES","selected":[]})
    def test_source_must_precede_native(self):
        source={"phase":"SOURCE_ONLY_BEFORE_APRIL_NATIVE_OUTCOMES",
                "selected":[{"id":i+1,"fen4":chess.STARTING_BOARD_FEN+" w KQkq -",
                "source_root_legal_count":20,"played_legal_move_uci":"e2e4",
                "source_game_sha256":str(i)} for i in range(16)]}
        with self.assertRaises(ValueError):
            build(source)
    def test_no_native_engine_imports(self):
        code=(Path(__file__).resolve().parents[1]/"harness"/"c3x_022_P0_april_chess_decision_primitives.py").read_text()
        self.assertNotIn("subprocess",code)
        self.assertNotIn("chess.engine",code)
        self.assertIn("profile(board)",code)
if __name__=="__main__":unittest.main()
