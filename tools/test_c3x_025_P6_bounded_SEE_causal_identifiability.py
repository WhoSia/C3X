#!/usr/bin/env python3
"""Binary SCM exhaustive proof and negative controls for C3X0.25 P6."""
import copy
import itertools
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_025_P6_bounded_SEE_trace_mediation_identifiability_countermodels import (
    LABELS,constructive_counterexamples,controlled,h,natural_indirect,observed,y)

class BoundedSEEMediationNotIdentified(unittest.TestCase):
    def test_all_model_binary_structural_functions_total(self):
        for label in LABELS:
            for t,k in itertools.product((0,1),repeat=2):
                self.assertIn(h(label,t),(0,1))
                self.assertIn(y(label,t,k),(0,1))
                self.assertEqual(controlled(label,t,k)["final_root_flip"],y(label,t,k))

    def test_treated_root_flip_still_does_not_identify_mediator(self):
        direct,mediated=LABELS[:2]
        for t in (0,1):
            self.assertEqual(observed(direct,t),observed(mediated,t))
        self.assertEqual((natural_indirect(direct),natural_indirect(mediated)),(0,1))
        self.assertNotEqual(controlled(direct,1,0),controlled(mediated,1,0))

    def test_stable_terminal_root_does_not_refute_hidden_mediation(self):
        no,compensated=LABELS[2:]
        for t in (0,1):
            self.assertEqual(observed(no,t),observed(compensated,t))
            self.assertEqual(observed(no,t)["binary_root_final_bestmove_flip"],0)
        self.assertEqual((natural_indirect(no),natural_indirect(compensated)),(0,-1))

    def test_late_path_activation_is_unseen_in_32_event_prefix(self):
        a,b=LABELS[:2]
        self.assertEqual(observed(a,1),observed(b,1))
        self.assertNotEqual(observed(a,1,True),observed(b,1,True))
        c,d=LABELS[2:]
        self.assertEqual(observed(c,1),observed(d,1))
        self.assertNotEqual(observed(c,1,True),observed(d,1,True))

    def test_witness_serialization_has_causal_disagreement_not_native_proof(self):
        proof=constructive_counterexamples()
        self.assertEqual(set(proof["two_constructive_counterexample_pairs"]),{
            "ROOT_FLIP_YES","ROOT_FLIP_NO"})
        for r in proof["two_constructive_counterexample_pairs"].values():
            self.assertTrue(r["same_partial_observation"])
            self.assertTrue(r["if_late_SEE_activation_is_actually_measured_then_models_diverge"])
            self.assertFalse(r["real_native_stockfish_physical_validity_established"])
        self.assertFalse(proof["natural_TT_SEE_mediation_proven_in_original_July_games"])

    def test_invalid_source_treatment_or_forced_mediator_fails_closed(self):
        with self.assertRaises(ValueError):observed("NOT_A_MODEL",0)
        with self.assertRaises(ValueError):observed(LABELS[0],2)
        with self.assertRaises(ValueError):y(LABELS[1],1,-1)

if __name__=="__main__":
    unittest.main(verbosity=2)
