#!/usr/bin/env python3
"""Dependency-free C3X 0.11 raw PGN preflight regression tests."""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from c3x_011_raw_preflight import inspect

def sample(tag_order=None, body="1. e4 e5 1-0"):
    tags = tag_order or ["Event", "Site", "Date", "Round", "White", "Black", "Result"]
    values = {"Event":"Example","Site":"?","Date":"2026.10.08","Round":"1",
              "White":"A","Black":"B","Result":"1-0"}
    return "\n".join(f'[{tag} "{values[tag]}"]' for tag in tags) + "\n\n" + body + "\n\n"

class RawPreflightTest(unittest.TestCase):
    def inspect_text(self, content):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"case.pgn"
            p.write_text(content)
            return inspect(p)
    def test_normal_two_games(self):
        r=self.inspect_text(sample()+sample())
        self.assertEqual(r["game_header_blocks"],2)
        self.assertFalse(r["required_header_missing"])
        self.assertFalse(r["malformed_lines"])
    def test_non_event_first_header(self):
        r=self.inspect_text(sample(["White","Black","Event","Result"]))
        self.assertEqual(r["game_header_blocks"],1)
    def test_duplicate_tag_rejected(self):
        r=self.inspect_text(sample().replace('[White "A"]','[White "A"]\n[White "C"]'))
        self.assertEqual(len(r["duplicate_header_tags"]),1)
    def test_missing_result_rejected(self):
        r=self.inspect_text(sample(["Event","White","Black"]))
        self.assertEqual(r["required_header_missing"][0]["missing"],["Result"])
    def test_no_movetext_rejected(self):
        r=self.inspect_text(sample(body=""))
        self.assertEqual(r["no_movetext_games"],[1])
    def test_malformed_tag_rejected(self):
        r=self.inspect_text(sample().replace('[White "A"]','[White A]'))
        self.assertTrue(r["malformed_lines"])
    def test_undecodable_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"case.pgn"
            p.write_bytes(sample().encode()+b"\xff")
            self.assertGreater(inspect(p)["decode_replacement_chars"],0)
if __name__=="__main__":
    unittest.main()
