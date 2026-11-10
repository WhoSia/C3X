"""R30 SARFA exact-section-2 numerical and epistemic contracts (stdlib)."""
import math
import unittest
from c3x_029_p42_r30_sarfa_section2_kernel import sarfa


class SarfaMathContracts(unittest.TestCase):
    def setUp(self):
        self.o = {"a": 2.0, "b": 1.0, "c": 0.0}

    def test_selected_action_drop_and_fixed_other_probabilities(self):
        x = sarfa(self.o, {"a": 0.0, "b": 1.0, "c": 0.0}, "a")
        self.assertGreater(x["specificity_delta_raw_signed"], 0.0)
        self.assertAlmostEqual(x["offtarget_kl_perturbed_to_original"], 0.0, places=14)
        self.assertAlmostEqual(x["offtarget_relevance"], 1.0)
        d = x["specificity_delta_raw_signed"]
        self.assertAlmostEqual(x["sarfa_harmonic_saliency"], 2 * d / (1 + d))

    def test_global_shift_cancels(self):
        v = sarfa(self.o, {k: x + 100 for k, x in self.o.items()}, "a")
        self.assertAlmostEqual(v["specificity_delta_raw_signed"], 0.0, places=12)
        self.assertAlmostEqual(v["sarfa_harmonic_saliency"], 0.0, places=12)

    def test_offtarget_only_change_is_suppressed(self):
        x = sarfa(self.o, {"a": 2.0, "b": 9.0, "c": -9.0}, "a")
        self.assertGreater(x["offtarget_kl_perturbed_to_original"], 0)
        self.assertLess(x["offtarget_relevance"], 1)

    def test_selected_improvement_is_not_signed_saliency(self):
        x = sarfa(self.o, {"a": 5.0, "b": 1.0, "c": 0.0}, "a")
        self.assertLess(x["specificity_delta_raw_signed"], 0)
        self.assertEqual(x["sarfa_harmonic_saliency"], 0)
        self.assertEqual(x["status"], "NO_POSITIVE_SELECTED_ACTION_DROP")

    def test_action_order_invariance(self):
        a = sarfa(self.o, {"a": 0, "b": 1, "c": 0}, "a")
        b = sarfa({"c": 0, "b": 1, "a": 2}, {"c": 0, "a": 0, "b": 1}, "a")
        self.assertEqual(a["sarfa_harmonic_saliency"], b["sarfa_harmonic_saliency"])

    def test_temperature_matters_and_is_declared(self):
        a = sarfa(self.o, {"a": 0, "b": 1, "c": 0}, "a", temperature=1)
        b = sarfa(self.o, {"a": 0, "b": 1, "c": 0}, "a", temperature=100)
        self.assertGreater(a["sarfa_harmonic_saliency"], b["sarfa_harmonic_saliency"])

    def test_fail_support_mismatch(self):
        with self.assertRaisesRegex(ValueError, "SUPPORT"):
            sarfa(self.o, {"a": 2, "b": 1, "d": 0}, "a")

    def test_fail_only_two_moves(self):
        with self.assertRaisesRegex(ValueError, "SUPPORT"):
            sarfa({"a": 1, "b": 0}, {"a": 0, "b": 0}, "a")

    def test_fail_invalid_temperature_and_nonfinite_q(self):
        with self.assertRaisesRegex(ValueError, "TEMPERATURE"):
            sarfa(self.o, self.o, "a", temperature=0)
        with self.assertRaisesRegex(ValueError, "NONFINITE"):
            sarfa(self.o, {"a": math.inf, "b": 1, "c": 0}, "a")

    def test_extreme_logit_scale_no_overflow(self):
        x = sarfa({"a": 10000, "b": 9999, "c": -9999},
                  {"a": 9999, "b": 10000, "c": -9999}, "a")
        self.assertTrue(math.isfinite(x["sarfa_harmonic_saliency"]))


if __name__ == "__main__":
    unittest.main()
