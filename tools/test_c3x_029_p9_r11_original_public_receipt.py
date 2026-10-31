#!/usr/bin/env python3
"""Cross-check current repository's original T3 receipt against adjudication."""
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from c3x_029_p9_r11_t3_public_factorial_adjudicator import evaluate

class ActualPublicReceipt(unittest.TestCase):
    def test_original_receipt_invariants(self):
        path=ROOT/"c3x/receipts/c3x-023-P1-R2-T3-native-source-exact-SEE-TT-two-by-two-operator-interaction-20261011.json"
        receipt=json.loads(path.read_text())
        result=evaluate(receipt)
        self.assertEqual(result["count_joint_only"],1)
        self.assertEqual(result["count_independent_chess_positions"],2)
        by={z["game_id"]:z for z in result["cases"]}
        self.assertEqual(set(by),{2,11})
        self.assertEqual(by[2]["arm_bestmoves"]["TT1_SEE_FLIP"],"b1b4")
        self.assertEqual(by[2]["joint_candidate_indicator_interaction"],1)
        self.assertFalse(by[11]["joint_only_new_candidate"])
        self.assertEqual(result["candidate_specific_margin"],"NOT_IDENTIFIED")
        self.assertEqual(result["robustness_beyond_pinned_depth12"],"UNMEASURED")

if __name__=="__main__":
    unittest.main()
