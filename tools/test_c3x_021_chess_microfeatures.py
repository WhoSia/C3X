#!/usr/bin/env python3
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
import chess
from c3x_021_march_sourceonly_chess_microfeatures import board_features,absolute_pins,passed_pawns,relative_pin_rays

class ChessSourceMicrostructure(unittest.TestCase):
    def test_absolute_pin_to_king(self):
        board=chess.Board("4r2k/8/8/8/8/8/4R3/4K3 w - - 0 1")
        pins=absolute_pins(board,chess.WHITE)
        self.assertEqual([x["pinned_square"] for x in pins],["e2"])
        self.assertFalse(any(x["pinned_square"]=="e2" for x in absolute_pins(board,chess.BLACK)))
    def test_relative_xray_is_not_absolute_pin(self):
        board=chess.Board("4r2k/8/8/8/8/8/4B3/K3Q3 w - - 0 1")
        rays=relative_pin_rays(board,chess.WHITE)
        self.assertTrue(any(x["blocker"]=="e2" and x["rear_target"]=="e1" for x in rays))
        self.assertFalse(any(x["pinned_square"]=="e2" for x in absolute_pins(board,chess.WHITE)))
    def test_passed_pawn_forward_opponents(self):
        board=chess.Board("7k/8/8/3p4/8/2P5/8/K7 w - - 0 1")
        self.assertNotIn("c3",passed_pawns(board,chess.WHITE))
        board2=chess.Board("7k/8/8/7p/8/2P5/8/K7 w - - 0 1")
        self.assertIn("c3",passed_pawns(board2,chess.WHITE))
    def test_valid_source_features_and_illegal_fen(self):
        f=board_features("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -")
        self.assertEqual(f["legal_move_count"],20)
        self.assertEqual(f["legal_check_moves"],[])
        self.assertTrue(f["unknown_or_unproven"])
        with self.assertRaises(ValueError):
            board_features("invalid fen")
    def test_engine_free(self):
        s=(Path(__file__).resolve().parents[1]/"harness"/"c3x_021_march_sourceonly_chess_microfeatures.py").read_text()
        self.assertNotIn("subprocess",s)
        self.assertNotIn("chess.engine",s)
        self.assertNotIn("Stockfish",s)
if __name__=="__main__": unittest.main()
