"""C3X 0.30/R1: numerical regression against 0.29 and extreme-softmax bug.

All data are mathematical fixtures, NOT observed chess source evaluations.
"""
import math
import unittest
from c3x_029_p42_r30_sarfa_section2_kernel import sarfa as old_sarfa
from c3x_030_r1_sarfa_logdomain import sarfa_logdomain, log_softmax, kl_from_log_probs


class OriginalFormulaAndNumericSafety(unittest.TestCase):
    def test_inherit_exact_normal_range_sarfa_scores(self):
        examples = [
            ({"a":2.0,"b":1.0,"c":0.0},
             {"a":0.0,"b":1.0,"c":0.0}, "a", 1.0),
            ({"a":0.0,"b":1.0,"c":3.0},
             {"a":-0.3,"b":2.0,"c":3.0}, "a", 100.0),
            ({"x":40,"y":10,"z":-100,"q":0},
             {"x":35,"y":12,"z":-99,"q":2}, "x", 100.0),
        ]
        for orig, changed, selected, t in examples:
            a=old_sarfa(orig, changed, selected, t)
            b=sarfa_logdomain(orig, changed, selected, t)
            self.assertAlmostEqual(
                a["sarfa_harmonic_saliency"],b["sarfa_harmonic_saliency"],places=11)
            self.assertAlmostEqual(
                a["offtarget_kl_perturbed_to_original"],
                b["offtarget_kl_perturbed_to_original"],places=11)

    def test_log_domain_recovers_large_but_finite_kl(self):
        o={"a":2.0,"b":0.0,"c":-1000.0}
        changed={"a":-1.0,"b":-1000.0,"c":0.0}
        old=old_sarfa(o,changed,"a")
        new=sarfa_logdomain(o,changed,"a")
        self.assertTrue(math.isinf(old["offtarget_kl_perturbed_to_original"]))
        self.assertTrue(math.isfinite(new["offtarget_kl_perturbed_to_original"]))
        self.assertAlmostEqual(new["offtarget_kl_perturbed_to_original"],1000.0)
        self.assertGreater(new["offtarget_relevance"],0.0)

    def test_shift_invariance_and_unchanged_relevance(self):
        old={"c":-3,"a":5,"b":0}
        altered={"c":-3,"a":1,"b":0}
        base=sarfa_logdomain(old,altered,"a")
        shifted=sarfa_logdomain({k:v+100000 for k,v in old.items()},
                                {k:v+100000 for k,v in altered.items()},"a")
        self.assertAlmostEqual(base["sarfa_harmonic_saliency"],
                               shifted["sarfa_harmonic_saliency"],places=10)
        self.assertAlmostEqual(base["offtarget_relevance"],1.0)
    
    def test_negative_delta_not_promoted(self):
        x=sarfa_logdomain({"a":1,"b":0,"c":0},{"a":2,"b":0,"c":0},"a")
        self.assertLess(x["specificity_delta_raw_signed"],0)
        self.assertEqual(x["sarfa_harmonic_saliency"],0.0)
    
    def test_shared_support_required(self):
        with self.assertRaisesRegex(ValueError,"FIXED_ACTION_SUPPORT"):
            sarfa_logdomain({"a":1,"b":2,"c":3},{"a":1,"b":2,"d":3},"a")

    def test_reject_boolean_numeric(self):
        with self.assertRaisesRegex(ValueError,"NONFINITE_INPUT"):
            sarfa_logdomain({"a":True,"b":2,"c":3},
                            {"a":2,"b":2,"c":3},"a")

    def test_reject_extreme_unrepresentable_q_spread(self):
        with self.assertRaisesRegex(ValueError,"UNREPRESENTABLE_Q_SPREAD"):
            sarfa_logdomain({"a":1e308,"b":-1e308,"c":0},
                            {"a":1e308,"b":-1e308,"c":0},"a")

    def test_temperature_guards(self):
        for t in (0,-1,math.inf,float("nan"),True):
            with self.assertRaisesRegex(ValueError,"TEMPERATURE"):
                sarfa_logdomain({"a":1,"b":2,"c":3},
                                {"a":2,"b":2,"c":3},"a",temperature=t)

    def test_kl_correct_direction(self):
        p=log_softmax([1,0],1)
        q=log_softmax([0,1],1)
        self.assertGreater(kl_from_log_probs(q,p),0)
        self.assertAlmostEqual(kl_from_log_probs(p,p),0.0,places=12)

    def test_no_chess_or_observation_claim(self):
        row=sarfa_logdomain({"a":1,"b":2,"c":3},
                            {"a":0,"b":2,"c":3},"a")
        self.assertTrue(row["no_chess_engine_or_physical_intervention"])
        self.assertTrue(row["not_a_new_attribution_method"])


if __name__=="__main__":
    unittest.main()
