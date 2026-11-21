"""R36 certificate tests against the two previously published real derived receipts.

No tests below create Stockfish outcomes; negative mutations are synthetic controls.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from c3x_030_r36_claim_gate import EvidenceError, audit, verify_r33, verify_r35

ROOT = Path(__file__).resolve().parents[1]
R33 = ROOT / "receipts" / "C3X_030_R33_cross_cohort_summary_20261121.json"
R35 = ROOT / "receipts" / "C3X_030_R35_root_lineage_20261121.json"


class ClaimGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r33 = json.loads(R33.read_text(encoding="utf-8"))
        cls.r35 = json.loads(R35.read_text(encoding="utf-8"))

    def test_actual_derived_receipts_and_scope(self):
        court = audit(self.r33, self.r35)
        self.assertEqual(court["authority"], "DERIVED_RECEIPT_CONSISTENCY_ONLY")
        self.assertFalse(court["raw_zip_rehash_this_run"])
        self.assertEqual(court["new_native_searches_this_run"], 0)
        self.assertEqual(court["human_participants_this_run"], 0)
        self.assertEqual(court["observed"]["R33_cross_cohort"]["physical_interventions"], 57)
        self.assertEqual(court["observed"]["R35_single_game"]["independent_game_histories"], 1)
        self.assertEqual([x["verdict"] for x in court["claim_court"]], [
            "FALSIFIED_IN_RECORDED_INTERVENTIONS",
            "FALSIFIED_IN_RECORDED_INTERVENTIONS",
            "LOCAL_TWO_ARM_WITNESS",
            "HOLD_UNIDENTIFIED",
            "HOLD_NO_INDEPENDENT_ALL_WINNER_JUDGE",
            "HOLD_NO_HUMAN_OUTCOME",
        ])

    def test_r33_three_effects_are_not_three_independent_strategy_wins(self):
        r = verify_r33(self.r33)
        self.assertEqual(r["final_choice_flip"], 3)
        self.assertEqual(r["child_changed_with_identical_public_score_bound_pv_and_final_move"], 15)
        self.assertEqual(r["unjudged_new_winner"], "R30-017:e2d3")

    def test_r35_first_changed_candidate_is_not_h3(self):
        r = verify_r35(self.r35)
        self.assertEqual(r["first_changed_candidate"], "d4b3")
        self.assertEqual(r["local_leader_lost"], "h2h3")
        self.assertEqual(r["intervening_state_mediator"], "UNIDENTIFIED")

    def test_reject_count_disagreement(self):
        altered = deepcopy(self.r33)
        altered["counts"]["all"]["direct_child_return_changed"] += 1
        with self.assertRaises(EvidenceError):
            verify_r33(altered)

    def test_reject_unobserved_child_as_zero(self):
        altered = deepcopy(self.r33)
        altered["counts"]["R29"]["direct_child_return_changed_unobserved"] = 0
        with self.assertRaises(EvidenceError):
            verify_r33(altered)

    def test_reject_missing_third_candidate(self):
        altered = deepcopy(self.r33)
        hit = next(x for x in altered["witnesses"] if x["id"] == "R30-017")
        hit["post_intervention_independent_judge_coverage"] = True
        with self.assertRaises(EvidenceError):
            verify_r33(altered)

    def test_reject_posthoc_referee_promotion(self):
        altered = deepcopy(self.r33)
        hit = next(x for x in altered["witnesses"] if x["id"] == "R29-029")
        hit["independent_reference_judge_label"] = "win"
        with self.assertRaises(EvidenceError):
            verify_r33(altered)

    def test_reject_r35_different_search_window(self):
        altered = deepcopy(self.r35)
        altered["results"][0]["matched_root_window"]["alpha"] = 369
        with self.assertRaises(EvidenceError):
            verify_r35(altered)

    def test_reject_h3_update_promotion(self):
        altered = deepcopy(self.r35)
        altered["results"][1]["same_window_h3_competition"]["treated_update"] = "1"
        with self.assertRaises(EvidenceError):
            verify_r35(altered)

    def test_reject_h3_as_first_changed_score(self):
        altered = deepcopy(self.r35)
        altered["results"][0]["first_same_window_score_change"]["move"] = "h2h3"
        with self.assertRaises(EvidenceError):
            verify_r35(altered)

    def test_reject_mediation_claim_without_actual_event_bridge(self):
        altered = deepcopy(self.r35)
        altered["results"][0]["comparison_limit"] = "complete TT/history mediation proved"
        with self.assertRaises(EvidenceError):
            verify_r35(altered)

    def test_reject_duplicate_witness(self):
        altered = deepcopy(self.r33)
        altered["witnesses"].append(deepcopy(altered["witnesses"][0]))
        with self.assertRaises(EvidenceError):
            verify_r33(altered)

    def test_output_is_deterministic(self):
        a = json.dumps(audit(self.r33, self.r35), sort_keys=True)
        b = json.dumps(audit(self.r33, self.r35), sort_keys=True)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
