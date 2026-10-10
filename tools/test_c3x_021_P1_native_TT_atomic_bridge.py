#!/usr/bin/env python3
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_021_P1_march_native_TT_atomic_bridge import (
    first_semantic_source_split,move_micro_comparison,root_depth_ladder
)

def candidate(value,move=1057,alpha=-100):
    return {"kind":"candidate","depth":4,"root_call":4,"trial":1,
            "move":move,"index":2,"alpha":alpha,"beta":alpha+20,
            "child_return":value,"root_nodes":11,"seq":1}

class P1NativeEvidenceFixtures(unittest.TestCase):
    def test_alpha_gate_requires_same_semantic_candidate(self):
        hit=first_semantic_source_split([candidate(-102)],[candidate(-98)])
        self.assertEqual(hit["kind"],"ALIGNED_CHILD_RETURN_DIFFERENCE")
        self.assertEqual(hit["gate_class"],"GATE_UP")
        self.assertEqual(hit["F_alpha_gate"],0)
        self.assertEqual(hit["V_alpha_gate"],1)
    def test_gate_other_direction(self):
        hit=first_semantic_source_split([candidate(-98)],[candidate(-102)])
        self.assertEqual(hit["gate_class"],"GATE_DOWN")
    def test_no_alignment_after_candidate_path_change(self):
        hit=first_semantic_source_split([candidate(-102)],[candidate(-98,move=1033)])
        self.assertEqual(hit["kind"],"PATH_DIVERGED_CANDIDATE_IDENTITY")
        self.assertNotIn("gate_class",hit)
    def test_strict_prefix_is_not_complete_equality(self):
        hit=first_semantic_source_split([candidate(-102)],[candidate(-102),candidate(-102)])
        self.assertEqual(hit["kind"],"TRACE_LENGTH_MISMATCH")
    def test_log_counter_not_a_chess_state(self):
        a=candidate(-100)
        b={**a,"root_nodes":999,"seq":542}
        hit=first_semantic_source_split([a],[b])
        self.assertEqual(hit["kind"],"TRACE_EQUAL")
    def test_action_join_uses_legal_uci_not_rootcall(self):
        m1={"move":"e2e4","native_move":796,"reply_legal_move_count":20,
            "reply_capture_count":0,"reply_check_count":0,
            "after_root_opponent_in_check":False,"reply_captures_destination":[],
            "attack_edge_added":[],"attack_edge_removed":[],
            "pin_added":[],"pin_removed":[],"occupied_target_attack_balance_delta":[]}
        m2={**m1,"move":"d2d4","native_move":731,"reply_legal_move_count":18,
            "attack_edge_added":[["P","d4","c5"]]}
        source={"profile":{"moves":[m1,m2],"legal_root_move_count":2}}
        out=move_micro_comparison("e2e4","d2d4",source)
        self.assertTrue(out["different_legal_reply_counts"])
        self.assertTrue(out["different_attacked_edge_gains"])
        self.assertTrue(out["same_board_different_root_move"])
        with self.assertRaises(RuntimeError):
            move_micro_comparison("e2e4","a7a5",source)
    def test_last_trial_of_each_depth(self):
        events=[]
        for depth in range(1,13):
            events.append({"kind":"after_sort","depth":depth,"first_move":12,
                           "value":depth,"trial":1})
        events.insert(5,{"kind":"after_sort","depth":5,"first_move":99,"value":9,"trial":2})
        d=root_depth_ladder(events)
        self.assertEqual(d["5"]["native_leader"],99)
        self.assertEqual(d["5"]["retry_count"],2)
        with self.assertRaises(RuntimeError):
            root_depth_ladder(events[:-1])
if __name__=="__main__":unittest.main()
