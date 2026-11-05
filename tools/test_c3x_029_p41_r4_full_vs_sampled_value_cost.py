"""Synthetic P41/R4 resource gate; no chess engine outcome."""
import unittest
from c3x_029_p41_r4_full_vs_sampled_value_cost import estimate


def sample():
    worlds=[]
    for i in range(16):
        branches=[{"opponent_reply":str(j),"own_legal_reply_count":20+j}
                  for j in range(4)]
        worlds.append({"branches":branches,
                       "expanded_legal_moves":1+4+sum(x["own_legal_reply_count"] for x in branches)})
    return {"game_events":8,"candidate_worlds":16,
            "cases":[{"worlds":worlds[i:i+2]} for i in range(0,16,2)]}


class CostEvidenceNotValueTest(unittest.TestCase):
    def test_observed_branch_arithmetic(self):
        d=estimate(sample())
        self.assertEqual(d["observed_legal_opponent_replies"],64)
        self.assertEqual(d["observed_legal_own_followups"],16*(20+21+22+23))
        self.assertEqual(d["sampled_opponent_branches"],48)
        self.assertEqual(d["sampled_own_followups"],144)

    def test_node_cost_is_hypothetical_not_measured(self):
        d=estimate(sample())
        self.assertEqual(d["hypothetical_sampled_leaf_requested_nodes"],144*96000)
        self.assertGreater(d["hypothetical_full_leaf_requested_nodes"],
                           d["hypothetical_sampled_leaf_requested_nodes"])
        self.assertIn("not a native engine measurement",d["limits"])

    def test_tampered_expansion_count_fails(self):
        x=sample()
        x["cases"][0]["worlds"][0]["expanded_legal_moves"]-=1
        with self.assertRaises(AssertionError):
            estimate(x)

    def test_missing_world_fails(self):
        x=sample()
        x["cases"].pop()
        with self.assertRaises(AssertionError):
            estimate(x)

    def test_invalid_budget_spec_fails(self):
        with self.assertRaises(AssertionError):
            estimate(sample(),reference_nodes=0)


if __name__=="__main__":
    unittest.main()
