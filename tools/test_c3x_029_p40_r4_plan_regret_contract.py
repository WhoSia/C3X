import unittest
from c3x_029_p40_r4_plan_regret_contract import evaluate_plan

def entry(legal,plan):
    return {"legal":{k:{"lower":v[0],"upper":v[1]} for k,v in legal.items()},
            "plan":plan}

class FuturePlanCostContract(unittest.TestCase):
    def test_nontrivial_plan_low_regret_with_all_replies(self):
        cases={"r0":entry({"a":(30,30),"b":(25,25)},["a"]),
               "r1":entry({"a":(10,10),"b":(12,12)},["a"])}
        out=evaluate_plan(cases,2,epsilon=5,verified_judge=False)
        self.assertEqual(out["decision"],"LOW_REGRET_CERTIFIED")
        self.assertEqual(out["judge"],"HOLD_UNVERIFIED")
        self.assertEqual(out["scope"],"ALL_LEGAL")

    def test_sampled_responses_cannot_prove_all_reply_low_regret(self):
        out=evaluate_plan({"r0":entry({"a":(30,30),"b":(25,25)},["a"])},
                          5,epsilon=5)
        self.assertEqual(out["decision"],"UNRESOLVED")
        self.assertEqual(out["scope"],"SAMPLED")

    def test_single_reply_can_refute_high_regret(self):
        out=evaluate_plan({"r1":entry({"a":(10,10),"b":(40,40)},["a"])},
                          5,epsilon=5,verified_judge=True)
        self.assertEqual(out["decision"],"HIGH_REGRET_WITNESS")
        self.assertEqual(out["judge"],"VERIFIED")

    def test_overlapping_score_bounds_require_abstention(self):
        out=evaluate_plan({"r0":entry({"a":(15,15),"b":(10,50)},["a"])},
                          1,epsilon=10,verified_judge=True)
        self.assertEqual(out["decision"],"UNRESOLVED")

    def test_all_legal_plan_cannot_get_tautological_zero(self):
        with self.assertRaisesRegex(ValueError,"TRIVIAL_ALL_LEGAL_PLAN"):
            evaluate_plan({"r0":entry({"a":(1,1),"b":(2,2)},["a","b"])},1)

    def test_empty_plan_is_availability_failure_not_zero_regret(self):
        out=evaluate_plan({"r0":entry({"a":(1,1),"b":(2,2)},[])},
                          1)
        self.assertEqual(out["decision"],"PLAN_UNAVAILABLE")

    def test_illegal_plan_choice_is_invalid(self):
        with self.assertRaisesRegex(ValueError,"INVALID_PLAN"):
            evaluate_plan({"r0":entry({"a":(1,1)},["c"])},1)

    def test_all_unknown_scores_must_not_certify_low_regret(self):
        out=evaluate_plan({"r0":entry({"a":(None,None),"b":(None,None)},["a"])},1,epsilon=10,verified_judge=True)
        self.assertEqual(out["decision"],"UNRESOLVED")
        self.assertEqual(out["regret_by_response"][0]["lower"],0)
        self.assertEqual(out["regret_by_response"][0]["upper"],float("inf"))

    def test_nan_and_inverted_infinite_intervals_rejected(self):
        for interval in ((float("nan"),12),(1,float("nan")),(float("inf"),None),(None,float("-inf"))):
            with self.subTest(interval=interval):
                with self.assertRaisesRegex(ValueError,"BAD_INTERVAL"):
                    evaluate_plan({"r0":entry({"a":interval,"b":(1,1)},["a"])},1)

    def test_judge_provenance_is_orthogonal_to_logical_result(self):
        row={"r0":entry({"a":(5,5),"b":(1,1)},["a"])}
        r=evaluate_plan(row,1,epsilon=1,verified_judge=False)
        self.assertEqual(r["decision"],"LOW_REGRET_CERTIFIED")
        self.assertEqual(r["scientific_status"],"HOLD_NO_INDEPENDENT_VALUE_JUDGE")

    def test_invalid_score_interval_cannot_pass(self):
        with self.assertRaisesRegex(ValueError,"BAD_INTERVAL"):
            evaluate_plan({"r0":entry({"a":(20,10),"b":(8,8)},["a"])},1)


if __name__=="__main__":
    unittest.main()
