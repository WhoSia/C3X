#!/usr/bin/env python3
"""Zero-native-engine tests for the March 2026 prospective selection contract."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"harness"))
from c3x_020_C_March2026_enginefree_blind16 import (
    N_SELECT,N_ELIGIBLE,MAX_SCANNED,SOURCE_URL,HISTORY_NAMES,
    chosen_ply,canonical_game_fingerprint,history_overlap
)

class EngineFreeMarchTest(unittest.TestCase):
    def test_source_month_and_fixed_denominator(self):
        self.assertIn("2026-03.pgn.zst",SOURCE_URL)
        self.assertEqual((N_ELIGIBLE,N_SELECT,MAX_SCANNED),(512,16,20000))
        self.assertEqual(len(HISTORY_NAMES),6)
        self.assertEqual(HISTORY_NAMES[-1],"february")
    def test_hash_selection_determinism_and_bounds(self):
        d1=canonical_game_fingerprint({"Event":"A"},["e2e4","e7e5"])
        d2=canonical_game_fingerprint({"Event":"A"},["e2e4","e7e5"])
        d3=canonical_game_fingerprint({"Event":"A"},["e2e4","c7c5"])
        self.assertEqual(d1,d2)
        self.assertNotEqual(d1,d3)
        self.assertGreaterEqual(chosen_ply(d1),30)
        self.assertLess(chosen_ply(d1),45)
        with self.assertRaises(ValueError):
            chosen_ply("fake")
    def test_all_six_history_inputs_are_required_and_sha_recorded(self):
        with tempfile.TemporaryDirectory() as td:
            src={}
            for name in HISTORY_NAMES:
                p=Path(td)/(name+".json")
                p.write_text(json.dumps({"selected":[{"fen4":"board-"+name}]}))
                src[name]=str(p)
            fens,receipts=history_overlap(src)
            self.assertEqual(len(fens),6)
            self.assertEqual(set(receipts),set(HISTORY_NAMES))
            self.assertTrue(all(len(row["sha256"])==64 for row in receipts.values()))
            src.pop("february")
            with self.assertRaises(ValueError):
                history_overlap(src)
    def test_source_uses_no_engine_api(self):
        p=(ROOT/"harness"/"c3x_020_C_March2026_enginefree_blind16.py").read_text()
        self.assertNotIn("subprocess",p)
        self.assertNotIn("stockfish",p.lower())
        self.assertNotIn("chess.engine",p)
        self.assertIn("board.legal_moves",p)

if __name__=="__main__":
    unittest.main()
