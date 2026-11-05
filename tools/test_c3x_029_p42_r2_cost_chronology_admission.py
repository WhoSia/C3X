"""P42/R2 regression: original permissive cases vs stricter scientific admission."""
import unittest
from test_c3x_029_p41_r3_independent_plan_court_preflight import fixture
from c3x_029_p41_r3_independent_plan_court_preflight import verify_case
from c3x_029_p42_r2_cost_chronology_admission import (
    audit_resource_account, audit_research_admission, METRICS
)

def complete_ledger(case):
    for rec in case["methods"].values():
        rec["engine_queries"] = 4
        rec["model_tokens"] = 0
        rec["model_calls"] = 0
    return case

class R2ResearchAdmissibility(unittest.TestCase):
    def test_original_preflight_accepts_lopsided_actual_compute(self):
        a, h = fixture()
        a["methods"]["pv"]["native_nodes"] = 1000
        self.assertEqual(verify_case(a, h)["status"],
                         "PASS_STRUCTURAL_PREFLIGHT_ONLY")
        complete_ledger(a)
        result = audit_resource_account(a)
        self.assertEqual(result["status"], "HOLD")
        self.assertIn("UNMATCHED_ACTUAL_native_nodes", result["reasons"])

    def test_original_preflight_accepts_fake_legal_game(self):
        a, h = fixture()
        self.assertEqual(verify_case(a, h)["status"],
                         "PASS_STRUCTURAL_PREFLIGHT_ONLY")
        out = audit_research_admission(complete_ledger(a), h)
        self.assertEqual(out["status"], "HOLD")
        self.assertIn("EXTERNAL_PROOF_MISSING_legal_full_history", out["reasons"])

    def test_declared_prejudge_is_not_trusted_chronology(self):
        a, h = fixture()
        out = audit_research_admission(complete_ledger(a), h,
                                       trusted_source=True, trusted_legal=True,
                                       trusted_cost=True, trusted_judge=True)
        self.assertIn("EXTERNAL_PROOF_MISSING_prediction_precedes_judge",
                      out["reasons"])

    def test_missing_cost_dimensions_fail_closed(self):
        a, _ = fixture()
        out = audit_resource_account(a)
        self.assertEqual(out["status"], "HOLD")
        self.assertTrue(any("MISSING_OR_INVALID_ACTUAL" in x for x in out["reasons"]))

    def test_matched_declared_cost_not_scientific_pass(self):
        a, h = fixture()
        a = complete_ledger(a)
        self.assertEqual(audit_resource_account(a)["status"],
                         "MATCHED_DECLARED_COST_ONLY")
        out = audit_research_admission(
            a, h, trusted_source=True, trusted_legal=True,
            trusted_chronology=True, trusted_cost=True, trusted_judge=True)
        self.assertEqual(out["status"],
                         "READY_FOR_SEPARATE_VALUE_EVALUATION_NOT_CHESS_PASS")

    def test_disallow_zero_vs_nonzero_actual_compute(self):
        a, _ = fixture()
        a = complete_ledger(a)
        a["methods"]["c3x"]["model_calls"] = 1
        self.assertIn("UNMATCHED_ACTUAL_model_calls",
                      audit_resource_account(a)["reasons"])

    def test_boolean_masquerading_as_count_rejected(self):
        a, _ = fixture()
        a = complete_ledger(a)
        a["methods"]["pv"]["engine_queries"] = True
        self.assertIn("MISSING_OR_INVALID_ACTUAL_pv_engine_queries",
                      audit_resource_account(a)["reasons"])

    def test_existing_budget_violations_not_waived(self):
        a, h = fixture()
        a = complete_ledger(a)
        a["methods"]["c3x"]["native_nodes"] = 30000
        out = audit_research_admission(
            a, h, trusted_source=True, trusted_legal=True,
            trusted_chronology=True, trusted_cost=True, trusted_judge=True)
        self.assertEqual(out["status"], "HOLD")
        self.assertIn("GLOBAL_BUDGET_native_nodes", out["reasons"])

if __name__ == "__main__":
    unittest.main()
