"""P42/R20 synthetic refuters: legal vs illegal original Stockfish16 root move.

Tests do not certify physical 2026 Game14; R20 always re-runs R18 and R19
with real original source, StageA hash and two cold Stockfish processes.
"""
import unittest
import chess
from c3x_029_p42_r20_source_native_legal_root_candidate_transport import (
 native_to_legal_uci,root_legal,classify
)

def integer(move):
    m=chess.Move.from_uci(move)
    return (m.from_square<<6)|m.to_square

def history(move):
    return [{"depth":i,"leader":integer(move),"score":-10,"average":-10}
            for i in range(1,13)]

def worlds():
    result={"A":history("e2e4"),"B":history("d2d4"),"C":history("e2e4"),
            "C_reverse":history("e2e4")}
    for d,m in ((9,"d2d4"),(10,"g1f3"),(11,"d2d4")):
        result["C_reverse"][d-1]["leader"]=integer(m)
    return result

def admitted():
    return {"status":"PASS_NATIVE_SOURCE_REVERSAL_CHANGED_INTERMEDIATE_ROOT_LEADER",
            "leader_changed_depths":[9,10,11]}

class R20RootCandidate(unittest.TestCase):
    def setUp(self):
        self.board=chess.Board()
    def test_original_native_legal_decoding(self):
        self.assertEqual(native_to_legal_uci(integer("e2e4"),self.board),"e2e4")
    def test_bad_nonlegal_move_is_not_leader(self):
        with self.assertRaisesRegex(ValueError,"NOT_LEGAL"):
            native_to_legal_uci(integer("e2e5"),self.board)
    def test_root_leader_zero_is_not_a_legal_move(self):
        with self.assertRaisesRegex(ValueError,"SPECIAL_OR_NONPOSITIVE"):
            native_to_legal_uci(0,self.board)
    def test_special_flag_is_not_silently_dropped(self):
        with self.assertRaisesRegex(ValueError,"SPECIAL_OR_NONPOSITIVE"):
            native_to_legal_uci(integer("e2e4")|(1<<14),self.board)
    def test_synthetic_real_candidate_return_and_third(self):
        result=classify(worlds(),admitted(),self.board)
        self.assertEqual(result["status"],"PASS_ACTUAL_NATIVE_LEGAL_ROOT_LEADER_CANDIDATE_TRANSPORT_ONLY")
        self.assertEqual(result["changed_root_leader_depths"],[9,10,11])
        self.assertEqual(result["first_original_B_recovery_depth"],9)
        self.assertEqual(result["third_candidate_emergence_depths"],[10])
        self.assertEqual(result["root_depths"][9]["C_reverse"],"g1f3")
        self.assertEqual(result["final_reversed_C_move"],"e2e4")
        self.assertFalse(result["independent_adversarial_future_reason_proved"])
    def test_unqualified_r19_provenance_is_hold(self):
        x=admitted();x["status"]="HOLD_NOT_NATIVE"
        self.assertEqual(classify(worlds(),x,self.board)["status"],
                         "HOLD_R19_ACTUAL_LEADER_EFFECT_NOT_ADMITTED")
    def test_wrong_declared_native_leader_changes_is_hold(self):
        x=admitted();x["leader_changed_depths"]=[9,11]
        self.assertEqual(classify(worlds(),x,self.board)["status"],
                         "HOLD_ROOT_INTERMEDIATE_SOURCE_RECHECK_DRIFT")
    def test_illegal_original_leader_is_hold(self):
        x=worlds();x["B"][1]["leader"]=integer("e2e5")
        self.assertEqual(classify(x,admitted(),self.board)["status"],
                         "HOLD_CHESS_ROOT_LEGALITY_OR_WORLD_MISSING")
    def test_missing_root_depth_is_hold(self):
        x=worlds();x["A"].pop()
        self.assertEqual(classify(x,admitted(),self.board)["status"],
                         "HOLD_CHESS_ROOT_LEGALITY_OR_WORLD_MISSING")
    def test_noninteger_move_is_hold(self):
        with self.assertRaisesRegex(ValueError,"SPECIAL_OR_NONPOSITIVE"):
            native_to_legal_uci(True,self.board)

if __name__=="__main__":
    unittest.main()
