#!/usr/bin/env python3
"""Atomic chess edges are tested independently of Stockfish and motif names."""
import sys
import unittest
from pathlib import Path
import chess
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"harness"))
from c3x_021_P1_atomic_decision_transition_graph import (
    SCHEMA,attack_edges,transition,profile,pins,sha
)

class AtomicTransitionFixtures(unittest.TestCase):
    def test_startpos_all_20_legal_moves_with_unique_native_codes(self):
        d=profile(chess.Board())
        self.assertEqual(d["legal_root_move_count"],20)
        self.assertEqual(len({q["native_move"] for q in d["moves"]}),20)
        self.assertEqual(len({q["move"] for q in d["moves"]}),20)
        self.assertEqual(d["moves"][0]["move"],"a2a3")
        self.assertEqual(d["moves"][0]["reply_legal_move_count"],20)
        self.assertTrue(d["moves"][0]["attack_edge_added"])
        self.assertTrue(d["moves"][0]["attack_edge_removed"])

    def test_pin_is_an_attack_and_legal_response_constraint_not_a_name(self):
        board=chess.Board("4r2k/8/8/8/8/8/4R3/4K3 w - - 0 1")
        self.assertIn(("R","e2"),pins(board))
        self.assertNotIn(chess.Move.from_uci("e2d2"),board.legal_moves)
        good=chess.Move.from_uci("e2e8")
        self.assertIn(good,board.legal_moves)
        out=transition(board,good)
        self.assertEqual(out["move"],"e2e8")
        self.assertTrue(out["root_capture"])
        self.assertTrue(any(row["square"]=="e8" for row in out["occupancy_delta"]))
        self.assertEqual(out["reply_captures_destination"],[])

    def test_ep_capture_does_not_capture_on_target_square(self):
        board=chess.Board("7k/8/8/3pP3/8/8/8/K7 w - d6 0 1")
        m=chess.Move.from_uci("e5d6")
        self.assertIn(m,board.legal_moves)
        out=transition(board,m)
        self.assertTrue(out["root_en_passant"])
        self.assertTrue(out["root_capture"])
        self.assertTrue(any(x["square"]=="d5" for x in out["occupancy_delta"]))

    def test_check_changes_response_fan_and_move_context(self):
        board=chess.Board("7k/8/8/8/8/8/6R1/K7 w - - 0 1")
        move=chess.Move.from_uci("g2g8")
        self.assertIn(move,board.legal_moves)
        x=transition(board,move)
        self.assertTrue(x["after_root_opponent_in_check"])
        self.assertTrue(x["reply_legal_move_count"]>=1)
        self.assertEqual(x["reply_check_count"],0)

    def test_illegal_root_fails(self):
        with self.assertRaises(ValueError):
            transition(chess.Board(),chess.Move.from_uci("e2e5"))

    def test_state_hash_stable_without_engine_dependency(self):
        board=chess.Board()
        a=profile(board)
        b=profile(board)
        self.assertEqual(sha(a),sha(b))
        self.assertEqual(SCHEMA,"c3x021-p1-atomic-move-affordance-state-transitions-v1")
        self.assertTrue(all("root_capture" in q for q in a["moves"]))
        self.assertTrue(all("after_root_opponent_in_check" in q for q in a["moves"]))
if __name__=="__main__":unittest.main()
