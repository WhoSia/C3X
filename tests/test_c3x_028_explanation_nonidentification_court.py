"""C3X explanation identifiability finite abstract counterexample, no Stockfish."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from c3x_028_explanation_nonidentification_court import court


class ExplainIdentifiability(unittest.TestCase):
    def test_same_engine_evidence_allows_opposite_chess_claims(self):
        r = court()
        self.assertEqual(r["possible_abstract_worlds"], 4)
        self.assertEqual(r["distinct_score_and_mechanism_observations"], 1)
        self.assertEqual(r["distinct_truth_values_for_chess_semantic_claim"], 2)
        self.assertFalse(r["legal_chess_worlds_constructed"])

if __name__ == "__main__":
    unittest.main()
