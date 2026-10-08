#!/usr/bin/env python3
"""Negative controls for early C3X historical JSONL/EPD coverage."""
import sys, tempfile, json, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_011_historical_world_loader import load
from g10_p19_source_census import canonicalize_fen_text
import hashlib
START="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
HASH=hashlib.sha256((START+" 0 1").encode()).hexdigest()
class TestHistoryLoader(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.d=Path(self.t.name)
 def test_jsonl_recovers_fen(self):
  (self.d/"early.jsonl").write_text(json.dumps({"fen":START+" 0 1"})+"\n")
  h,m=load(self.d);self.assertIn(HASH,h);self.assertEqual(m[0]["kind"],".jsonl")
 def test_epd_ignores_semantic_labels(self):
  (self.d/"sts.epd").write_text(START+' bm e4; id "Undermine"; c0 "theme";\n')
  h,m=load(self.d);self.assertIn(HASH,h);self.assertEqual(len(h),1)
 def test_bad_jsonl_fails(self):
  (self.d/"early.jsonl").write_text('{"fen":')
  with self.assertRaisesRegex(ValueError,"HISTORY_BAD_JSONL"):load(self.d)
 def test_bad_epd_fails(self):
  (self.d/"sts.epd").write_text("not a fen")
  with self.assertRaisesRegex(ValueError,"HISTORY_BAD_EPD"):load(self.d)
 def test_empty_fails(self):
  with self.assertRaisesRegex(ValueError,"HISTORY_EMPTY_INVENTORY"):load(self.d)
if __name__=="__main__":unittest.main()
