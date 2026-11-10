"""R28-M2 tiny cross-game transfer contracts; all data synthetic."""
import copy
import unittest
from test_c3x_029_p42_r28_m1_fixed_binprop_nearby_negative_audit import synthetic_court
from c3x_029_p42_r28_m1_fixed_binprop_nearby_negative_audit import audit
from c3x_029_p42_r28_m2_nearby_negative_cross_game_transfer import (
    transport, classify, select_model)


def base():
    a, b = synthetic_court()
    return audit(a, b)


class CrossGameContract(unittest.TestCase):
    def test_two_disjoint_event_folds(self):
        result = transport(base())
        self.assertEqual(len(result["folds"]), 2)
        self.assertEqual({f["train_event"] for f in result["folds"]},
                         {f["diagnostic_test_event"] for f in result["folds"]})
        self.assertTrue(all(f["train_pairs"] == 6 and f["other_event_pairs"] == 6
                            for f in result["folds"]))

    def test_feature_orientation_has_no_tacit_inverse(self):
        pair = {"predicate_contrasts": {"x": {"positive": True, "negative": False}}}
        self.assertTrue(classify(pair, "x", 1))
        self.assertFalse(classify(pair, "x", -1))
        rev = {"predicate_contrasts": {"x": {"positive": False, "negative": True}}}
        self.assertFalse(classify(rev, "x", 1))
        self.assertTrue(classify(rev, "x", -1))

    def test_no_duplicate_prefixes(self):
        d = base()
        d["nearby_groups"][1]["rank1"] = d["nearby_groups"][0]["rank1"]
        with self.assertRaisesRegex(ValueError, "DUPLICATE_PREFIX"):
            transport(d)

    def test_historic_small_corpus_no_pvalue_claim(self):
        d = transport(base())
        self.assertTrue(d["not_independent_prospective_transport"])
        self.assertTrue(d["no_significance_or_causal_mediation_claim"])

    def test_reject_invalid_label(self):
        d = base()
        d["nearby_groups"][0]["positive_cp"] = -100000
        with self.assertRaisesRegex(ValueError, "INVERTED_SCORE"):
            transport(d)

    def test_reject_unadmitted_pair(self):
        d = base()
        d["nearby_groups"][0]["admitted_minimum_gap"] = False
        with self.assertRaisesRegex(ValueError, "INADMISSIBLE"):
            transport(d)

    def test_train_selection_excludes_test_leakage(self):
        a = [{"predicate_contrasts": {
            "first": {"positive": True, "negative": False},
            "second": {"positive": False, "negative": False}}}]
        b = [{"predicate_contrasts": {
            "first": {"positive": False, "negative": True},
            "second": {"positive": True, "negative": False}}}]
        selected, _ = select_model(a, ["first", "second"])
        self.assertEqual(selected["feature"], "first")
        self.assertEqual(selected["orientation"], 1)
        self.assertFalse(classify(b[0], selected["feature"], selected["orientation"]))


if __name__ == "__main__":
    unittest.main()
