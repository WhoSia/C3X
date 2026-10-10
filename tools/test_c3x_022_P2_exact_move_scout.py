#!/usr/bin/env python3
"""Forecasts must be literal UCI, sealed before any native reader suppression."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_022_P2_two_stage_exact_move_scout import exact_forecast,native_world,ECOLOGIES,WORLDS
class SpecificUciForecasts(unittest.TestCase):
    def test_disagree_cross_order_restores_exact_uci(self):
        o=exact_forecast("e2e4","d2d4","O",True)
        f=exact_forecast("e2e4","d2d4","F",True)
        self.assertEqual(o["predicted_UCI"],"d2d4")
        self.assertEqual(f["predicted_UCI"],"e2e4")
        self.assertTrue(o["predicted_flip"] and f["predicted_flip"])
    def test_equal_order_predicts_no_flip(self):
        for order in WORLDS:
            z=exact_forecast("e2e4","e2e4",order,True)
            self.assertEqual(z["predicted_UCI"],"e2e4")
            self.assertFalse(z["predicted_flip"])
    def test_no_target_is_not_a_positive_or_negative(self):
        v=exact_forecast("e2e4","d2d4","O",False)
        self.assertEqual(v["status"],"NO_TREATMENT")
        self.assertIsNone(v["predicted_UCI"])
        self.assertIsNone(v["predicted_flip"])
    def test_unreconstructible_clock_rejected(self):
        world={"fen4":"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -",
               "played_legal_move_uci":"e2e4","source_root_legal_count":20}
        with self.assertRaises(RuntimeError):
            native_world(world)
    def test_puzzles_and_twic_preserved_as_distinct_ecologies(self):
        self.assertEqual(ECOLOGIES,("twic","lichess_puzzles"))
        p=Path(__file__).resolve().parents[1]/"harness"/"c3x_022_P2_two_stage_exact_move_scout.py"
        s=p.read_text()
        self.assertNotIn('"V",',s)
        self.assertIn("first_pair(discoveries[order],RULES[role])",s)
        self.assertIn("root_depth_ladder",s)
if __name__=="__main__":unittest.main()
