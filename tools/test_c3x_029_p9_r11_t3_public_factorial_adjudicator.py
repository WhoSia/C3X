#!/usr/bin/env python3
"""Pure receipt contract tests; uses no Stockfish or protected source bytes."""
import sys
import unittest
from copy import deepcopy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p9_r11_t3_public_factorial_adjudicator import evaluate

def fixture():
    def arm(move,cp,nodes):
        return {"bestmove":move,"score_cp":cp,"nodes":nodes}
    return {"schema":"c3x023-P1-R2-T3-two-preregistered-SEE-pruning-events-cross-real-physical-TT-first-v1",
            "treatment_validation":{"number_distinct_preselected_chess_positions":2},
            "root_cases":[
                {"game_id":2,"arms":{"TT0_SEE_SHAM":arm("e1g1",-8,20062),
                  "TT1_SEE_SHAM":arm("e1g1",-8,41685),
                  "TT0_SEE_FLIP":arm("e1g1",1,46783),
                  "TT1_SEE_FLIP":arm("b1b4",-4,47563)}},
                {"game_id":11,"arms":{"TT0_SEE_SHAM":arm("c7d6",-95,64424),
                  "TT1_SEE_SHAM":arm("d8b8",-104,68114),
                  "TT0_SEE_FLIP":arm("c7d6",-95,64426),
                  "TT1_SEE_FLIP":arm("d8b8",-104,68116)}}]}

class T3Factorial(unittest.TestCase):
    def test_joint_only_and_negative(self):
        z=evaluate(fixture())
        self.assertEqual(z["count_joint_only"],1)
        by={x["game_id"]:x for x in z["cases"]}
        self.assertEqual(by[2]["joint_candidate_indicator_interaction"],1)
        self.assertEqual(by[11]["joint_candidate_indicator_interaction"],0)
        self.assertTrue(all(x["per_candidate_score_margin_status"]=="NOT_IDENTIFIED" for x in z["cases"]))
        self.assertEqual(z["count_independent_chess_positions"],2)
    def test_incomplete_factorial_rejected(self):
        t=fixture()
        del t["root_cases"][0]["arms"]["TT1_SEE_FLIP"]
        with self.assertRaisesRegex(ValueError,"FACTORIAL_ARMS"):
            evaluate(t)
    def test_nonindependent_game_duplicate_rejected(self):
        t=fixture()
        t["root_cases"][1]["game_id"]=2
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            evaluate(t)
    def test_wrong_schema_rejected(self):
        t=fixture()
        t["schema"]="untrusted"
        with self.assertRaisesRegex(ValueError,"SCHEMA"):
            evaluate(t)

if __name__=="__main__":
    unittest.main()
