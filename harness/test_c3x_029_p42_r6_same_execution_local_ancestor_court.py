"""C3X P42/R6 old C3b + new actual-key local witness join tests.

Synthetic event data only: NOT native Stockfish validation or causal mediation.
"""
import unittest
from c3x_029_p42_r6_same_execution_local_ancestor_court import (
    joint_court, parse_original_native
)
from test_c3x_029_p42_r5_game14_local_spine_court import trace

def c3b_run(*,root_call=7,parent_score=44,root_move=344,
            source_key=9876,full=True):
    events=[
        ("ANCESTOR_SNAPSHOT",1,source_key,776,0,11),
        ("CHILD_VALUE_RETURNED",1,12345,776,parent_score,11),
        ("PARENT_CANDIDATE_VALUE",1,source_key,776,parent_score,11),
        ("FRAME_RETURN",1,source_key,776,parent_score,11),
        ("PARENT_CANDIDATE_VALUE",0,7890,root_move,-parent_score,22),
        ("ROOT_FRAME_RETURN",0,7890,root_move,-parent_score,22),
    ]
    if not full:
        events=events[:-1]
    lines=[]
    for sequence,(event,ply,key,move,value,frame) in enumerate(events,1):
        lines.append(
            f"event={event} sequence={sequence} root_call={root_call} "
            f"ply={ply} key64={key} native_move={move} "
            f"value={value} frame_id={frame}"
        )
    return "\n".join(lines)+"\n"

class R6JointTests(unittest.TestCase):
    def test_full_synthetic_join_is_only_observational(self):
        outcome=joint_court(c3b_run()*2,trace()*2)
        self.assertEqual(outcome["status"],
                         "PASS_JOINT_SOURCE_LOCAL_AND_OBSERVED_ROOT_CANDIDATE_ONLY")
        self.assertEqual(outcome["source_c3b_candidate_edges"],[2,2])
        self.assertFalse(outcome["root_causation_certified"])
        self.assertFalse(outcome["natural_mediation_certified"])
        self.assertFalse(outcome["chess_strategic_semantics_verified"])
    def test_original_c3b_has_partial_path(self):
        result=joint_court(c3b_run(full=False)*2,trace()*2)
        self.assertTrue(result["status"].startswith("HOLD_ORIGINAL_C3B_"))
    def test_root_candidate_is_new_move(self):
        result=joint_court(c3b_run(root_move=999)*2,trace()*2)
        self.assertEqual(result["status"],"HOLD_UNRESTRICTED_ROOT_CANDIDATE_ID_MISMATCH")
    def test_parent_return_score_not_same(self):
        result=joint_court(c3b_run(parent_score=50)*2,trace()*2)
        self.assertEqual(result["status"],"HOLD_SAME_EXECUTION_PARENT_NATIVE_VALUE_DIVERGENCE")
    def test_full_game_source_identity_mismatch(self):
        result=joint_court(c3b_run(source_key=99)*2,trace()*2)
        self.assertEqual(result["status"],"HOLD_SAME_EXECUTION_GUARD_SOURCE_ID_DRIFT")
    def test_wrong_root_call_mismatch(self):
        result=joint_court(c3b_run(root_call=8)*2,trace()*2)
        self.assertEqual(result["status"],"HOLD_SAME_EXECUTION_GUARD_SOURCE_ID_DRIFT")
    def test_missing_cold_replay(self):
        result=joint_court(c3b_run(),trace()*2)
        self.assertEqual(result["status"],"HOLD_COLD_REPLAY_GROUP_COUNT_MISMATCH")
    def test_local_missing_child_is_rejected(self):
        result=joint_court(c3b_run()*2,trace(omit_child=True)*2)
        self.assertEqual(result["status"],"HOLD_LOCAL_ORIGINAL_BRANCH_NOT_CERTIFIED")
    def test_old_source_frame_event_parser_is_separate_from_root_boundary(self):
        mixed=c3b_run()+"event=ROOT_BOUNDARY depth=1 leader=344 score=4\n"
        groups=parse_original_native(mixed)
        self.assertEqual(len(groups),1)
        self.assertEqual(len(groups[0]),6)
    def test_unknown_native_c3b_number_rejected(self):
        with self.assertRaisesRegex(ValueError,"NONNUMERIC"):
            parse_original_native(c3b_run().replace("frame_id=11","frame_id=no"))

if __name__=="__main__":
    unittest.main()
