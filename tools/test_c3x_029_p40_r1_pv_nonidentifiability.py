"""P40/R1 logical identifiability tests, independent of chess engine."""
import unittest
from c3x_029_p40_r1_pv_nonidentifiability import (
    construct_world, exact_root_summary, adversarial_response_value,
    explicit_counterexample,
)


class P40ExactPvNonidentifiabilityTest(unittest.TestCase):
    def test_same_exact_transcript_opposite_offpv_contrasts(self):
        a = construct_world(2, 0)
        b = construct_world(0, 2)
        self.assertEqual(exact_root_summary(a), exact_root_summary(b))
        self.assertEqual(adversarial_response_value(a, "A", "r1"), 2)
        self.assertEqual(adversarial_response_value(b, "A", "r1"), 0)

    def test_exact_minimax_root_scores_not_approximations(self):
        for tree in (construct_world(2, 0), construct_world(0, 2)):
            result = exact_root_summary(tree)
            self.assertEqual(result["chosen_root"], "A")
            for root in ("A", "B"):
                self.assertEqual(result["candidates"][root]["root_value"], 0)
                self.assertEqual(result["candidates"][root]["single_pv"],
                                 [root, "r0", "u0"])

    def test_pv_nonidentifiability_persists_at_many_hidden_values(self):
        baseline = exact_root_summary(construct_world(0, 0))
        for i in range(0, 101):
            self.assertEqual(exact_root_summary(construct_world(i, 0)), baseline)
            self.assertEqual(exact_root_summary(construct_world(0, i)), baseline)

    def test_negative_offpv_values_change_observed_minimax_and_rejected(self):
        with self.assertRaisesRegex(ValueError, "OFFPV"):
            construct_world(-1, 0)

    def test_no_chess_embedding_or_forecast_claim(self):
        out = explicit_counterexample()
        self.assertEqual(out["G0_offpv_A_minus_B"], 2)
        self.assertEqual(out["G1_offpv_A_minus_B"], -2)
        self.assertIn("not", out["status"].lower())


if __name__ == "__main__":
    unittest.main()
