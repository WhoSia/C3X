"""P35/R6: mock UCI transport, exercising forced, pair and unrestricted go commands.

These tests validate the orchestration; they do NOT replace native Stockfish execution.
"""
import os
import stat
import tempfile
import unittest
from pathlib import Path

from c3x_029_p35_r5_search_route_court import run_once

MOCK_ENGINE = r'''#!/usr/bin/env python3
import os,sys
for raw in sys.stdin:
    command=raw.strip()
    if command=="uci":
        print("id name Stockfish 16")
        print("option name Use NNUE type check default true")
        print("uciok",flush=True)
    elif command=="isready":
        print("readyok",flush=True)
    elif command.startswith("go "):
        options=command.split()
        if "searchmoves" in options:
            first=options[options.index("searchmoves")+1]
        else:
            first="a7a6"
        print("info depth 1 score cp 12 nodes 24000 pv "+first,flush=True)
        print("bestmove "+first,flush=True)
        if os.getenv("C3X_P35_ROUTE_AUDIT"):
            print("C3X_P35_ROUTE key=17 arm=NNUE psq=12 value=8",file=sys.stderr,flush=True)
        print("GO_SAW "+command,file=sys.stderr,flush=True)
    elif command=="quit":
        break
'''

class P35RootCompetitionContract(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.engine=Path(self.tmp.name)/"mock_stockfish"
        self.engine.write_text(MOCK_ENGINE)
        self.engine.chmod(self.engine.stat().st_mode | stat.S_IXUSR)
    def tearDown(self):
        self.tmp.cleanup()

    def exercise(self, root, expected):
        plain=run_once(str(self.engine),["e2e4"],root,24000,False)
        traced=run_once(str(self.engine),["e2e4"],root,24000,True)
        self.assertEqual(plain["bestmove"],expected)
        self.assertEqual(plain["final_info"],traced["final_info"])
        self.assertEqual(plain["route_count"],0)
        self.assertEqual(traced["route_count"],1)
        self.assertEqual(traced["route_by_arm"]["NNUE"],1)

    def test_forced_one_root_not_natural_choice(self):
        self.exercise("e8f7","e8f7")
    def test_pair_restricted_choice(self):
        self.exercise(["e8f7","e5f4"],"e8f7")
    def test_unrestricted_can_select_third(self):
        self.exercise(None,"a7a6")
    def test_pair_requires_two_distinct_roots(self):
        with self.assertRaisesRegex(ValueError,"INVALID_PAIR_ROOTS"):
            run_once(str(self.engine),[],["e8f7","e8f7"],24000,False)
if __name__=="__main__":
    unittest.main()
