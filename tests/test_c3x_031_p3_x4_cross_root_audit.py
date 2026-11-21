"""P3-X4 synthetic locality theorem and actual original-source failure guards.

Set C3X_P2_B2_ZIP and C3X_P3_X2_ZIP to test original research archive
re-read and adversarial corrupted source signatures. CI sets both.
"""
import copy
import os
import unittest

from c3x_031_p3_x4_cross_root_audit import (
    classify,source_zip,audit,P2_MEMBER,X2_MEMBER,P2_SHA,X2_SHA
)


def originals():
    b2=os.getenv("C3X_P2_B2_ZIP")
    x2=os.getenv("C3X_P3_X2_ZIP")
    if not b2 or not x2:
        raise unittest.SkipTest("Original research ZIPs not configured for this local unit test")
    return source_zip(b2,P2_MEMBER,P2_SHA),source_zip(x2,X2_MEMBER,X2_SHA)


class CrossRootDecisionTests(unittest.TestCase):
    def test_no_change(self):
        self.assertEqual(classify("e2e4","d2d4","e2e4"),"NO_FINAL_CHANGE")

    def test_target_displaced(self):
        self.assertEqual(classify("e2e4","e2e4","d2d4"),"TARGET_DISPLACED")

    def test_target_promoted(self):
        self.assertEqual(classify("e2e4","d2d4","d2d4"),"TARGET_PROMOTED")

    def test_off_target_third_winner(self):
        self.assertEqual(classify("b8d8","h5e2","f5h3"),"OFF_TARGET_SWITCH")

    def test_malformed_source_move_fails(self):
        with self.assertRaises(ValueError):
            classify("","h5e2","f5h3")

    def test_actual_128_plus_12_original_source_results(self):
        p2,x2=originals()
        result=audit(p2,x2)
        self.assertEqual(result["original_P2_root_classification"],{
            "NO_FINAL_CHANGE":114,"TARGET_DISPLACED":8,"TARGET_PROMOTED":6})
        self.assertEqual(result["original_X2_root_classification"],{
            "NO_FINAL_CHANGE":1,"OFF_TARGET_SWITCH":2,
            "TARGET_DISPLACED":7,"TARGET_PROMOTED":2})
        self.assertEqual(result["off_target_source_unique_games"],1)
        self.assertEqual(result["new_stockfish_searches"],0)

    def test_actual_tampered_native_source_open_rejected(self):
        p2,x2=originals()
        cell=x2["horizon_cells"][0]
        cell["arms"]["both_off0"]["genuine_source_event"]["open"]["key"]="WRONG_FULL_KEY"
        with self.assertRaises(ValueError):
            audit(p2,x2)

    def test_actual_cold_process_divergence_rejected(self):
        p2,x2=originals()
        cell=x2["horizon_cells"][0]
        cell["arms"]["both_off0"]["native_root_best"]["move"]="b2b3"
        with self.assertRaises(ValueError):
            audit(p2,x2)

    def test_actual_missing_original_horizon_retained_in_denominator(self):
        p2,x2=originals()
        x2["horizon_cells"].pop()
        with self.assertRaises(ValueError):
            audit(p2,x2)

    def test_original_frozen_event_count_cannot_be_rewritten(self):
        p2,x2=originals()
        p2["source_event_results"].pop()
        with self.assertRaises(ValueError):
            audit(p2,x2)


if __name__=="__main__":
    unittest.main()
