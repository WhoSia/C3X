"""R28 synthetic counterexample contracts for nearby-negative matched prefixes.

No synthetic judge result is scientific evidence.
"""
import unittest
from unittest.mock import patch
import chess
from test_c3x_029_p42_r27_j1_cui_tree_independent_referee import worlds_and_tree
from c3x_029_p42_r27_j1_cui_tree_independent_referee import reconstruct
from c3x_029_p42_r28_m1_fixed_binprop_nearby_negative_audit import (
    audit, feature_vector, FEATURES, GAP_CP,
)


def synthetic_court():
    raw, tree = worlds_and_tree()
    with patch("c3x_029_p42_r27_j1_cui_tree_independent_referee.source_positions",
               return_value=raw):
        worlds = reconstruct(None, tree)
    judged = {"schema": "c3x042-r27-j1-cui-two-layer-independent-9-path-referee-v1",
              "source_tree_sha256": "f41e96bbf598aa824e65467cd1f1c782674aa275460211ce02b68f6eff1d4d5e",
              "new_native_search_count": 72, "cases": []}
    for source, turn, roots in worlds:
        rated_roots = []
        for root, paths in roots:
            rated_roots.append({
                "root_uci": root, "independently_judged_paths": [
                    {key: val for key, val in x.items() if key != "board"}
                    | {"depths": {"16": {"root_mover_cp": 30 - 20 * x["rank2"]}}}
                    for x in paths]})
        judged["cases"].append({"case_id": source["case_id"],
                                "event_family": source["event_family"],
                                "roots": rated_roots})
    return worlds, judged


class NearbyNegativeContract(unittest.TestCase):
    def test_all_twelve_prefix_groups_exact_legal_join(self):
        worlds, judged = synthetic_court()
        result = audit(worlds, judged)
        self.assertEqual(result["n_source_tree_leaves"], 36)
        self.assertEqual(result["n_matched_first_reply_prefixes"], 12)
        self.assertEqual(result["n_admitted_positive_nearby_negative_pairs"], 12)
        self.assertEqual(len(result["feature_summaries"]), len(FEATURES))
        self.assertTrue(all(x["gap_cp"] == 40 for x in result["nearby_groups"]))

    def test_reject_mismatched_move_score_join(self):
        worlds, judged = synthetic_court()
        judged["cases"][0]["roots"][0]["independently_judged_paths"][0]["own_second"] = "e7e5"
        with self.assertRaisesRegex(ValueError, "CUSTODY"):
            audit(worlds, judged)

    def test_reject_judge_byte_provenance_drift(self):
        worlds, judged = synthetic_court()
        judged["source_tree_sha256"] = "fake"
        with self.assertRaisesRegex(ValueError, "JOIN"):
            audit(worlds, judged)

    def test_reject_duplicate_rank_pair(self):
        worlds, judged = synthetic_court()
        judged["cases"][0]["roots"][0]["independently_judged_paths"][1]["rank2"] = 1
        with self.assertRaisesRegex(ValueError, "DUPLICATE"):
            audit(worlds, judged)

    def test_signed_perspective_of_material(self):
        b = chess.Board()
        self.assertEqual(feature_vector(b, chess.WHITE)["material_ahead"], False)
        self.assertEqual(feature_vector(b, chess.BLACK)["material_ahead"], False)
        b.remove_piece_at(chess.D8)
        self.assertTrue(feature_vector(b, chess.WHITE)["material_ahead"])
        self.assertFalse(feature_vector(b, chess.BLACK)["material_ahead"])

    def test_same_prefix_not_assumed_same_referee_outcome(self):
        worlds, judged = synthetic_court()
        result = audit(worlds, judged)
        self.assertTrue(all(row["positive_second_opponent_reply"] !=
                            row["negative_second_opponent_reply"]
                            for row in result["nearby_groups"]))


if __name__ == "__main__":
    unittest.main()
