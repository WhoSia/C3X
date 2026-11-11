"""Synthetic-only tests; not new native chess engine experiments."""
import unittest
from c3x_030_p8_fritz_empty_square_saliency import summarize

def fixture():
    return {"schema": "c3x030-p8-fritz-raw-probe-v1",
            "original_q": {"a": 2., "b": 1., "c": 0.},
            "selected_action": "a", "temperature": 1.,
            "square_probes": [
                {"square": sq, "was_empty_at_source": True,
                 "pawn_probes": {color: {
                     "status": "legal_measured",
                     "position_legality_verified_externally": True,
                     "same_action_legal_in_perturbation": True,
                     "same_engine_and_search_budget": True,
                     "perturbed_q": {"a": a, "b": 1., "c": 0.}
                 } for color, a in (("white", 1.), ("black", -1.))}}
                for sq in ("d4", "e4", "f4", "g4")]}

class FritzEvidenceTest(unittest.TestCase):
    def test_deterministic_top3(self):
        x = summarize(fixture())
        self.assertEqual([r["square"] for r in x["ranked_complete_top3"]], ["d4", "e4", "f4"])
        self.assertEqual(x["complete_two_color_count"], 4)
        self.assertEqual(x["number_of_new_native_searches_in_this_adapter"], 0)
    def test_incomplete_is_unknown(self):
        x = fixture()
        x["square_probes"][0]["pawn_probes"]["white"] = {"status": "illegal_check"}
        y = summarize(x)
        self.assertIsNone(y["all_candidates"][0]["max_two_color_saliency_or_null"])
        self.assertEqual(y["incomplete_unknown_count"], 1)
    def test_square_bounds(self):
        x = fixture(); x["square_probes"][0]["square"] = "e8"
        with self.assertRaisesRegex(ValueError, "SQUARE_IDENTITY"): summarize(x)
    def test_duplicate_square(self):
        x = fixture(); x["square_probes"][1]["square"] = "d4"
        with self.assertRaisesRegex(ValueError, "SQUARE_IDENTITY"): summarize(x)
    def test_source_occupied(self):
        x = fixture(); x["square_probes"][0]["was_empty_at_source"] = False
        with self.assertRaisesRegex(ValueError, "NOT_PROVEN_EMPTY"): summarize(x)
    def test_missing_color(self):
        x = fixture(); del x["square_probes"][0]["pawn_probes"]["black"]
        with self.assertRaisesRegex(ValueError, "BOTH_PAWN_COLORS"): summarize(x)
    def test_engine_budget(self):
        x = fixture(); x["square_probes"][0]["pawn_probes"]["white"]["same_engine_and_search_budget"] = False
        with self.assertRaisesRegex(ValueError, "ENGINE_OR_BUDGET"): summarize(x)
    def test_illegal_selected_move(self):
        x = fixture(); x["square_probes"][0]["pawn_probes"]["black"]["same_action_legal_in_perturbation"] = False
        with self.assertRaisesRegex(ValueError, "SELECTED_ACTION_NOT_LEGAL"): summarize(x)
    def test_unmeasured_q_not_allowed(self):
        x = fixture(); x["square_probes"][0]["pawn_probes"]["black"]["status"] = "not_measured"
        with self.assertRaisesRegex(ValueError, "UNMEASURED_SCORES"): summarize(x)
    def test_fixed_action_support(self):
        x = fixture(); del x["square_probes"][0]["pawn_probes"]["white"]["perturbed_q"]["c"]
        with self.assertRaisesRegex(ValueError, "FIXED_ACTION_SUPPORT"): summarize(x)

if __name__ == "__main__":
    unittest.main()
