"""P7 synthetic-only regression tests (not new chess observations)."""
import copy
import unittest
from c3x_p7_independent_judge_audit import audit, SOURCE_SCHEMA


def sample():
    roots = []
    for rid, root in enumerate(("e2e4", "d2d4")):
        leaves = []
        for i in range(4):
            leaves.append({"path_uci": [root, "a1a2", "b1c3", "b8c6", "g1f3" if i == 0 else f"h{i}h{i+1}"],
                           "scores": {"10": {"root_mover_cp": 10*i-rid, "actual_nodes": 50},
                                      "12": {"root_mover_cp": 40-10*i-rid, "actual_nodes": 60}}})
        roots.append({"root_uci": root, "independent_leaf_scores": leaves,
                      "depth_summaries": {
                          "10": {"min_over_only_four_source_selected_paths_cp": -rid,
                                 "max_over_only_four_source_selected_paths_cp": 30-rid,
                                 "span_across_only_four_paths_cp": 30,
                                 "actual_independent_nodes": 200},
                          "12": {"min_over_only_four_source_selected_paths_cp": 10-rid,
                                 "max_over_only_four_source_selected_paths_cp": 40-rid,
                                 "span_across_only_four_paths_cp": 30,
                                 "actual_independent_nodes": 240}}})
    return {"schema": SOURCE_SCHEMA, "independent_engine_family": "Berserk14",
            "source_selected_replies_unchanged_by_referee": True,
            "full_opponent_universe_judged": False,
            "source_engine_actual_causal_decision_proven": False,
            "independent_search_count": 16, "depths": [10, 12], "roots": roots}


class TestP7(unittest.TestCase):
    def test_valid(self):
        x = audit(sample())
        self.assertEqual(x["new_native_engine_searches"], 0)
        self.assertEqual(x["depth12_selected_minimum_margin_a_minus_b_cp"], 1)
        self.assertTrue(x["roots"][0]["minimum_path_sets_disjoint_across_depths"])

    def test_forged_summary(self):
        x = sample(); x["roots"][0]["depth_summaries"]["12"]["actual_independent_nodes"] = 10
        with self.assertRaisesRegex(ValueError, "SUMMARY_MISMATCH"): audit(x)

    def test_duplicate_path(self):
        x = sample()
        x["roots"][0]["independent_leaf_scores"][1]["path_uci"] = copy.deepcopy(x["roots"][0]["independent_leaf_scores"][0]["path_uci"])
        with self.assertRaisesRegex(ValueError, "DUPLICATE_PATH"): audit(x)

    def test_missing_depth(self):
        x = sample(); del x["roots"][0]["independent_leaf_scores"][2]["scores"]["12"]
        with self.assertRaisesRegex(ValueError, "DEPTH_MISSING"): audit(x)

    def test_false_scope(self):
        x = sample(); x["full_opponent_universe_judged"] = True
        with self.assertRaisesRegex(ValueError, "RECEIPT_SCOPE"): audit(x)

    def test_bad_nodes(self):
        x = sample(); x["roots"][0]["independent_leaf_scores"][0]["scores"]["10"]["actual_nodes"] = 0
        with self.assertRaisesRegex(ValueError, "NUMERIC_PROVENANCE"): audit(x)

    def test_count(self):
        x = sample(); x["independent_search_count"] = 15
        with self.assertRaisesRegex(ValueError, "SEARCH_COUNT"): audit(x)

    def test_root_disagreement(self):
        x = sample(); x["roots"][0]["independent_leaf_scores"][0]["path_uci"][0] = "d2d4"
        with self.assertRaisesRegex(ValueError, "ROOT_PATH_DISAGREEMENT"): audit(x)


if __name__ == "__main__":
    unittest.main()
