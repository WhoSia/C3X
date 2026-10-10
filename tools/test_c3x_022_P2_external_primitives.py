#!/usr/bin/env python3
"""Never build chess labels or native outcomes into pre-engine legal move profiles."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_022_P2_external_preengine_chess_decision_primitives import SOURCE_SHA,prepare
class P2ChessPrimitives(unittest.TestCase):
    def test_precommitted_TWIC_puzzle_source_sha(self):
        self.assertEqual(SOURCE_SHA,"ebe6648f43f64c6f31e0d547845bec3d87c663093fd68298acf2ebe4c0287554")
    def test_bad_source_denominator_fails(self):
        with self.assertRaises(ValueError):
            prepare({"phase":"ENGINE_BLIND_SOURCE_FREEZE_NO_TT_FORECAST_OUTCOME","selected_count":16})
    def test_missing_source_phase_fails(self):
        with self.assertRaises(ValueError):
            prepare({"phase":"NATIVE_OUTCOME_SELECTED","selected_count":32})
    def test_no_engine_and_all_legal_root_moves(self):
        s=(Path(__file__).resolve().parents[1]/"harness"/
           "c3x_022_P2_external_preengine_chess_decision_primitives.py").read_text()
        self.assertNotIn("subprocess",s)
        self.assertNotIn("chess.engine",s)
        self.assertIn("profile(b)",s)
        self.assertIn("P2_CROSS_ECOLOGY_FEN_COLLISION",s)
if __name__=="__main__":unittest.main()
