import sys
import unittest
from pathlib import Path

import chess

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "harness"))
from c3x_029_p32_original_history_reply_value_native import (
    material_cp, replay_original, need, perspective)


class P32HistoryValueInputs(unittest.TestCase):
    def example(self):
        history = ["g1f3", "g8f6", "f3g1", "f6g8", "g1f3", "g8f6", "f3g1", "f6g8",
                   "e2e4", "e7e5"]
        b = chess.Board()
        for v in history:
            b.push_uci(v)
        return {
            "full_original_mainline_uci": history,
            "source_ply_before_original_move": 8,
            "played_legal_move_uci": "e2e4",
            "fen4": " ".join(chess.Board().fen().split()[:4])
        }

    def test_history_fen_was_generated_from_actual_prefix(self):
        row = self.example()
        b = chess.Board()
        for v in row["full_original_mainline_uci"][:8]:
            b.push_uci(v)
        row["fen4"] = " ".join(b.fen(en_passant="fen").split()[:4])
        out = replay_original(row)
        self.assertEqual(len(out.move_stack), 8)
        self.assertTrue(out.is_repetition(3))
        self.assertIn(chess.Move.from_uci("e2e4"), out.legal_moves)

    def test_fen_mismatch_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "FROZEN_FEN_MISMATCH"):
            replay_original(self.example())

    def test_material_delta_is_antisymmetric(self):
        b = chess.Board()
        self.assertEqual(material_cp(b, chess.WHITE), 0)
        self.assertEqual(material_cp(b, chess.BLACK), 0)
        b.remove_piece_at(chess.A7)
        self.assertEqual(material_cp(b, chess.WHITE), 100)
        self.assertEqual(material_cp(b, chess.BLACK), -100)

    def test_source_move_checked(self):
        r = self.example()
        b = chess.Board()
        for v in r["full_original_mainline_uci"][:8]:
            b.push_uci(v)
        r["fen4"] = " ".join(b.fen(en_passant="fen").split()[:4])
        r["played_legal_move_uci"] = "e2e3"
        with self.assertRaisesRegex(ValueError, "SOURCE_MOVE_DRIFT"):
            replay_original(r)


if __name__ == "__main__":
    unittest.main()
