import unittest
from itertools import product

from c3x_030_s4m_r2_progress_certificate import Node, verify_progress


class ProgressCertificateTest(unittest.TestCase):
    def test_flat_wdl_can_label_a_closed_cycle_as_a_win(self):
        graph = {
            "a": Node(True, frozenset({"b"})),
            "b": Node(False, frozenset({"a"})),
        }
        # Fixed winner's perspective: both local WDL equations accept +1.
        flat = dict.fromkeys(graph, 1)
        for state, node in graph.items():
            aggregate = max if node.winner_to_move else min
            self.assertEqual(flat[state], aggregate(flat[c] for c in node.successors))
        for a, b in product(range(1, 4), repeat=2):
            with self.assertRaises(ValueError):
                verify_progress(graph, set(), "a", {"a": a, "b": b})

    def test_winner_may_ignore_a_cycle_but_opponent_may_choose_it(self):
        graph = {
            "a": Node(True, frozenset({"b", "win"})),
            "b": Node(False, frozenset({"a"})),
            "win": Node(False, frozenset()),
        }
        self.assertEqual(
            verify_progress(graph, {"win"}, "a", {"a": 1, "win": 0}),
            {"a": ("win",), "win": ()},
        )
        graph["a"] = Node(False, graph["a"].successors)
        with self.assertRaisesRegex(ValueError, "uncovered reply"):
            verify_progress(graph, {"win"}, "a", {"a": 1, "win": 0})

    def test_invalid_anchors_and_dangling_edges(self):
        for node, terminals, ranks in [
            (Node(False, frozenset()), set(), {"a": 0}),
            (Node(False, frozenset()), {"a"}, {"a": True}),
            (Node(True, frozenset({"a"})), {"a"}, {"a": 0}),
            (Node(True, frozenset({"missing"})), set(), {"a": 2, "missing": 0}),
        ]:
            with self.subTest(node=node, ranks=ranks), self.assertRaises(ValueError):
                verify_progress({"a": node}, terminals, "a", ranks)

    def test_exhaustive_agreement_with_bounded_reachability(self):
        # Two nonterminals and two fixed leaves. Enumerate all outgoing sets
        # and turn assignments. Wins stabilize by the second expansion.
        states = ("a", "b", "win", "draw")
        outgoing = [
            frozenset(state for state, enabled in zip(states, mask) if enabled)
            for mask in product((False, True), repeat=4)
            if any(mask)
        ]
        checked = 0
        for left, right, turn_a, turn_b in product(outgoing, outgoing, (False, True), (False, True)):
            graph = {
                "a": Node(turn_a, left), "b": Node(turn_b, right),
                "win": Node(False, frozenset()), "draw": Node(False, frozenset()),
            }
            ranks = {"win": 0}
            for ply in (1, 2):
                reached = set(ranks)
                for state in ("a", "b"):
                    node = graph[state]
                    options = [child in reached for child in node.successors]
                    choose = any if node.winner_to_move else all
                    if choose(options):
                        ranks.setdefault(state, ply)
            for root in ("a", "b"):
                accepted = False
                for a, b in product((None, 1, 2), repeat=2):
                    candidate = {"win": 0}
                    candidate.update((state, rank) for state, rank in zip(("a", "b"), (a, b)) if rank is not None)
                    try:
                        verify_progress(graph, {"win"}, root, candidate)
                    except ValueError:
                        continue
                    accepted = True
                self.assertEqual(accepted, root in ranks, (graph, root))
            checked += 1
        self.assertEqual(checked, 900)


if __name__ == "__main__":
    unittest.main()
