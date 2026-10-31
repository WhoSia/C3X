#!/usr/bin/env python3
"""Original T3/C3b/R3 receipt consistency, without protected path data."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from c3x_029_p9_r14_cross_receipt_type_audit import audit
P=[
"c3x/receipts/c3x-023-P1-R2-T3-native-source-exact-SEE-TT-two-by-two-operator-interaction-20261011.json",
"c3x/receipts/c3x-024-P2-R2-native-ancestor-root-full-and-partial-development-20261011.json",
"c3x/receipts/c3x-024-P2-R3-source-root-candidate-reached-but-not-final-and-May11-partial-20261011.json"
]
class CertificateTypes(unittest.TestCase):
    def test_original_receipts(self):
        data=[json.loads((ROOT/p).read_text()) for p in P]
        result=audit(*data)
        self.assertEqual(result["game2_joint_selected"],"b1b4")
        self.assertEqual(result["full_source_to_root_candidates_reached_but_lost"],2)
        self.assertFalse(result["game2_source_guard_full_chain_is_joint_arm"])
        self.assertEqual(result["complete_causal_mediation"],"NOT_IDENTIFIED")
    def test_corrupt_class_count_fails(self):
        data=[json.loads((ROOT/p).read_text()) for p in P]
        data[1]["source_certificates"]["full_ancestor_root_arms"]=3
        with self.assertRaisesRegex(ValueError,"R2_COUNTS"):audit(*data)
    def test_corrupt_t3_winner_fails(self):
        data=[json.loads((ROOT/p).read_text()) for p in P]
        for case in data[0]["root_cases"]:
            if case["game_id"]==2: case["arms"]["TT1_SEE_FLIP"]["bestmove"]="e1g1"
        with self.assertRaisesRegex(ValueError,"T3_JOINT"):audit(*data)
if __name__=="__main__":unittest.main()
