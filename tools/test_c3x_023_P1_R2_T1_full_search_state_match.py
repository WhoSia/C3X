#!/usr/bin/env python3
"""Exact SEE source search-window match: test contact, true state equality, mismatch."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_023_P1_R2_T1_full_computational_SEE_state_audit import match_full_state,FULL_STATE
def sample(ordinal,state_alpha=-30,kind="witness"):
    e={"kind":kind,"root_call":5,"root_move":31,"key64":22,
       "parent_key64":12,"path_hash":9,"path_length":4,"move":421,
       "site":"quiet_prune","threshold":-95,"original":0,"delivered":0,"altered":0,
       "state_ply":4,"state_depth":5,"state_alpha":state_alpha,"state_beta":2,
       "state_rule50":4,"state_occupied_given":0,"state_occupied64":0}
    return {"line_ordinal":ordinal,"source":"native_SEE","fields":e},e
def setup(ordinal,tt=False,alpha=-30):
    a,e=sample(ordinal,alpha)
    src={"source":"physical_TT" if tt else "TT_value_used",
         "line_ordinal":7,
         "fields":{"kind":"reader_block" if tt else "used","key64":17,
                   "root_call":5,"slot":1,"epoch":3}}
    return {"ordered_source_operator_trace":[src,a],"native_see_events":[e]}
ROLE={"physical":{"key64":17,"slot":1,"epoch":3},"root_calls":[5,6]}
class T1(unittest.TestCase):
    def test_true_search_window_equal_after_operator(self):
        x=match_full_state(setup(18),setup(20,True),ROLE)
        self.assertEqual(x["full_window_state_matches"],1)
        self.assertEqual(x["different_state_after_TT"],0)
        self.assertTrue(x["equal_chess_source_and_window_is_not_natural_mediation_proof"])
    def test_same_position_not_same_search_window(self):
        x=match_full_state(setup(18),setup(20,True,alpha=-29),ROLE)
        self.assertEqual(x["full_window_state_matches"],0)
        self.assertEqual(x["different_state_after_TT"],1)
        self.assertEqual(x["mismatch_fields"]["state_alpha"],1)
    def test_source_BEFORE_selected_TT_does_not_count(self):
        x=match_full_state(setup(6),setup(20,True),ROLE)
        self.assertEqual(x["path_after_TT"],0)
    def test_invalid_missing_native_field_is_blocked(self):
        a=setup(18);del a["ordered_source_operator_trace"][1]["fields"]["state_beta"]
        b=setup(20,True)
        with self.assertRaises(ValueError):match_full_state(a,b,ROLE)
    def test_all_required_native_context_fields(self):
        self.assertEqual(len(FULL_STATE),7)
if __name__=="__main__":unittest.main()
