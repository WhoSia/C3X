#!/usr/bin/env python3
"""Deterministic bounded reference-model and proof-carrying source trace tests.
No physical native TT FIRST, no new source cohort, no strength claim.
"""
import copy
import itertools
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_025_P4_sf16_TT_three_slot_transition_reference import (
    AGE_MASK,CLUSTER_SIZE,GEN_CYCLE,Cluster,Entry,EXACT,LOWER,UPPER,
    constructive_witnesses)
from c3x_025_P5_search_lineage_partial_certificate_checker import (
    compare,validate_arm,synthetic_fixture)

class P4TTSourceMicroSemantics(unittest.TestCase):
    def test_declared_counterexamples_witnessed_without_native_claim(self):
        w=constructive_witnesses()
        self.assertEqual((w["P4_I_ignored_probe_hit_can_modify_later_replacement"]["later_different_key_miss_replaces_active_slot"],
            w["P4_I_ignored_probe_hit_can_modify_later_replacement"]["later_different_key_miss_replaces_no_refresh_slot"]),(1,0))
        self.assertFalse(w["P4_II_move_writer_can_differ_from_score_writer"]["numeric_score_fields_update"])
        self.assertFalse(w["P4_III_low16_alias_is_not_full64_identity"]["full64_source_writer_verified"])
        self.assertFalse(w["P4_IV_boundaries"]["natural_TT_SEE_mediation_proven"])

    def test_exact_three_slot_bounded_exhaustion_reference_independent_oracle(self):
        # 2^3 choices of compact key; 2^3 depths; 2^3 bound-generation
        # combinations per 3 slots = 8^3 = 512 unique old slot vectors.
        # x2 current generation x3 probes = 3072 pure state transitions.
        # This is NOT an unbounded proof of the real native C++ implementation.
        variants=[Entry(key16=k,depth8=d,genBound8=g)
                  for k in (1,2) for d in (0,12) for g in (0,8)]
        count=0;hit=miss=0
        for triple in itertools.product(variants,repeat=CLUSTER_SIZE):
            for generation in (0,16):
                for key in (1,2,3):
                    before=copy.deepcopy(list(triple))
                    expected_idx=None
                    for i,e in enumerate(before):
                        if e.key16==key or e.depth8==0:
                            expected_idx=i
                            break
                    if expected_idx is None:
                        scores=[e.depth8-((GEN_CYCLE+generation-e.genBound8)&AGE_MASK)
                                for e in before]
                        expected_idx=min(range(3),key=lambda i:scores[i])
                    c=Cluster(before,generation)
                    res=c.probe(key)
                    self.assertEqual(res.slot,expected_idx)
                    self.assertEqual(res.found,
                        bool(before[expected_idx].depth8) if
                        before[expected_idx].key16==key or before[expected_idx].depth8==0
                        else False)
                    if res.refreshed:
                        self.assertEqual(c.slots[res.slot].genBound8,
                            generation|(before[res.slot].genBound8&7))
                        self.assertEqual(sum(a.genBound8!=b.genBound8
                            for a,b in zip(c.slots,before)),int(
                                c.slots[res.slot].genBound8!=before[res.slot].genBound8))
                    else:self.assertEqual(c.state()["three_slots"],
                         [vars(e) for e in before])
                    hit+=int(res.found);miss+=int(not res.found);count+=1
        self.assertEqual(count,3072)
        self.assertTrue(hit>0 and miss>0)

    def test_move_provenance_not_equivalent_to_score_field(self):
        c=Cluster([Entry(key16=55,depth8=32,genBound8=LOWER,
                         move16=5,value16=88,eval16=27),Entry(),Entry()],16)
        before=copy.deepcopy(c.slots[0])
        r=c.save(0,55,144,False,UPPER,10,47,6)
        self.assertTrue(r["move16_written"])
        self.assertFalse(r["score_fields_written"])
        self.assertEqual(c.slots[0].move16,47)
        for f in ("key16","depth8","genBound8","value16","eval16"):
            self.assertEqual(getattr(c.slots[0],f),getattr(before,f))
        another=c.save(0,55,73,True,EXACT,7,0,-6)
        self.assertFalse(another["move16_written"])
        self.assertTrue(another["score_fields_written"])
        self.assertEqual(c.slots[0].move16,47)
        self.assertEqual(c.slots[0].value16,73)

    def test_age_counterfactual_not_a_readonly_probe(self):
        prior=Cluster([Entry(key16=i+1,depth8=12,genBound8=0)
                       for i in range(3)],16)
        mutate=prior.clone()
        shadow=prior.clone()
        res_a=mutate.probe(1,True);res_b=shadow.probe(1,False)
        self.assertTrue(res_a.found and res_b.found)
        self.assertEqual((mutate.probe(4).slot,shadow.probe(4).slot),(1,0))
        self.assertNotEqual(mutate.state(),shadow.state())

    def test_low16_alias_is_not_full64_source_provenance(self):
        two=Cluster([Entry(key16=0x42,depth8=19),Entry(),Entry()])
        self.assertEqual(two.probe(0x00010042).slot,two.probe(0x00020042).slot)
        self.assertTrue(two.probe(0x00020042).found)

    def test_generation_wrap_and_fail_closed_inputs(self):
        c=Cluster(generation=248);c.new_search()
        self.assertEqual(c.generation,0)
        with self.assertRaises(ValueError):Cluster(generation=249)
        with self.assertRaises(ValueError):c.probe(-1)
        with self.assertRaises(ValueError):c.save(0,1,1,False,LOWER,-7,4,2)

