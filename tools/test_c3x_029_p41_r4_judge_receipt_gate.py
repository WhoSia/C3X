"""P41/R4: original 30-ply chess-history referee receipt gate tests."""
import copy
import unittest
import chess
from c3x_029_p41_r4_judge_receipt_gate import validate_judge_receipt

HISTORY="""c2c4 c7c5 g1f3 g8f6 b1c3 b8c6 e2e3 e7e6 d2d4 d7d5
c4d5 e6d5 f1b5 a7a6 b5c6 b7c6 e1g1 f8d6 d4c5 d6c5
c3a4 c5d6 d1c2 d8c7 h2h3 e8g8 b2b3 f6e4 c1b2 c8f5""".split()

def fixture():
    b=chess.Board()
    for u in HISTORY:b.push_uci(u)
    rootfen=b.fen()
    mover=b.turn
    selected=[]
    for _ in range(3):
        legal=sorted(m.uci() for m in b.legal_moves)
        selected.append(legal[0])
        b.push_uci(legal[0])
    return {"engine_family":"other-independent-engine",
        "verified_source_commit":"a"*40,
        "binary_sha256":"b"*64,
        "source_audit_verified":True,
        "original_chess_history_uci":HISTORY,
        "original_root_fen":rootfen,
        "candidate_root_uci":selected[0],
        "opponent_reply_uci":selected[1],
        "own_continuation_uci":selected[2],
        "evaluated_fen":b.fen(),
        "requested_nodes":96000,"actual_nodes":96000,"depth":12,
        "root_side_cp":35,"lowerbound":False,"upperbound":False,
        "root_mover_is_white":mover,
        "pv_uci":[]}

class ActualSourceEligibility(unittest.TestCase):
    def test_exact_30ply_legality_and_fen(self):
        x=validate_judge_receipt(fixture())
        self.assertEqual(x["score_interval_root_mover_cp"],{"lower":35,"upper":35})
        self.assertIn("NOT_INDEPENDENT_VALUE_TRUTH",x["status"])

    def test_old_shallow_2_to_5_nodes_rejected(self):
        for n in (2,5):
            with self.subTest(n=n):
                a=fixture();a["actual_nodes"]=n;a["depth"]=1
                with self.assertRaisesRegex(ValueError,"INSUFFICIENT_NODES"):
                    validate_judge_receipt(a)

    def test_wrong_board_and_illegal_continuation_rejected(self):
        a=fixture();a["evaluated_fen"]=chess.STARTING_FEN
        with self.assertRaisesRegex(ValueError,"JUDGE_FEN_MISMATCH"):
            validate_judge_receipt(a)
        a=fixture();a["own_continuation_uci"]="a1a8"
        with self.assertRaisesRegex(ValueError,"ILLEGAL_BRANCH"):
            validate_judge_receipt(a)

    def test_same_engine_family_cannot_be_independent(self):
        a=fixture();a["engine_family"]="stockfish"
        with self.assertRaisesRegex(ValueError,"NOT_INDEPENDENT_FAMILY"):
            validate_judge_receipt(a)

    def test_mate_and_conflicting_bounds_refused(self):
        a=fixture();a["root_side_mate"]=1
        with self.assertRaisesRegex(ValueError,"MATE_AS_CP"):
            validate_judge_receipt(a)
        a=fixture();a["lowerbound"]=True;a["upperbound"]=True
        with self.assertRaisesRegex(ValueError,"CONFLICTING_SCORE_BOUNDS"):
            validate_judge_receipt(a)

    def test_unverified_source_identity_rejected(self):
        a=fixture();a["source_audit_verified"]=False
        with self.assertRaisesRegex(ValueError,"SOURCE_NOT_AUDITED"):
            validate_judge_receipt(a)

    def test_lowerbound_retains_one_sided_interval(self):
        a=fixture();a["lowerbound"]=True
        r=validate_judge_receipt(a)
        self.assertEqual(r["score_interval_root_mover_cp"],{"lower":35,"upper":None})

if __name__=="__main__":
    unittest.main()
