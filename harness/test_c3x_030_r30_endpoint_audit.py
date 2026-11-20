"""Deterministic dependency-free tests for the R30 causal-scope gates."""
import copy
import unittest

from c3x_030_r30_endpoint_audit import audit, audit_trial


def fixture():
    sham = {
        "read": {"seq": "4", "root": "a2a3", "attempt": "1", "hint": "b2b3", "mask": "0",
                 "effective": "b2b3", "mask_move": "0", "mask_value": "0"},
        "masked": [], "cutoffs": [], "replies": ["b2b3"],
        "direct_child": {"stopped": "0", "child_value": "17"},
        "target_candidate": {"update": "0", "value": "-17"},
        "best": {"move": "e2e3"}, "producer": {"attempt": "1"},
        "last_report": {"public": {"score": "17", "kind": "cp", "bound": "none"}},
    }
    mask = copy.deepcopy(sham)
    mask["read"].update(mask="1", effective="(none)", mask_move="1")
    mask["masked"] = [dict(mask["read"])]
    mask["direct_child"]["child_value"] = "19"
    mask["target_candidate"]["update"] = "1"
    mask["best"]["move"] = "a2a3"
    mask["last_report"]["public"].update(score="19", bound="upper")
    restore = copy.deepcopy(sham)
    restore["uci_changed"] = False
    return {"id": "TEST-001", "stratum": "close", "source_attempt": 1,
            "arms": {"move": {"sham": sham, "mask": mask, "restore": restore}}}


class R30AuditTests(unittest.TestCase):
    def test_total_effect_is_not_mediation(self):
        case = fixture()
        result = audit({"positions": [case]}, [])
        self.assertEqual(result["totals"]["final_choice_changed"], 1)
        trial = result["final_choice_cases"][0]
        self.assertFalse(trial["target_candidate_update_is_rank"])
        self.assertIn("not established", trial["causal_scope"])
        self.assertEqual(trial["masked_score"], ["19", "upper"])

    def test_broken_restore_fails_closed(self):
        case = fixture()
        case["arms"]["move"]["restore"]["best"]["move"] = "a2a3"
        with self.assertRaisesRegex(ValueError, "Restoration"):
            audit({"positions": [case]}, [])

    def test_changed_pretreatment_read_fails_closed(self):
        case = fixture()
        case["arms"]["move"]["mask"]["read"]["root"] = "e2e3"
        with self.assertRaisesRegex(ValueError, "Pre-treatment"):
            audit({"positions": [case]}, [])

    def test_abstentions_remain_in_denominator(self):
        case = fixture()
        extra = {"id": "TEST-002", "stratum": "depth-reversal", "arms": {}}
        with self.assertRaisesRegex(ValueError, "Abstention"):
            audit({"positions": [case, extra]}, [])
        result = audit({"positions": [case, extra]},
                       [{"case": "TEST-002", "stratum": "depth-reversal"}])
        self.assertEqual(result["totals"]["tested_positions"], 1)
        self.assertEqual(result["totals"]["abstained_positions"], 1)

    def test_stopped_child_is_not_a_false_negative(self):
        case = fixture()
        case["arms"]["move"]["mask"]["direct_child"]["stopped"] = "1"
        result = audit_trial(case, "move", case["arms"]["move"])
        self.assertIsNone(result["child_return_changed"])

    def test_earlier_read_not_mislabeled_as_producer(self):
        case = fixture()
        case["source_attempt"] = 3
        result = audit_trial(case, "move", case["arms"]["move"])
        self.assertFalse(result["within_original_producer"])
        self.assertEqual(result["event_attempt"], 1)


if __name__ == "__main__":
    unittest.main()
