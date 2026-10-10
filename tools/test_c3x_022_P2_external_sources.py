#!/usr/bin/env python3
"""C3X022 P2 engine-free two-ecology source and leakage guards."""
import csv
import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
import chess
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_022_P2_external_TWIC_puzzle_engineblind_selector import (
    HISTORY,TWIC_ISSUE,TWIC_URL,PUZZLE_URL,prior_fens,twic,puzzles)

class ExternalSourceFixtures(unittest.TestCase):
    def test_exact_eight_prior_source_corpora(self):
        self.assertEqual(HISTORY,("prior","october","november","december","january",
                                  "february","march","april"))
        with self.assertRaises(ValueError):
            prior_fens({"prior":"/tmp/not_exists"})
    def test_archive_provenance_is_original(self):
        self.assertEqual(TWIC_ISSUE,1656)
        self.assertEqual(TWIC_URL,"https://theweekinchess.com/zips/twic1656g.zip")
        self.assertEqual(PUZZLE_URL,"https://database.lichess.org/lichess_db_puzzle.csv.zst")
    def test_engine_free_script_and_no_twic_full_mainline_output(self):
        p=Path(__file__).resolve().parents[1]/"harness"/"c3x_022_P2_external_TWIC_puzzle_engineblind_selector.py"
        s=p.read_text()
        self.assertNotIn("subprocess",s)
        self.assertNotIn("chess.engine",s)
        self.assertNotIn('"full_original_mainline_uci"',s)
        self.assertNotIn('"source_headers"',s)
        self.assertIn('"source_game_sha256"',s)
    def test_invalid_or_too_small_TWIC_archive_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            z=Path(td)/"twic.zip"
            with zipfile.ZipFile(z,"w") as f:
                f.writestr("twic1656.pgn","[Event \"small\"]\n\n1. e4 e5 *\n")
            with self.assertRaises(RuntimeError) as e:
                twic(z,set())
            self.assertIn("TWIC_ELIGIBLE_512_NOT_FOUND",str(e.exception))
    def test_puzzle_solver_fen_is_after_scripted_opponent_move(self):
        board=chess.Board()
        before=board.fen()
        script="e2e4 e7e5"
        moves=[chess.Move.from_uci(m) for m in script.split()]
        self.assertIn(moves[0],board.legal_moves)
        board.push(moves[0])
        self.assertIn(moves[1],board.legal_moves)
        self.assertNotEqual(before,board.fen())
        self.assertEqual(board.turn,chess.BLACK)
        self.assertEqual(board.legal_moves.count(),20)
    def test_invalid_puzzle_archive_fails_no_silent_source_change(self):
        import zstandard
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"p.csv.zst"
            raw=b"PuzzleId,FEN,Moves,Rating,Themes,GameUrl\n"
            p.write_bytes(zstandard.ZstdCompressor().compress(raw))
            with self.assertRaises(RuntimeError):
                puzzles(p,set())
if __name__=="__main__":unittest.main()
