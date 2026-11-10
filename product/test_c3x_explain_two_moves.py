"""C3X 0.30 P1 product explanation contracts. Fake engine only in unit tests."""
import unittest
from unittest.mock import Mock

import chess
import chess.engine

from c3x_explain_two_moves import (
    verify_board_and_pair,measured_features,difference_facts,
    root_analysis,ranked_replies_and_own_responses,generate,make_markdown,
    ROOT_DEPTHS,REPLY_DEPTH,SCHEMA
)


class SimulatedEngine:
    def __init__(self):
        self.calls=0

    def analyse(self,board,limit,root_moves=None,multipv=None,game=None,info=None):
        self.calls+=1
        depth=limit.depth
        if root_moves is not None:
            move=root_moves[0]
            cp=50 if move.uci()=="e2e4" else 40
            return {"depth":depth,"nodes":177,"pv":[move],
                    "score":chess.engine.PovScore(chess.engine.Cp(cp),board.turn)}
        if multipv:
            moves=sorted(board.legal_moves,key=lambda m:m.uci())[:multipv]
            return [{"depth":depth,"nodes":222,
                     "pv":[move],
                     "score":chess.engine.PovScore(chess.engine.Cp(-15),board.turn)}
                     for move in moves]
        m=next(iter(board.legal_moves))
        return {"depth":depth,"nodes":333,"pv":[m],
                "score":chess.engine.PovScore(chess.engine.Cp(10),board.turn)}


class ProductContracts(unittest.TestCase):
    def setUp(self):
        self.board=chess.Board()

    def test_legal_pair(self):
        b,a,c=verify_board_and_pair(self.board.fen(),"e2e4","d2d4")
        self.assertEqual(a.uci(),"e2e4")
        self.assertEqual(c.uci(),"d2d4")

    def test_identical_or_illegal_refused(self):
        for a,b in (("e2e4","e2e4"),("e2e5","d2d4")):
            with self.assertRaisesRegex(ValueError,"TWO_DISTINCT"):
                verify_board_and_pair(self.board.fen(),a,b)

    def test_invalid_fen(self):
        with self.assertRaisesRegex(ValueError,"BAD_FEN"):
            verify_board_and_pair("not_a_fen","e2e4","d2d4")

    def test_check_capture_facts_true(self):
        b=chess.Board()
        for u in ("f2f3","e7e5","g2g4"):b.push_uci(u)
        x=measured_features(b,chess.Move.from_uci("d8h4"))
        self.assertTrue(x["gives_check"])
        self.assertTrue(x["opponent_in_check_after_move"])
        self.assertEqual(x["san"],"Qh4#")

        b=chess.Board()
        for u in ("e2e4","d7d5"):b.push_uci(u)
        self.assertTrue(measured_features(b,chess.Move.from_uci("e4d5"))["is_capture"])

    def test_shared_development_not_fabricated_difference(self):
        a=measured_features(self.board,chess.Move.from_uci("e2e4"))
        b=measured_features(self.board,chess.Move.from_uci("d2d4"))
        d=difference_facts(a,b)
        self.assertIn("is_capture",d["suppressed_shared_measured_facts"])
        self.assertTrue(d["shared_features_not_proposed_as_differentiating_reasons"])

    def test_engine_depth_gate(self):
        mock=Mock()
        mock.analyse.return_value={
            "depth":7,"nodes":100,"pv":[chess.Move.from_uci("e2e4")],
            "score":chess.engine.PovScore(chess.engine.Cp(1),chess.WHITE)}
        with self.assertRaisesRegex(ValueError,"INCOMPLETE"):
            root_analysis(self.board,chess.Move.from_uci("e2e4"),mock,8)

    def test_engine_forced_move_pv_gate(self):
        mock=Mock()
        mock.analyse.return_value={
            "depth":8,"nodes":100,"pv":[chess.Move.from_uci("d2d4")],
            "score":chess.engine.PovScore(chess.engine.Cp(1),chess.WHITE)}
        with self.assertRaisesRegex(ValueError,"FORCED_ROOT"):
            root_analysis(self.board,chess.Move.from_uci("e2e4"),mock,8)

    def test_actual_chess_branch_structure_mock_only(self):
        engine=SimulatedEngine()
        out=generate(self.board,"e2e4","d2d4",engine)
        self.assertEqual(out["schema"],SCHEMA)
        self.assertEqual(out["candidate_A_minus_B_cp_by_depth_or_null"],{"8":10,"10":10})
        self.assertEqual(len(out["root_candidates"]),2)
        self.assertEqual(engine.calls,16) # 4 root calls + 2*(1 multi +3 own)
        for row in out["root_candidates"]:
            probe=row["opponent_reply_probe"]
            self.assertEqual(probe["sampled_reply_count"],3)
            self.assertEqual(len(probe["reply_lines"]),3)
            self.assertGreater(probe["opponent_replies_total"],3)

    def test_markup_usable_and_limits_visible(self):
        result=generate(self.board,"e2e4","d2d4",SimulatedEngine())
        md=make_markdown(result)
        self.assertIn("# C3X — 두 후보 수의 차이는 무엇인가?",md)
        self.assertIn("최악값",md)
        self.assertIn("인과",md)
        self.assertIn("| 8 |",md)

    def test_terminal_rule_state_refused(self):
        b=chess.Board("8/8/8/8/8/8/4K3/7k w - - 0 1")
        with self.assertRaisesRegex(ValueError,"TERMINAL"):
            verify_board_and_pair(b.fen(),"e2e3","e2e4")


if __name__=="__main__":
    unittest.main()
