import unittest
from c3x_018_trial_call_identity_patch import patch

BASE = """namespace Stockfish {
static constexpr int c3x017_root_event_limit = 4096;
void run() {
  c3x017_root_event_count = 0;
              if(c3x017_root_event_count<c3x017_root_event_limit && rootDepth>=1) {
              sync_cout << "info string c3x017_root_event kind=window_enter seq=" << c3x017_root_event_count
              << "info string c3x017_root_event kind=window_exit seq=" << c3x017_root_event_count
              << "info string c3x017_root_event kind=after_sort seq=" << c3x017_root_event_count
              << "info string c3x017_root_event kind=candidate seq=" << c3x017_root_event_count;
}
}"""

class TrialCallPatchTest(unittest.TestCase):
    def test_all_four_event_kinds_tagged(self):
        result = patch(BASE)
        self.assertEqual(result.count('<< " trial=" << c3x018_trial_at_depth'), 4)
        self.assertEqual(result.count('<< " root_call=" << c3x018_root_call_id'), 4)

    def test_exactly_one_call_increment_site(self):
        result = patch(BASE)
        self.assertEqual(result.count("++c3x018_root_call_id;"), 1)
        self.assertEqual(result.count("++c3x018_trial_at_depth;"), 1)

    def test_counters_reset(self):
        result = patch(BASE)
        self.assertIn("c3x018_last_depth = -1;", result)
        self.assertIn("c3x018_trial_at_depth = 0;", result)

    def test_duplicate_anchor_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "C3X018_ANCHOR_STATE_COUNT_2"):
            patch(BASE.replace("static constexpr int c3x017_root_event_limit = 4096;",
                               "static constexpr int c3x017_root_event_limit = 4096;" * 2))

    def test_missing_prior_observer_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "C3X018_ANCHOR"):
            patch("namespace Stockfish {}")

    def test_double_apply_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "C3X018_ANCHOR_STATE_COUNT_0"):
            patch(patch(BASE))

if __name__ == "__main__":
    unittest.main()
