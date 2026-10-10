#!/usr/bin/env python3
"""R3 observed native SEE post-source activation is not global event extinction."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
import chess
from c3x_023_P1_R3_native_SEE_activation_frontier_chess_exchange_bridge import (
    categorized,root_exchange,T1_SHA)
def ev(key=10,window=0,site="quiet_prune",ordinal=60):
    fields={"kind":"witness","root_call":7,"root_move":23,
       "key64":key,"parent_key64":3,"path_hash":99,"path_length":2,
       "path_exact":"3,"+format(key,"x"),"move":21,
       "site":site,"threshold":-40,"source_ply":5,"source_depth":4,
       "source_alpha":window,"source_beta":100,"source_pv":0,
       "source_rule50":3,"source_occupancy64":776,
       "occupied_is_output_arg":0,"input_occ_defined":1,
       "branch_prune_if_no_extra_capture_guard":0,
       "branch_direct_continuation":1,
       "original":1,"delivered":1,"altered":0}
    return {"source":"native_SEE","fields":fields,"line_ordinal":ordinal}
def obj(rows,cap=False):
    return {"ordered_source_operator_trace":rows,
            "native_see_events":[x["fields"] for x in rows]+
                                ([{"kind":"censored"}] if cap else [])}
class R3(unittest.TestCase):
    def test_shared_state_and_one_sided_after_TT(self):
        a=obj([ev(10),ev(11)])
        b=obj([ev(10),ev(12)])
        x=categorized(a,b,20,20)
        self.assertEqual(x["same_full_source_state_post_TT_both_arms_count"],1)
        self.assertEqual(x["original_only_post_TT_prefix_native_SEE_states"],1)
        self.assertEqual(x["TT_FIRST_only_post_TT_prefix_native_SEE_states"],1)
        self.assertEqual(x["original_only_site_counts"]["quiet_prune"],1)
    def test_same_chess_node_different_alpha_is_state_divergence(self):
        x=categorized(obj([ev(10,window=0)]),
                      obj([ev(10,window=1)]),20,20)
        self.assertEqual(x["same_full_source_state_post_TT_both_arms_count"],0)
        self.assertEqual(x["source_path_same_but_search_state_different_original_events"],1)
    def test_pre_vs_post_temporal_migration(self):
        x=categorized(obj([ev(10,ordinal=30)]),
                      obj([ev(10,ordinal=5)]),20,20)
        self.assertEqual(x["post_in_one_but_PRE_TT_in_other_original_events"],1)
    def test_censored_count_is_not_global_absence(self):
        x=categorized(obj([ev(10)],True),obj([]),20,20)
        self.assertTrue(x["first32_source_observation_censored"])
        self.assertTrue(x["DO_NOT_CLAIM_ABSENT_UNSEEN_PATH"])
    def test_chess_direct_legal_recapture_distinct_from_pseudo_attack(self):
        b=chess.Board()
        x=root_exchange(b,"e2e4")
        self.assertEqual(x["immediate_legal_capture_of_moved_piece_count"],0)
        self.assertGreater(x["opponent_legal_response_count"],0)
    def test_frozen_T1_replay_SHA(self):
        self.assertEqual(T1_SHA,
         "1975a515755e31a4c9445239750bde88211a13c328f667d86cabba2ce58effeb")
if __name__=="__main__":unittest.main()
