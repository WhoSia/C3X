#!/usr/bin/env python3
"""Post-outcome audit must preserve frozen source and invalidate mismatches."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_022_P2_postoutcome_depth_chess_disagreement_audit import (
    explain,SOURCE_SHA,PRIMITIVES_SHA,STAGEB_SHA)
class PostoutcomeChessAudit(unittest.TestCase):
    def test_frozen_source_digest_lengths(self):
        for sha in (SOURCE_SHA,PRIMITIVES_SHA,STAGEB_SHA):
            self.assertEqual(len(sha),64)
    def test_cannot_skip_unreported_ecology(self):
        with self.assertRaises((KeyError,ValueError)):
            explain({"per_ecology":{}},{"ecologies":{}},{"ecologies":{}})
    def test_exact_game_count_required(self):
        with self.assertRaises(ValueError):
            explain({"per_ecology":{"twic":{"cases":[]}}},{"ecologies":{"twic":{"selected":[]}}},
                    {"ecologies":{"twic":{"selected":[]}}})
    def test_no_prediction_refit_and_no_native_calls(self):
        code=(Path(__file__).resolve().parents[1]/"harness"/
              "c3x_022_P2_postoutcome_depth_chess_disagreement_audit.py").read_text()
        self.assertNotIn("subprocess",code)
        self.assertNotIn("chess.engine",code)
        self.assertIn("predicted_root_move",code)
        self.assertIn("root_depths_not_comparable",code)
        self.assertIn("actual_equal_to_other_order_baseline",code)
        self.assertIn("POST_OUTCOME_DESCRIPTIVE__NEVER_PROSPECTIVE",code)
if __name__=="__main__":unittest.main()
