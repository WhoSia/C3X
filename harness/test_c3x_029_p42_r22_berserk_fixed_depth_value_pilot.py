"""Separate Berserk depth protocol tests: do not lower prior node standard."""
import unittest,chess,chess.engine
from c3x_029_p42_r22_berserk_fixed_depth_value_pilot import quality,finalize

def sample(depth=16,nodes=2000,score=23,pv=None):
    return {"depth":depth,"nodes":nodes,"pv":pv or [chess.Move.from_uci("e7e5")],
            "score":chess.engine.PovScore(chess.engine.Cp(score),chess.WHITE)}
def candidate(root,cp):
    return {"root_uci":root,"depth_modes":{
      str(k):{"status":"DEPTH_CONTROLLED_FINITE_SEARCH_ONLY","root_mover_cp":cp,
              "actual_nodes":1500*k} for k in (12,16)}}
class DepthPilot(unittest.TestCase):
    def setUp(self):self.board=chess.Board();self.board.push_uci("e2e4")
    def test_actual_depth_and_cost_metadata(self):
        r=quality(self.board,sample(),16,chess.WHITE)
        self.assertEqual(r["status"],"DEPTH_CONTROLLED_FINITE_SEARCH_ONLY")
        self.assertEqual(r["actual_nodes"],2000)
    def test_wrong_side_score_viewpoint(self):
        self.assertEqual(quality(self.board,sample(),16,chess.BLACK)["root_mover_cp"],-23)
    def test_depth_not_reached_holds(self):
        self.assertEqual(quality(self.board,sample(depth=11),12,chess.WHITE)["status"],
                         "HOLD_DEPTH_UNDERREQUEST")
    def test_tiny_real_search_holds(self):
        self.assertEqual(quality(self.board,sample(nodes=3),16,chess.WHITE)["status"],
                         "HOLD_INSUFFICIENT_REAL_SEARCH")
    def test_illegal_pv_rejected(self):
        z=sample(pv=[chess.Move.from_uci("e2e4")])
        self.assertEqual(quality(self.board,z,16,chess.WHITE)["status"],"HOLD_ILLEGAL_PV")
    def test_mate_not_cp(self):
        z=sample();z["score"]=chess.engine.PovScore(chess.engine.Mate(2),chess.WHITE)
        self.assertEqual(quality(self.board,z,16,chess.WHITE)["status"],"HOLD_MATE_OR_NONCP")
    def test_bound_not_exact(self):
        z=sample();z["upperbound"]=True
        self.assertEqual(quality(self.board,z,16,chess.WHITE)["status"],"HOLD_BOUND_SCORE")
    def test_full_pair_valid_but_not_truth(self):
        row={"case_id":1,"event_family":"historical",
             "candidates":[candidate("e2e4",10),candidate("d2d4",20)]}
        out=finalize([row])
        self.assertEqual(out["eligible_pairs"],1)
        self.assertEqual(out["cases"][0]["depth16_margin_cp"],10)
        self.assertFalse(out["objective_chess_value_certified"])
        self.assertFalse(out["node_cost_equality_certified"])
    def test_one_ineligible_root_holds_pair(self):
        row={"case_id":1,"event_family":"historical",
             "candidates":[candidate("e2e4",10),candidate("d2d4",20)]}
        row["candidates"][0]["depth_modes"]["12"]["status"]="HOLD_DEPTH_UNDERREQUEST"
        self.assertEqual(finalize([row])["eligible_pairs"],0)
    def test_no_knowledge_of_global_best_move(self):
        row={"case_id":1,"event_family":"historical",
             "candidates":[candidate("e2e4",10),candidate("d2d4",20)]}
        out=finalize([row])
        self.assertFalse(out["pre_frozen_strategic_plan_beyond_PV_compared"])
        self.assertFalse(out["root_causal_source_mediation_certified"])
if __name__=="__main__":
    unittest.main()
