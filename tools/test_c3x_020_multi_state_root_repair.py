#!/usr/bin/env python3
"""Bounded source and harness contract tests; native scientific run is separate."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "harness")]
from c3x_020_multi_state_root_repair_overlay import patch
from c3x_020_B_minimal_multi_state_native_court import (
    SECOND, boundary_config, second_config, snapshot, actual_contacts
)


def source_fixture():
    return """namespace Stockfish {
static thread_local int c3x019_return_repair_contacts = 0;
void search_test() {
  c3x019_return_repair_contacts = 0;
      // C3X019 one-site synthetic edge intervention, after child subtree search.
      if (rootNode)
      {
          RootMove& rm = *std::find(thisThread->rootMoves.begin(),
                                    thisThread->rootMoves.end(), move);
      }
      if (!Threads.stop)
          completedDepth = rootDepth;
}
}
"""


class SourceContract(unittest.TestCase):
    def test_original_native_sites_are_distinct(self):
        p = patch(source_fixture())
        self.assertIn("c3x020_second_contacts = 0;", p)
        self.assertIn("c3x020_boundary_contacts = 0;", p)
        self.assertLess(p.index("C3X020 independently selected second root candidate return"),
                        p.index("C3X019 one-site synthetic edge intervention"))
        self.assertLess(p.index("completedDepth = rootDepth;"),
                        p.index("C3X020 boundary snapshot/graft"))
        self.assertIn('c3x020_boundary_mode[0]', p)
        self.assertIn('c3x020_second_mode[0]', p)
        self.assertIn('const bool matched = kind == \'O\' ||', p)

    def test_fail_closed_on_duplicate_anchor(self):
        with self.assertRaisesRegex(RuntimeError, "ANCHOR_COUNT_2"):
            patch(source_fixture() +
                  "      if (!Threads.stop)\n          completedDepth = rootDepth;\n")

    def test_fail_closed_on_missing_019_overlay(self):
        with self.assertRaisesRegex(RuntimeError, "SECOND_AFTER_CHILD_ANCHOR_COUNT_0"):
            patch(source_fixture().replace(
                "C3X019 one-site synthetic edge intervention",
                "MISSING ROOT RETURN BASE"))

    def test_reapplication_is_rejected(self):
        with self.assertRaises(RuntimeError):
            patch(patch(source_fixture()))


class FrozenCaseSelection(unittest.TestCase):
    def test_second_sites_frozen_to_same_candidate(self):
        self.assertEqual(set(SECOND), {3, 6, 10})
        self.assertEqual({k: (v["expected"], v["target"]) for k, v in SECOND.items()},
                         {3: (-179, -206), 6: (96, 89), 10: (-892, -459)})
        self.assertNotIn(7, SECOND)

    def test_sham_is_unreachable_move(self):
        self.assertEqual(second_config(6, sham=True)["move"], 65535)
        self.assertEqual(second_config(6)["move"], 1307)

    def test_observation_has_no_known_score_snapshot_prerequisite(self):
        self.assertEqual(boundary_config(10,1291)["mode"],"O")
        self.assertEqual(boundary_config(10,1291)["target_average"],0)

    def test_snapshot_requires_actual_single_source_observation(self):
        good={"boundary_state_events":[dict(kind="observed",
                 before_score=103,after_score=103,
                 before_average=104,after_average=104)]}
        self.assertEqual(snapshot(good), {"score":103,"average":104})
        bad={"boundary_state_events":good["boundary_state_events"] * 2}
        with self.assertRaises(RuntimeError):
            snapshot(bad)

    def test_contacts_distinguish_scientific_and_control_arms(self):
        events={"root_return_events":[{"kind":"repaired"}],
                "second_return_events":[{"kind":"repaired"}],
                "boundary_state_events":[{"kind":"repaired"}]}
        self.assertTrue(actual_contacts(events,1,1,1))
        with self.assertRaises(RuntimeError):
            actual_contacts(events,1,0,1)
        changed={**events,"second_return_events":[{"kind":"source_mismatch"}]}
        with self.assertRaises(RuntimeError):
            actual_contacts(changed,1,1,1)


if __name__ == "__main__":
    unittest.main()
