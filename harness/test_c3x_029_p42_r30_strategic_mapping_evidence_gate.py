"""R30-C: evidence matrix admission must not be granted from mere tree metrics."""
import unittest
from c3x_029_p42_r30_strategic_mapping_evidence_gate import (
    audit_experiment, audit_many)


def sample():
    return {
        "experiment": "R27-source-Cui-2layer",
        "source_receipt": "github:42580681868",
        "stages": ["R1", "R4", "R5"],
        "same_original_position": True,
        "actual_physical_source_intervention": False,
        "actual_final_root_change": False,
        "independently_judged_plan": True,
        "same_endpoint_horizon": True,
        "prospective_before_outcome_source": False,
        "explanation_move_mask_control": False,
        "human_utility_evaluated": False,
    }


class MappingContracts(unittest.TestCase):
    def test_r27_does_not_become_causal(self):
        x = audit_experiment(sample())
        self.assertFalse(x["flagship_same_world_causal_strategic_admission"])
        self.assertIn("actual_physical_source_intervention", x["failure_gates"])

    def test_cui_strategy_is_not_human_trial(self):
        x = audit_experiment(sample())
        self.assertFalse(x["explanation_behavioral_validity_tested"])

    def test_all_specific_evidence_gates_required(self):
        r = sample()
        for key in (
            "same_original_position", "actual_physical_source_intervention",
            "actual_final_root_change", "independently_judged_plan",
            "same_endpoint_horizon", "prospective_before_outcome_source"):
            r[key] = True
        self.assertTrue(audit_experiment(r)["flagship_same_world_causal_strategic_admission"])
        r["same_endpoint_horizon"] = False
        self.assertFalse(audit_experiment(r)["flagship_same_world_causal_strategic_admission"])

    def test_reject_unsupported_stage(self):
        r = sample()
        r["stages"] = ["R10"]
        with self.assertRaisesRegex(ValueError, "STAGE"):
            audit_experiment(r)

    def test_reject_nonboolean_causality(self):
        r = sample()
        r["actual_final_root_change"] = "true"
        with self.assertRaisesRegex(ValueError, "NONBOOLEAN"):
            audit_experiment(r)

    def test_reject_duplicate_rows(self):
        a = sample()
        with self.assertRaisesRegex(ValueError, "DUPLICATE"):
            audit_many([a, a])

    def test_collect_without_imaginary_generalization(self):
        a = sample()
        b = sample()
        b["experiment"] = "R29-temporal-negative"
        b["stages"] = ["R1", "R5", "R7"]
        b["independently_judged_plan"] = False
        z = audit_many([a, b])
        self.assertEqual(z["n_experiments"], 2)
        self.assertEqual(z["n_admitted_same_world"], 0)


if __name__ == "__main__":
    unittest.main()
