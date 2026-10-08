#!/usr/bin/env python3
"""P8-EP8 true searchmoves semantics and legal-convergence regression gates."""
import unittest
from unittest.mock import patch
import chess
from harness import c3x_013_p8ep8_tcec_conditional_uci as ep8

class EP8Tests(unittest.TestCase):
    def test_certified_two_path_convergence(self):
        x=ep8.worlds()
        self.assertEqual(len(x),2)
        self.assertEqual(x["a"][2],"NORMAL_CAPTURE")
        self.assertEqual(x["b"][2],"EN_PASSANT")
        self.assertEqual(x["a"][1].fen(en_passant="fen"),ep8.EXPECTED)
        self.assertEqual(x["a"][1].fen(en_passant="fen"),x["b"][1].fen(en_passant="fen"))
        for key in ("a","b"):
            self.assertIn(x[key][3],x[key][0].legal_moves)

    def test_all_three_arms_have_correct_board_depth_and_searchmoves(self):
        actual=ep8.worlds()
        calls=[]
        def stub(exe,board,depth,forced_reply=None):
            calls.append((board.fen(en_passant="fen"),depth,forced_reply.uci() if forced_reply else None))
            self.assertTrue(board.is_valid())
            if forced_reply is not None:
                self.assertIn(forced_reply,board.legal_moves)
            return {"score_white_cp":50 if forced_reply is not None else 30,
                    "mate_white":None,"nodes":123,"depth_completed":depth,
                    "first_move":forced_reply.uci() if forced_reply else "c4d3",
                    "root_reply_constrained":forced_reply is not None}
        with patch.object(ep8,"measure",stub):
            result=ep8.sample("fake",8,actual)
        self.assertEqual(len(calls),6)
        self.assertEqual([k[1] for k in calls],[8,8,7,8,8,7])
        self.assertEqual(sum(k[2]=="c4b3" for k in calls),2)
        self.assertEqual(result["branches"]["a"]["forced_minus_free_white_cp"],20)
        self.assertTrue(result["equal_endpoint_cold_run_exact"])
        self.assertFalse(result["branches"]["b"]["PV_first_reply_is_convergence_capture"])

    def test_mate_is_not_fake_centipawn_gap(self):
        def stub(exe,board,depth,forced_reply=None):
            return {"score_white_cp":None if forced_reply else 20,
                    "mate_white":2 if forced_reply else None,
                    "nodes":100,"depth_completed":depth,
                    "first_move":"c4b3" if forced_reply else "c4d3",
                    "root_reply_constrained":forced_reply is not None}
        with patch.object(ep8,"measure",stub):
            r=ep8.sample("fake",8,ep8.worlds())
        for k in ("a","b"):
            self.assertIsNone(r["branches"][k]["forced_minus_free_white_cp"])

if __name__=="__main__":
    unittest.main()
