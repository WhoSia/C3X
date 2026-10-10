#!/usr/bin/env python3
"""P1 StageA frozen only O/F + native SEE ancestor, no reader block V."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_023_P1_native_stageA_baseline_source_SEE_identity_registry import (
    literal,SOURCE_SHA,ECOLOGIES,ROLES,WORLDS
)
class P1BeforeInterventions(unittest.TestCase):
    def test_M0_vs_M1_exact_literal_forecast(self):
        x=literal("a2a3","g1f3",True)
        self.assertEqual(x["M0"],"a2a3")
        self.assertEqual(x["M1"],"g1f3")
        self.assertFalse(x["M0_predict_flip"])
        self.assertTrue(x["M1_predict_flip"])
    def test_missing_pair_excluded_not_fabricated(self):
        x=literal("a2a3","g1f3",False)
        self.assertIsNone(x["M0"])
        self.assertEqual(x["status"],"NO_ELIGIBLE_SOURCE")
    def test_source_and_ecology_fixed(self):
        self.assertEqual(len(SOURCE_SHA),64)
        self.assertEqual(ECOLOGIES,("may2026_broadcast","lichess_CC0_nonmate_puzzles"))
        self.assertEqual(ROLES,("STRICT","BROAD"))
        self.assertEqual(WORLDS,("O","F"))
    def test_cannot_contaminate_stageA_with_TT_reader_intervention(self):
        s=(Path(__file__).resolve().parents[1]/"harness"/
          "c3x_023_P1_native_stageA_baseline_source_SEE_identity_registry.py").read_text()
        self.assertIn('"actual_TT_FIRST_interventions":0',s)
        self.assertIn('"actual_SEE_Boolean_interventions":0',s)
        self.assertIn("passive_ancestry",s)
        self.assertIn("P1_NATIVE_POSITION_ANCESTOR_MISSING",s)
        self.assertNotIn('play(engine,world,order,"V"',s)
if __name__=="__main__":unittest.main()
