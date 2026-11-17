import unittest

from c3x_030_r23_native_replay import join, source_result


def receipt(move="e2e4", native_move="e2e4", value=114, alpha=115, beta=140):
    return [
        "C3X_R23_GO_BEGIN",
        "C3X_R23_START attempt=1 iteration=8",
        f"C3X_R23_CANDIDATE attempt=1 id=1 move={native_move} "
        f"value={value} alpha={alpha} beta={beta} update=1",
        "C3X_R23_END attempt=1 stopped=0",
        "C3X_R23_START attempt=2 iteration=9",
        "C3X_R23_END attempt=2 stopped=1",
        f"C3X_R23_PUBLIC sink_attempt=2 producer=1 move={move} updated=1 tb=0 "
        "depth=9 value=115 bound=upper score=35 kind=cp nodes=24000",
        f"C3X_R23_BEST move={move} producer=1",
    ]


class NativeProvenanceTest(unittest.TestCase):
    def setUp(self):
        self.stdout = ["info depth 9 seldepth 8 multipv 1 score cp 35 upperbound "
                       "nodes 24000 nps 90000 time 2 pv e2e4", "bestmove e2e4"]

    def test_exact_emitting_and_source_attempt_ids_are_distinct(self):
        data = join(self.stdout, receipt())
        report, = data["reports"]
        self.assertEqual(report["status"], "bounded")
        self.assertEqual(report["public"]["sink_attempt"], "2")
        self.assertEqual(report["source"]["attempt"], "1")
        self.assertEqual(data["best_attempt_end"]["stopped"], "0")

    def test_matching_numbers_cannot_replace_candidate_identity(self):
        with self.assertRaisesRegex(ValueError, "producer"):
            join(self.stdout, receipt(native_move="d2d4"))

    def test_reject_inconsistent_bound(self):
        with self.assertRaisesRegex(ValueError, "producer"):
            join(self.stdout, receipt(value=123))

    def test_native_fail_high_uses_threshold(self):
        self.assertEqual(source_result({"value": "141", "alpha": "115", "beta": "140"}),
                         (140, "lower"))


if __name__ == "__main__":
    unittest.main()
