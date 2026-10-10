#!/usr/bin/env python3
"""T1 exact native search state must be genuinely equal beyond board FEN."""
import sys,unittest,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_023_P1_R2_T1_native_search_state_matcher import whole,compare_original_treated

def event():
    return {"kind":"witness","root_call":8,"root_move":416,"key64":0x123,
      "parent_key64":0x55,"path_hash":99,"path_length":2,"path_exact":"55,123",
      "move":1029,"site":"quiet_prune","threshold":-95,
      "source_ply":6,"source_depth":3,"source_alpha":-20,"source_beta":21,
      "source_pv":0,"source_rule50":7,"source_occupancy64":123456,
      "occupied_is_output_arg":0,"input_occ_defined":1,
      "branch_prune_if_no_extra_capture_guard":1,
      "branch_direct_continuation":1,
      "original":0,"delivered":0,"altered":0}

def arm(ev,ordinal=30):
    return {"ordered_source_operator_trace":[{
         "source":"native_SEE","fields":ev,"line_ordinal":ordinal}],
         "native_see_events":[ev]}

class StrictSourceState(unittest.TestCase):
    def test_equal_full_measured_state_after_operator_source(self):
        a=arm(event());b=arm(event(),50)
        x=compare_original_treated(a,b,20,25)
        self.assertEqual(x["post_TT_full_search_window_state_matches"],1)
        self.assertEqual(x["status"],"POST_TT_COMPUTATIONAL_SEE_INPUT_WINDOW_MATCH")
        self.assertTrue(x["first_two_full_computational_match_candidates"][0]["source_legal_site_only"])
    def test_same_board_path_but_changed_search_window_not_exact(self):
        v=event();v["source_alpha"]=-19
        x=compare_original_treated(arm(event()),arm(v,50),20,25)
        self.assertEqual(x["post_TT_full_search_window_state_matches"],0)
        self.assertEqual(x["differences_by_field"]["DIFFERENT_source_alpha"],1)
        self.assertEqual(x["status"],"SAME_POSITION_PATH_DIFFERENT_COMPUTATIONAL_STATE")
    def test_early_SEE_cannot_mediate(self):
        x=compare_original_treated(arm(event(),8),arm(event(),9),10,15)
        self.assertEqual(x["post_TT_full_search_window_state_matches"],0)
        self.assertEqual(x["differences_by_field"]["BEFORE_TT_SOURCE_EVENT"],1)
    def test_repeated_SEE_source_not_uniquely_identified(self):
        e=event();a=arm(e)
        a["ordered_source_operator_trace"].append(
            {"source":"native_SEE","fields":e,"line_ordinal":40})
        x=compare_original_treated(a,arm(e,45),20,25)
        self.assertEqual(x["differences_by_field"]["DUPLICATE_SOURCE_IDENTITY"],1)
    def test_full_source_ancestor_path_not_hash_alone(self):
        e=event();e["path_exact"]="aa,123"
        with self.assertRaises(ValueError):whole(e)
        e=event();e["path_exact"]="55,999"
        with self.assertRaises(ValueError):whole(e)
    def test_same_state_different_native_SEE_boolean_is_fault(self):
        b=event();b["original"]=1;b["delivered"]=1
        with self.assertRaises(ValueError):
            compare_original_treated(arm(event()),arm(b,50),20,25)
    def test_capture_occupied_is_OUTPUT_and_must_not_be_dereferenced(self):
        e=event();e["site"]="capture_prune";e["occupied_is_output_arg"]=1
        self.assertIsNotNone(whole(e))
if __name__=="__main__":unittest.main()
