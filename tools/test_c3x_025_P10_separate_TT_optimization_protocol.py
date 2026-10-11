#!/usr/bin/env python3
"""Synthetic protocol gate, not actual engine game strength."""
import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_025_P10_separate_TT_policy_strength_and_performance_adjudicator import (
    SCHEMA,R0,ARMS,adjudicate,demo,MIN_PAIRS)
def manifest(n=8,source="SYNTHETIC_TEST_ONLY"):
    return {"schema":"c3x025-P10-separate-engine-optimization-prereg-source-v1",
      "baseline":R0,"candidate":ARMS[0],"source_unseen_and_disjoint":True,
      "color_swap_pairing":True,"stop_after_pairs":n,
      "GPL_rights_scope_verified":True,"source_mode":source,
      "performance_native_nodes_time_verified":False}
def pairs(n=8):
    return [{"opening_index":i+1,"same_opening_hash_confirmed":True,
      "opponent_color_swapped":True,"both_legal_and_complete":True,
      "same_engine_build_contract":True,"A_white_points":0.5,
      "A_black_points":0.5} for i in range(n)]
class P10IsSeparate(unittest.TestCase):
    def test_no_synthetic_strength_claim(self):
        a=demo()
        self.assertEqual(a["game_strength_optimization_status"],
            "SYNTHETIC_SMOKE_TEST__NO_ENGINE_STRENGTH_CLAIM")
        self.assertEqual(a["candidate_minus_original_game_points"],0)
    def test_exposed_July_not_independent(self):
        a=manifest();a["source_unseen_and_disjoint"]=False
        with self.assertRaisesRegex(ValueError,"EXPOSED"):adjudicate(a,pairs())
    def test_no_dual_TT_policy_arms(self):
        a=manifest();a["candidate"]="R1_AND_R2_UNREGISTERED"
        with self.assertRaisesRegex(ValueError,"UNREGISTERED"):adjudicate(a,pairs())
    def test_must_use_opposite_colours_and_same_original_opening(self):
        p=pairs();p[3]["opponent_color_swapped"]=False
        with self.assertRaisesRegex(ValueError,"COLOR"):adjudicate(manifest(),p)
    def test_unresolved_illegal_game_hold(self):
        p=pairs();p[0]["both_legal_and_complete"]=False
        with self.assertRaisesRegex(ValueError,"ILLEGAL"):adjudicate(manifest(),p)
    def test_unregistered_optional_stopping_not_allowed(self):
        a=manifest();a["stop_after_pairs"]=7
        with self.assertRaisesRegex(ValueError,"STOPPING"):adjudicate(a,pairs())
    def test_license_scope_missing_is_hard_fail(self):
        a=manifest();a["GPL_rights_scope_verified"]=False
        with self.assertRaisesRegex(ValueError,"LICENSE"):adjudicate(a,pairs())
    def test_no_inference_from_99_native_pairs_even_if_all_win(self):
        a=manifest(99,"NATIVE_ORIGINAL_MATCHES");p=pairs(99)
        for x in p:x["A_white_points"]=x["A_black_points"]=1
        r=adjudicate(a,p)
        self.assertEqual(r["game_strength_optimization_status"],
            "HOLD_UNDERPOWERED_PREDECLARED_MINIMUM")
    def test_even_100_perfect_native_results_without_nodes_timing_are_hold(self):
        a=manifest(100,"NATIVE_ORIGINAL_MATCHES");p=pairs(100)
        for x in p:x["A_white_points"]=x["A_black_points"]=1
        r=adjudicate(a,p)
        self.assertEqual(r["game_strength_optimization_status"],
            "HOLD_NO_NATIVE_NODE_TIME_AND_MEMORY_EVIDENCE")
    def test_no_fake_positive_on_exact_R0_equivalence(self):
        a=manifest(100,"NATIVE_ORIGINAL_MATCHES");p=pairs(100)
        a["performance_native_nodes_time_verified"]=True
        r=adjudicate(a,p)
        self.assertEqual(r["game_strength_optimization_status"],
            "NO_SIGNIFICANT_POSITIVE_PAIRED_GAME_STRENGTH_EVIDENCE")
        self.assertEqual(r["paired_10k_bootstrap_95pct_game_point_improvement"],[0,0])
if __name__=="__main__":unittest.main(verbosity=2)
