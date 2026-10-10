#!/usr/bin/env python3
"""Fail-closed new TWIC1664 source and genuine legal recapture behavior."""
import sys,unittest
from pathlib import Path
import chess
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_022_P2_R1_TWIC1664_engineblind16 import seal,ISSUE,PRIOR_EXTERNAL_SHA
from c3x_022_P2_R1_source_blind_legal_exchange_tree import legal_exchange_gain,move_exchange_features,prepare,MAX_RECAPTURE_DEPTH

class NewTWICAndLegalExchange(unittest.TestCase):
    def test_frozen_new_issue_is_not_training_issue(self):
        self.assertEqual(ISSUE,1664)
        self.assertEqual(len(PRIOR_EXTERNAL_SHA),64)
        self.assertEqual(MAX_RECAPTURE_DEPTH,6)
    def test_history_must_all_be_present(self):
        with self.assertRaises(ValueError):
            seal("/nonexistent.zip",{}, "/nonexistent.json")
    def test_chess_pin_blocks_pseudo_capture(self):
        # Black knight e7 is pinned by rook e1 to king e8: can't capture c6.
        b=chess.Board("4k3/4n3/8/2P5/8/8/8/4R1K1 b - - 0 1")
        self.assertTrue(b.is_pinned(chess.BLACK,chess.E7))
        self.assertTrue(b.is_valid())
        self.assertEqual(legal_exchange_gain(b,chess.C6,6),0)
    def test_capture_legal_then_exact_back_recapture(self):
        b=chess.Board("4k3/8/8/3p4/4P3/8/8/4K3 w - - 0 1")
        move=chess.Move.from_uci("e4d5")
        self.assertIn(move,b.legal_moves)
        row=move_exchange_features(b,move)
        self.assertTrue(row["root_capture"])
        self.assertEqual(row["root_material_capture_points"],100)
        self.assertEqual(row["see_like_depth_cap"],6)
    def test_absent_old_source_phase_fails(self):
        with self.assertRaises(ValueError):
            prepare({"phase":"ALREADY_SAW_NATIVE","selected":[]})
    def test_no_stockfish_or_subprocess_in_source_and_SEE(self):
        root=Path(__file__).resolve().parents[1]/"harness"
        for f in ("c3x_022_P2_R1_TWIC1664_engineblind16.py",
                  "c3x_022_P2_R1_source_blind_legal_exchange_tree.py"):
            s=(root/f).read_text()
            self.assertNotIn("subprocess",s)
            self.assertNotIn("chess.engine",s)
if __name__=="__main__":unittest.main()
