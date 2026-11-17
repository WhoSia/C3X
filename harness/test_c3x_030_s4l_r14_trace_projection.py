"""Check the incremental-information boundary and paired-score accounting."""

import unittest

from c3x_030_s4l_r14_trace_projection import projections
from c3x_030_s4l_r14_trace_score import score


def go(*events, total=None):
    return ["C3X_S4K_GO_BEGIN epoch=1", *events,
            f"C3X_S4K_GO_END epoch=1 root_score_total={len(events) if total is None else total}"]


def root(iteration, value, ordinal=0):
    return (f"C3X_S4L_ROOT_SCORE epoch=1 ordinal={ordinal} iteration={iteration} "
            f"value={value} alpha=-328 beta=328 will_update_root_pv=1")


class TraceProjectionTests(unittest.TestCase):
    def setUp(self):
        self.public = [{"cp": 12, "depth": 5, "bound": False},
                       {"cp": 24, "depth": 6, "bound": True}]

    def test_same_depth_is_already_public_even_if_public_bound(self):
        out = projections(self.public, go(root(6, 150)), True)
        self.assertEqual(out["values"], {"public_tree": 12, "public_last": 24, "trace": 12})

    def test_deeper_ordinary_in_window_score_changes_augmented_value(self):
        out = projections(self.public, go(root(7, -330), root(7, -160, 1)), False)
        self.assertEqual(out["values"]["trace"], 48)
        self.assertEqual(out["trace_event"]["ordinal"], 1)

    def test_truncated_root_trace_falls_back(self):
        out = projections(self.public, go(root(7, 160), total=2), True)
        self.assertEqual(out["trace_status"], "incomplete_go_trace")
        self.assertEqual(out["values"]["trace"], 12)

    def test_only_independently_judged_changes_enter_gain_count(self):
        f = {"questions_sha256": "frozen", "rows": {
            k: {"signs": {"public_tree": -1, "public_last": 1, "trace": 1}} for k in ("a", "b")
        }}
        j = {"questions_sha256": "frozen", "depth": 16, "rows": {
            "a": [{"point": {"depth": 16, "cp": 80, "bound": False}},
                  {"point": {"depth": 16, "cp": 35, "bound": False}}],
            "b": [{"point": None}, {"point": None}],
        }}
        self.assertEqual(score(f, j)["paired_trace"], {"changed": 1, "gained": 1, "lost": 0})


if __name__ == "__main__":
    unittest.main()
