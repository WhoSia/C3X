"""P36/R4 synthetic ranking uncertainty tests. No empirical result invented."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "harness"))
from c3x_029_p36_r4_march8_budget_stability import near_stability


def rec(pair=("a2a3","b2b3"), margin=12, discordance=False, pv1_upper=False):
    return {
        "two_candidate_search":[
            {"root_uci":pair[0], "score_lowerbound":False,"score_upperbound":pv1_upper},
            {"root_uci":pair[1], "score_lowerbound":False,"score_upperbound":False}
        ],
        "reported_root_order_discordant":discordance,
        "reported_pv1_minus_pv2_signed_cp":-margin if discordance else margin,
        "candidate_margin_cp":margin,
        "candidate_margin_stratum":"rank_unresolved" if discordance else (
            "near" if margin<20 else "intermediate"),
    }


class NativeBudgetStabilityTest(unittest.TestCase):
    def test_stable_exact_two_moves(self):
        x=near_stability(rec(),{48000:rec(margin=7),96000:rec(margin=11)})
        self.assertEqual(x["status"],"BUDGET_STABLE_NEAR_FINITE_DEPTH_ONLY")

    def test_pv1_bound_prevents_certification(self):
        x=near_stability(rec(),{48000:rec(),96000:rec(pv1_upper=True)})
        self.assertEqual(x["status"],"BUDGET_STABLE_NEAR_BUT_PV1_SCORE_BOUND_HOLD")

    def test_candidate_replacement_rejected(self):
        x=near_stability(rec(),{48000:rec(pair=("a2a3","c2c3")),96000:rec()})
        self.assertEqual(x["status"],"REJECTED_AS_BUDGET_STABLE_NEAR_CASE")

    def test_unchanged_pair_with_winner_flip_rejected(self):
        x=near_stability(rec(),{48000:rec(pair=("b2b3","a2a3")),96000:rec()})
        self.assertIn("48000:winner_changed",x["failure_reasons"])

    def test_inverted_native_score_order_rejected(self):
        x=near_stability(rec(),{48000:rec(discordance=True),96000:rec()})
        self.assertIn("48000:native_pv_order_discordant",x["failure_reasons"])

    def test_wide_margin_rejected(self):
        x=near_stability(rec(),{48000:rec(margin=21),96000:rec(margin=10)})
        self.assertIn("48000:not_near",x["failure_reasons"])


if __name__ == "__main__":
    unittest.main()
