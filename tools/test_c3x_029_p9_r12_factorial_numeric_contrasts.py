#!/usr/bin/env python3
"""Tests for source-reported scalar interaction, not candidate valuation."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p9_r12_factorial_numeric_contrasts import analyze

def case(g, moves, nodes, scores):
    keys=("TT0_SEE_SHAM","TT1_SEE_SHAM","TT0_SEE_FLIP","TT1_SEE_FLIP")
    return {"game_id":g,"arms":{k:{"bestmove":m,"nodes":n,"score_cp":s} for k,m,n,s in zip(keys,moves,nodes,scores)}}

def fixture():
    return {"schema":"c3x023-P1-R2-T3-two-preregistered-SEE-pruning-events-cross-real-physical-TT-first-v1",
      "root_cases":[case(2,["e1g1","e1g1","e1g1","b1b4"],[20062,41685,46783,47563],[-8,-8,1,-4]),
      case(11,["c7d6","d8b8","c7d6","d8b8"],[64424,68114,64426,68116],[-95,-104,-95,-104])]}

class TestR12(unittest.TestCase):
    def test_known_interactions(self):
        d={r["game_id"]:r for r in analyze(fixture())["cases"]}
        self.assertEqual(d[2]["nodes_four_arm_contrast"],-20843)
        self.assertEqual(d[11]["nodes_four_arm_contrast"],0)
        self.assertEqual(d[2]["reported_root_cp_four_arm_arithmetic_contrast"],-5)
        self.assertEqual(d[11]["reported_root_cp_four_arm_arithmetic_contrast"],0)
        self.assertEqual(d[2]["selection_indicator_contrast"],1)
        self.assertFalse(d[2]["root_cp_contrast_is_candidate_margin"])
        self.assertEqual(d[2]["per_candidate_score_status"],"UNMEASURED")
    def test_wrong_schema(self):
        d=fixture();d["schema"]="garbage"
        with self.assertRaisesRegex(ValueError,"SCHEMA"):analyze(d)
    def test_missing_arm(self):
        d=fixture();del d["root_cases"][1]["arms"]["TT1_SEE_FLIP"]
        with self.assertRaisesRegex(ValueError,"FACTORIAL"):analyze(d)
    def test_duplicate_game(self):
        d=fixture();d["root_cases"][1]["game_id"]=2
        with self.assertRaisesRegex(ValueError,"DISTINCT"):analyze(d)

if __name__=="__main__":unittest.main()
