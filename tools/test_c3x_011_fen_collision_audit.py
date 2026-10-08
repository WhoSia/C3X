#!/usr/bin/env python3
"""C3X 0.11 P19 FEN collision negative/positive tests (synthetic only)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c3x_011_fen_collision_audit import audit, read_source

PGN = """[Event "Synthetic"]
[Site "?"]
[Date "2026.10.08"]
[Round "1"]
[White "A"]
[Black "B"]
[Result "*"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 *
"""

class P19CollisionRegression(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/"one.pgn").write_text(PGN, encoding="utf-8")
    def test_legal_worlds(self):
        hashes, stats, example = read_source("A", self.root/"one.pgn", 1, 160)
        self.assertEqual(stats["games"], 1)
        self.assertEqual(len(hashes), 12)
        self.assertEqual(len(example), 12)
    def test_cross_source_shared_worlds_removed(self):
        (self.root/"two.pgn").write_text(PGN, encoding="utf-8")
        result = audit({"A":self.root/"one.pgn", "B":self.root/"two.pgn"}, set(), 1, 160)
        self.assertEqual(result["cross_source_shared_worlds"],12)
        self.assertEqual(result["source"]["A"]["unique_worlds_remaining"],0)
        self.assertEqual(result["source"]["B"]["unique_worlds_remaining"],0)
        self.assertFalse(result["source_preseal_granted"])
    def test_historical_collision_removed(self):
        hashes,_,_ = read_source("A",self.root/"one.pgn",1,160)
        result = audit({"A":self.root/"one.pgn"},set(hashes),1,160)
        self.assertEqual(result["source"]["A"]["historical_collision_worlds"],12)
        self.assertEqual(result["source"]["A"]["unique_worlds_remaining"],0)
    def test_empty_pgn_fails_closed(self):
        (self.root/"one.pgn").write_text("", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "EMPTY_PGN"):
            read_source("A",self.root/"one.pgn",1,160)
    def test_illegal_san_fails_closed(self):
        (self.root/"one.pgn").write_text(PGN.replace("1. e4 e5","1. e5 e5"))
        with self.assertRaisesRegex(ValueError, "ILLEGAL_OR_UNPARSABLE_PGN"):
            read_source("A",self.root/"one.pgn",1,160)
    def test_never_promotes_authority(self):
        result = audit({"A":self.root/"one.pgn"},set(),1,160)
        self.assertEqual(result["verdict"],"AUDIT_ONLY_HISTORICAL_COVERAGE_NOT_SEALED")
        self.assertFalse(result["historical_coverage_proven_complete"])
        self.assertFalse(result["outcomes_opened"])
if __name__=="__main__":
    unittest.main()
