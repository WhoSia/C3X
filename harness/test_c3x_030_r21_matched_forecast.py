import unittest

from c3x_030_r21_matched_forecast import trace_point
from c3x_030_r21_score import score


def events(*updates):
    rows = ["C3X_S4K_GO_BEGIN epoch=1"]
    for ordinal, (value, alpha, beta) in enumerate(updates):
        rows.append(f"C3X_S4L_ROOT_SCORE ordinal={ordinal} epoch=1 iteration=9 "
                    f"value={value} alpha={alpha} beta={beta} will_update_root_pv=1")
    rows.append(f"C3X_S4K_GO_END epoch=1 root_score_total={len(updates)}")
    return rows


class MatchedForecastTest(unittest.TestCase):
    def test_fails_outside_window_and_preserves_uci_bound(self):
        base = {"cp": 0, "bound": False, "depth": 8}
        upper = {"cp": 10, "bound": True, "depth": 9, "upper": True, "lower": False}
        trace = events((100, 50, 110), (200, 50, 110))
        self.assertEqual(trace_point([base, upper], trace, True),
                         (None, "no_compatible_deeper_event"))
        event, status = trace_point([base, upper], trace, False)
        self.assertEqual((event["ordinal"], event["cp"], status), (0, -30, "added"))

    def test_missing_end_never_adds_value(self):
        base = {"cp": 0, "bound": False, "depth": 8}
        self.assertEqual(trace_point([base], events((100, 50, 110))[:-1], True),
                         (None, "missing_unique_go_boundary"))

    def test_disagreeing_referee_does_not_enter_stable_analysis(self):
        def values(depth, a, b):
            return [{"point": {"cp": cp, "depth": depth, "bound": False}} for cp in (a, b)]

        forecasts = {"pv": 1, "pv_strict": None, "tree": -1, "trace": 1, "trace_r14": -1}
        prediction = {"cohort_sha256": "same", "rows": {"q": {"signs": forecasts,
                      "round": "1.2", "reply": "e7e6", "leaves": []}}}
        judge = {"cohort_sha256": "same", "rows": {"q": {"14": values(14, 1, 0),
                                                       "16": values(16, 0, 1)}}}
        result = score(prediction, judge)["scores"]
        self.assertEqual(result["14"]["trace_gains"], 1)
        self.assertEqual(result["16"]["trace_losses"], 1)
        self.assertEqual(result["stable"]["judge_coverage"], 0)
        self.assertEqual(result["14"]["arms"]["pv_strict"]["coverage"], 0)


if __name__ == "__main__":
    unittest.main()
