#!/usr/bin/env python3
"""Forecasts must be literal UCI, sealed before any native reader suppression."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_022_P2_two_stage_exact_move_scout import exact_forecast,native_world,ECOLOGIES,WORLDS,stockfish16_encoded_move,source_depth_ladder
import chess
class SpecificUciForecasts(unittest.TestCase):
    def test_disagree_cross_order_restores_exact_uci(self):
        o=exact_forecast("e2e4","d2d4","O",True)
        f=exact_forecast("e2e4","d2d4","F",True)
        self.assertEqual(o["predicted_UCI"],"d2d4")
        self.assertEqual(f["predicted_UCI"],"e2e4")
        self.assertTrue(o["predicted_flip"] and f["predicted_flip"])
    def test_equal_order_predicts_no_flip(self):
        for order in WORLDS:
            z=exact_forecast("e2e4","e2e4",order,True)
            self.assertEqual(z["predicted_UCI"],"e2e4")
            self.assertFalse(z["predicted_flip"])
    def test_no_target_is_not_a_positive_or_negative(self):
        v=exact_forecast("e2e4","d2d4","O",False)
        self.assertEqual(v["status"],"NO_TREATMENT")
        self.assertIsNone(v["predicted_UCI"])
        self.assertIsNone(v["predicted_flip"])
    def test_unreconstructible_clock_rejected(self):
        world={"fen4":"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -",
               "played_legal_move_uci":"e2e4","source_root_legal_count":20}
        with self.assertRaises(RuntimeError):
            native_world(world)
    def test_pinned_sf16_castling_internal_code_includes_type_and_rook_origin(self):
        board=chess.Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
        m=chess.Move.from_uci("e1c1")
        self.assertIn(m,board.legal_moves)
        self.assertEqual(stockfish16_encoded_move(board,m),(3<<14)+(4<<6)+0)
        row={"fen4":" ".join(board.fen().split()[:4]),
             "source_halfmove_clock":0,"source_fullmove_number":1,
             "played_legal_move_uci":"e1c1","native_move":4*64+2,
             "source_root_legal_count":board.legal_moves.count()}
        world,clock,changed=native_world(row)
        self.assertEqual(world["native_move"],49408)
        self.assertEqual(world["source_chess_coordinate_move"],258)
    def test_pinned_sf16_en_passant_internal_code(self):
        b=chess.Board("7k/8/8/3pP3/8/8/8/K7 w - d6 0 1")
        m=chess.Move.from_uci("e5d6")
        self.assertIn(m,b.legal_moves)
        self.assertTrue(b.is_en_passant(m))
        self.assertEqual(stockfish16_encoded_move(b,m),
                         (2<<14)+m.from_square*64+m.to_square)
    def test_normal_move_bits_unchanged(self):
        b=chess.Board()
        m=chess.Move.from_uci("e2e4")
        self.assertEqual(stockfish16_encoded_move(b,m),
                         m.from_square*64+m.to_square)
    def test_early_terminal_puzzle_does_not_invent_missing_depths(self):
        d=source_depth_ladder([])
        self.assertEqual(d,{})
        seen=[{"kind":"after_sort","depth":1,"first_move":123,
               "value":0,"trial":1}]
        partial=source_depth_ladder(seen)
        self.assertIn("1",partial)
        self.assertNotIn("12",partial)
        self.assertTrue(partial["1"]["terminal_or_source_trace_partial"])
    def test_legacy_no_lineage_guard_is_still_strict_by_default(self):
        s=(Path(__file__).resolve().parents[1]/"harness"/
           "c3x_018_native_TT_lineage_factorial_6_8.py").read_text()
        self.assertIn("allow_empty_lineage=False",s)
        self.assertIn('need(events or allow_empty_lineage, "NO_LINEAGE_EVENTS")',s)
    def test_puzzles_and_twic_preserved_as_distinct_ecologies(self):
        self.assertEqual(ECOLOGIES,("twic","lichess_puzzles"))
        p=Path(__file__).resolve().parents[1]/"harness"/"c3x_022_P2_two_stage_exact_move_scout.py"
        s=p.read_text()
        self.assertNotIn('"V",',s)
        self.assertIn("first_pair(discoveries[order],RULES[role])",s)
        self.assertIn("root_depth_ladder",s)
if __name__=="__main__":unittest.main()
