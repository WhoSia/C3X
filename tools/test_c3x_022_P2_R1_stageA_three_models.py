#!/usr/bin/env python3
"""P2-R1 exact UCI candidate survival model locked before V interventions."""
import sys,unittest
from pathlib import Path
import chess
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_022_P2_R1_depth11_survivor_exact_forecast_stageA import (
    forecast_three,native_leader_uci,ROLES,WORLDS,SOURCE_SHA,PRIMITIVE_SHA)
from c3x_022_P2_two_stage_exact_move_scout import stockfish16_encoded_move
class BeforeInterventionThreeModels(unittest.TestCase):
    def test_M2_promotes_less_exposed_depth11_survivor(self):
        x=forecast_three("a2a3","d2d4","e2e4",{"a2a3":500,"d2d4":0,"e2e4":100},True)
        self.assertEqual((x["M0"],x["M1"],x["M2"]),("a2a3","d2d4","e2e4"))
        self.assertTrue(x["M2_positive_prediction"])
    def test_M2_survivor_same_or_more_exposed_stays_put(self):
        x=forecast_three("a2a3","d2d4","e2e4",{"a2a3":100,"d2d4":0,"e2e4":100},True)
        self.assertEqual(x["M2"],"a2a3")
    def test_missing_depth11_stays_original(self):
        x=forecast_three("a2a3","d2d4",None,{"a2a3":500,"d2d4":0},True)
        self.assertEqual(x["M2"],"a2a3")
    def test_no_eligible_is_not_counted_positive(self):
        x=forecast_three("a2a3","d2d4","e2e4",{},False)
        self.assertEqual(x["status"],"NO_TREATMENT")
        self.assertIsNone(x["M2"])
    def test_native_leader_exact_legal_not_naive_untyped(self):
        b=chess.Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
        m=chess.Move.from_uci("e1c1")
        self.assertEqual(native_leader_uci(b,stockfish16_encoded_move(b,m)),"e1c1")
        self.assertIsNone(native_leader_uci(b,65535))
    def test_StageA_never_uses_V(self):
        s=(Path(__file__).resolve().parents[1]/"harness"/
           "c3x_022_P2_R1_depth11_survivor_exact_forecast_stageA.py").read_text()
        self.assertIn("first_pair(events[order],RULES[role])",s)
        self.assertIn("FIRST_TT_interventions_performed",s)
        self.assertNotIn('play(engine,w,order,"V"',s)
        self.assertEqual(len(SOURCE_SHA),len(PRIMITIVE_SHA))
if __name__=="__main__":unittest.main()
