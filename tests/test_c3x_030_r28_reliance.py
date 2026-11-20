"""Regression checks for R28 outcome eligibility and exact PV comparisons."""
import unittest

from c3x_030_r28_pv_check import fork_pairs
from c3x_030_r28_reliance import label
from c3x_030_r28_score_reliance import score


def item(item_id, verdict):
    return {"id": item_id, "judge": {"label": verdict},
            "recommendation": "e2e4", "alternative": "d2d4"}


class RelianceTests(unittest.TestCase):
    def test_distinct_eligibility_and_missing_outcomes(self):
        items = [item(str(i), verdict) for i, verdict in enumerate(
            ("agree", "reverse", "reverse", "reverse", "unresolved", "agree"))]
        choices = {"0": ("d2d4", "e2e4"), "1": ("d2d4", "d2d4"),
                   "2": ("d2d4", "e2e4"), "3": ("e2e4", "d2d4"),
                   "4": ("d2d4", "e2e4"), "5": ("e2e4", None)}
        result = score(items, {key: dict(zip(("pre", "post"), moves))
                               for key, moves in choices.items()})
        self.assertEqual(result["beneficial_adoption"]["rate"], 1.0)
        self.assertEqual(result["justified_retention"], {"count": 1, "eligible": 2, "rate": 0.5})
        self.assertEqual(result["harmful_adoption"]["rate"], 0.5)
        self.assertEqual(result["correct_reconsideration"]["rate"], 1.0)
        self.assertEqual(result["counts"]["incomplete"], 1)
        self.assertIsNone(result["supported_retention"]["rate"])

    def test_audit_demotion_keeps_responses_and_excludes_reliance_label(self):
        items = [item("a", "reverse"), item("b", "agree"), item("c", "reverse")]
        responses = {key: {"pre": "d2d4", "post": "e2e4"} for key in ("a", "b", "c")}
        audit = {key: {"label": value} for key, value in (("a", "unresolved"), ("b", "agree"))}
        result = score(items, responses, all_replies=audit)
        self.assertIsNone(result["harmful_adoption"]["rate"])
        self.assertEqual(result["beneficial_adoption"]["eligible"], 1)
        self.assertEqual(result["counts"]["complete"], 3)
        self.assertEqual(result["counts"]["unresolved"], 2)
        self.assertEqual(result["counts"]["unaudited"], 1)

    def test_unlisted_or_impossible_choice_rejected(self):
        for responses in ({"bad": {}}, {"a": {"pre": "e2e5"}}):
            with self.assertRaises(ValueError):
                score([item("a", "agree")], responses)

    def test_judge_threshold_uses_both_depths(self):
        for values, expected in (((25, 25), "agree"), ((-26, -25), "reverse"),
                                  ((-26, -24), "unresolved"), ((None, 80), "unresolved")):
            self.assertEqual(label(values), expected)

    def test_pv_fork_keeps_score_bound_state(self):
        first = {"move": "e2e4", "cp": 20, "upperbound": False, "lowerbound": False,
                 "depth": 10, "pv": ["e2e4", "e7e5"], "pv_san": ["e4", "e5"]}
        second = {**first, "depth": 12, "upperbound": True,
                  "pv": ["e2e4", "c7c5"], "pv_san": ["e4", "c5"]}
        self.assertEqual(fork_pairs([first, second])[0]["score_kinds"], ["point", "upperbound"])
        self.assertEqual(fork_pairs([first, {**second, "pv": ["d2d4", "c7c5"]}]), [])


if __name__ == "__main__":
    unittest.main()
