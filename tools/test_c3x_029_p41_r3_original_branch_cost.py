"""P41/R3 authentic original action-count and budget regression tests."""
import copy
import hashlib
import json
import os
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from c3x_029_p41_r3_original_branch_cost import SHA,audit

class RealArchivedBranchCost(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=os.environ.get("C3X_P41_BRANCH_SOURCE")
        if not path:raise unittest.SkipTest("authentic original P39 R2 source required")
        raw=Path(path).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError("ORIGINAL_HASH")
        cls.j=json.loads(raw)

    def test_all_actual_reply_counts_and_cost(self):
        r=audit(self.j)
        self.assertEqual((r["original_roots"],r["opponent_first_replies"],
                          r["own_reply_candidates"],r["total_legal_expansions"]),
                         (16,644,24894,25554))
        self.assertEqual(r["projected_native_nodes"],2389824000)
        self.assertFalse(r["forecast_cost_is_observed"])

    def test_tampered_own_count_rejected(self):
        x=copy.deepcopy(self.j)
        x["cases"][0]["worlds"][0]["branches"][0]["own_legal_reply_count"]+=1
        with self.assertRaisesRegex(ValueError,"EXPANSION_COUNT_MISMATCH"):
            audit(x)

    def test_no_missing_case_accepted(self):
        x=copy.deepcopy(self.j)
        x["candidate_worlds"]=15
        with self.assertRaisesRegex(ValueError,"INVALID_ORIGINAL_DENOMINATOR"):
            audit(x)

    def test_node_budget_must_be_positive(self):
        with self.assertRaisesRegex(ValueError,"BAD_NODE_BUDGET"):
            audit(self.j,0)

if __name__=="__main__":unittest.main()
