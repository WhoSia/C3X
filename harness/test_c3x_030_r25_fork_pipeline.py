"""R25 integration regression: real, already-exposed R24 records; no engine calls."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "product"))

from c3x_plan_evidence_report import synthesize, korean_markdown


class PlanEvidencePipelineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen = json.loads((ROOT / "receipts" /
            "C3X_030_R25_EXPOSED_FORK_EVIDENCE_20261117.json").read_text(encoding="utf-8"))
        cls.output = synthesize(cls.frozen)

    def test_two_precisely_scoped_development_cases(self):
        self.assertEqual(self.output["schema"], "C3X_030_R25_PLAN_AUDIT_V1")
        results = [x["audit"] for x in self.output["results"]]
        self.assertEqual(len(results), 2)
        self.assertEqual([r["first_divergence_ply"] for r in results], [3, 2])
        self.assertEqual([r["chooser"] for r in results], ["white", "black"])
        self.assertEqual([r["displayed_cp"] for r in results], [39, 89])
        self.assertEqual(results[0]["native_values"], [128, 131])
        self.assertEqual(results[1]["native_values"], [292, 292])

    def test_judge_disciplines_have_opposite_outcomes(self):
        spanish, tcec = [x["audit"] for x in self.output["results"]]
        self.assertEqual(spanish["verdict"], "DEPTH_SENSITIVE_FORK_PREFERENCE")
        self.assertEqual([x["preferred"] for x in spanish["judge_order"]], ["f1e1", "d2d4"])
        self.assertEqual([x["margin_cp"] for x in spanish["judge_order"]], [12, 61])
        self.assertEqual(tcec["verdict"], "JUDGE_ORDER_STABLE_AT_TESTED_DEPTHS")
        self.assertEqual([x["preferred"] for x in tcec["judge_order"]], ["d6e7", "d6e7"])
        self.assertEqual([x["margin_cp"] for x in tcec["judge_order"]], [16, 11])

    def test_no_fake_intervention_or_plan_pass(self):
        for case in self.output["results"]:
            r = case["audit"]
            self.assertFalse(r["both_continuations_replayed"])
            self.assertIn("CAUSAL_CONTRAST_UNPROVEN", r["provenance"])
            self.assertIn("PLAN_TRANSPORT_UNPROVEN", r["provenance"])
            self.assertEqual(case["next_trial"]["result"], "NOT_TESTED")

    def test_reader_is_warned_who_changed_move(self):
        text = korean_markdown(self.output)
        self.assertIn("백의 후속 선택이 달라진 사례", text)
        self.assertIn("예측한 흑의 응수가 달라진", text)
        self.assertIn("미시험", text)
        self.assertNotIn("학습 효과 입증", text)


if __name__ == "__main__":
    unittest.main()
