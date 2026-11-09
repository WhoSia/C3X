"""R23 historical two near-tie games: no non-exhaustive regret certificate."""
import unittest
from c3x_029_p42_r23_independent_all_opponent_reply_value_court import (
 sample_selection,reduce_reply_court,FROZEN_EXPLORATORY_CASES)

def r22():
    cases=[]
    for i in range(8):
        ids=list(FROZEN_EXPLORATORY_CASES)+[f"prior-{j}" for j in range(6)]
        margin=[0,6,65,52,74,63,66,208][i]
        cases.append({"case_id":ids[i],"both_technically_evaluable":True,
                      "depth16_margin_cp":margin})
    return {"schema":"c3x042-r22-berserk-independent-fixed-depth-feasibility-v1",
            "cases":cases}

def one_entry(hold=False):
    replies=[{"reply":r,"modes":{
      "12":{"status":"DEPTH_CONTROLLED_FINITE_SEARCH_ONLY","root_mover_cp":score,
            "actual_nodes":20000},
      "16":{"status":"HOLD_DEPTH_UNDERREQUEST" if hold and r=="a2a3"
            else "DEPTH_CONTROLLED_FINITE_SEARCH_ONLY",
            "root_mover_cp":score-1,"actual_nodes":200000}}}
        for r,score in (("a2a3",30),("b2b3",-10))]
    pair={"root":"e2e4","source_reply_values":replies,
          "frozen_forecasts":{"stockfish_pv":"b2b3",
                              "simple_json":"a2a3","c3x_legal_plan":None}}
    return {"case_id":"test","event_family":"original_historical",
            "pairs":[pair,pair]}

class IndependentWorstReplyPilot(unittest.TestCase):
    def test_exact_two_pinned_selection(self):
        self.assertEqual(sample_selection(r22()),FROZEN_EXPLORATORY_CASES)
    def test_r22_source_id_drift_is_hard_hold(self):
        q=r22();q["cases"][0]["case_id"]="some_other"
        with self.assertRaisesRegex(ValueError,"SELECTION_DRIFT"):
            sample_selection(q)
    def test_fewer_original_cases_holds(self):
        q=r22();q["cases"].pop()
        with self.assertRaisesRegex(ValueError,"SELECTION_DRIFT"):
            sample_selection(q)
    def test_all_legal_reply_complete_score_and_old_pv_hit(self):
        q=reduce_reply_court([one_entry()])
        self.assertEqual(q["complete_depth16_root_reply_sweeps"],2)
        r=q["cases"][0]["frozen_candidate_roots"][0]
        self.assertEqual(r["independent_min_after_opponent_reply_cp"]["16"],-11)
        self.assertEqual(r["minimizing_reply_uci"]["16"],["b2b3"])
        self.assertTrue(r["original_frozen_forecast_hits_if_complete"]["16"]["stockfish_pv"])
        self.assertFalse(q["independent_judge_is_objective_truth"])
        self.assertTrue(q["selection_by_R22_postoutcome_margin"])
    def test_one_missing_reply_prevents_universal_minimum(self):
        r=reduce_reply_court([one_entry(hold=True)])["cases"][0]["frozen_candidate_roots"][0]
        self.assertFalse(r["all_reply_depth_coverage"]["16"])
        self.assertIsNone(r["independent_min_after_opponent_reply_cp"]["16"])
        self.assertIsNone(r["original_frozen_forecast_hits_if_complete"]["16"])
    def test_actual_nodes_are_metered_per_depth(self):
        r=reduce_reply_court([one_entry()])["cases"][0]["frozen_candidate_roots"][0]
        self.assertEqual(r["total_actual_native_nodes_by_depth"]["12"],40000)
        self.assertEqual(r["total_actual_native_nodes_by_depth"]["16"],400000)
    def test_incorrect_frozen_shape_never_called_prospective(self):
        q=reduce_reply_court([one_entry()])
        self.assertFalse(q["prospective_new_game_cohort"])
        self.assertFalse(q["Cui_k3_or_BinProp_strong_baseline_compared"])
        self.assertFalse(q["root_source_mediation_certified"])
    def test_no_global_root_claim(self):
        self.assertFalse(reduce_reply_court([one_entry()])["global_root_decision_certified"])
if __name__=="__main__":
    unittest.main()