class P5StructuralProofObligations(unittest.TestCase):
    def fresh(self):
        return synthetic_fixture()

    def test_synthetic_complete_trace_is_explicitly_noncausal(self):
        d=self.fresh()
        r=compare(d["OBS"],d["TREAT"])
        self.assertEqual(r["status"],"TRACE_CHAIN_COMPLETE_NONCAUSAL")
        self.assertTrue(r["stated_computational_state_equal"])
        self.assertFalse(r["natural_TT_SEE_mediation_proven"])
        self.assertFalse(r["source_same_native_event_crossarm_proved"])

    def test_same_chess_path_but_changed_window_not_equal_computation(self):
        d=self.fresh()
        for e in d["TREAT"]:e["state"]["alpha"]=-25
        r=compare(d["OBS"],d["TREAT"])
        self.assertEqual(r["full_state_label"],
                         "SAME_CHESS_PATH_DIFFERENT_COMPUTATIONAL_STATE")
        self.assertIn("alpha",r["differing_state_fields"])
        self.assertFalse(r["stated_computational_state_equal"])

    def test_native_semantic_consumption_must_be_evidenced(self):
        d=self.fresh()
        del d["OBS"][1]["tt_value_actually_consumed"]
        r=compare(d["OBS"],d["TREAT"])
        self.assertEqual(r["status"],"HOLD_OR_INSUFFICIENT_SOURCE_EVIDENCE")
        self.assertIn("NO_ACTUAL_SEMANTIC_USE",r["OBS"]["status"])

    def test_real_writer_reader_block_missing_means_hold(self):
        d=self.fresh()
        d["TREAT"][0]["physically_blocked_and_writer_verified"]=False
        self.assertIn("HOLD_NO_NATIVE_PHYSICAL",compare(
            d["OBS"],d["TREAT"])["TREAT"]["status"])

    def test_missing_branch_and_return_is_a_hold_not_an_imputed_path(self):
        d=self.fresh()
        d["TREAT"]=[x for x in d["TREAT"] if x["kind"]!="BRANCH_DECISION"]
        # Reparent later events to keep chain structurally well-formed.
        for i,e in enumerate(d["TREAT"]):
            e["parent"]=None if i==0 else d["TREAT"][i-1]["id"]
        r=compare(d["OBS"],d["TREAT"])
        self.assertEqual(r["TREAT"]["status"],
                         "HOLD_MISSING_ORDERED_SOURCE_E0_TO_E6_EVENTS")
        self.assertFalse(r["natural_TT_SEE_mediation_proven"])

    def test_wrong_event_ordering_is_rejected_not_filled(self):
        d=self.fresh()
        d["TREAT"][2]["serial"]=d["TREAT"][1]["serial"]
        with self.assertRaisesRegex(ValueError,"SERIAL"):
            compare(d["OBS"],d["TREAT"])

    def test_broken_parent_or_repeated_event_id_is_rejected(self):
        d=self.fresh()
        d["OBS"][3]["parent"]="SOME_OTHER_UNVERIFIED_PARENT"
        with self.assertRaisesRegex(ValueError,"POINTER"):
            compare(d["OBS"],d["TREAT"])
        d=self.fresh();d["OBS"][3]["id"]=d["OBS"][2]["id"]
        with self.assertRaisesRegex(ValueError,"DUPLICATED"):
            compare(d["OBS"],d["TREAT"])

    def test_trace_censor_and_missing_source_fields_are_hold_or_error(self):
        d=self.fresh()
        d["TREAT"][2]["censored"]=True
        r=compare(d["OBS"],d["TREAT"])
        self.assertEqual(r["TREAT"]["status"],
                         "HOLD_CENSORED_TRACE_WITH_FINITE_PREFIX")
        d=self.fresh()
        del d["TREAT"][2]["state"]["pv"]
        with self.assertRaisesRegex(ValueError,"FULL_COMPUTATIONAL_STATE_FIELDS"):
            compare(d["OBS"],d["TREAT"])

    def test_unverified_passive_see_and_illegal_final_uci_are_hold(self):
        d=self.fresh()
        d["OBS"][2]["see_native_original_equals_delivered"]=False
        self.assertEqual(compare(d["OBS"],d["TREAT"])["OBS"]["status"],
                         "HOLD_SEE_CALL_NOT_PROVED_PASSIVE")
        d=self.fresh()
        d["TREAT"][-1]["legal_terminal_UCI"]=False
        self.assertEqual(compare(d["OBS"],d["TREAT"])["TREAT"]["status"],
                         "HOLD_NO_LEGAL_EXACT_FINAL_UCI_CERTIFICATE")

if __name__=="__main__":
    unittest.main(verbosity=2)
