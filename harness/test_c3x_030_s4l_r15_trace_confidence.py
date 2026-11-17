"""Distinguish within-call replacement from aspiration restarts."""

import unittest

from c3x_030_s4l_r15_trace_confidence import probabilities, within_iteration_switch


def trace(*moves):
    events = [
        f"C3X_S4L_ROOT_SCORE epoch=1 ordinal={i} iteration={d} root_id={r} "
        f"root_move_raw={m} will_update_root_pv=1"
        for i, (d, r, m) in enumerate(moves)
    ]
    return ["C3X_S4K_GO_BEGIN epoch=1", *events,
            f"C3X_S4K_GO_END epoch=1 root_score_total={len(events)}"]


class TraceConfidenceTests(unittest.TestCase):
    def test_same_call_with_two_candidates_is_a_switch(self):
        self.assertTrue(within_iteration_switch(trace((7, 20, 32), (7, 20, 64))))

    def test_new_root_invocation_and_earlier_depth_are_not_switches(self):
        self.assertFalse(within_iteration_switch(trace((6, 10, 32), (6, 10, 64),
                                                       (7, 20, 32), (7, 21, 64))))

    def test_confidence_shift_preserves_winner_and_sets_aside_missing_trace(self):
        self.assertEqual(probabilities(1, False), [4, 4, 24])
        self.assertEqual(probabilities(1, True), [6, 6, 20])
        self.assertIsNone(probabilities(1, None))


if __name__ == "__main__":
    unittest.main()
