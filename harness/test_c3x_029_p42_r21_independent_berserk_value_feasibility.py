"""Synthetic safety boundaries for R21 cross-family value feasibility only."""
import unittest
import chess
import chess.engine
from c3x_029_p42_r21_independent_berserk_value_feasibility import reference_info,summarize

def info(nodes=96000,depth=9,cp=32,pv=None):
    return {"nodes":nodes,"depth":depth,
       "score":chess.engine.PovScore(chess.engine.Cp(cp),chess.WHITE),
       "pv":[chess.Move.from_uci("e7e5")] if pv is None else pv}
def pair(cp1,cp2):
    return {"case_id":"synthetic","event_family":"TEST",
      "candidate_pairs":[{"root_uci":root,
         "budgets":{"48000":dict(status="ELIGIBLE_FINITE_INDEPENDENT_ENGINE_SEARCH",
                 actual_nodes=48000,depth=5,root_mover_cp=cp,lowerbound=False,upperbound=False),
                 "96000":dict(status="ELIGIBLE_FINITE_INDEPENDENT_ENGINE_SEARCH",
                 actual_nodes=96000,depth=8,root_mover_cp=cp,lowerbound=False,upperbound=False)}}
       for root,cp in (("e2e4",cp1),("d2d4",cp2))]}

class IndependentFamilyGate(unittest.TestCase):
    def setUp(self):
        self.board=chess.Board();self.board.push_uci("e2e4")
    def test_actual_native_nonshallow_value(self):
        r=reference_info(self.board,info(),96000,True)
        self.assertEqual(r["status"],"ELIGIBLE_FINITE_INDEPENDENT_ENGINE_SEARCH")
        self.assertEqual(r["root_mover_cp"],32)
    def test_wrong_point_of_view_flips_sign(self):
        r=reference_info(self.board,info(),96000,False)
        self.assertEqual(r["root_mover_cp"],-32)
    def test_early_stop_must_hold(self):
        r=reference_info(self.board,info(nodes=6,depth=1),96000,True)
        self.assertEqual(r["status"],"HOLD_INSUFFICIENT_REAL_NODES")
    def test_shallow_depth_must_hold(self):
        self.assertEqual(reference_info(self.board,info(depth=1),96000,True)["status"],
                         "HOLD_SHALLOW_REFEREE")
    def test_broken_native_pv_holds(self):
        self.assertEqual(reference_info(self.board,info(pv=[chess.Move.from_uci("e2e4")]),96000,True)["status"],
                         "HOLD_ILLEGAL_NATIVE_PV")
    def test_mate_not_fabricated_as_cp(self):
        t=info();t["score"]=chess.engine.PovScore(chess.engine.Mate(2),chess.WHITE)
        self.assertEqual(reference_info(self.board,t,96000,True)["status"],
                         "HOLD_MATE_OR_MISSING_SCORE")
    def test_native_none_nodes_holds(self):
        t=info();t.pop("nodes")
        self.assertEqual(reference_info(self.board,t,96000,True)["status"],
                         "HOLD_INSUFFICIENT_REAL_NODES")
    def test_technical_finite_near_tie_is_not_chess_truth(self):
        r=summarize([pair(12,14)])
        self.assertEqual(r["technically_eligible_pairs"],1)
        self.assertEqual(r["eligible_exploratory_near_tie_pairs"],1)
        self.assertFalse(r["judge_is_objective_chess_truth"])
        self.assertFalse(r["new_game_event_prospective_cohort"])
    def test_broad_margin_not_selected(self):
        r=summarize([pair(-70,70)])
        self.assertEqual(r["eligible_exploratory_near_tie_pairs"],0)
        self.assertEqual(r["all_frozen_cases"],1)
    def test_frozen_two_candidate_requirement(self):
        a=pair(0,2);a["candidate_pairs"].pop()
        with self.assertRaisesRegex(ValueError,"FROZEN_PAIR"):
            summarize([a])
    def test_one_missing_referee_excludes_entire_pair(self):
        x=pair(0,2)
        x["candidate_pairs"][0]["budgets"]["48000"]["status"]="HOLD_INSUFFICIENT_REAL_NODES"
        report=summarize([x])
        self.assertEqual(report["technically_eligible_pairs"],0)
        self.assertIsNone(report["cases"][0]["cp_margin_96k"])
    def test_score_bounds_do_not_form_exacts(self):
        x=pair(0,2)
        x["candidate_pairs"][0]["budgets"]["96000"]["upperbound"]=True
        r=summarize([x])
        self.assertEqual(r["technically_eligible_pairs"],0)

if __name__=="__main__":
    unittest.main()
