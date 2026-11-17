"""Check legal reply contrasts, joined forecasts and abstentions."""

import unittest
from copy import deepcopy

from c3x_030_s4l_r12_reply_questions import fingerprint, freeze
from c3x_030_s4l_r12_explanation_score import score


class ReplyContrastTests(unittest.TestCase):
    def setUp(self):
        self.cohort = {"selection": [{"round": "1.1", "history": [], "roots": ["e2e4", "d2d4"]}]}
        self.questions = freeze(self.cohort, [{"round": "1.1", "reply": "g8f6"}])
        self.key = next(iter(self.questions))
        self.predictions = {"question_sha256": fingerprint(self.questions),
                            "forecasts": {self.key: {"pv": 1, "tree": -1, "trace": 1}}}
        self.judge = {"depth": 12, "rows": [{"round": "1.1", "roots": {
            root: {"g8f6": {"point": {"ordered": value, "bound": False, "depth": 12}}}
            for root, value in (("e2e4", 20), ("d2d4", 10))
        }}]}

    def test_fixed_reply_scoring(self):
        self.assertEqual(score(self.questions, self.predictions, self.judge)["paired_correct"],
                         {"pv": 1, "tree": 0, "trace": 1})

    def test_reply_legal_after_both_roots(self):
        bad = {"selection": [{"round": "1.1", "history": ["e2e4", "d7d5"],
                              "roots": ["e4d5", "e4e5"]}]}
        with self.assertRaises(ValueError):
            freeze(bad, [{"round": "1.1", "reply": "d5d4"}])

    def test_missing_trace_means_no_joint_score(self):
        self.predictions["forecasts"][self.key]["trace"] = None
        verdict = score(self.questions, self.predictions, self.judge)
        self.assertEqual(verdict["arm_coverage"], {"pv": 1, "tree": 1, "trace": 0})
        self.assertIsNone(verdict["paired_correct"])

    def test_uci_null_moves_are_not_game_moves(self):
        for target in ("history", "root", "reply"):
            cohort = deepcopy(self.cohort)
            request = {"round": "1.1", "reply": "g8f6"}
            case = cohort["selection"][0]
            if target == "history":
                case["history"] = ["0000", "0000"]
            elif target == "root":
                case["roots"][0] = "0000"
            else:
                request["reply"] = "0000"
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, "Null moves"):
                freeze(cohort, [request])

    def test_bound_or_stale_depth_abstains(self):
        for mutation in ({"bound": True}, {"depth": 11}):
            judge = deepcopy(self.judge)
            judge["rows"][0]["roots"]["e2e4"]["g8f6"]["point"].update(mutation)
            self.assertEqual(score(self.questions, self.predictions, judge)["judge_coverage"], 0)

    def test_question_changes_invalidate_forecast(self):
        self.questions[self.key]["reply"] = "g8h6"
        with self.assertRaisesRegex(ValueError, "frozen questions"):
            score(self.questions, self.predictions, self.judge)


if __name__ == "__main__":
    unittest.main()
