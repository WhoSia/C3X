#!/usr/bin/env python3
"""C3X022-P0 independent April chess source contract tests."""
import sys
import unittest
import json
import tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_022_P0_april2026_engineblind_source import (
    ARCHIVE_SHA, ARCHIVE_URL, HISTORY, MARCH_SHA, collect_historical
)
class AprilNativeBlind(unittest.TestCase):
    def test_official_archive_pin(self):
        self.assertEqual(len(ARCHIVE_SHA),64)
        self.assertEqual(ARCHIVE_SHA,"97b036f3a3639ae3be59c1508b1e18c76ac1b2e8fada4587d1b5c5a93c438d5d")
        self.assertIn("2026-04.pgn.zst",ARCHIVE_URL)
    def test_historical_seven_not_six(self):
        self.assertEqual(len(HISTORY),7)
        self.assertEqual(HISTORY[-1],"march")
        self.assertEqual(HISTORY[0],"prior")
    def test_source_only_no_search_engine(self):
        s=(Path(__file__).resolve().parents[1]/"harness"/"c3x_022_P0_april2026_engineblind_source.py").read_text()
        self.assertNotIn("subprocess",s)
        self.assertNotIn("chess.engine",s)
        self.assertNotIn("stockfish",s.lower())
        self.assertIn("select_compressed_archive",s)
    def test_historical_count_mismatch_fails(self):
        with self.assertRaises(ValueError):
            collect_historical({"prior":"/tmp/nope"})
    def test_march_cannot_be_substituted(self):
        with tempfile.TemporaryDirectory() as td:
            p={}
            for name in HISTORY:
                x=Path(td)/(name+".json")
                x.write_text(json.dumps({"selected":[{"fen4":"8/8/8/8/8/8/8/8 w - -"}]}))
                p[name]=str(x)
            with self.assertRaises(ValueError):
                collect_historical(p)
    def test_frozen_march_sha(self):
        self.assertEqual(len(MARCH_SHA),64)
if __name__=="__main__": unittest.main()
