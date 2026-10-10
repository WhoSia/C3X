#!/usr/bin/env python3
"""No Actions required: deterministic semantic-prefix proof unit tests."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "harness"))
from c3x_019_February_semantic_root_prefix_audit import (
    analyze, candidate_identity, first_semantic_divergence,
    matching_episode_event, semantic, window_class
)


class RootSemanticPrefixTest(unittest.TestCase):
    def test_ignore_only_explicit_observer_counters(self):
        a = {"kind": "candidate", "depth": 4, "root_call": 4, "seq": 19,
             "root_nodes": 100, "child_return": -55, "alpha": -10}
        b = {**a, "seq": 19, "root_nodes": 300}
        self.assertEqual(semantic(a), semantic(b))
        self.assertIsNone(first_semantic_divergence([a], [b]))
        b["child_return"] = -56
        self.assertEqual(first_semantic_divergence([a], [b])[0], 0)

    def test_alpha_beta_boundary_separate_from_choice(self):
        self.assertEqual(window_class(-11, -10, 10), "below_alpha")
        self.assertEqual(window_class(-10, -10, 10), "at_alpha")
        self.assertEqual(window_class(3, -10, 10), "inside_window")
        self.assertEqual(window_class(10, -10, 10), "at_or_above_beta")

    def test_candidate_key_requires_source_context(self):
        x = {"kind": "candidate", "depth": 10, "root_call": 19,
             "trial": 2, "index": 1, "move": 1291, "alpha": 94,
             "beta": 114, "before": 104, "child_return": 103}
        self.assertEqual(candidate_identity(x),
                         candidate_identity({**x, "child_return": 114}))
        self.assertNotEqual(candidate_identity(x),
                            candidate_identity({**x, "root_call": 20}))
        self.assertNotEqual(candidate_identity(x),
                            candidate_identity({**x, "alpha": 95}))

    def test_ambiguous_episode_fails_closed(self):
        witness = {"depth": 4, "root_call": 4, "trial": 1}
        ev = {**witness, "kind": "window_exit", "value": -100}
        with self.assertRaisesRegex(RuntimeError, "NON_UNIQUE"):
            matching_episode_event([ev, dict(ev)], "window_exit", witness)

    def test_unknown_or_reordered_selected_games_fails(self):
        with self.assertRaisesRegex(RuntimeError, "FIXED_FOUR_CASES"):
            analyze({"cases": [{"game_id": 6}]})

    def test_root_nodes_only_difference_cannot_explain_root_choice(self):
        row = {"kind": "candidate", "depth": 4, "root_call": 4,
               "trial": 1, "index": 2, "move": 2910,
               "alpha": 103, "beta": 123, "before": -32001,
               "child_return": -459, "after": -32001, "root_nodes": 178}
        self.assertIsNone(first_semantic_divergence(
            [row], [{**row, "root_nodes": 180, "seq": 8}]))


if __name__ == "__main__":
    unittest.main()
