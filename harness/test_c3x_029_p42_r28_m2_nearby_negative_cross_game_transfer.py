"""R28-M2 pure standard-library cross-game audit tests, no chess installation."""
import unittest
from c3x_029_p42_r28_m2_nearby_negative_cross_game_transfer import (
    transport, classify, select_model)

FEATURES = (
    "material_ahead", "material_not_behind", "bishop_pair",
    "rook_on_open_file", "rook_on_semi_open_file",
    "passed_pawn", "opponent_king_in_check", "has_queen")


def base():
    rows = []
    for event in ("Synthetic Sahel", "Synthetic Cerrado"):
        for i in range(6):
            row = {
                "event_family": event, "root_uci": "e2e4" if i < 3 else "d2d4",
                "rank1": i % 3 + 1,
                "admitted_minimum_gap": True, "gap_cp": 40,
                "positive_cp": 25, "nearby_negative_cp": -15,
                "shared_first_opponent_reply": "e7e5",
                "negative_second_opponent_reply": "g8f6",
                "predicate_contrasts": {}}
            for j, name in enumerate(FEATURES):
                pos = (i + j) % 2 == 0
                neg = (i + 2 * j) % 3 == 0
                row["predicate_contrasts"][name] = {"positive": pos, "negative": neg}
            rows.append(row)
    return {
        "schema": "c3x042-r28-m1-fixed-concept-nearby-negatives-v1",
        "status": "EXPLORATORY_FIXED_PREDICATE_NEARBY_NEGATIVE_AUDIT",
        "n_matched_first_reply_prefixes": 12,
        "n_admitted_positive_nearby_negative_pairs": 12,
        "feature_summaries": {x: {} for x in FEATURES},
        "nearby_groups": rows,
    }


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
