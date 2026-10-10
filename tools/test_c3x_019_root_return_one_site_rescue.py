#!/usr/bin/env python3
"""Fail-closed source fixture and frozen return-edge contract tests."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
sys.path.insert(0,str(ROOT/"harness"))

from c3x_019_root_return_one_site_rescue_overlay import patch
from c3x_019_Feb_four_first_root_return_rescue_native import (
    FIXED, config, source_pair_assert
)


SOURCE_FIXTURE = """namespace Stockfish {
  c3x017_root_event_count = 0;
      if (rootNode)
      {
          RootMove& rm = *std::find(thisThread->rootMoves.begin(),
                                    thisThread->rootMoves.end(), move);
"""


class ReturnEdgePatchTest(unittest.TestCase):
    def test_exact_once_before_root_score(self):
        updated=patch(SOURCE_FIXTURE)
        self.assertIn("static thread_local int c3x019_return_repair_contacts = 0;",updated)
        self.assertEqual(updated.count("c3x019_return_repair kind="),1)
        self.assertLess(updated.index("C3X019 one-site synthetic edge intervention"),
                        updated.index("RootMove& rm ="))
        self.assertIn("value = Value(c3x019_target);",updated)
        self.assertIn('c3x018_root_call_id ==',updated)
        self.assertIn('c3x018_trial_at_depth ==',updated)
        self.assertIn('c3x019_before == c3x019_expected',updated)

    def test_bad_or_duplicate_source_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError,"ANCHOR"):
            patch(SOURCE_FIXTURE.replace("RootMove& rm", "RootMover& rm"))
        with self.assertRaisesRegex(RuntimeError,"ANCHOR"):
            patch(SOURCE_FIXTURE+SOURCE_FIXTURE)

    def test_four_fixed_cases_and_single_source_edit(self):
        self.assertEqual([c[0] for c in FIXED],[3,6,7,10])
        self.assertEqual([c[2] for c in FIXED],[4,10,4,4])
        for case in FIXED:
            c=config(case)
            self.assertEqual(c["mode"],"REPAIR")
            self.assertEqual(c["replacement"],case[9])
            self.assertEqual(c["expected"],case[10])
            self.assertEqual(config(case,"OBS")["mode"],"OBS")
            sham=config(case,sham=True)
            self.assertEqual(sham["move"],65535)
            self.assertNotEqual(sham["move"],c["move"])

    def test_frozen_source_candidate_identity(self):
        case=FIXED[1]
        o={"kind":"candidate","depth":10,"root_call":19,"trial":2,
           "move":1291,"index":1,"alpha":94,"beta":114,
           "child_return":103,"before":104,"after":103}
        v={**o,"child_return":114,"after":114}
        x={"game_id":6,"selector":"STRICT",
           "arms":{"F":{"all_root_search_events":[o]},
                   "FIRST":{"all_root_search_events":[v]}}}
        source_pair_assert(case,x)
        x["arms"]["FIRST"]["all_root_search_events"]=[{**v,"move":1234}]
        with self.assertRaisesRegex(RuntimeError,"MISMATCH"):
            source_pair_assert(case,x)


if __name__=="__main__":
    unittest.main()
