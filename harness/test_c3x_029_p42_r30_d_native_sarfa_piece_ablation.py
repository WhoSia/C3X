"""R30-D source-native SARFA pilot contracts. Fake chess engine is NOT evidence."""
import unittest
from unittest.mock import Mock

import chess
import chess.engine
from c3x_029_p42_r30_d_native_sarfa_piece_ablation import (
    supported_removals, forced_q, support_three, run, TEMPERATURE_CP)


def fake_engine():
    engine = Mock()
    def analyze(board, _limit, **kwargs):
        root = kwargs["root_moves"][0]
        # Purely synthetic deterministic Q proxy. NEVER present as engine result.
        score = len(board.piece_map()) * 2 + chess.square_file(root.from_square)
        return {
            "depth": 10, "nodes": 120,
            "score": chess.engine.PovScore(chess.engine.Cp(score), board.turn),
            "pv": [root],
        }
    engine.analyse.side_effect = analyze
    return engine


class SourceSARFAContracts(unittest.TestCase):
    def setUp(self):
        self.board = chess.Board()
        self.roots = [{"root":"e2e4"}, {"root":"d2d4"}]
        self.support = support_three(self.board, self.roots)

    def test_three_legal_actions_two_frozen_plus_third(self):
        self.assertEqual(self.support[:2], ["e2e4", "d2d4"])
        self.assertEqual(len(set(self.support)), 3)
        self.assertTrue(all(chess.Move.from_uci(x) in self.board.legal_moves
                            for x in self.support))

    def test_three_piece_removals_preserve_all_candidate_legality(self):
        baseline, ablations = supported_removals(self.board, self.support)
        self.assertTrue(baseline.is_valid())
        self.assertEqual(len(ablations), 3)
        self.assertTrue(all(b.is_valid() for _, b in ablations))
        self.assertTrue(all(chess.Move.from_uci(u) in b.legal_moves
                            for _, b in ablations for u in self.support))

    def test_forced_real_engine_interface_protocol(self):
        scores, nodes = forced_q(self.board, self.support, fake_engine())
        self.assertEqual(len(scores), 3)
        self.assertEqual(nodes, 360)

    def test_reject_action_support_change(self):
        b = self.board.copy(stack=True)
        b.remove_piece_at(chess.E2)
        with self.assertRaisesRegex(ValueError, "ROOT_ACTION_SUPPORT_CHANGED"):
            forced_q(b, self.support, fake_engine())

    def test_full_two_case_counterfeit_run_only(self):
        worlds = []
        for i in (1,2):
            worlds.append(({"case_id":"synthetic:%d"%i,
                            "event_family":"synthetic:%d"%i},
                           chess.Board(), self.roots))
        d = run(worlds, fake_engine())
        self.assertEqual(d["new_actual_engine_calls"], 24)
        self.assertTrue(d["piece_removal_is_not_a_reachable_chess_transition"])
        self.assertTrue(d["not_actual_source_internal_computation_intervention"])
        self.assertEqual(d["new_actual_source_nodes"], 24*120)

    def test_frozen_candidates_must_be_distinct(self):
        with self.assertRaisesRegex(ValueError, "TWO_SOURCE_ROOTS"):
            support_three(self.board, [{"root":"e2e4"}, {"root":"e2e4"}])


if __name__ == "__main__":
    unittest.main()
