"""P42 R1 pure-math adversarial regression; no chess-oracle assertion."""
import unittest
from tools.c3x_029_p42_regret_nonidentification_court import (
    BranchWorld, score, constant_shift_refuter, posthoc_oracle_refuter
)

class P42RegretIdentificationTests(unittest.TestCase):
    def test_equal_zero_regret_opposite_root_values(self):
        result = constant_shift_refuter()
        self.assertEqual(result["a_regret"], result["b_regret"])
        self.assertEqual(result["a_regret"], 0)
        self.assertGreater(result["a_minimax"], result["b_minimax"])

    def test_posthoc_oracle_zero_regret(self):
        result = posthoc_oracle_refuter()
        self.assertEqual(result["posthoc_regret"], 0)
        self.assertEqual(len(result["posthoc_plan"]), 2)

    def test_reject_partial_response_map(self):
        w = BranchWorld({"m": {"r1": {"a": 1, "b": 0}, "r2": {"a": 2, "b": 1}}},
                        {"m": {"r1": ("a",)}})
        with self.assertRaisesRegex(ValueError, "RESPONSE_COVERAGE"):
            score(w, "m")

    def test_reject_all_legal_triviality(self):
        w = BranchWorld({"m": {"r1": {"a": 1, "b": 0}}},
                        {"m": {"r1": ("a", "b")}})
        with self.assertRaisesRegex(ValueError, "TRIVIAL_PLAN"):
            score(w, "m")

    def test_reject_illegal_plan(self):
        w = BranchWorld({"m": {"r1": {"a": 1, "b": 0}}},
                        {"m": {"r1": ("x",)}})
        with self.assertRaisesRegex(ValueError, "ILLEGAL_PLAN"):
            score(w, "m")

if __name__ == "__main__":
    unittest.main()
