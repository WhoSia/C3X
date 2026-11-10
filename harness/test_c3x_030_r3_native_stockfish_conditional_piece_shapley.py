"""R3 valid chess-variant lattice and real UCI-protocol mock contracts.

Synthetic engine scores are NOT Stockfish results.
"""
import unittest
from unittest.mock import Mock

import chess
import chess.engine

from c3x_030_r3_native_stockfish_conditional_piece_shapley import (
    static_board, coalition_board, choose_complete_three,
    white_win_probability, native_evaluate, run, N_FEATURES)


def fixture_engine():
    engine = Mock()
    def analyse(board, _limit, **_):
        # Deterministic chess-derived synthetic score from board inventory,
        # not a physical Stockfish experiment or chess ground truth.
        pawns = len(board.pieces(chess.PAWN, chess.WHITE))
        knights = len(board.pieces(chess.KNIGHT, chess.BLACK))
        cp = 100 * pawns - 40 * knights
        return {
            "depth": 10, "nodes": 111, "pv": [],
            "score": chess.engine.PovScore(chess.engine.Cp(cp), chess.WHITE)
        }
    engine.analyse.side_effect = analyse
    return engine


class NativePieceSHAPContracts(unittest.TestCase):
    def setUp(self):
        self.board=chess.Board()
    
    def test_all_eight_legal_coalitions_exactly_once(self):
        pieces, boards=choose_complete_three(self.board)
        self.assertEqual(len(pieces),3)
        self.assertEqual(len(boards),8)
        self.assertTrue(all(b.is_valid() for b in boards))
        self.assertEqual(len({b.fen() for b in boards}),8)
        self.assertEqual(boards[7].board_fen(),self.board.board_fen())

    def test_all_subsets_still_contain_both_kings(self):
        _, boards=choose_complete_three(self.board)
        for b in boards:
            self.assertEqual(len(b.pieces(chess.KING,chess.WHITE)),1)
            self.assertEqual(len(b.pieces(chess.KING,chess.BLACK)),1)
            
    def test_exact_piece_names_from_genuine_source_positions(self):
        source={"case_id":"synthetic:case","event_family":"synthetic:event"}
        roots=[{"root":"e2e4"},{"root":"d2d4"}]
        z=run([(source,self.board,roots)],fixture_engine())
        self.assertEqual(z["total_actual_native_search_queries"],8)
        self.assertEqual(z["total_actual_native_nodes"],8*111)
        self.assertEqual(len(z["cases"][0]["selected_piece_names"]),3)
        self.assertEqual(len(z["cases"][0]["masked_coalition_evaluations"]),8)
        self.assertAlmostEqual(z["cases"][0]["conditional_shapley"]["efficiency_residual"],0)
        self.assertTrue(z["not_full_spinnato_piece_SHAP_benchmark"])

    def test_reject_mask_out_of_bounds(self):
        pieces, _ = choose_complete_three(self.board)
        with self.assertRaisesRegex(ValueError,"MASK_RANGE"):
            coalition_board(static_board(self.board),pieces,8)

    def test_explicit_white_perspective(self):
        self.assertAlmostEqual(white_win_probability(0),0.5)
        self.assertGreater(white_win_probability(100),0.5)
        self.assertLess(white_win_probability(-100),0.5)
        self.assertAlmostEqual(white_win_probability(-10000),0.0)

    def test_reject_non_numeric_cp(self):
        with self.assertRaisesRegex(ValueError,"INTEGER_WHITE_CP"):
            white_win_probability(0.0)

    def test_engine_score_is_mate_surrogate_and_flagged(self):
        e=Mock()
        e.analyse.return_value={
            "depth":10,"nodes":20,
            "score":chess.engine.PovScore(chess.engine.Mate(3),chess.WHITE)}
        value=native_evaluate(self.board,e)
        self.assertTrue(value["is_mate_score"])
        self.assertEqual(value["mate_plies"],3)
        self.assertLessEqual(value["white_score_cp_or_arbitrary_mate_surrogate"],10000)

    def test_reject_incomplete_engine_depth(self):
        e=fixture_engine()
        e.analyse.return_value={
            "depth":9,"nodes":12,
            "score":chess.engine.PovScore(chess.engine.Cp(1),chess.WHITE)}
        with self.assertRaisesRegex(ValueError,"INCOMPLETE_NATIVE"):
            native_evaluate(self.board,e)

    def test_terminal_source_fails(self):
        b=chess.Board("8/8/8/8/8/8/4K3/7k w - - 0 1")
        with self.assertRaisesRegex(ValueError,"TERMINAL"):
            static_board(b)


if __name__=="__main__":
    unittest.main()
