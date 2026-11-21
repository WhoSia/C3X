"""Test fallback evidence, channel priority and public iteration projections."""
import unittest

from c3x_030_r30_observed_reply import select
from c3x_030_r30_public_iteration import public_view


def probe(seq, attempt, hint, *, root="a5a4", hit="1", excluded="0"):
    return {"seq": str(seq), "attempt": str(attempt), "hint": hint,
            "root": root, "hit": hit, "excluded": excluded}


def reply(seq, move):
    return {"seq": str(seq), "move": move}


class R30Tests(unittest.TestCase):
    def test_first_reply_must_come_from_same_probe(self):
        probes = [probe(1, 8, "b3b4"), probe(2, 9, "c2c4"), probe(3, 10, "b3b4")]
        replies = [reply(1, "b3b4"), reply(2, "d2d4"), reply(2, "c2c4"), reply(3, "c2c4")]
        self.assertEqual(select(probes, [], replies, 10, "a5a4", "a2a3"),
                         {"fallback": probes[0]})

    def test_cutoff_stays_separate_and_primary_wins(self):
        probes = [probe(1, 8, "b3b4"), probe(2, 10, "c2c4")]
        replies = [reply(1, "b3b4"), reply(2, "c2c4")]
        cutoffs = [{"seq": "2"}]
        self.assertEqual(select(probes, cutoffs, replies, 10, "a5a4", "b3b4"),
                         {"move": probes[0], "value": probes[1]})
        self.assertEqual(select(probes, cutoffs, replies, 10, "a5a4", "a2a3"),
                         {"fallback": probes[0], "value": probes[1]})

    def test_fallback_does_not_select_post_producer_or_singular_reads(self):
        probes = [probe(1, 9, "c2c4"), probe(2, 10, "c2c4", excluded="1"),
                  probe(3, 11, "c2c4"), probe(4, 10, "c2c4", hit="0")]
        replies = [reply(i, "c2c4") for i in range(1, 5)]
        self.assertEqual(select(probes, [], replies, 10, "a5a4", None),
                         {"fallback": probes[0]})

    def test_public_view_ignores_search_counters_but_preserves_bound(self):
        log = "info depth 2 seldepth 3 multipv 1 score cp -15 nodes 990 pv e2e4\nbestmove e2e4"
        self.assertEqual(public_view(log), public_view(log.replace("990", "999")))
        self.assertNotEqual(public_view(log), public_view(log.replace("nodes", "upperbound nodes")))
        self.assertEqual(public_view(log)["final"], public_view(log.replace("depth 2", "depth 3"))["final"])
        self.assertNotEqual(public_view(log)["iterations"], public_view(log.replace("depth 2", "depth 3"))["iterations"])


if __name__ == "__main__":
    unittest.main()
