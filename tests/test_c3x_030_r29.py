"""Test event selection, provenance, and transfer scoring for R29."""
import unittest

import chess

from c3x_030_r29_learner import build_key, score
from c3x_030_r29_local_tt_move import nominate, nominate_cutoff, probe_signature
from c3x_030_r29_unseen import choose_events, stratum


def probe(seq, attempt, root="a5a4", hint="b3b4", hit="1", excluded="0"):
    return dict(seq=str(seq), attempt=str(attempt), root=root, hint=hint, hit=hit, excluded=excluded)


class EventTests(unittest.TestCase):
    def test_boundaries_and_missing_points(self):
        cases = [((-15, 15), "depth-reversal"), ((-30, 30), "depth-reversal"),
                 ((28, 30), "close"), ((100, 120), "large-stable"),
                 ((-100, -120), "large-stable"), ((100, -2), "intermediate"),
                 ((None, 100), "point-unavailable")]
        self.assertEqual([stratum(values) for values, _ in cases], [expected for _, expected in cases])

    def test_nominate_only_preceding_read_on_same_root(self):
        logs = [probe(1, 8), probe(2, 9, root="f6d7"), probe(3, 10, hint="b3a4"),
                probe(4, 11), probe(5, 11), probe(6, 13)]
        self.assertEqual(nominate(logs, 12)["seq"], "4")
        self.assertEqual(nominate(logs, 13)["seq"], "6")

    def test_exclude_misses_and_singular_reads_in_external_rule(self):
        logs = [probe(1, 9), probe(2, 10, excluded="1"), probe(3, 10, hit="0"),
                probe(4, 10, hint="b3a4")]
        cutoffs = [{"seq": "4"}]
        arms = choose_events(logs, cutoffs, 10, "a5a4", "b3b4")
        self.assertEqual({kind: row["seq"] for kind, row in arms.items()}, {"move": "1", "value": "4"})
        self.assertEqual(nominate_cutoff(logs, cutoffs, 10), logs[-1])

    def test_probe_match_excludes_only_effective_changes(self):
        clean = {**probe(9, 10), "effective": "b3b4", "mask": "0", "tt_value": "100"}
        masked = {**clean, "effective": "(none)", "mask": "1"}
        self.assertEqual(probe_signature(clean), probe_signature(masked))
        self.assertNotEqual(probe_signature(clean), probe_signature({**masked, "tt_value": "101"}))

    def test_legality_accepts_alternative_pawn_and_separate_scores(self):
        board = chess.Board("2r2b1r/pp3p1p/4k3/1B1Rpp2/3n4/1N3P2/PPP3PP/2KR4 w - - 3 21")
        data = {"near": {}, "transfer": {"T": {"fen": board.fen(), "pawn": "c2",
                                              "bishop": "b5", "knight": "d4"}}}
        key = build_key(data)
        self.assertEqual(list(key["T"]["plans"]), ["a2a4"])
        self.assertTrue(score(key, {"T": {"threat": "b5", "plan": "a4"}})["T"]["both"])
        result = score(key, {"T": {"threat": "c5", "plan": "a4"}})["T"]
        self.assertTrue(result["plan"])
        self.assertFalse(result["both"])
        self.assertTrue(score(key, {})["T"]["incomplete"])


if __name__ == "__main__":
    unittest.main()
