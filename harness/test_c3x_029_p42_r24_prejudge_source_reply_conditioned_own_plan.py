"""R24/B pre-judge source policy tests; fake engine is never evidence."""
import unittest,chess
from c3x_029_p42_r24_prejudge_source_reply_conditioned_own_plan import (
 admit,freeze,DEPTH,SF_COMMIT
)
class Fake:
    def __init__(self):self.calls=0
    def analyse(self,board,limit,game,info):
        self.calls+=1
        return {"depth":DEPTH,"nodes":1100,
                "pv":[sorted(board.legal_moves,key=lambda m:m.uci())[0]]}
def tiny():
    board=chess.Board()
    return [({"case_id":"synthetic","event_family":"fake"},
             board,[{"root":"e2e4","replies":["e7e5","c7c5"]}])]
class R24FreezeTests(unittest.TestCase):
    def test_all_predefined_replies_selected_before_judge(self):
        eng=Fake();out=freeze(tiny(),eng)
        self.assertEqual(out["reply_conditioned_own_moves"],2)
        self.assertEqual(eng.calls,2)
        self.assertEqual(out["pre_reference_source_engine_commit"],SF_COMMIT)
        self.assertFalse(out["reference_score_used_to_generate_plan"])
    def test_admitted_move_is_current_turn_and_legal(self):
        bd=chess.Board()
        r=admit(bd,{"depth":12,"nodes":1234,"pv":[chess.Move.from_uci("e2e4")]})
        self.assertEqual(r["own_uci"],"e2e4")
    def test_early_depth_refused(self):
        with self.assertRaisesRegex(ValueError,"DEPTH_UNREACHED"):
            admit(chess.Board(),{"depth":11,"nodes":1000,"pv":[chess.Move.from_uci("e2e4")]})
    def test_no_actual_nodes_refused(self):
        with self.assertRaisesRegex(ValueError,"NODES_MISSING"):
            admit(chess.Board(),{"depth":12,"nodes":0,"pv":[chess.Move.from_uci("e2e4")]})
    def test_unphysical_boolean_nodes_refused(self):
        with self.assertRaisesRegex(ValueError,"NODES_MISSING"):
            admit(chess.Board(),{"depth":12,"nodes":True,"pv":[chess.Move.from_uci("e2e4")]})
    def test_illegal_own_move_refused(self):
        with self.assertRaisesRegex(ValueError,"ILLEGAL_OR_NO_PV"):
            admit(chess.Board(),{"depth":12,"nodes":50,"pv":[chess.Move.from_uci("e7e5")]})
    def test_empty_prediction_refused(self):
        with self.assertRaisesRegex(ValueError,"ILLEGAL_OR_NO_PV"):
            admit(chess.Board(),{"depth":12,"nodes":50,"pv":[]})
    def test_incorrect_reply_universe_is_not_invented(self):
        board=chess.Board()
        case=({"case_id":"fake","event_family":"fake"},board,
              [{"root":"e2e4","replies":["g1f3"]}])
        with self.assertRaises(ValueError):
            freeze([case],Fake())
    def test_frozen_policy_does_not_pretend_to_be_strong_cui_or_causal_c3x(self):
        x=freeze(tiny(),Fake())
        self.assertFalse(x["cui_k3_strong_baseline_claim"])
        self.assertFalse(x["c3x_native_causal_explanation_claim"])
        self.assertTrue(x["selection_is_post_R22_exploratory"])
    def test_total_own_plan_native_cost_is_reported(self):
        a=freeze(tiny(),Fake())["cases"][0]["root_candidates"][0]
        self.assertEqual(a["actual_source_nodes_total"],2200)
        self.assertEqual([x["opponent_reply"] for x in a["conditional_own_plan"]],["e7e5","c7c5"])
if __name__=="__main__":unittest.main()
