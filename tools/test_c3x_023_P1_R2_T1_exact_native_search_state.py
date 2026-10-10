#!/usr/bin/env python3
"""All sources: C++ three-layer overlay, same chess node not same alpha-beta."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_022_P2_R2_native_SEE_source_witness_overlay import patch as p0,ANCHORS
from c3x_023_P1_native_SEE_parent_path_key_overlay import patch as p1,MAIN,QS
from c3x_023_P1_R2_T1_native_full_search_state_overlay import patch as t1
from c3x_023_P1_R2_T1_exact_computational_SEE_comparator import temporal_common

FIELDS={"kind":"witness","site":"quiet_prune","key64":800,
        "parent_key64":700,"path_hash":1234,"path_length":3,"root_call":2,
        "root_move":45,"move":111,"threshold":-95,"original":1,
        "delivered":1,"altered":0,"t1_path":"600,700,800",
        "t1_ply":3,"t1_depth":2,"t1_alpha":-32,"t1_beta":14,
        "t1_pv":0,"t1_qsearch":0,"t1_rule50":3,
        "t1_occupied_present":0,"t1_occupied_out":0}
TARGET={"physical":{"key64":987,"slot":0,"epoch":4},"root_calls":[2,3]}

def obs(t1_overrides=None,see_line=40):
    z=dict(FIELDS);z.update(t1_overrides or {})
    score={"kind":"used","key64":987,"root_call":2}
    return {"native_see_events":[z],"ordered_source_operator_trace":[
      {"source":"TT_value_used","line_ordinal":10,"fields":score},
      {"source":"native_SEE","line_ordinal":see_line,"fields":z}]}
def treated(t1_overrides=None,see_line=45):
    z=dict(FIELDS);z.update(t1_overrides or {})
    block={"kind":"reader_block","key64":987,"root_call":2,"slot":0,"epoch":4}
    return {"native_see_events":[z],"ordered_source_operator_trace":[
      {"source":"physical_TT","line_ordinal":12,"fields":block},
      {"source":"native_SEE","line_ordinal":see_line,"fields":z}]}

class SourceState(unittest.TestCase):
    def test_chain_rejects_ambiguous_cpp_source_or_double_patch(self):
        src=('#include <algorithm>\nnamespace Stockfish {\n'+
            '\n'.join(a for a,b in ANCHORS)+'\n'+MAIN+'\n'+QS)
        base=p1(p0(src))
        result=t1(base)
        for field in ("t1_alpha","t1_beta","t1_path","t1_rule50",
                      "t1_occupied_out","c3x023_t1_current"):
            self.assertIn(field,result)
        self.assertEqual(result.count("C3X023_T1_Scope c3x023_t1_frame"),2)
        with self.assertRaises(ValueError):t1(result)
    def test_exact_native_comp_state_after_source(self):
        x=temporal_common(obs(),treated(),TARGET)
        self.assertEqual(x["status"],"EXACT_SEARCH_STATE_COMMON_SEE_AFTER_SOURCE")
        self.assertEqual(x["search_exact_common_events"],1)
        self.assertFalse(x["exact_state_events"][0]["natural_TT_SEE_mediation_proved"])
    def test_different_alpha_beta_even_with_same_board(self):
        x=temporal_common(obs(),treated({"t1_beta":22}),TARGET)
        self.assertEqual(x["search_exact_common_events"],0)
        self.assertEqual(x["reason_census"].get("SAME_CHESS_PATH_DIFFERENT_COMPUTATIONAL_WINDOW"),1)
    def test_different_exact_ancestor_vector_never_match(self):
        x=temporal_common(obs(),treated({"t1_path":"601,700,800"}),TARGET)
        self.assertEqual(x["search_exact_common_events"],0)
        self.assertEqual(x["reason_census"].get("SAME_HASH_DIFFERENT_EXACT_ANCESTRY"),1)
    def test_source_event_preceding_real_TT_source_not_mediator(self):
        x=temporal_common(obs(see_line=9),treated(),TARGET)
        self.assertEqual(x["reason_census"].get("PRE_TT_SOURCE_EVENT_NONMEDIATING"),1)
    def test_occupied_is_output_not_unobserved_input(self):
        x=temporal_common(obs(),treated({"t1_occupied_out":64}),TARGET)
        self.assertEqual(x["reason_census"].get("SAME_CALL_STATE_DIFFERENT_NATIVE_SEE_OCCUPANCY_OUTPUT"),1)
    def test_source_without_original_score_use_holds(self):
        x=obs();x["ordered_source_operator_trace"]=x["ordered_source_operator_trace"][1:]
        self.assertEqual(temporal_common(x,treated(),TARGET)["status"],
                         "HOLD_REAL_TT_SOURCE_USE_OR_BLOCK_MISSING")
if __name__=="__main__":unittest.main()
