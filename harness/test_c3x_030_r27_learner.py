"""Regression tests for legal witnesses and withheld learner answers."""
import unittest

import chess

from c3x_030_r27_learner_items import training_reply_items
from c3x_030_r27_learner_packet import assessment_html, lesson_html, score

BASE = "4r1k1/1pq2p1p/2p1rnp1/p1B5/2P1p1P1/PP3P1P/2BR1Q2/4R1K1 b - - 0 31"


class R27LearnerTests(unittest.TestCase):
    def setUp(self):
        near = training_reply_items(chess.Board(BASE))
        self.items = {"near": {"N1": near[0], "N2": near[1]}, "transfer": {}}

    def test_one_new_branch_preserves_legal_recapture(self):
        self.assertEqual(self.items["near"]["N1"]["witnesses"],
                         {"b3b4": ["b4", "Nxc5", "bxc5"]})
        self.assertFalse(self.items["near"]["N2"]["witnesses"])

    def test_scoring_requires_a_witness_and_reports_missing(self):
        self.assertEqual(score(self.items, {})["near"]["items"]["N1"]["verdict"], "missing")
        response = {"N1": {"verdict": "yes", "move": "b4"}, "N2": {"verdict": "no"}}
        self.assertEqual(score(self.items, response)["near"]["correct"], 2)
        for move in ("bxa4", "bxa4+", "", "zz9"):
            response["N1"]["move"] = move
            self.assertEqual(score(self.items, response)["near"]["correct"], 1)

    def test_scoring_rejects_unknown_questions_and_tampered_keys(self):
        with self.assertRaisesRegex(ValueError, "Unexpected response ID"):
            score(self.items, {"N3": {"verdict": "no"}})
        self.items["near"]["N1"]["witnesses"] = {}
        with self.assertRaisesRegex(ValueError, "Key differs"):
            score(self.items, {})

    def test_assessment_contains_boards_and_no_answer_labels(self):
        result = assessment_html(self.items)
        self.assertEqual(result.count("<table"), 2)
        self.assertNotIn("bxc5", result)
        self.assertNotIn("Nxc5", result)
        self.assertNotIn("witnesses", result)

    def test_worked_reply_explanation_absent_from_A(self):
        a, b = (lesson_html(BASE, arm, {}) for arm in ("A", "B"))
        self.assertNotIn("b3 폰을 b4로", a)
        self.assertIn("b3 폰을 b4로", b)
        self.assertIn("<details>", a)


if __name__ == "__main__":
    unittest.main()
