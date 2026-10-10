#!/usr/bin/env python3
"""Tests: same SEE source path before selected TT use must NOT be called mediator."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev import (
    SELECTED,post_source_match,STUDY)
def see(ordinal):
    e={"kind":"witness","root_call":5,"root_move":31,"key64":22,
       "parent_key64":12,"path_hash":9,"path_length":4,"move":421,
       "site":"quiet_prune","threshold":-95,"original":0,"delivered":0,"altered":0}
    return {"source":"native_SEE","fields":e,"line_ordinal":ordinal},e
def obj(ordinal,tt=False):
    z,e=see(ordinal)
    src="physical_TT" if tt else "TT_value_used"
    k="reader_block" if tt else "used"
    t={"source":src,"line_ordinal":10,"fields":{
       "kind":k,"key64":54,"slot":0,"epoch":3,"root_call":5}}
    return {"ordered_source_operator_trace":[t,z],"native_see_events":[e]}
class CausalTemporalSources(unittest.TestCase):
    def setUp(self):
        self.role={"physical":{"key64":54,"slot":0,"epoch":3},
                   "root_calls":[5,6]}
    def test_after_both_real_source_events_is_eligible(self):
        r=post_source_match(obj(20),obj(50,True),self.role)
        self.assertEqual(r["strict_post_source_matches"],1)
        self.assertEqual(r["status"],"AFTER_NATIVE_TT_REAL_USE_COMMON_SOURCE_SEE_FOUND")
        self.assertFalse(r["claimed_natural_mediation"])
    def test_earlier_source_SEE_cannot_mediate(self):
        a=obj(9);v=obj(50,True)
        r=post_source_match(a,v,self.role)
        self.assertEqual(r["strict_post_source_matches"],0)
        self.assertEqual(r["status"],"NO_POST_TT_COMMON_SEE_IN_OBSERVED_SCOPE")
    def test_missing_real_native_use_or_actual_TT_block_HOLD(self):
        a=obj(40);a["ordered_source_operator_trace"]=a["ordered_source_operator_trace"][1:]
        r=post_source_match(a,obj(50,True),self.role)
        self.assertEqual(r["status"],"HOLD_NATIVE_TT_USE_OR_ACTUAL_SOURCE_BLOCK_MISSING")
    def test_fixed_six_development_outcome_selected_not_heldout(self):
        self.assertEqual(len(SELECTED),6)
        self.assertIn("POST_R1_DEVELOPMENT",STUDY)
    def test_play_trace_opt_in(self):
        s=(Path(__file__).resolve().parents[1]/"harness"/
            "c3x_018_native_TT_lineage_factorial_6_8.py").read_text()
        self.assertIn("ordered_source_trace=False",s)
        self.assertIn('answer["ordered_source_operator_trace"]=ordered',s)
if __name__=="__main__":unittest.main()
