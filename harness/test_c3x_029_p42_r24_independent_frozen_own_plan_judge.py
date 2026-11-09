"""C3X R24-B2 falsification tests for strict source-before-judge and finite score."""
import unittest,chess
from c3x_029_p42_r24_independent_frozen_own_plan_judge import (
 source_policy,signed_gap,reduce_native,FROZEN_PLAN_SHA,PLAN_SCHEMA
)
GOOD="DEPTH_CONTROLLED_FINITE_SEARCH_ONLY"
def result(cp,nodes=1100):
    return {"status":GOOD,"root_mover_cp":cp,"actual_nodes":nodes}
def fake_cases():
    b=chess.Board()
    return [({"case_id":"X","event_family":"fake"},b,
             [{"root":"e2e4","replies":["c7c5","e7e5"]}])]
def frozen():
    return {"schema":PLAN_SCHEMA,
      "status":"FROZEN_BEFORE_INDEPENDENT_REFERENCE_OWN_ACTION_JUDGING",
      "reference_score_used_to_generate_plan":False,
      "selection_is_post_R22_exploratory":True,
      "reply_conditioned_own_moves":147,
      "cases":[{"case_id":"X","root_candidates":[
        {"root_uci":"e2e4","conditional_own_plan":[
          {"opponent_reply":"c7c5","own_uci":"g1f3","source_depth":12,"source_nodes":5000},
          {"opponent_reply":"e7e5","own_uci":"g1f3","source_depth":12,"source_nodes":5000}
        ]}]}]}
def source_rows():
    result=[]
    for reply,cost in (("c7c5",2),("e7e5",0)):
        modes={}
        for d in ("12","16"):
            modes[d]={"unrestricted":result_score(40+cost),
                      "frozen_policy":result_score(39+cost),
                      "signed_reference_gap_cp":1,
                      "unrestricted_pv_own_move":"g1f3"}
        result.append({"opponent_reply":reply,"frozen_own_move":"g1f3",**modes})
    return [{"case_id":"X","event_family":"fake",
             "roots":[{"root":"e2e4","source_plan_nodes":10000,"reply_results":result}]}]
def result_score(cp):
    return result(cp)
class R24Judge(unittest.TestCase):
    def test_freeze_contract_prejudged_action_admitted(self):
        x=source_policy(fake_cases(),frozen())
        self.assertEqual(len(x),1)
    def test_not_prejudged_weakens_admission(self):
        x=frozen();x["reference_score_used_to_generate_plan"]=True
        with self.assertRaisesRegex(ValueError,"PREJUDGE_POLICY_PROVENANCE"):
            source_policy(fake_cases(),x)
    def test_all_legal_reply_order_immutable(self):
        x=frozen();x["cases"][0]["root_candidates"][0]["conditional_own_plan"].reverse()
        with self.assertRaisesRegex(ValueError,"LEGAL_REPLY_FREEZE_DRIFT"):
            source_policy(fake_cases(),x)
    def test_illegal_post_reply_own_move_hold(self):
        x=frozen();x["cases"][0]["root_candidates"][0]["conditional_own_plan"][0]["own_uci"]="e7e5"
        with self.assertRaisesRegex(ValueError,"OWN_MOVE_ILLEGAL"):
            source_policy(fake_cases(),x)
    def test_wrong_root_id_hold(self):
        x=frozen();x["cases"][0]["root_candidates"][0]["root_uci"]="d2d4"
        with self.assertRaisesRegex(ValueError,"ROOT_ORDER"):
            source_policy(fake_cases(),x)
    def test_judge_gap_signed_not_clamped(self):
        self.assertEqual(signed_gap(result(30),result(40)),-10)
    def test_judge_absent_score_is_none(self):
        self.assertIsNone(signed_gap({"status":"HOLD_DEPTH"},result(35)))
    def test_complete_all_reply_policy_min_uses_frozen_scores(self):
        z=reduce_native(source_rows())
        r=z["cases"][0]["roots"][0]["depth_evaluations"]["16"]
        self.assertEqual(r["worst_frozen_plan_value_cp"],39)
        self.assertEqual(r["worst_unrestricted_judge_response_value_cp"],40)
        self.assertTrue(r["all_legal_reply_plan_scores_finite"])
        self.assertFalse(z["independent_chess_truth_proven"])
    def test_one_unqualified_reply_prevents_frozen_min_claim(self):
        src=source_rows();src[0]["roots"][0]["reply_results"][0]["16"]["signed_reference_gap_cp"]=None
        z=reduce_native(src)
        out=z["cases"][0]["roots"][0]["depth_evaluations"]["16"]
        self.assertFalse(out["all_legal_reply_plan_scores_finite"])
        self.assertNotIn("worst_frozen_plan_value_cp",out)
    def test_explicit_reference_source_sha_present(self):
        z=reduce_native(source_rows())
        self.assertEqual(z["prejudge_plan_sha256"],FROZEN_PLAN_SHA)
        self.assertFalse(z["cui_k3_or_binprop_strong_baseline_implemented"])
        self.assertFalse(z["prospective_heldout"])
if __name__=="__main__":unittest.main()
