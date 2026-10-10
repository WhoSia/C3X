#!/usr/bin/env python3
"""M3v2 decision tests: no chess engine or TT FIRST treatment.
"""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_024_P3_Sep2025_128_preFIRST_M0_M1_M2_M3v1_M3v2 import exact_m3v2
class NewPreTreatmentM3V2Rule(unittest.TestCase):
    def test_strict_root_order_disagreement(self):
        self.assertEqual(exact_m3v2("STRICT",123,123,"e2e4","d2d4","c2c4"),("d2d4",True))
    def test_strict_depth11_backstop(self):
        self.assertEqual(exact_m3v2("STRICT",123,123,"e2e4","e2e4","g1f3"),("g1f3",True))
    def test_no_priority_to_depth11_when_order_disagrees(self):
        self.assertEqual(exact_m3v2("STRICT",123,123,"e2e4","d2d4","g1f3"),("d2d4",True))
    def test_broad_never_triggers(self):
        self.assertEqual(exact_m3v2("BROAD",123,123,"e2e4","d2d4","g1f3"),("e2e4",False))
    def test_physical_reader_candidate_not_original_winner(self):
        self.assertEqual(exact_m3v2("STRICT",456,123,"e2e4","d2d4","g1f3"),("e2e4",False))
    def test_stable_stays_null(self):
        self.assertEqual(exact_m3v2("STRICT",123,123,"e2e4","e2e4",None),("e2e4",False))
if __name__=="__main__":unittest.main()
