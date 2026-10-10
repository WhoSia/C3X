#!/usr/bin/env python3
"""Pre-native source protocol: legally distinct Lichess broadcast and CC0 puzzles."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_023_P1_may2026_broadcast_nonmate_cc0_puzzle_engineblind32 import (
    BROADCAST_URL,PUZZLE_URL,PUZZLE_SNAPSHOT_SHA,source_fens,create,may_source,
    puzzles_nonmate,FIRST_ELIGIBLE,PICK)
class P1SourceTests(unittest.TestCase):
    def test_official_sources_distinct_and_original_snapshot_pinned(self):
        self.assertIn("/broadcast/lichess_db_broadcast_2026-05.pgn.zst",BROADCAST_URL)
        self.assertIn("lichess_db_puzzle.csv.zst",PUZZLE_URL)
        self.assertEqual(len(PUZZLE_SNAPSHOT_SHA),64)
        self.assertEqual((FIRST_ELIGIBLE,PICK),(512,16))
    def test_strict_historical_missing_before_unseen_source(self):
        with self.assertRaises(ValueError):
            source_fens({}, "/nonexistent", "/nonexistent")
    def test_new_source_functions_no_stockfish(self):
        s=(Path(__file__).resolve().parents[1]/"harness"/
          "c3x_023_P1_may2026_broadcast_nonmate_cc0_puzzle_engineblind32.py").read_text()
        self.assertNotIn("subprocess",s)
        self.assertNotIn("chess.engine",s)
        self.assertIn('"full_original_mainline_uci"',s)
        self.assertIn("CC BY-SA 4.0",s)
        self.assertIn('"license":"CC0"',s)
        self.assertIn("MATE_IN_ONE_EXCLUDED",s)
        self.assertIn("source_file_SHA256",s)
    def test_cannot_claim_dataset_success_without_real_files(self):
        with self.assertRaises((ValueError,FileNotFoundError)):
            create("/nonexistent","/nonexistent",{}, "/nonexistent", "/nonexistent")
if __name__=="__main__":unittest.main()
