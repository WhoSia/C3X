"""R29 temporal events: genuine legal history fixtures, no synthetic evidence claims."""
import copy
import unittest

import chess
from test_c3x_029_p42_r28_m1_fixed_binprop_nearby_negative_audit import synthetic_court
from c3x_029_p42_r28_m1_fixed_binprop_nearby_negative_audit import audit as old_audit
from c3x_029_p42_r29_t1_temporal_source_event_audit import (
    analyze, temporal_events, FEATURES)


def fixtures():
    worlds, judged = synthetic_court()
    # The legacy R27 synthetic fixture deliberately uses one event label for
    # both cases; actual research input has two distinct source event labels.
    worlds[1][0]["event_family"] = "synthetic_second_game"
    judged["cases"][1]["event_family"] = "synthetic_second_game"
    return worlds, old_audit(worlds, judged)


class TemporalContracts(unittest.TestCase):
    def test_capture_in_middle_of_legal_four_ply_history(self):
        board = chess.Board()
        for move in ("e2e4", "d7d5", "e4d5", "d8d5", "b1c3"):
            board.push_uci(move)
        features = temporal_events(board, chess.WHITE)
        self.assertEqual(set(features), set(FEATURES))
        self.assertTrue(features["opponent_second_captured"])
        self.assertFalse(features["source_second_captured"])
        self.assertFalse(features["source_second_immediate_recapture"])

    def test_full_36_leaf_source_label_join(self):
        worlds, labels = fixtures()
        out = analyze(worlds, labels)
        self.assertEqual(out["source_path_count"], 36)
        self.assertEqual(out["matched_prefix_count"], 12)
        self.assertEqual(len(out["feature_summaries"]), 8)
        self.assertTrue(out["no_new_chess_searches_or_judge_calls"])

    def test_label_source_move_drift_rejected(self):
        worlds, labels = fixtures()
        labels["nearby_groups"][0]["positive_second_opponent_reply"] = "a1a8"
        with self.assertRaisesRegex(ValueError, "PATH_DRIFT"):
            analyze(worlds, labels)

    def test_duplicate_label_key_rejected(self):
        worlds, labels = fixtures()
        labels["nearby_groups"][1]["rank1"] = labels["nearby_groups"][0]["rank1"]
        labels["nearby_groups"][1]["root_uci"] = labels["nearby_groups"][0]["root_uci"]
        with self.assertRaisesRegex(ValueError, "DUPLICATE_LABEL"):
            analyze(worlds, labels)

    def test_reject_wrong_final_side_to_move(self):
        b = chess.Board()
        for move in ("e2e4", "e7e5"):
            b.push_uci(move)
        with self.assertRaisesRegex(ValueError, "FINAL_TURN"):
            temporal_events(b, chess.WHITE)

    def test_reject_opponent_mover_as_root_mover(self):
        b = chess.Board()
        for move in ("e2e4", "e7e5", "g1f3", "b8c6", "b1c3"):
            b.push_uci(move)
        with self.assertRaisesRegex(ValueError, "FINAL_TURN"):
            temporal_events(b, chess.BLACK)

    def test_provenance_mismatch_rejected(self):
        worlds, labels = fixtures()
        labels["source_tree_sha256"] = "wrong"
        with self.assertRaisesRegex(ValueError, "CUSTODY"):
            analyze(worlds, labels)


if __name__ == "__main__":
    unittest.main()
