"""R27-J1 source-judge custody and legal path regression; no scientific fake data."""
import copy
import unittest
from unittest.mock import patch

import chess

from c3x_029_p42_r27_j1_cui_tree_independent_referee import (
    reconstruct, TREE_SCHEMA
)


def worlds_and_tree():
    games, cases = [], []
    for ix in (1, 2):
        board = chess.Board()
        roots = []
        source_roots = []
        for root in ("e2e4", "d2d4"):
            branch = []
            for idx, first in enumerate(("e7e5", "c7c5", "d7d5"), 1):
                subs = [
                    {"opponent_move_uci": reply, "opponent_engine_rank": j,
                     "player_response_uci": "b1c3"}
                    for j, reply in enumerate(("g8f6", "b8c6", "a7a6"), 1)
                ]
                branch.append({
                    "opponent_move_uci": first,
                    "opponent_engine_rank": idx,
                    "player_response_uci": "g1f3",
                    "next_opponent_branches": subs})
            roots.append({
                "root_uci": root, "leaf_paths": 9,
                "continuation_plies_after_root": 4, "first_layer": branch})
            after_root = board.copy()
            after_root.push_uci(root)
            source_roots.append({"root": root,
                                 "replies": [m.uci() for m in after_root.legal_moves]})
        source = {"case_id": "synthetic-%d" % ix, "event_family": "fixture"}
        games.append((source, board, source_roots))
        cases.append({"case_id": source["case_id"], "event_family": "fixture",
                      "roots": roots})
    tree = {
        "schema": TREE_SCHEMA,
        "status": "SOURCE_ONLY_ACTUAL_RECURSIVE_TWO_OPPONENT_LAYER_NO_JUDGE",
        "independent_judge_consulted_to_build_tree": False,
        "opponent_k": 3, "total_leaf_paths": 36,
        "total_engine_queries": 64, "cases": cases}
    return games, tree


class RefereeContract(unittest.TestCase):
    def test_exact_36_legally_reconstructed_leaves(self):
        worlds, tree = worlds_and_tree()
        with patch(
            "c3x_029_p42_r27_j1_cui_tree_independent_referee.source_positions",
            return_value=worlds
        ):
            ready = reconstruct(None, tree)
        self.assertEqual(len(ready), 2)
        self.assertEqual(sum(len(root[1]) for c in ready for root in c[2]), 36)
        self.assertTrue(all(path["rank1"] in (1, 2, 3)
                            for c in ready for root in c[2]
                            for path in root[1]))

    def test_no_referee_source_leakage(self):
        worlds, tree = worlds_and_tree()
        tree["independent_judge_consulted_to_build_tree"] = True
        with self.assertRaisesRegex(ValueError, "CUSTODY"):
            reconstruct(None, tree)

    def test_reject_tampered_opponent_rank(self):
        worlds, tree = worlds_and_tree()
        tree["cases"][0]["roots"][0]["first_layer"][0]["opponent_engine_rank"] = 2
        with patch(
            "c3x_029_p42_r27_j1_cui_tree_independent_referee.source_positions",
            return_value=worlds
        ):
            with self.assertRaisesRegex(ValueError, "FIRST_ENGINE_RANK"):
                reconstruct(None, tree)

    def test_reject_illegal_source_response(self):
        worlds, tree = worlds_and_tree()
        tree["cases"][0]["roots"][0]["first_layer"][0]["player_response_uci"] = "e7e5"
        with patch(
            "c3x_029_p42_r27_j1_cui_tree_independent_referee.source_positions",
            return_value=worlds
        ):
            with self.assertRaisesRegex(ValueError, "FIRST_PATH_ILLEGAL"):
                reconstruct(None, tree)

    def test_require_two_complete_cases(self):
        worlds, tree = worlds_and_tree()
        tree["cases"].pop()
        with patch(
            "c3x_029_p42_r27_j1_cui_tree_independent_referee.source_positions",
            return_value=worlds
        ):
            with self.assertRaisesRegex(ValueError, "CASE_COUNT"):
                reconstruct(None, tree)


if __name__ == "__main__":
    unittest.main()
